<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useAgents } from '@/hooks/useAgents';
import type { Agent } from '@/hooks/useAgents';
import { useAuthStore } from '@/stores/auth';

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
    await loadAgents(); // Refresh the list
  }
};

onMounted(() => {
  loadAgents();
});
</script>

<template>
  <div class="p-4">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">AI Agents</h1>
      <button
        class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
      >
        Create New Agent
      </button>
    </div>

    <!-- Loading and Error States -->
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
      <p class="mt-2 text-gray-600 dark:text-gray-400">Loading agents...</p>
    </div>

    <div
      v-else-if="error"
      class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded"
      role="alert"
    >
      <p>{{ error }}</p>
    </div>

    <!-- Agents Grid -->
    <div
      v-else-if="agents.length > 0"
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
    >
      <div
        v-for="agent in agents"
        :key="agent.id"
        class="border rounded-lg p-4 hover:shadow-lg transition-shadow bg-white dark:bg-gray-800"
      >
        <div class="flex justify-between items-start mb-2">
          <h3 class="text-lg font-semibold">{{ agent.name }}</h3>
          <span
            :class="[
              'px-2 py-1 text-xs rounded-full',
              agent.is_active
                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
            ]"
          >
            {{ agent.is_active ? 'Active' : 'Inactive' }}
          </span>
        </div>

        <p class="text-gray-600 dark:text-gray-400 text-sm mb-4">
          {{ agent.description || 'No description provided' }}
        </p>

        <div class="text-sm text-gray-500 dark:text-gray-400 mb-4">
          <p>Model: {{ agent.model_id }}</p>
          <p v-if="agent.tool_categories?.length" class="mt-1">
            Tools: {{ agent.tool_categories.join(', ') }}
          </p>
        </div>

        <div class="flex justify-end gap-2">
          <button
            class="text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
            @click="$router.push(`/agents/${agent.id}`)"
          >
            Edit
          </button>
          <button
            class="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200"
            @click="handleDeleteAgent(agent.id)"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else
      class="text-center py-12 bg-gray-50 dark:bg-gray-800 rounded-lg"
    >
      <p class="text-gray-600 dark:text-gray-400 mb-4">
        You haven't created any AI agents yet.
      </p>
      <button
        class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
      >
        Create Your First Agent
      </button>
    </div>
  </div>
</template>

<style scoped>
.grid {
  transition: all 0.3s ease;
}
</style>
