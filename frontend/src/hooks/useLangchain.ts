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

  return {
    getModels,
    getTools,
    loading,
    error,
  };
};
