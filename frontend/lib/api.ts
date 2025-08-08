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

type ResponseType = "json" | "blob" | "text";

class ApiClient {
  private baseUrl: string;
  private apiBaseUrl: string;
  private isRefreshing = false;
  private refreshPromise: Promise<TokenResponse | null> | null = null;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
    // For endpoints that don't need the /api prefix (kept for compatibility)
    this.apiBaseUrl =
      process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
  }

  private async getAuthToken(): Promise<string | null> {
    if (typeof window !== "undefined") {
      return localStorage.getItem("access_token");
    }
    return null;
  }

  private async getRefreshToken(): Promise<string | null> {
    if (typeof window !== "undefined") {
      return localStorage.getItem("refresh_token");
    }
    return null;
  }

  private async refreshAccessToken(): Promise<TokenResponse | null> {
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
        console.log("No refresh token available");
        return null;
      }

      console.log("🔄 Attempting to refresh access token...");
      const response = await fetch(`${this.baseUrl}/api/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        console.log("❌ Token refresh failed:", response.status);
        if (typeof window !== "undefined") {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        }
        return null;
      }

      const tokenData: TokenResponse = await response.json();
      console.log("✅ Token refreshed successfully");

      if (typeof window !== "undefined") {
        localStorage.setItem("access_token", tokenData.access_token);
      }

      return tokenData;
    } catch (error) {
      console.error("❌ Error refreshing token:", error);
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
      }
      return null;
    }
  }

  private async handleResponse<T>(
    response: Response,
    responseType: ResponseType
  ): Promise<T> {
    if (!response.ok) {
      // Build a useful error and ATTACH STATUS so callers can branch on 404
      let message = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const text = await response.text();
        if (text) {
          try {
            const parsed = JSON.parse(text);
            message =
              (parsed && (parsed.detail || parsed.message || parsed.error)) ||
              text ||
              message;
          } catch {
            message = text || message;
          }
        }
      } catch {
        // ignore
      }
      const err: any = new Error(message);
      err.status = response.status;
      err.url = response.url;
      throw err;
    }

    // Success
    if (responseType === "blob") {
      return (await response.blob()) as T;
    }
    if (responseType === "text") {
      return (await response.text()) as T;
    }

    // Default: JSON with safe guard for empty bodies / non-json
    const contentType = response.headers.get("content-type") || "";
    const raw = await response.text();
    if (!raw) return null as T;

    if (contentType.includes("application/json")) {
      try {
        return JSON.parse(raw) as T;
      } catch {
        // Fall through to text if server sent invalid JSON
      }
    }
    // Not JSON or failed to parse -> return raw text
    return raw as unknown as T;
  }

  async request<T>(
    endpoint: string,
    options: RequestInit & { responseType?: ResponseType } = {},
    retryCount: number = 0
  ): Promise<T> {
    // Add /api prefix to all endpoints unless already present
    const apiEndpoint = endpoint.startsWith("/api")
      ? endpoint
      : `/api${endpoint}`;
    const url = `${this.baseUrl}${apiEndpoint}`;
    console.log(`Making request to: ${url}`);

    const token = await this.getAuthToken();

    // Check if body is FormData to handle file uploads
    const isFormData = options.body instanceof FormData;

    const responseType: ResponseType = options.responseType ?? "json";

    const headers: HeadersInit = {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    };

    const config: RequestInit = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);

      // If we get a 401 and this is the first attempt, try to refresh the token
      if (response.status === 401 && retryCount === 0) {
        console.log("🔄 Got 401, attempting token refresh...");
        const refreshedToken = await this.refreshAccessToken();

        if (refreshedToken) {
          console.log("🔄 Retrying request with new token...");
          return this.request<T>(endpoint, options, retryCount + 1);
        } else {
          console.log("❌ Token refresh failed, redirecting to login...");
          if (typeof window !== "undefined") {
            window.location.href = "/";
          }
          throw new Error("Authentication failed. Please log in again.");
        }
      }

      return await this.handleResponse<T>(response, responseType);
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  get<T>(
    endpoint: string,
    options: RequestInit & { responseType?: ResponseType } = {}
  ): Promise<T> {
    return this.request<T>(endpoint, { method: "GET", ...options });
  }

  post<T>(
    endpoint: string,
    data?: any,
    options: RequestInit & { responseType?: ResponseType } = {}
  ): Promise<T> {
    const isFormData = data instanceof FormData;
    return this.request<T>(endpoint, {
      method: "POST",
      body: data ? (isFormData ? data : JSON.stringify(data)) : undefined,
      ...options,
    });
  }

  put<T>(
    endpoint: string,
    data?: any,
    options: RequestInit & { responseType?: ResponseType } = {}
  ): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    });
  }

  patch<T>(
    endpoint: string,
    data?: any,
    options: RequestInit & { responseType?: ResponseType } = {}
  ): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PATCH",
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    });
  }

  delete<T>(
    endpoint: string,
    options: RequestInit & { responseType?: ResponseType } = {}
  ): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE", ...options });
  }
}

export const api = new ApiClient();

// Thin helpers (kept, but now you can also fetch blobs if needed)
export const apiGet = <T>(
  endpoint: string,
  options?: RequestInit & { responseType?: ResponseType }
) => api.get<T>(endpoint, options);
export const apiPost = <T>(
  endpoint: string,
  data?: any,
  options?: RequestInit & { responseType?: ResponseType }
) => api.post<T>(endpoint, data, options);
export const apiPut = <T>(
  endpoint: string,
  data?: any,
  options?: RequestInit & { responseType?: ResponseType }
) => api.put<T>(endpoint, data, options);
export const apiDelete = <T>(
  endpoint: string,
  options?: RequestInit & { responseType?: ResponseType }
) => api.delete<T>(endpoint, options);
export const apiPatch = <T>(
  endpoint: string,
  data?: any,
  options?: RequestInit & { responseType?: ResponseType }
) => api.patch<T>(endpoint, data, options);

// Profile picture specific functions
// (Your API returns JSON metadata; keep as-is)
export const getLatestProfilePicture = (employeeId: number) =>
  apiGet<{
    FilePath: string;
    FileName: string;
    FileSize: number;
    MimeType: string;
  }>(`/api/profile/${employeeId}/latest`);

export const getProfilePicture = (pictureId: number) =>
  apiGet<{
    FilePath: string;
    FileName: string;
    FileSize: number;
    MimeType: string;
  }>(`/api/profile/picture/${pictureId}`);

// Optional: direct blob fetch if you add an endpoint that streams the image
export const getLatestProfilePictureBlob = (employeeId: number) =>
  apiGet<Blob>(`/api/profile/${employeeId}/latest`, { responseType: "blob" });
