interface ApiResponse<T = any> {
    data?: T;
    error?: string;
    message?: string;
  }
  
  interface ApiError {
    detail: string;
    status_code: number;
  }

  interface TokenResponse {
    access_token: string;
    token_type: string;
    expires_in: number;
  }
  
  class ApiClient {
    private baseUrl: string;
    private apiBaseUrl: string;
    private isRefreshing = false;
    private refreshPromise: Promise<TokenResponse | null> | null = null;

    constructor() {
      this.baseUrl = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';
      // For endpoints that don't need the /api prefix
      this.apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';
    }
  
    private async getAuthToken(): Promise<string | null> {
      if (typeof window !== 'undefined') {
        return localStorage.getItem('access_token');
      }
      return null;
    }

    private async getRefreshToken(): Promise<string | null> {
      if (typeof window !== 'undefined') {
        return localStorage.getItem('refresh_token');
      }
      return null;
    }

    private async refreshAccessToken(): Promise<TokenResponse | null> {
      // Prevent multiple simultaneous refresh attempts
      if (this.isRefreshing && this.refreshPromise) {
        return this.refreshPromise;
      }

      this.isRefreshing = true;
      this.refreshPromise = this.performTokenRefresh();
      
      try {
        const result = await this.refreshPromise;
        return result;
      } finally {
        this.isRefreshing = false;
        this.refreshPromise = null;
      }
    }

    private async performTokenRefresh(): Promise<TokenResponse | null> {
      try {
        const refreshToken = await this.getRefreshToken();
        if (!refreshToken) {
          console.log('No refresh token available');
          return null;
        }

        console.log('🔄 Attempting to refresh access token...');
        const response = await fetch(`${this.baseUrl}/api/auth/refresh`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (!response.ok) {
          console.log('❌ Token refresh failed:', response.status);
          // Clear tokens on refresh failure
          if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
          }
          return null;
        }

        const tokenData: TokenResponse = await response.json();
        console.log('✅ Token refreshed successfully');

        // Store new tokens
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', tokenData.access_token);
        }

        return tokenData;
      } catch (error) {
        console.error('❌ Error refreshing token:', error);
        // Clear tokens on error
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
        return null;
      }
    }
  
    private async handleResponse<T>(response: Response): Promise<T> {
      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        
        try {
          const errorData: ApiError = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // If parsing fails, use the default message
        }
  
        throw new Error(errorMessage);
      }
  
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return response.json();
      }
      
      return response.text() as T;
    }
  
    async request<T>(
      endpoint: string,
      options: RequestInit = {},
      retryCount: number = 0
    ): Promise<T> {
      // Add /api prefix to all endpoints
      const apiEndpoint = endpoint.startsWith('/api') ? endpoint : `/api${endpoint}`;
      const url = `${this.baseUrl}${apiEndpoint}`;
      console.log(`Making request to: ${url}`); // Add this debug log
      
      const token = await this.getAuthToken();
      
      // Check if body is FormData to handle file uploads
      const isFormData = options.body instanceof FormData;
  
      const config: RequestInit = {
        headers: {
          // Don't set Content-Type for FormData, let browser set it with boundary
          ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
          ...(token && { Authorization: `Bearer ${token}` }),
          ...options.headers,
        },
        ...options,
      };
  
      try {
        const response = await fetch(url, config);
        
        // If we get a 401 and this is the first attempt, try to refresh the token
        if (response.status === 401 && retryCount === 0) {
          console.log('🔄 Got 401, attempting token refresh...');
          const refreshedToken = await this.refreshAccessToken();
          
          if (refreshedToken) {
            console.log('🔄 Retrying request with new token...');
            // Retry the request with the new token
            return this.request<T>(endpoint, options, retryCount + 1);
          } else {
            console.log('❌ Token refresh failed, redirecting to login...');
            // Token refresh failed, redirect to login
            if (typeof window !== 'undefined') {
              window.location.href = '/';
            }
            throw new Error('Authentication failed. Please log in again.');
          }
        }
        
        return await this.handleResponse<T>(response);
      } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        throw error;
      }
    }
  
    async get<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
      return this.request<T>(endpoint, { method: 'GET', ...options });
    }
  
    async post<T>(endpoint: string, data?: any, options: RequestInit = {}): Promise<T> {
      // Check if data is FormData (for file uploads)
      const isFormData = data instanceof FormData;
      
      return this.request<T>(endpoint, {
        method: 'POST',
        body: data ? (isFormData ? data : JSON.stringify(data)) : undefined,
        ...options,
      });
    }
  
    async put<T>(endpoint: string, data?: any, options: RequestInit = {}): Promise<T> {
      return this.request<T>(endpoint, {
        method: 'PUT',
        body: data ? JSON.stringify(data) : undefined,
        ...options,
      });
    }
  
    async delete<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
      return this.request<T>(endpoint, { method: 'DELETE', ...options });
    }
  
    async patch<T>(endpoint: string, data?: any, options: RequestInit = {}): Promise<T> {
      return this.request<T>(endpoint, {
        method: 'PATCH',
        body: data ? JSON.stringify(data) : undefined,
        ...options,
      });
    }
  }
  
  export const api = new ApiClient();
  export const apiGet = <T>(endpoint: string, options?: RequestInit) => api.get<T>(endpoint, options);
export const apiPost = <T>(endpoint: string, data?: any, options?: RequestInit) => api.post<T>(endpoint, data, options);
export const apiPut = <T>(endpoint: string, data?: any, options?: RequestInit) => api.put<T>(endpoint, data, options);
export const apiDelete = <T>(endpoint: string, options?: RequestInit) => api.delete<T>(endpoint, options);
export const apiPatch = <T>(endpoint: string, data?: any, options?: RequestInit) => api.patch<T>(endpoint, data, options);

// Profile picture specific functions
export const getLatestProfilePicture = (employeeId: number) => 
  apiGet<{ FilePath: string; FileName: string; FileSize: number; MimeType: string }>(`/api/profile/${employeeId}/latest`);

export const getProfilePicture = (pictureId: number) => 
  apiGet<{ FilePath: string; FileName: string; FileSize: number; MimeType: string }>(`/api/profile/picture/${pictureId}`);