import { ref } from 'vue';
import axios from 'axios';

interface Agent {
  id: string;
  name: string;
  description?: string;
  model_id: string;
  user_id: string;
  tool_categories?: string[];
  custom_instructions?: string;
  configuration?: Record<string, any>;
  is_active?: boolean;
}

interface CreateAgentData {
  name: string;
  description?: string;
  model_id: string;
  user_id: string;
  tool_categories?: string[];
  custom_instructions?: string;
  configuration?: Record<string, any>;
}

interface UpdateAgentData {
  name?: string;
  description?: string;
  model_id?: string;
  tool_categories?: string[];
  custom_instructions?: string;
  is_active?: boolean;
  configuration?: Record<string, any>;
}

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:5000';
const AGENTS_ENDPOINT = `${API_BASE_URL}/api/v1/agents`;

export const useAgents = () => {
  const loading = ref(false);
  const error = ref<string | null>(null);

  const createAgent = async (data: CreateAgentData): Promise<Agent | null> => {
    try {
      loading.value = true;
      error.value = null;
      const response = await axios.post(AGENTS_ENDPOINT, data);
      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create agent';
      return null;
    } finally {
      loading.value = false;
    }
  };

  const getAgent = async (agentId: string): Promise<Agent | null> => {
    try {
      loading.value = true;
      error.value = null;
      const response = await axios.get(`${AGENTS_ENDPOINT}/${agentId}`);
      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to get agent';
      return null;
    } finally {
      loading.value = false;
    }
  };

  const listUserAgents = async (userId: string): Promise<Agent[]> => {
    try {
      loading.value = true;
      error.value = null;
      const response = await axios.get(`${AGENTS_ENDPOINT}/user/${userId}`);
      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to list agents';
      return [];
    } finally {
      loading.value = false;
    }
  };

  const updateAgent = async (agentId: string, data: UpdateAgentData): Promise<Agent | null> => {
    try {
      loading.value = true;
      error.value = null;
      const response = await axios.patch(`${AGENTS_ENDPOINT}/${agentId}`, data);
      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update agent';
      return null;
    } finally {
      loading.value = false;
    }
  };

  const deleteAgent = async (agentId: string): Promise<boolean> => {
    try {
      loading.value = true;
      error.value = null;
      await axios.delete(`${AGENTS_ENDPOINT}/${agentId}`);
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete agent';
      return false;
    } finally {
      loading.value = false;
    }
  };

  const incrementAgentUsage = async (agentId: string): Promise<boolean> => {
    try {
      loading.value = true;
      error.value = null;
      await axios.post(`${AGENTS_ENDPOINT}/${agentId}/increment-usage`);
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to increment agent usage';
      return false;
    } finally {
      loading.value = false;
    }
  };

  return {
    createAgent,
    getAgent,
    listUserAgents,
    updateAgent,
    deleteAgent,
    incrementAgentUsage,
    loading,
    error,
  };
};
