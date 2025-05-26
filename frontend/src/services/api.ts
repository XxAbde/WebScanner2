const API_BASE = 'http://localhost:5001/api/v1';

export interface User {
  id: number;
  email: string;
  username: string;
  is_guest: boolean;
  scan_limit: number;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  last_login: string | null;
  remaining_scans: number | string;
}

export interface AuthResponse {
  message: string;
  user: User;
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

class ApiService {
  private baseURL: string;
  private token: string | null;

  constructor() {
    this.baseURL = API_BASE;
    this.token = localStorage.getItem('access_token');
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      method: 'GET',
      mode: 'cors',
      cache: 'no-cache',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
      },
      ...options,
    };

    console.log(`🔄 Making request to: ${url}`);
    console.log(`📋 Config:`, config);

    try {
      const response = await fetch(url, config);
      
      console.log(`📡 Response status: ${response.status}`);
      console.log(`📋 Response headers:`, Object.fromEntries(response.headers.entries()));
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ Error response: ${errorText}`);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      console.log(`✅ Success response:`, data);
      
      return data;
    } catch (error) {
      console.error('💥 Request failed:', error);
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Cannot connect to backend server. Please ensure the backend is running on http://localhost:5001');
      }
      
      throw error;
    }
  }

  // Test methods
  async testConnection() {
    return await this.request('/test/ping');
  }

  async testBackendHealth() {
    const url = 'http://localhost:5001/health';
    console.log(`🏥 Testing backend health: ${url}`);
    
    try {
      const response = await fetch(url, { 
        method: 'GET',
        mode: 'cors',
        headers: { 'Accept': 'application/json' }
      });
      
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('✅ Backend health check passed:', data);
      return data;
    } catch (error) {
      console.error('❌ Backend health check failed:', error);
      throw error;
    }
  }

  // Auth methods that map to users.py endpoints
  async register(userData: {
    email: string;
    username: string;
    password: string;
  }): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/users/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    
    if (response.access_token) {
      this.setToken(response.access_token, response.refresh_token);
    }
    
    return response;
  }

  async login(credentials: {
    email: string;
    password: string;
  }): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/users/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    
    if (response.access_token) {
      this.setToken(response.access_token, response.refresh_token);
    }
    
    return response;
  }

  async createGuestUser(): Promise<AuthResponse> {
    const timestamp = Date.now();
    const guestData = {
      email: `guest_${timestamp}@example.com`,
      username: `guest_${timestamp}`,
      password: `guest_pass_${timestamp}`,
    };

    const response = await this.register(guestData);
    
    if (response.user) {
      const guestUser = {
        ...response.user,
        is_guest: true,
        plan: 'guest',
        scanLimit: 3
      };
      localStorage.setItem('user_data', JSON.stringify(guestUser));
      localStorage.setItem('guest_token', response.access_token);
    }
    
    return response;
  }

  setToken(accessToken: string, refreshToken?: string) {
    this.token = accessToken;
    localStorage.setItem('access_token', accessToken);
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken);
    }
  }

  clearTokens() {
    this.token = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('guest_token');
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  getCurrentUser(): User | null {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  }
}

export default new ApiService();