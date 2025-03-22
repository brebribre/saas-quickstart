<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { useAgents } from '@/hooks/useAgents';
import type { Agent } from '@/hooks/useAgents';
import { useAuthStore } from '@/stores/auth';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Avatar } from '@/components/ui/avatar';
import { MoreVertical, Pencil, Trash, MessageSquare, Bot, Search, FileText, Plus } from 'lucide-vue-next';
import { useToast } from '@/components/ui/toast/use-toast';
import { Separator } from '@/components/ui/separator'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Input } from '@/components/ui/input';
import CreateAgentDialog from '@/components/CreateAgentDialog.vue';

const { toast } = useToast();
const { listUserAgents, deleteAgent, loading, error } = useAgents();
const { user } = useAuthStore();
const agents = ref<Agent[]>([]);
const searchQuery = ref('');
const showCreateDialog = ref(false);

const filteredAgents = computed(() => {
  if (!searchQuery.value) return agents.value;
  const query = searchQuery.value.toLowerCase();
  return agents.value.filter(agent => 
    agent.name.toLowerCase().includes(query)
  );
});

const loadAgents = async () => {
    if (!user) {
        console.error('User not found');
        return;
    }
    const fetchedAgents = await listUserAgents(user.id);
    agents.value = fetchedAgents;
};

const handleDeleteAgent = async (agentId: string) => {
  try {
    const success = await deleteAgent(agentId);
    if (success) {
      await loadAgents();
      toast({
        title: 'Agent deleted',
        description: 'The agent was successfully deleted.',
      });
    } else {
      toast({
        title: 'Delete failed',
        description: 'Failed to delete the agent. Please try again.',
        variant: 'destructive',
      });
    }
  } catch (err) {
    toast({
      title: 'Error',
      description: err instanceof Error ? err.message : 'An unexpected error occurred',
      variant: 'destructive',
    });
  }
};

const handleAgentCreated = async (agentId: string) => {
  await loadAgents();
  toast({
    title: 'Agent created',
    description: 'Your new agent is ready to use.',
  });
};

onMounted(() => {
  loadAgents();
});
</script>

