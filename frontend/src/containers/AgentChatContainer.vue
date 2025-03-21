<script setup lang="ts">
// Inbox view component
import type { Agent } from '@/hooks/useAgents'
import { useRoute } from 'vue-router'
import { ref, onMounted, computed, nextTick } from 'vue'
import { useAgents } from '@/hooks/useAgents'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar } from '@/components/ui/avatar'
import { Bot, Send, User, ArrowLeft, Paperclip, X } from 'lucide-vue-next'
import { useLangchain } from '@/hooks/useLangchain'
import type { AIModel } from '@/hooks/useLangchain'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useToast } from '@/components/ui/toast/use-toast'
import { useAuthStore } from '@/stores/auth'
import JsonMessageContent from '@/components/messageMarkdown/JsonMessageContent.vue'
import MarkdownContent from '@/components/messageMarkdown/MarkdownContent.vue'
import { useFiles } from '@/hooks/useFiles'
import { Progress } from '@/components/ui/progress'

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

const { getAgent, updateAgent } = useAgents()
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

const sendMessage = async () => {
  if (!messageInput.value.trim() || !agent.value) return

  const question = messageInput.value
  messageInput.value = '' // Clear input right away for better UX

  try {
    const userId = authStore.user?.id
    if (!userId) {
      throw new Error('User ID not found')
    }

    // Add user message immediately to chat history
    const userMessage: ChatMessage = {
      role: 'user',
      content: question,
      timestamp: new Date().toISOString()
    }
    
    // Update agent's chat history locally
    if (!agent.value.chat_history) {
      agent.value.chat_history = []
    }
    agent.value.chat_history.push(userMessage)
    isLoading.value = true
    
    // Scroll to bottom after adding user message
    scrollToBottom()

    // Get AI response
    await askAgent(
      question,
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
  
  // Check file size and type
  for (const file of files) {
    if (file.size > 50 * 1024 * 1024) { // 50MB
      uploadError.value = `File ${file.name} exceeds the 50MB size limit`
      return
    }
    
    if (!isFileTypeAllowed(file)) {
      uploadError.value = `File type of ${file.name} is not allowed`
      return
    }
  }
  
  uploadError.value = ''
  selectedFiles.value = [...selectedFiles.value, ...files]
  
  // Reset file input
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// Remove file from selection
const removeFile = (index: number) => {
  selectedFiles.value = selectedFiles.value.filter((_, i) => i !== index)
}

// Handle file upload and send message
const uploadAndSendMessage = async () => {
  if (!selectedFiles.value.length || !agent.value) return
  
  try {
    const userId = authStore.user?.id
    if (!userId) {
      throw new Error('User ID not found')
    }
    
    // Upload the files
    const results = await uploadFiles(
      agentId,
      selectedFiles.value, 
      userId,
      (progress) => {} // We're using the reactive uploadProgress from useFiles
    )
    
    // If files were uploaded successfully, compose message text
    if (results.length > 0) {
      // Create a message with file info
      let messageContent = 'I\'ve shared the following files:\n'
      results.forEach(file => {
        messageContent += `- ${file.filename} (${formatFileSize(file.file_size)})\n`
      })
      
      // Set the message input and send
      messageInput.value = messageContent
      await sendMessage()
      
      // Clear selected files
      selectedFiles.value = []
    }
    
  } catch (error) {
    toast({
      title: 'Error',
      description: error instanceof Error ? error.message : 'Failed to upload files',
      variant: 'destructive',
    })
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
  <div class="flex flex-col h-[calc(100vh-4rem)]">
    <!-- Header -->
    <div class="border-b p-4">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div class="flex items-center gap-3">
          <Button variant="ghost" size="icon" @click="$router.push('/agents')" class="mr-2">
            <ArrowLeft class="h-4 w-4" />
          </Button>
          <Avatar class="h-10 w-10 bg-primary/10">
            <Bot class="h-6 w-6 text-primary" />
          </Avatar>
          <div>
            <h1 class="text-xl font-semibold truncate">{{ agent?.name }}</h1>
            <p class="text-sm text-muted-foreground line-clamp-1">{{ agent?.description }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-sm text-muted-foreground whitespace-nowrap">Model:</span>
          <Select v-model="selectedModel" @update:model-value="handleModelChange">
            <SelectTrigger class="w-[180px] sm:w-[200px]">
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
                'max-w-[95%] sm:max-w-[85%] lg:max-w-[75%] xl:max-w-[65%]',
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
          <h4 class="text-sm font-medium">Selected Files ({{ selectedFiles.length }})</h4>
          <div class="flex gap-2">
            <Button variant="outline" size="sm" @click="selectedFiles = []">
              Cancel
            </Button>
            <Button size="sm" @click="uploadAndSendMessage" :disabled="isLoading || isFileUploading">
              Upload & Send
            </Button>
          </div>
        </div>
        
        <div v-if="uploadError" class="text-sm text-destructive mb-2">{{ uploadError }}</div>
        
        <div class="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-1">
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
          class="shrink-0"
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

        <Input
          v-model="messageInput"
          placeholder="Type your message..."
          class="flex-1"
        />
        <Button type="submit" size="icon" :disabled="isLoading || isFileUploading">
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
</style>
