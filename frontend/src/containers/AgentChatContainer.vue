<script setup lang="ts">
import type { Agent } from '@/hooks/useAgents'
import { useRoute } from 'vue-router'
import { ref, onMounted, computed, nextTick } from 'vue'
import { useAgents } from '@/hooks/useAgents'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar } from '@/components/ui/avatar'
import { Bot, Send, User, ArrowLeft, Paperclip, X, Trash2 } from 'lucide-vue-next'
import { useLangchain } from '@/hooks/useLangchain'
import type { AIModel } from '@/hooks/useLangchain'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useToast } from '@/components/ui/toast/use-toast'
import { useAuthStore } from '@/stores/auth'
import JsonMessageContent from '@/components/messageMarkdown/JsonMessageContent.vue'
import MarkdownContent from '@/components/messageMarkdown/MarkdownContent.vue'
import { useFiles } from '@/hooks/useFiles'
import { Progress } from '@/components/ui/progress/index'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  steps?: Array<{
    step: string
    description: string
    tool_used?: string
    input?: Record<string, any>
    output?: string | number
  }>
}

// Define a type for date indicators
interface DateIndicator {
  id: string;
  type: 'date';
  date: Date;
  
}

// Define a type for chat messages (already have ChatMessage interface)
type MessageItem = {
  id: string | number;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  steps?: Array<{
    step: string;
    description: string;
    tool_used?: string;
    input?: Record<string, any>;
    output?: string | number;
  }>;
};

// Type for either a message or date indicator
type ChatItem = MessageItem | DateIndicator;

// Define a type for content blocks
interface ContentBlock {
  type: 'markdown' | 'json' | string; // Extensible for future types
  content: string;
}

const route = useRoute()
const agentId = route.params.agentId as string
const { toast } = useToast()

const { getAgent, updateAgent, clearAgentHistory } = useAgents()
const { getModels, askAgent } = useLangchain()
const authStore = useAuthStore()
const { 
  uploadFiles,
  formatFileSize,
  isFileTypeAllowed,
  uploadProgress,
  loading: isFileUploading
} = useFiles()

const availableModels = ref<AIModel[]>([])
const selectedModel = ref<string>('')

const agent = ref<Agent | null>(null)
const messageInput = ref('')
const isLoading = ref(false)

const logsContainer = ref()

// Add file handling refs
const fileInput = ref<HTMLInputElement | null>(null)
const selectedFiles = ref<File[]>([])
const uploadError = ref('')
const isDraggingFile = ref(false)  // New ref for tracking drag state

// Add a ref for the dialog state
const isClearHistoryOpen = ref(false)

// Add a helper function to format dates
const formatDate = (date: Date) => {
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  
  if (date.toDateString() === today.toDateString()) {
    return 'Today';
  } else if (date.toDateString() === yesterday.toDateString()) {
    return 'Yesterday';
  } else {
    return new Intl.DateTimeFormat('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined 
    }).format(date);
  }
};

// Modified computed property with proper typing
const messagesWithDateIndicators = computed(() => {
  // Initialize with a welcome message using agent's created_at timestamp
  const welcomeMessage: MessageItem = {
    id: 'welcome',
    content: `Hello! I'm ${agent.value?.name || 'your AI assistant'}. How can I help you today?`,
    sender: 'ai',
    timestamp: agent.value?.created_at ? new Date(agent.value.created_at) : new Date(),
    steps: []
  };
  
  if (!agent.value?.chat_history) return [welcomeMessage];
  
  const chatMessages = (agent.value.chat_history as ChatMessage[]).map((msg: ChatMessage, index: number) => ({
    id: index,
    content: msg.content,
    sender: msg.role === 'user' ? 'user' : 'ai' as 'user' | 'ai',
    timestamp: new Date(msg.timestamp),
    steps: msg.steps
  }));
  
  // Combine welcome message with chat history if needed
  const allMessages = chatMessages.length === 0 || chatMessages[0].sender !== 'ai' 
    ? [welcomeMessage, ...chatMessages]
    : chatMessages;
  
  // Add date indicators between messages
  const result: ChatItem[] = [];
  let currentDate: Date | null = null;
  
  allMessages.forEach(message => {
    const messageDate = new Date(message.timestamp);
    messageDate.setHours(0, 0, 0, 0);  // Reset time to start of day
    
    if (!currentDate || messageDate.getTime() !== currentDate.getTime()) {
      currentDate = messageDate;
      // Add a date indicator
      result.push({
        id: `date-${messageDate.getTime()}`,
        type: 'date',
        date: messageDate
      });
    }
    
    result.push(message);
  });
  
  return result;
});

