interface ApiResponse<T = any> {
    data?: T;
    error?: string;
    message?: string;
  }
  
  interface ApiError {
    detail: string;
    status_code: number;
  }
  
  class ApiClient {
    private baseUrl: string;
    private apiBaseUrl: string;
  
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
      options: RequestInit = {}
    ): Promise<T> {
      // Use the base URL directly since all our endpoints are API endpoints
      const url = `${this.baseUrl}${endpoint}`;
      console.log(`Making request to: ${url}`); // Add this debug log
      
      const token = await this.getAuthToken();
  
      const config: RequestInit = {
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
          ...options.headers,
        },
        ...options,
      };
  
      try {
        const response = await fetch(url, config);
        return await this.handleResponse<T>(response);
      } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        throw error;
      }
    }
  
    async get<T>(endpoint: string): Promise<T> {
      return this.request<T>(endpoint, { method: 'GET' });
    }
  
    async post<T>(endpoint: string, data?: any): Promise<T> {
      return this.request<T>(endpoint, {
        method: 'POST',
        body: data ? JSON.stringify(data) : undefined,
      });
    }
  
    async put<T>(endpoint: string, data?: any): Promise<T> {
      return this.request<T>(endpoint, {
        method: 'PUT',
        body: data ? JSON.stringify(data) : undefined,
      });
    }
  
    async delete<T>(endpoint: string): Promise<T> {
      return this.request<T>(endpoint, { method: 'DELETE' });
    }
  
    async patch<T>(endpoint: string, data?: any): Promise<T> {
      return this.request<T>(endpoint, {
        method: 'PATCH',
        body: data ? JSON.stringify(data) : undefined,
      });
    }
  }
  
  export const api = new ApiClient();
  export const apiGet = <T>(endpoint: string) => api.get<T>(endpoint);
  export const apiPost = <T>(endpoint: string, data?: any) => api.post<T>(endpoint, data);
  export const apiPut = <T>(endpoint: string, data?: any) => api.put<T>(endpoint, data);
  export const apiDelete = <T>(endpoint: string) => api.delete<T>(endpoint); // Fixed this line
  export const apiPatch = <T>(endpoint: string, data?: any) => api.patch<T>(endpoint, data);