<script setup lang="ts">
// Inbox view component
import type { Agent } from '@/hooks/useAgents'
import { useRoute } from 'vue-router'
import { ref, onMounted, computed } from 'vue'
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

const availableModels = ref<AIModel[]>([])
const selectedModel = ref<string>('')

const agent = ref<Agent | null>(null)
const messageInput = ref('')

// Remove the hardcoded messages array and use computed property instead
const messages = computed(() => {
  if (!agent.value?.chat_history) return []
  
  return agent.value.chat_history.map((msg: ChatMessage, index: number) => ({
    id: index,
    content: msg.content,
    sender: msg.role === 'user' ? 'user' : 'ai',
    timestamp: new Date(msg.timestamp),
    steps: msg.steps
  }))
})

const sendMessage = async () => {
  if (!messageInput.value.trim() || !agent.value) return

  const question = messageInput.value
  messageInput.value = '' // Clear input right away for better UX

  try {
    const response = await askAgent({
      question,
      agentId: agent.value.id,
      modelId: agent.value.model_id
    })

    // The chat history will be updated in the backend
    // Refresh the agent to get the updated chat history
    agent.value = await getAgent(agentId)

  } catch (err) {
    toast({
      title: 'Error',
      description: err instanceof Error ? err.message : 'Failed to send message',
      variant: 'destructive',
    })
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

onMounted(async () => {
  agent.value = await getAgent(agentId)
  availableModels.value = await getModels()
  if (agent.value) {
    selectedModel.value = agent.value.model_id
  }
})

</script>

<template>
  <div class="flex flex-col h-[calc(100vh-4rem)]">
    <!-- Header -->
    <div class="border-b p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <Button variant="ghost" size="icon" @click="$router.push('/agents')" class="mr-2">
            <ArrowLeft class="h-4 w-4" />
          </Button>
          <Avatar class="h-10 w-10 bg-primary/10">
            <Bot class="h-6 w-6 text-primary" />
          </Avatar>
          <div>
            <h1 class="text-xl font-semibold">{{ agent?.name }}</h1>
            <p class="text-sm text-muted-foreground">{{ agent?.description }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-sm text-muted-foreground">Model:</span>
          <Select v-model="selectedModel" @update:model-value="handleModelChange">
            <SelectTrigger class="w-[200px]">
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
    <ScrollArea class="flex-1 p-4">
      <div class="space-y-4">
        <div
          v-for="message in messages"
          :key="message.id"
          :class="[
            'flex gap-3',
            message.sender === 'user' ? 'justify-end' : 'justify-start'
          ]"
        >
          <div
            :class="[
              'flex gap-3 max-w-[80%]',
              message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'
            ]"
          >
            <Avatar :class="[
              'h-8 w-8 shrink-0',
              message.sender === 'ai' ? 'bg-primary/10' : 'bg-secondary'
            ]">
              <Bot v-if="message.sender === 'ai'" class="h-5 w-5 text-primary" />
              <User v-else class="h-5 w-5 text-secondary-foreground" />
            </Avatar>
            <div
              :class="[
                'rounded-lg px-4 py-2',
                message.sender === 'ai'
                  ? 'bg-muted'
                  : 'bg-primary text-primary-foreground'
              ]"
            >
              <p class="text-sm">{{ message.content }}</p>
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
      </div>
    </ScrollArea>

    <!-- Message Input -->
    <div class="border-t p-4">
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
</style>
