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
import { MoreVertical, Pencil, Trash, MessageSquare, Bot, Search } from 'lucide-vue-next';
import { useToast } from '@/components/ui/toast/use-toast';
import { Separator } from '@/components/ui/separator'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Input } from '@/components/ui/input';

const { toast } = useToast();
const { listUserAgents, deleteAgent, loading, error } = useAgents();
const { user } = useAuthStore();
const agents = ref<Agent[]>([]);
const searchQuery = ref('');

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

onMounted(() => {
  loadAgents();
});
</script>

<template>
  <div class="p-4">
    <div class="flex justify-between items-center mb-6">
      <h1 class="scroll-m-20 text-4xl font-bold tracking-tight">AI Agents</h1>
      <div class="flex items-center gap-3">
        <div class="relative">
          <Search class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            v-model="searchQuery"
            class="pl-8 w-[200px]"
            placeholder="Search agents..."
            type="search"
          />
        </div>
        <Button>
          Create New Agent
        </Button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
    >
      <Card
        v-for="agent in filteredAgents"
        :key="agent.id"
        class="relative group"
      >
        <CardHeader class="pb-2">
          <div class="flex justify-between items-center gap-2">
            <div class="flex items-center gap-2">
              <Avatar class="h-8 w-8 bg-primary/10">
                <Bot class="h-5 w-5 text-primary" />
              </Avatar>
              <CardTitle class="text-lg leading-8">{{ agent.name }}</CardTitle>
            </div>
            <Badge :variant="agent.is_active ? 'default' : 'secondary'" class="shrink-0 text-xs">
              {{ agent.is_active ? 'Active' : 'Inactive' }}
            </Badge>
          </div>
        </CardHeader>

        <CardContent class="pb-3">
          <div class="space-y-2">
            <div v-if="agent.description" class="flex gap-1.5 text-xs">
            
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <p class="line-clamp-1 cursor-help">{{ agent.description }}</p>
                  </TooltipTrigger>
                  <TooltipContent class="max-w-xs whitespace-normal">
                    <p>{{ agent.description }}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>

            <div class="flex items-center gap-1.5 text-xs">
              <span class="font-medium shrink-0">Model:</span>
              <Badge variant="outline" class="bg-primary/5 text-xs h-5">
                {{ agent.model_id }}
              </Badge>
            </div>

            <div v-if="agent.tool_categories?.length" class="flex items-center gap-1.5 flex-wrap">
              <span class="text-xs font-medium shrink-0">Tools:</span>
              <div class="flex flex-wrap gap-1">
                <Badge 
                  v-for="tool in agent.tool_categories" 
                  :key="tool"
                  variant="secondary"
                  class="bg-secondary/10 text-xs h-5"
                >
                  {{ tool }}
                </Badge>
              </div>
            </div>
          </div>
        </CardContent>

        <Separator class="mb-3" />

        <CardFooter class="pt-0">
          <div class="flex justify-between items-center w-full">
            <Button 
              variant="default" 
              size="sm" 
              class="h-8 text-xs gap-1.5" 
              @click="$router.push(`/chat/${agent.id}`)"
            >
              <MessageSquare class="h-3.5 w-3.5" />
              Chat
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <Button variant="ghost" size="sm" class="h-8 w-8 p-0">
                  <MoreVertical class="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" class="w-40">
                <DropdownMenuItem @click="$router.push(`/agents/${agent.id}`)">
                  <Pencil class="h-3.5 w-3.5 mr-2" />
                  Edit
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
    <Card v-else-if="agents.length > 0" class="text-center p-6">
      <CardHeader>
        <CardTitle>No Matching Agents</CardTitle>
        <CardDescription>No agents found matching your search criteria</CardDescription>
      </CardHeader>
    </Card>

    <!-- Empty State -->
    <Card v-else class="text-center p-6">
      <CardHeader>
        <CardTitle>No AI Agents Yet</CardTitle>
        <CardDescription>Get started by creating your first AI agent</CardDescription>
      </CardHeader>
      <CardFooter class="flex justify-center">
        <Button>
          Create Your First Agent
        </Button>
      </CardFooter>
    </Card>
  </div>
</template>

<style scoped>
.grid {
  transition: all 0.3s ease;
}
</style>