const scrollToBottom = () => {
  nextTick(() => {
    const messagesContainer = document.querySelector('.space-y-4')
    if (messagesContainer) {
      const lastMessage = messagesContainer.lastElementChild
      if (lastMessage) {
        lastMessage.scrollIntoView({ behavior: 'smooth', block: 'end' })
      }
    }
  })
}

// Add function to auto-resize the textarea based on content
const autoResizeTextarea = (e: Event) => {
  const textarea = e.target as HTMLTextAreaElement
  
  // Reset height to auto first to get the correct scrollHeight
  textarea.style.height = 'auto'
  
  // Set the height to match content (with a max height applied in CSS)
  textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`
}

// Modified sendMessage function to handle file uploads
const sendMessage = async () => {
  if ((!messageInput.value.trim() && !selectedFiles.value.length) || !agent.value) return

  try {
    const userId = authStore.user?.id
    if (!userId) {
      throw new Error('User ID not found')
    }

    // Handle file uploads first if there are any files selected
    let fileDetails = ''
    if (selectedFiles.value.length > 0) {
      isLoading.value = true

      // Upload the files
      const results = await uploadFiles(
        agentId,
        selectedFiles.value, 
        userId,
        (progress) => {} // We're using the reactive uploadProgress from useFiles
      )
      
      // Add file details to the message if files were uploaded successfully
      if (results.length > 0) {
        fileDetails = '\n'
        results.forEach(file => {
          fileDetails += `- ${file.filename} (${formatFileSize(file.file_size)})\n`
        })
        
        // Clear selected files after successful upload
        selectedFiles.value = []
      }
    }

    // Prepare the message content
    let finalMessage = messageInput.value.trim()
    
    // If we have files but no message, add a default message
    if (!finalMessage && fileDetails) {
      finalMessage = 'I\'ve shared the following files:' + fileDetails
    } 
    // If we have both a message and files, append the file details
    else if (finalMessage && fileDetails) {
      finalMessage += fileDetails
    }
    
    // Only proceed if we have a message to send (from input or file upload)
    if (!finalMessage) {
      isLoading.value = false
      return
    }

    // Add user message immediately to chat history
    const userMessage: ChatMessage = {
      role: 'user',
      content: finalMessage,
      timestamp: new Date().toISOString()
    }
    
    // Update agent's chat history locally
    if (!agent.value.chat_history) {
      agent.value.chat_history = []
    }
    agent.value.chat_history.push(userMessage)
    isLoading.value = true
    
    // Clear input right after sending
    messageInput.value = ''
    
    // Scroll to bottom after adding user message
    scrollToBottom()

    // Get AI response
    await askAgent(
      finalMessage,
      userId,
      agent.value.id,
      agent.value.model_id
    )

    // Refresh the agent to get the updated chat history with AI response
    agent.value = await getAgent(agentId)
    
    // Scroll to bottom again after getting AI response
    scrollToBottom()

  } catch (err) {
    // Remove the user message if there was an error
    if (agent.value?.chat_history) {
      agent.value.chat_history.pop()
    }
    
    toast({
      title: 'Error',
      description: err instanceof Error ? err.message : 'Failed to send message',
      variant: 'destructive',
    })
  } finally {
    isLoading.value = false
  }
}

const handleModelChange = async (value: string | number | null | Record<string, any>) => {
  try {
    if (!agent.value || !value || typeof value !== 'string') return
    
    const success = await updateAgent(agent.value.id, {
      model_id: value
    })
    
    if (success) {
      agent.value.model_id = value
      toast({
        title: 'Model updated',
        description: 'The agent model has been updated successfully.',
      })
    } else {
      toast({
        title: 'Update failed',
        description: 'Failed to update the agent model. Please try again.',
        variant: 'destructive',
      })
    }
  } catch (err) {
    toast({
      title: 'Error',
      description: err instanceof Error ? err.message : 'An unexpected error occurred',
      variant: 'destructive',
    })
  }
}

// Function to parse message content into blocks
const parseMessageToBlocks = (text: string): ContentBlock[] => {
  if (!text) return [];
  
  const blocks: ContentBlock[] = [];
  const jsonBlockRegex = /```json\n([\s\S]*?)\n```/g;
  
  let lastIndex = 0;
  let match;
  
  // Find all JSON blocks and extract them
  while ((match = jsonBlockRegex.exec(text)) !== null) {
    // Add text before the json block as markdown
    if (match.index > lastIndex) {
      const textBefore = text.substring(lastIndex, match.index).trim();
      if (textBefore) {
        blocks.push({ type: 'markdown', content: textBefore });
      }
    }
    
    // Add the json block
    blocks.push({ type: 'json', content: match[1].trim() });
    
    lastIndex = match.index + match[0].length;
  }
  
  // Add remaining text after the last json block as markdown
  if (lastIndex < text.length) {
    const textAfter = text.substring(lastIndex).trim();
    if (textAfter) {
      blocks.push({ type: 'markdown', content: textAfter });
    }
  }
  
  // If no blocks were found (no json), add the entire text as markdown
  if (blocks.length === 0 && text.trim()) {
    blocks.push({ type: 'markdown', content: text.trim() });
  }
  
  return blocks;
}

// Handle file selection
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (!target.files?.length) return
  
  const files = Array.from(target.files)
  const supportedFiles: File[] = []
  const unsupportedFiles: string[] = []
  const oversizedFiles: string[] = []
  
  // Validate files
  files.forEach(file => {
    if (file.size > 50 * 1024 * 1024) { // 50MB
      oversizedFiles.push(file.name)
    } else if (!isFileTypeAllowed(file)) {
      unsupportedFiles.push(file.name)
    } else {
      supportedFiles.push(file)
    }
  })
  
  // Handle errors for oversized files
  if (oversizedFiles.length > 0) {
    const fileNames = oversizedFiles.length > 3 
      ? `${oversizedFiles.slice(0, 3).join(', ')} and ${oversizedFiles.length - 3} more` 
      : oversizedFiles.join(', ')
    
    uploadError.value = `File${oversizedFiles.length > 1 ? 's' : ''} exceeding 50MB size limit: ${fileNames}`
    
    toast({
      title: 'Files too large',
      description: `${oversizedFiles.length} file${oversizedFiles.length > 1 ? 's' : ''} exceed the 50MB size limit`,
      variant: 'destructive',
    })
  }
  
  // Handle unsupported file types
  if (unsupportedFiles.length > 0) {
    const fileNames = unsupportedFiles.length > 3 
      ? `${unsupportedFiles.slice(0, 3).join(', ')} and ${unsupportedFiles.length - 3} more` 
      : unsupportedFiles.join(', ')
    
    if (!oversizedFiles.length) {
      uploadError.value = `Unsupported file type${unsupportedFiles.length > 1 ? 's' : ''}: ${fileNames}`
    }
    
    toast({
      title: 'Unsupported file type',
      description: `${unsupportedFiles.length} file${unsupportedFiles.length > 1 ? 's' : ''} of unsupported type were removed`,
      variant: 'destructive',
    })
  }
  
  // Add supported files to selection
  if (supportedFiles.length > 0) {
    // Only clear error if we have valid files to add
    if (supportedFiles.length === files.length) {
      uploadError.value = ''
    }
    selectedFiles.value = [...selectedFiles.value, ...supportedFiles]
    
    // Show toast if some files were accepted
    if (unsupportedFiles.length > 0 || oversizedFiles.length > 0) {
      toast({
        title: 'Files added',
        description: `${supportedFiles.length} file${supportedFiles.length > 1 ? 's' : ''} were added successfully`,
      })
    }
  }
  
  // Reset file input
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// Drag and drop handlers
const handleDragEnter = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
  isDraggingFile.value = true
}

const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
}

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
  
  // Only set dragging to false if leaving the main container
  if (e.currentTarget === e.target) {
    isDraggingFile.value = false
  }
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
  isDraggingFile.value = false
  
  const droppedFiles = e.dataTransfer?.files
  if (!droppedFiles?.length) return
  
  const files = Array.from(droppedFiles)
  const supportedFiles: File[] = []
  const unsupportedFiles: string[] = []
  const oversizedFiles: string[] = []
  
  // Validate files
  files.forEach(file => {
    if (file.size > 50 * 1024 * 1024) { // 50MB
      oversizedFiles.push(file.name)
    } else if (!isFileTypeAllowed(file)) {
      unsupportedFiles.push(file.name)
    } else {
      supportedFiles.push(file)
    }
  })
  
  // Handle errors for oversized files
  if (oversizedFiles.length > 0) {
    const fileNames = oversizedFiles.length > 3 
      ? `${oversizedFiles.slice(0, 3).join(', ')} and ${oversizedFiles.length - 3} more` 
      : oversizedFiles.join(', ')
    
    uploadError.value = `File${oversizedFiles.length > 1 ? 's' : ''} exceeding 50MB size limit: ${fileNames}`
    
    toast({
      title: 'Files too large',
      description: `${oversizedFiles.length} file${oversizedFiles.length > 1 ? 's' : ''} exceed the 50MB size limit`,
      variant: 'destructive',
    })
  }
  
  // Handle unsupported file types
  if (unsupportedFiles.length > 0) {
    const fileNames = unsupportedFiles.length > 3 
      ? `${unsupportedFiles.slice(0, 3).join(', ')} and ${unsupportedFiles.length - 3} more` 
      : unsupportedFiles.join(', ')
    
    if (!oversizedFiles.length) {
      uploadError.value = `Unsupported file type${unsupportedFiles.length > 1 ? 's' : ''}: ${fileNames}`
    }
    
    toast({
      title: 'Unsupported file type',
      description: `${unsupportedFiles.length} file${unsupportedFiles.length > 1 ? 's' : ''} of unsupported type were removed`,
      variant: 'destructive',
    })
  }
  
  // Add supported files to selection
  if (supportedFiles.length > 0) {
    // Only clear error if we have valid files to add
    if (supportedFiles.length === files.length) {
      uploadError.value = ''
    }
    selectedFiles.value = [...selectedFiles.value, ...supportedFiles]
    
    // Show toast if some files were accepted
    if (unsupportedFiles.length > 0 || oversizedFiles.length > 0) {
      toast({
        title: 'Files added',
        description: `${supportedFiles.length} file${supportedFiles.length > 1 ? 's' : ''} were added successfully`,
      })
    }
  }
}

// Remove file from selection
const removeFile = (index: number) => {
  selectedFiles.value = selectedFiles.value.filter((_, i) => i !== index)
}

// File selection panel UI without the buttons
const getFileListLabel = () => {
  if (selectedFiles.value.length === 0) return ''
  return `Selected Files (${selectedFiles.value.length})`
}

// Add function to clear chat history
const clearHistory = async () => {
  try {
    isLoading.value = true
    const success = await clearAgentHistory(agentId)
    
    if (success) {
      // Update local agent data
      if (agent.value && agent.value.chat_history) {
        agent.value.chat_history = []
      }
      
      toast({
        title: 'History cleared',
        description: 'Chat history has been cleared successfully.',
      })
      
      // Close the dialog
      isClearHistoryOpen.value = false
    } else {
      toast({
        title: 'Error',
        description: 'Failed to clear chat history. Please try again.',
        variant: 'destructive',
      })
    }
  } catch (err) {
    toast({
      title: 'Error',
      description: err instanceof Error ? err.message : 'An unexpected error occurred',
      variant: 'destructive',
    })
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  agent.value = await getAgent(agentId)
  availableModels.value = await getModels()
  if (agent.value) {
    selectedModel.value = agent.value.model_id
    // Scroll to bottom if there are messages when the component is mounted
    if (agent.value.chat_history?.length) {
      scrollToBottom()
    }
  }
})

</script>

<template>
  <div 
    class="flex flex-col h-[calc(100vh-4rem)]"
    @dragenter="handleDragEnter"
    @dragover="handleDragOver" 
    @dragleave="handleDragLeave"
    @drop="handleDrop"
    :class="{ 'file-drop-active': isDraggingFile }"
  >
    <!-- Header -->
    <div class="border-b p-4 bg-card">
      <!-- Navigation and Agent Info -->
      <div class="flex items-center gap-3 mb-3">
        <Button variant="ghost" size="icon" @click="$router.push('/agents')" class="shrink-0">
          <ArrowLeft class="h-4 w-4" />
        </Button>
        <Avatar class="h-10 w-10 bg-primary/10 shrink-0">
          <Bot class="h-6 w-6 text-primary" />
        </Avatar>
        <div class="min-w-0 flex-1">
          <h1 class="text-xl font-semibold truncate">{{ agent?.name }}</h1>
          <p class="text-sm text-muted-foreground line-clamp-1">{{ agent?.description }}</p>
        </div>
      </div>

      <!-- Controls and Settings -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <!-- Tool Categories -->
        <div v-if="agent?.tool_categories?.length" class="flex flex-wrap items-center gap-2">
          <span class="text-sm font-medium text-foreground/90 whitespace-nowrap">Tools:</span>
          <div class="flex flex-wrap gap-1">
            <span 
              v-for="tool in agent.tool_categories" 
              :key="tool"
              class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-background"
            >
              {{ tool }}
            </span>
          </div>
        </div>
        <div v-else class="hidden sm:block"><!-- Empty space for grid alignment --></div>

        <!-- Model, Clear History and Configuration Controls -->
        <div class="flex items-center gap-2 justify-start sm:justify-end">
          <Button 
            variant="outline" 
            size="sm" 
            class="flex items-center gap-1"
            @click="$router.push(`/agents/configuration/${agentId}`)"
          >
            <ArrowLeft class="h-4 w-4 rotate-180" />
            <span class="hidden xs:inline">Configure</span>
          </Button>
          
          <Dialog v-model:open="isClearHistoryOpen">
            <DialogTrigger asChild>
              <Button variant="outline" size="sm" class="flex items-center gap-1">
                <Trash2 class="h-4 w-4" />
                <span class="hidden xs:inline">Clear History</span>
              </Button>
            </DialogTrigger>
            <DialogContent class="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Clear chat history?</DialogTitle>
                <DialogDescription>
                  This will permanently delete all messages. This action cannot be undone.
                </DialogDescription>
              </DialogHeader>
              <DialogFooter class="mt-4 flex justify-end gap-2">
                <Button 
                  variant="outline" 
                  @click="isClearHistoryOpen = false"
                >
                  Cancel
                </Button>
                <Button 
                  variant="destructive" 
                  @click="clearHistory"
                  :disabled="isLoading"
                >
                  Clear
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          
          <div class="flex items-center gap-2">
            <span class="text-sm font-medium text-foreground/90 whitespace-nowrap">Model:</span>
            <Select v-model="selectedModel" @update:model-value="handleModelChange">
              <SelectTrigger class="w-[180px]">
                <SelectValue placeholder="Select a model" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem 
                  v-for="model in availableModels" 
                  :key="model.id" 
                  :value="model.id"
                >
                  {{ model.name }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>
    </div>

    <!-- Chat Messages -->
    <ScrollArea ref="logsContainer" class="flex-1 px-2 mb-4 sm:px-4">
      <div class="space-y-4">
        <template v-for="item in messagesWithDateIndicators" :key="item.id">
          <!-- Date separator -->
          <div v-if="'type' in item" class="flex justify-center my-4">
            <div class="bg-muted px-3 py-1 rounded-full text-xs text-muted-foreground">
              {{ formatDate(item.date) }}
            </div>
          </div>
          
          <!-- Regular message -->
          <div
            v-else
            :class="[
              'flex gap-2 sm:gap-3',
              item.sender === 'user' ? 'justify-end' : 'justify-start'
            ]"
          >
            <div
              :class="[
                'flex gap-2 sm:gap-3',
                'max-w-[95%]',
                item.sender === 'user' ? 'flex-row-reverse' : 'flex-row'
              ]"
            >
              <Avatar :class="[
                'h-6 w-6 sm:h-8 sm:w-8 shrink-0',
                item.sender === 'ai' ? 'bg-primary/10' : 'bg-secondary'
              ]">
                <Bot v-if="item.sender === 'ai'" class="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
                <User v-else class="h-4 w-4 sm:h-5 sm:w-5 text-secondary-foreground" />
              </Avatar>
              <div
                :class="[
                  'rounded-lg px-3 py-2 sm:px-4 sm:py-2',
                  item.sender === 'ai'
                    ? 'bg-muted'
                    : 'bg-primary text-primary-foreground'
                ]"
              >
                <div 
                  v-if="item.sender === 'user'"
                  class="text-sm break-words"
                >{{ item.content }}</div>
                <template v-else>
                  <!-- Handle multiple content blocks -->
                  <div class="message-blocks">
                    <template v-for="(block, index) in parseMessageToBlocks(item.content)" :key="index">
                      <!-- JSON Block -->
                      <JsonMessageContent 
                        v-if="block.type === 'json'"
                        :content="block.content" 
                        class="mb-2 last:mb-0"
                      />
                      
                      <!-- Markdown Block -->
                      <MarkdownContent
                        v-else-if="block.type === 'markdown'"
                        :content="block.content"
                        class="mb-2 last:mb-0"
                      />
                      
                      <!-- Future block types can be added here -->
                      <div v-else class="text-sm break-words p-2 mb-2 last:mb-0">
                        {{ block.content }}
                      </div>
                    </template>
                  </div>
                </template>
                
                <!-- Show reasoning steps for AI messages -->
                <div v-if="item.steps && item.steps.length > 0" class="mt-2 text-xs space-y-1 opacity-80">
                  <div v-for="step in item.steps" :key="step.step" class="border-l-2 pl-2">
                    <p><strong>{{ step.step }}:</strong> {{ step.description }}</p>
                    <p v-if="step.tool_used" class="italic">Used: {{ step.tool_used }}</p>
                  </div>
                </div>
                <p class="text-xs mt-1 opacity-70">
                  {{ item.timestamp.toLocaleTimeString() }}
                </p>
              </div>
            </div>
          </div>
        </template>
        
        <!-- Loading Animation - moved outside the v-for loop -->
        <div v-if="isLoading" class="flex gap-2 sm:gap-3 justify-start">
          <Avatar class="h-6 w-6 sm:h-8 sm:w-8 shrink-0 bg-primary/10">
            <Bot class="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
          </Avatar>
          <div class="rounded-lg px-3 py-2 sm:px-4 sm:py-2 bg-muted">
            <div class="flex gap-1">
              <div class="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-primary/50 animate-bounce [animation-delay:-0.3s]"></div>
              <div class="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-primary/50 animate-bounce [animation-delay:-0.15s]"></div>
              <div class="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-primary/50 animate-bounce"></div>
            </div>
          </div>
        </div>
      </div>
    </ScrollArea>

    <!-- File Upload Progress Overlay -->
    <div v-if="isFileUploading" class="fixed inset-0 bg-background/80 flex items-center justify-center z-50">
      <div class="bg-card p-6 rounded-lg shadow-lg max-w-md w-full">
        <h3 class="font-medium text-lg mb-4">Uploading Files...</h3>
        <Progress :value="uploadProgress" class="w-full mb-2" />
        <p class="text-sm text-muted-foreground">{{ uploadProgress }}% complete</p>
      </div>
    </div>

    <!-- File selection panel -->
    <div v-if="selectedFiles.length > 0" class="px-2 sm:px-4 pb-2">
      <div class="bg-muted p-3 rounded-md">
        <div class="flex justify-between items-center mb-2">
          <h4 class="text-sm font-medium">{{ getFileListLabel() }}</h4>
          <Button 
            variant="ghost" 
            size="sm" 
            @click="selectedFiles = []"
            :disabled="isLoading || isFileUploading"
          >
            <X class="h-3.5 w-3.5 mr-1" />
            Clear files
          </Button>
        </div>
        
        <div v-if="uploadError" class="text-sm text-destructive mb-2">{{ uploadError }}</div>
        
        <div class="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-1 mb-3">
          <div 
            v-for="(file, index) in selectedFiles" 
            :key="index"
            class="flex items-center bg-background rounded-md p-1.5 pr-2 text-xs"
          >
            <div class="w-6 h-6 flex items-center justify-center bg-muted rounded-md mr-1.5 text-[10px]">
              {{ file.name.split('.').pop()?.toUpperCase() }}
            </div>
            <div class="truncate max-w-[100px]">{{ file.name }}</div>
            <div class="text-muted-foreground ml-1.5">({{ formatFileSize(file.size) }})</div>
            <Button 
              variant="ghost" 
              size="icon" 
              class="h-5 w-5 ml-1"
              @click="removeFile(index)"
            >
              <X class="h-3 w-3" />
            </Button>
          </div>
        </div>
        
        <!-- Add helper text -->
        <p class="text-xs text-muted-foreground mt-2">
          These files will be sent when you click <strong>Send</strong>. Type an optional message to accompany them.
        </p>
      </div>
    </div>

    <!-- File drop overlay - shown when dragging files -->
    <div 
      v-if="isDraggingFile" 
      class="fixed inset-0 bg-primary/10 flex items-center justify-center z-50 pointer-events-none"
    >
      <div class="bg-card p-8 rounded-lg shadow-lg border-2 border-dashed border-primary text-center">
        <Paperclip class="h-12 w-12 mx-auto mb-4 text-primary" />
        <h3 class="text-xl font-medium">Drop files here</h3>
        <p class="text-sm text-muted-foreground mt-2">Files will be uploaded and shared in the chat</p>
      </div>
    </div>

    <!-- Message Input -->
    <div class="border-t pt-4">
      <form @submit.prevent="sendMessage" class="flex gap-2">
        <!-- Add file upload button -->
        <Button 
          type="button" 
          variant="ghost" 
          size="icon" 
          @click="fileInput?.click()"
          :disabled="isLoading || isFileUploading" 
          class="shrink-0 self-end"
        >
          <Paperclip class="h-4 w-4" />
        </Button>
        <!-- Hidden file input -->
        <input 
          type="file" 
          ref="fileInput" 
          multiple 
          @change="handleFileSelect"
          class="hidden" 
          accept=".xlsx,.xls,.csv,.jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.txt,.json"
        />

        <!-- Replace Input with Textarea -->
        <Textarea
          v-model="messageInput"
          placeholder="Type your message..."
          class="flex-1 resize-none min-h-[40px] max-h-[200px]"
          :rows="1"
          @keydown.enter.exact.prevent="sendMessage"
          @input="autoResizeTextarea"
        />
        
        <Button type="submit" size="icon" :disabled="isLoading || isFileUploading" class="self-end">
          <Send class="h-4 w-4" />
        </Button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.scroll-area {
  height: 100%;
}

/* Simple message styling */
.text-sm {
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.break-words {
  overflow-wrap: break-word;
}

/* Message blocks container */
.message-blocks > :deep(*:not(:last-child)) {
  margin-bottom: 0.75rem;
}

/* Style for inline code elements */
:deep(.inline-code) {
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.875em;
  padding: 0.2em 0.4em;
  color: #e83e8c;
}

/* Add styles for file handling */
.file-item-enter-active,
.file-item-leave-active {
  transition: all 0.3s ease;
}

.file-item-enter-from,
.file-item-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Drag and drop styles */
.file-drop-active {
  position: relative;
}

.file-drop-active::after {
  content: '';
  position: absolute;
  inset: 0;
  border: 2px dashed var(--primary);
  pointer-events: none;
  border-radius: 0.5rem;
  z-index: 1;
}

/* Style for textarea to look like the input */
textarea {
  line-height: 1.5;
  overflow-y: auto !important;
}

/* Add this to your existing styles */
.xs\:inline {
  @media (min-width: 475px) {
    display: inline;
  }
}
</style>
