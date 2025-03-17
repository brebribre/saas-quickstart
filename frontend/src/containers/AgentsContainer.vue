<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useAgents } from '@/hooks/useAgents';
import type { Agent } from '@/hooks/useAgents';
import { useAuthStore } from '@/stores/auth';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { MoreVertical, Pencil, Trash } from 'lucide-vue-next';

const { listUserAgents, deleteAgent, loading, error } = useAgents();
const { user } = useAuthStore();
const agents = ref<Agent[]>([]);

const loadAgents = async () => {
    if (!user) {
        console.error('User not found');
        return;
    }
    const fetchedAgents = await listUserAgents(user.id);
    agents.value = fetchedAgents;
};

const handleDeleteAgent = async (agentId: string) => {
  const success = await deleteAgent(agentId);
  if (success) {
    await loadAgents();
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
      <Button>
        Create New Agent
      </Button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <Card v-for="i in 3" :key="i">
        <CardHeader>
          <Skeleton class="h-4 w-3/4" />
          <Skeleton class="h-4 w-1/2 mt-2" />
        </CardHeader>
        <CardContent>
          <Skeleton class="h-20 w-full" />
        </CardContent>
        <CardFooter>
          <Skeleton class="h-8 w-full" />
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
      v-else-if="agents.length > 0"
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
    >
      <Card
        v-for="agent in agents"
        :key="agent.id"
        class="relative"
      >
        <CardHeader>
          <div class="flex justify-between items-start">
            <div>
              <CardTitle>{{ agent.name }}</CardTitle>
              <CardDescription>{{ agent.description || 'No description provided' }}</CardDescription>
            </div>
            <Badge :variant="agent.is_active ? 'default' : 'secondary'">
              {{ agent.is_active ? 'Active' : 'Inactive' }}
            </Badge>
          </div>
        </CardHeader>

        <CardContent>
          <div class="space-y-2 text-sm text-muted-foreground">
            <p>Model: {{ agent.model_id }}</p>
            <p v-if="agent.tool_categories?.length">
              Tools: {{ agent.tool_categories.join(', ') }}
            </p>
          </div>
        </CardContent>

        <CardFooter class="flex justify-end">
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button variant="ghost" size="icon">
                <MoreVertical class="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem @click="$router.push(`/agents/${agent.id}`)">
                <Pencil class="h-4 w-4 mr-2" />
                Edit
              </DropdownMenuItem>
              <DropdownMenuItem @click="handleDeleteAgent(agent.id)" class="text-destructive">
                <Trash class="h-4 w-4 mr-2" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </CardFooter>
      </Card>
    </div>

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
