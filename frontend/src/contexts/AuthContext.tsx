
import React, { createContext, useContext, useState, useEffect } from 'react';
import { AuthUser } from '@/types';

interface AuthContextType {
  user: AuthUser | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  loginAsGuest: () => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for stored auth token
    const storedUser = localStorage.getItem('auth_user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      // Mock API call - replace with actual API
      const response = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      
      if (!response.ok) throw new Error('Login failed');
      
      const userData = await response.json();
      setUser(userData.user);
      localStorage.setItem('auth_user', JSON.stringify(userData.user));
    } catch (error) {
      // For demo purposes, use mock data
      const mockUser: AuthUser = {
        id: 1,
        email,
        username: email.split('@')[0],
        created_at: new Date().toISOString(),
        is_verified: true,
        token: 'mock-token-123'
      };
      setUser(mockUser);
      localStorage.setItem('auth_user', JSON.stringify(mockUser));
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, username: string, password: string) => {
    setIsLoading(true);
    try {
      // Mock API call - replace with actual API
      const response = await fetch('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, username, password }),
      });
      
      if (!response.ok) throw new Error('Registration failed');
      
      const userData = await response.json();
      setUser(userData.user);
      localStorage.setItem('auth_user', JSON.stringify(userData.user));
    } catch (error) {
      // For demo purposes, use mock data
      const mockUser: AuthUser = {
        id: 2,
        email,
        username,
        created_at: new Date().toISOString(),
        is_verified: false,
        token: 'mock-token-456'
      };
      setUser(mockUser);
      localStorage.setItem('auth_user', JSON.stringify(mockUser));
    } finally {
      setIsLoading(false);
    }
  };

  const loginAsGuest = async () => {
    setIsLoading(true);
    try {
      const guestUser: AuthUser = {
        id: 0,
        email: 'guest@example.com',
        username: 'Guest User',
        created_at: new Date().toISOString(),
        is_verified: false,
        scan_limit: 3,
        is_guest: true,
        token: 'guest-token'
      };
      setUser(guestUser);
      localStorage.setItem('auth_user', JSON.stringify(guestUser));
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('auth_user');
  };

  return (
    <AuthContext.Provider value={{ user, login, register, loginAsGuest, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};
