import { apiPost, setAuthToken, removeAuthToken, getAuthToken, isAuthenticated } from './api';

/**
 * Interface for login credentials
 */
interface LoginCredentials {
  email: string;
  password: string;
}

/**
 * Interface for login response
 */
interface LoginResponse {
  token: string;
  user: {
    id: string;
    name: string;
    email: string;
  };
}

/**
 * Login a user with email and password
 * @param credentials - The login credentials
 * @returns The login response with token and user data
 */
export const login = async (credentials: LoginCredentials): Promise<LoginResponse> => {
  try {
    // Don't include auth token in login request
    const response = await apiPost('auth/login', credentials, {}, false);
    
    // Store the token
    if (response.token) {
      setAuthToken(response.token);
    }
    
    return response;
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
};

/**
 * Register a new user
 * @param userData - The user registration data
 * @returns The registration response
 */
export const register = async (userData: any): Promise<any> => {
  try {
    // Don't include auth token in registration request
    const response = await apiPost('auth/register', userData, {}, false);
    return response;
  } catch (error) {
    console.error('Registration failed:', error);
    throw error;
  }
};

/**
 * Logout the current user
 */
export const logout = (): void => {
  removeAuthToken();
  // You can add additional cleanup here if needed
};

/**
 * Get the current user's profile
 * @returns The user profile data
 */
export const getCurrentUser = async (): Promise<any> => {
  try {
    // This request should include the auth token
    const response = await apiPost('auth/me', {});
    return response.user;
  } catch (error) {
    console.error('Failed to get current user:', error);
    throw error;
  }
};

/**
 * Refresh the authentication token
 * @returns The new token
 */
export const refreshToken = async (): Promise<string> => {
  try {
    const response = await apiPost('auth/refresh', {});
    
    if (response.token) {
      setAuthToken(response.token);
      return response.token;
    }
    
    throw new Error('No token received');
  } catch (error) {
    console.error('Token refresh failed:', error);
    throw error;
  }
};

// Export auth utilities from api.ts for convenience
export { getAuthToken, setAuthToken, removeAuthToken, isAuthenticated }; 