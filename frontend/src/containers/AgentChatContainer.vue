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
import { Bot, Send, User, ArrowLeft } from 'lucide-vue-next'
import { useLangchain } from '@/hooks/useLangchain'
import type { AIModel } from '@/hooks/useLangchain'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useToast } from '@/components/ui/toast/use-toast'
import { useAuthStore } from '@/stores/auth'
import JsonMessageContent from '@/components/messageMarkdown/JsonMessageContent.vue'

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

const route = useRoute()
const agentId = route.params.agentId as string
const { toast } = useToast()

const { getAgent, updateAgent } = useAgents()
const { getModels, askAgent } = useLangchain()
const authStore = useAuthStore()

const availableModels = ref<AIModel[]>([])
const selectedModel = ref<string>('')

const agent = ref<Agent | null>(null)
const messageInput = ref('')
const isLoading = ref(false)

const logsContainer = ref()

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
        lastMessage.scrollIntoView({ behavior: 'smooth' })
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

const formatText = (text: string) => {
  if (!text) return '';
  
  // Format inline code (text within single backticks)
  const formattedText = text.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
  
  // Replace line breaks with <br> tags
  return formattedText.replace(/\n/g, '<br>');
}

// Function to check if content contains a JSON code block
const hasJsonCodeBlock = (text: string): boolean => {
  return text.includes('```json') && text.includes('```');
}

// Function to extract JSON from a code block
const extractJsonFromCodeBlock = (text: string): string => {
  const jsonRegex = /```json\n([\s\S]*?)\n```/;
  const match = text.match(jsonRegex);
  
  if (match && match[1]) {
    return match[1].trim();
  }
  
  return '';
}

// Function to get text outside JSON code blocks
const getTextOutsideJsonBlocks = (text: string): string => {
  if (!text) return '';
  
  // Replace all JSON code blocks with an empty string
  return text.replace(/```json\n[\s\S]*?\n```/g, '').trim();
}

// Function to process message content, handling JSON blocks and regular text
const processMessageContent = (text: string) => {
  if (!text) return { isJson: false, content: '' };
  
  if (hasJsonCodeBlock(text)) {
    const jsonContent = extractJsonFromCodeBlock(text);
    if (jsonContent) {
      return { isJson: true, content: jsonContent };
    }
  }
  
  return { isJson: false, content: text };
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
    <ScrollArea ref="logsContainer" class="flex-1 px-2 mb-2 sm:px-4">
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
                  <!-- Handle the combined display of JSON and text -->
                  <div>
                    <!-- Show the JSON component if there's a JSON code block -->
                    <JsonMessageContent 
                      v-if="hasJsonCodeBlock(item.content)"
                      :content="extractJsonFromCodeBlock(item.content)" 
                    />
                    
                    <!-- Show the text outside of JSON blocks -->
                    <div 
                      v-if="getTextOutsideJsonBlocks(item.content)" 
                      class="text-sm break-words" 
                      v-html="formatText(getTextOutsideJsonBlocks(item.content))"
                    ></div>
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

    <!-- Message Input -->
    <div class="border-t p-2 sm:p-4">
      <form @submit.prevent="sendMessage" class="flex gap-2">
        <Input
          v-model="messageInput"
          placeholder="Type your message..."
          class="flex-1"
        />
        <Button type="submit" size="icon">
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

/* Style for inline code elements */
:deep(.inline-code) {
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.875em;
  padding: 0.2em 0.4em;
  color: #e83e8c;
}
</style>
