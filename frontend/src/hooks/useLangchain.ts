import { ref } from 'vue';
import axios from 'axios';

export interface AIModel {
  id: string;
  name: string;
  provider: string;
}

export interface Tool {
  name: string;
  description: string;
}

export interface ToolCategory {
  name: string;
  description: string;
  tools: Tool[];
}

export interface ToolCategories {
  [key: string]: ToolCategory;
}

export interface AgentStep {
  step: string;
  description: string;
  tool_used?: string;
  input?: Record<string, any>;
  output?: string | number;
}

export interface AgentResponse {
  steps: AgentStep[];
  final_answer: string;
}

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:5000';
const LANGCHAIN_ENDPOINT = `${API_BASE_URL}/api/v1/langchain`;

export const useLangchain = () => {
  const loading = ref(false);
  const error = ref<string | null>(null);

  const getModels = async (): Promise<AIModel[]> => {
    try {
      loading.value = true;
      error.value = null;
      const response = await axios.get(`${LANGCHAIN_ENDPOINT}/models`);
      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to get AI models';
      return [];
    } finally {
      loading.value = false;
    }
  };

  const getTools = async (): Promise<ToolCategories> => {
    try {
      loading.value = true;
      error.value = null;
      const response = await axios.get(`${LANGCHAIN_ENDPOINT}/tools`);
      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to get available tools';
      return {};
    } finally {
      loading.value = false;
    }
  };

  const askAgent = async (
    question: string,
    userId: string,
    agentId: string,
    modelId: string = 'claude-3-5-haiku-20241022',
    toolCategories?: string[]
  ): Promise<AgentResponse> => {
    try {
      loading.value = true;
      error.value = null;
      const response = await axios.post(`${LANGCHAIN_ENDPOINT}/agent/ask`, {
        question,
        user_id: userId,
        agent_id: agentId,
        model: modelId,
        tool_categories: toolCategories
      });
      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to get agent response';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    getModels,
    getTools,
    askAgent,
    loading,
    error,
  };
};
