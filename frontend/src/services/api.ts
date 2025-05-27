const API_BASE_URL = import.meta.env.VITE_API_URL || '';

interface LoginResponse {
  message: string;
  access_token: string;
  refresh_token: string;
  expires_in: number;
  user: {
    id: number;
    email: string;
    username: string;
    created_at: string;
    is_verified: boolean;
    is_admin?: boolean;
    is_guest?: boolean;
  };
}

interface RegisterResponse {
  message: string;
  access_token: string;
  refresh_token: string;
  expires_in: number;
  user: {
    id: number;
    email: string;
    username: string;
    created_at: string;
    is_verified: boolean;
    is_admin?: boolean;
    is_guest?: boolean;
  };
}

class ApiService {
  private baseUrl = API_BASE_URL;

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Add auth token if available
    const user = localStorage.getItem('auth_user');
    if (user) {
      const parsedUser = JSON.parse(user);
      if (parsedUser.token) {
        defaultHeaders['Authorization'] = `Bearer ${parsedUser.token}`;
      }
    }

    const config: RequestInit = {
      headers: { ...defaultHeaders, ...options.headers },
      ...options,
    };

    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || errorData.message || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  // Auth endpoints
  async login(email: string, password: string): Promise<LoginResponse> {
    return this.request<LoginResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(email: string, username: string, password: string): Promise<RegisterResponse> {
    return this.request<RegisterResponse>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, username, password }),
    });
  }

  async getCurrentUser() {
    return this.request('/api/v1/auth/me');
  }

  async refreshToken(refreshToken: string) {
    return this.request('/api/v1/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }

  // Scan endpoints
  async startScan(targetUrl: string) {
    return this.request('/api/v1/scans', {
      method: 'POST',
      body: JSON.stringify({ target_url: targetUrl }),
    });
  }

  async getScans() {
    return this.request('/api/v1/scans');
  }

  async getScan(scanId: number) {
    return this.request(`/api/v1/scans/${scanId}`);
  }
}

export const apiService = new ApiService();