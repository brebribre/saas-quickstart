/**
 * API utilities for managing endpoints and versions
 */

// API version configuration
export const API_VERSION = 'v1';
export const API_BASE_URL = `/api/${API_VERSION}`;

// Auth token storage key
export const AUTH_TOKEN_KEY = 'auth_token';

/**
 * Get the stored authentication token
 * @returns The stored token or null if not found
 */
export const getAuthToken = (): string | null => {
  return localStorage.getItem(AUTH_TOKEN_KEY);
};

/**
 * Set the authentication token
 * @param token - The token to store
 */
export const setAuthToken = (token: string): void => {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
};

/**
 * Remove the stored authentication token
 */
export const removeAuthToken = (): void => {
  localStorage.removeItem(AUTH_TOKEN_KEY);
};

/**
 * Check if the user is authenticated
 * @returns True if the user has a stored token
 */
export const isAuthenticated = (): boolean => {
  return !!getAuthToken();
};

/**
 * Get the full URL for an API endpoint
 * @param endpoint - The endpoint path without the base URL
 * @returns The full URL with the base URL and API version
 */
export const getApiUrl = (endpoint: string): string => {
  // Remove leading slash if present
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint;
  return `${API_BASE_URL}/${cleanEndpoint}`;
};

/**
 * Get common fetch options with authentication headers if available
 * @param includeAuth - Whether to include the auth token if available
 * @returns Fetch options with appropriate headers
 */
export const getFetchOptions = (includeAuth = true): RequestInit => {
  const options: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  // Add auth token if available and requested
  if (includeAuth) {
    const token = getAuthToken();
    if (token) {
      (options.headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }
  }

  return options;
};

/**
 * Common fetch options with JSON headers
 */
export const defaultFetchOptions = getFetchOptions();

/**
 * Basic error handler for fetch requests
 * @param response - The fetch response object
 * @returns The response if it's ok, otherwise throws an error
 */
export const handleApiResponse = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `API error: ${response.status}`);
  }
  return response.json();
};

/**
 * Make a GET request to the API
 * @param endpoint - The endpoint to request
 * @param options - Additional fetch options
 * @param includeAuth - Whether to include auth token
 * @returns The parsed JSON response
 */
export const apiGet = async (endpoint: string, options = {}, includeAuth = true) => {
  const fetchOptions = getFetchOptions(includeAuth);
  const response = await fetch(getApiUrl(endpoint), {
    ...fetchOptions,
    method: 'GET',
    ...options,
  });
  return handleApiResponse(response);
};

/**
 * Make a POST request to the API
 * @param endpoint - The endpoint to request
 * @param data - The data to send in the request body
 * @param options - Additional fetch options
 * @param includeAuth - Whether to include auth token
 * @returns The parsed JSON response
 */
export const apiPost = async (endpoint: string, data: any, options = {}, includeAuth = true) => {
  const fetchOptions = getFetchOptions(includeAuth);
  const response = await fetch(getApiUrl(endpoint), {
    ...fetchOptions,
    method: 'POST',
    body: JSON.stringify(data),
    ...options,
  });
  return handleApiResponse(response);
};

/**
 * Send a message via Telegram
 * @param message - The message to send
 * @param chatId - Optional chat ID to send the message to
 * @returns The response from the API
 */
export const sendTelegramMessage = async (message: string, chatId?: string) => {
  const data: { message: string; chat_id?: string } = { message };
  
  if (chatId) {
    data.chat_id = chatId;
  }
  
  return apiPost('bot/send/text', data);
}; 