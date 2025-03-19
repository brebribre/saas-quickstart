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
import { marked } from 'marked'

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

// Remove the hardcoded messages array and use computed property instead
const messages = computed(() => {
  if (!agent.value?.chat_history) return []
  
  return (agent.value.chat_history as ChatMessage[]).map((msg: ChatMessage, index: number) => ({
    id: index,
    content: msg.content,
    sender: msg.role === 'user' ? 'user' : 'ai',
    timestamp: new Date(msg.timestamp),
    steps: msg.steps
  }))
})

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
    const response = await askAgent(
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

// Add this function to safely render markdown
const renderMarkdown = (content: string) => {
  try {
    return marked(content)
  } catch (err) {
    return content
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
    <ScrollArea ref="logsContainer" class="flex-1 p-2 sm:p-4">
      <div class="space-y-4">
        <div
          v-for="message in messages"
          :key="message.id"
          :class="[
            'flex gap-2 sm:gap-3',
            message.sender === 'user' ? 'justify-end' : 'justify-start'
          ]"
        >
          <div
            :class="[
              'flex gap-2 sm:gap-3',
              'max-w-[85%] sm:max-w-[75%]',
              message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'
            ]"
          >
            <Avatar :class="[
              'h-6 w-6 sm:h-8 sm:w-8 shrink-0',
              message.sender === 'ai' ? 'bg-primary/10' : 'bg-secondary'
            ]">
              <Bot v-if="message.sender === 'ai'" class="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
              <User v-else class="h-4 w-4 sm:h-5 sm:w-5 text-secondary-foreground" />
            </Avatar>
            <div
              :class="[
                'rounded-lg px-3 py-2 sm:px-4 sm:py-2',
                message.sender === 'ai'
                  ? 'bg-muted prose prose-sm dark:prose-invert max-w-none'
                  : 'bg-primary text-primary-foreground'
              ]"
            >
              <div 
                class="text-sm break-words"
                v-html="message.sender === 'ai' ? renderMarkdown(message.content) : message.content"
              ></div>
              <!-- Show reasoning steps for AI messages -->
              <div v-if="message.steps && message.steps.length > 0" class="mt-2 text-xs space-y-1 opacity-80">
                <div v-for="step in message.steps" :key="step.step" class="border-l-2 pl-2">
                  <p><strong>{{ step.step }}:</strong> {{ step.description }}</p>
                  <p v-if="step.tool_used" class="italic">Used: {{ step.tool_used }}</p>
                </div>
              </div>
              <p class="text-xs mt-1 opacity-70">
                {{ message.timestamp.toLocaleTimeString() }}
              </p>
            </div>
          </div>
        </div>

        <!-- Loading Animation -->
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

/* Add these styles to handle markdown content properly */
.prose {
  max-width: none;
}

.prose pre {
  background-color: rgb(var(--muted));
  padding: 0.75rem;
  border-radius: 0.375rem;
  margin: 0.5rem 0;
}

.prose code {
  background-color: rgb(var(--muted));
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
}

.prose ul, .prose ol {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.prose p {
  margin: 0.5rem 0;
}

.prose *:first-child {
  margin-top: 0;
}

.prose *:last-child {
  margin-bottom: 0;
}

/* Add responsive styles for markdown content */
.prose pre {
  max-width: 100%;
  overflow-x: auto;
}

.prose img {
  max-width: 100%;
  height: auto;
}

@media (max-width: 640px) {
  .prose {
    font-size: 0.875rem;
  }
  
  .prose pre {
    padding: 0.5rem;
    margin: 0.25rem 0;
  }
  
  .prose code {
    padding: 0.125rem 0.25rem;
  }
  
  .prose ul, .prose ol {
    margin: 0.25rem 0;
    padding-left: 1.25rem;
  }
  
  .prose p {
    margin: 0.25rem 0;
  }
}
</style>
