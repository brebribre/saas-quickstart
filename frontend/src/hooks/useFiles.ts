import { ref } from 'vue';
import axios from 'axios';

export interface FileRecord {
  id: string;
  agent_id: string;
  user_id: string;
  filename: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  uploaded_at: string;
}

export interface FileUploadResponse {
  id: string;
  filename: string;
  file_size: number;
  mime_type: string;
  uploaded_at: string;
}

export interface FileUrl {
  signedUrl: string;
  filename: string;
}

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:5000';
const FILES_ENDPOINT = `${API_BASE_URL}/api/v1/file`;

export const useFiles = () => {
  const loading = ref(false);
  const uploadProgress = ref(0);
  const error = ref<string | null>(null);

  /**
   * Upload a file for an agent
   */
  const uploadFile = async (
    agentId: string, 
    file: Blob, 
    userId: string,
    onProgress?: (progress: number) => void
  ): Promise<FileUploadResponse | null> => {
    try {
      loading.value = true;
      error.value = null;
      uploadProgress.value = 0;
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', userId);
      
      const response = await axios.post(`${FILES_ENDPOINT}/${agentId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            uploadProgress.value = progress;
            if (onProgress) onProgress(progress);
          }
        }
      });
      
      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to upload file';
      return null;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Upload multiple files for an agent
   */
  const uploadFiles = async (
    agentId: string, 
    files: Blob[], 
    userId: string,
    onProgress?: (progress: number) => void
  ): Promise<FileUploadResponse[]> => {
    const results: FileUploadResponse[] = [];
    let overallProgress = 0;
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const result = await uploadFile(agentId, file, userId, (progress) => {
        // Calculate weighted progress based on file's position in array
        const fileWeight = 1 / files.length;
        const fileContribution = progress * fileWeight;
        const previousFilesContribution = (i / files.length) * 100;
        overallProgress = previousFilesContribution + fileContribution;
        
        if (onProgress) onProgress(Math.round(overallProgress));
      });
      
      if (result) {
        results.push(result);
      }
    }
    
    return results;
  };

  /**
   * List all files for a specific agent
   */
  const listAgentFiles = async (agentId: string, userId: string): Promise<FileRecord[]> => {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await axios.get(`${FILES_ENDPOINT}/agent/${agentId}`, {
        params: { user_id: userId }
      });
      
      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to list files';
      return [];
    } finally {
      loading.value = false;
    }
  };

  /**
   * Get a signed URL to access a file
   */
  const getFileUrl = async (fileId: string, userId: string): Promise<FileUrl | null> => {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await axios.get(`${FILES_ENDPOINT}/${fileId}/url`, {
        params: { user_id: userId }
      });
      
      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to get file URL';
      return null;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Delete a file
   */
  const deleteFile = async (fileId: string, userId: string): Promise<boolean> => {
    try {
      loading.value = true;
      error.value = null;
      
      await axios.delete(`${FILES_ENDPOINT}/${fileId}`, {
        params: { user_id: userId }
      });
      
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete file';
      return false;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Check if file type is allowed
   */
  const isFileTypeAllowed = (file: { type: string }): boolean => {
    const allowedTypes = [
      'application/vnd.ms-excel', 
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.oasis.opendocument.spreadsheet',
      'text/csv', 'text/plain', 'application/json',
      'application/pdf', 'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];
    
    // Check image types
    if (file.type.startsWith('image/')) {
      return true;
    }
    
    return allowedTypes.includes(file.type);
  };

  /**
   * Format file size for display
   */
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
  };

  return {
    uploadFile,
    uploadFiles,
    listAgentFiles,
    getFileUrl,
    deleteFile,
    isFileTypeAllowed,
    formatFileSize,
    loading,
    uploadProgress,
    error,
  };
};