<template>
  <div class="p-2 sm:p-4">
    <!-- Header Section -->
    <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-6">
      <h1 class="scroll-m-20 text-2xl font-bold tracking-tight">AI Agents</h1>
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
        <div class="relative">
          <Search class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            v-model="searchQuery"
            class="pl-8 w-full sm:w-[200px]"
            placeholder="Search agents..."
            type="search"
          />
        </div>
        <Button class="w-full sm:w-auto" @click="showCreateDialog = true">
          <Plus class="h-4 w-4 mr-2" />
          Create New Agent
        </Button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
      <Card v-for="i in 3" :key="i">
        <CardHeader class="pb-2">
          <div class="flex justify-between items-center gap-2">
            <div class="flex items-center gap-2">
              <Skeleton class="h-8 w-8 rounded-full" />
              <Skeleton class="h-8 w-32" />
            </div>
            <Skeleton class="h-5 w-16" />
          </div>
        </CardHeader>
        <CardContent class="pb-3">
          <div class="space-y-2">
            <Skeleton class="h-4 w-full" />
            <div class="flex items-center gap-1.5">
              <Skeleton class="h-4 w-12" />
              <Skeleton class="h-5 w-24" />
            </div>
            <div class="flex items-center gap-1.5">
              <Skeleton class="h-4 w-10" />
              <div class="flex gap-1">
                <Skeleton class="h-5 w-16" />
                <Skeleton class="h-5 w-16" />
              </div>
            </div>
          </div>
        </CardContent>
        <Separator class="mb-3" />
        <CardFooter class="pt-0">
          <div class="flex justify-between items-center w-full">
            <Skeleton class="h-8 w-20" />
            <Skeleton class="h-8 w-8" />
          </div>
        </CardFooter>
      </Card>
    </div>

    <!-- Error State -->
    <Alert v-else-if="error" variant="destructive">
      <AlertDescription>
        {{ error }}
      </AlertDescription>
    </Alert>

    <!-- Agents Grid -->
    <div
      v-else-if="filteredAgents.length > 0"
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4"
    >
      <Card
        v-for="agent in filteredAgents"
        :key="agent.id"
        class="relative group border border-border hover:border-primary/20 transition-colors duration-200 bg-muted/30"
      >
        <CardHeader class="pb-2">
          <div class="flex items-center gap-3 mb-2">
            <Avatar class="h-10 w-10 bg-primary/10">
              <Bot class="h-6 w-6 text-primary" />
            </Avatar>
            <div>
              <p class="text-sm text-muted-foreground">AI Assistant</p>
              <CardTitle class="text-base sm:text-lg leading-tight">{{ agent.name }}</CardTitle>
            </div>
          </div>
        </CardHeader>

        <CardContent class="pb-3">
          <div v-if="agent.description" class="flex gap-1.5 text-xs mb-2">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <p class="line-clamp-2 cursor-help text-xs sm:text-sm text-muted-foreground">{{ agent.description }}</p>
                </TooltipTrigger>
                <TooltipContent class="max-w-[250px] sm:max-w-xs whitespace-normal">
                  <p>{{ agent.description }}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </CardContent>

        <CardFooter class="pt-2 flex justify-between items-center">
          <p class="text-xs text-muted-foreground">
            + {{ agent.tool_categories?.length || 0 }} tools
          </p>
          <div class="flex gap-2">
            <Button 
              variant="default" 
              size="sm" 
              class="h-8 text-xs" 
              @click="$router.push(`/agents/chat/${agent.id}`)"
            >
              Chat
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <Button variant="ghost" size="sm" class="h-8 w-8 p-0 rounded-full">
                  <MoreVertical class="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" class="w-40">
                <DropdownMenuItem @click="$router.push(`/agents/${agent.id}`)">
                  <Pencil class="h-3.5 w-3.5 mr-2" />
                  Edit
                </DropdownMenuItem>
                <DropdownMenuItem @click="$router.push(`/agents/configuration/${agent.id}`)">
                  <FileText class="h-3.5 w-3.5 mr-2" />
                  Files
                </DropdownMenuItem>
                <DropdownMenuItem @click="handleDeleteAgent(agent.id)" class="text-destructive">
                  <Trash class="h-3.5 w-3.5 mr-2" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </CardFooter>
      </Card>
    </div>

    <!-- Empty Search Results -->
    <Card v-else-if="agents.length > 0" class="border border-border text-center p-6 max-w-md mx-auto">
      <CardHeader>
        <div class="flex justify-center mb-2">
          <Avatar class="h-12 w-12 bg-muted">
            <Search class="h-6 w-6 text-muted-foreground" />
          </Avatar>
        </div>
        <CardTitle>No Matching Agents</CardTitle>
        <CardDescription>No agents found matching your search criteria</CardDescription>
      </CardHeader>
      <CardFooter class="flex justify-center pt-2">
        <Button variant="outline" @click="searchQuery = ''">
          Clear Search
        </Button>
      </CardFooter>
    </Card>

    <!-- Empty State -->
    <Card v-else class="border border-border text-center p-6 max-w-md mx-auto">
      <CardHeader>
        <div class="flex justify-center mb-2">
          <Avatar class="h-12 w-12 bg-primary/10">
            <Bot class="h-6 w-6 text-primary" />
          </Avatar>
        </div>
        <CardTitle>No AI Agents Yet</CardTitle>
        <CardDescription>Get started by creating your first AI agent</CardDescription>
      </CardHeader>
      <CardFooter class="flex justify-center pt-2">
        <Button @click="showCreateDialog = true">
          Create Your First Agent
        </Button>
      </CardFooter>
    </Card>

    <!-- Create Agent Dialog -->
    <CreateAgentDialog 
      v-model:open="showCreateDialog" 
      @created="handleAgentCreated" 
    />
  </div>
</template>

<style scoped>
.grid {
  transition: all 0.3s ease;
}

/* Add responsive styles for cards */
@media (max-width: 640px) {
  :deep(.card) {
    padding: 0.75rem;
  }
  
  :deep(.card-header) {
    padding: 0.75rem;
  }
  
  :deep(.card-content) {
    padding: 0.75rem;
  }
  
  :deep(.card-footer) {
    padding: 0.75rem;
  }
}
</style>
