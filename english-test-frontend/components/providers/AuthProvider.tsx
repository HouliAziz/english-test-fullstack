'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { apiClient, User as ApiUser } from '@/lib/api';

interface User {
  id: string;
  email: string;
  name: string;
  username: string;
  avatar?: string;
  level: 'beginner' | 'intermediate' | 'advanced';
  totalScore: number;
  streakDays: number;
  joinedDate: string;
  first_name?: string;
  last_name?: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  signup: (email: string, password: string, name: string, username: string) => Promise<boolean>;
  logout: () => void;
  updateProfile: (updates: Partial<User>) => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function convertApiUserToUser(apiUser: ApiUser): User {
  const fullName = [apiUser.first_name, apiUser.last_name].filter(Boolean).join(' ') || apiUser.username;
  
  return {
    id: apiUser.id.toString(),
    email: apiUser.email,
    name: fullName,
    username: apiUser.username,
    level: apiUser.level,
    totalScore: 0, // Will be updated from statistics
    streakDays: 0, // Will be updated from statistics
    joinedDate: apiUser.created_at.split('T')[0],
    first_name: apiUser.first_name,
    last_name: apiUser.last_name,
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in by trying to get profile
    const checkAuth = async () => {
      try {
        const response = await apiClient.getProfile();
        const convertedUser = convertApiUserToUser(response.user);
        setUser(convertedUser);
      } catch (error) {
        // Token is invalid or expired, clear it
        apiClient.clearToken();
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    try {
      const response = await apiClient.login({
        username: email, // Backend accepts email as username
        password,
      });
      
      const convertedUser = convertApiUserToUser(response.user);
      setUser(convertedUser);
      setIsLoading(false);
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      setIsLoading(false);
      return false;
    }
  };

  const signup = async (email: string, password: string, name: string, username: string): Promise<boolean> => {
    setIsLoading(true);
    try {
      const nameParts = name.split(' ');
      const first_name = nameParts[0] || '';
      const last_name = nameParts.slice(1).join(' ') || '';

      const response = await apiClient.register({
        username,
        email,
        password,
        first_name,
        last_name,
        level: 'beginner',
      });
      
      const convertedUser = convertApiUserToUser(response.user);
      setUser(convertedUser);
      setIsLoading(false);
      return true;
    } catch (error) {
      console.error('Signup failed:', error);
      setIsLoading(false);
      return false;
    }
  };

  const logout = () => {
    apiClient.logout();
    setUser(null);
  };

  const updateProfile = async (updates: Partial<User>) => {
    if (!user) return;
    
    try {
      // Convert frontend user updates to backend format
      const backendUpdates: any = {};
      
      if (updates.first_name !== undefined) backendUpdates.first_name = updates.first_name;
      if (updates.last_name !== undefined) backendUpdates.last_name = updates.last_name;
      if (updates.email !== undefined) backendUpdates.email = updates.email;
      if (updates.level !== undefined) backendUpdates.level = updates.level;

      const response = await apiClient.updateProfile(backendUpdates);
      const convertedUser = convertApiUserToUser(response.user);
      setUser(convertedUser);
    } catch (error) {
      console.error('Profile update failed:', error);
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, signup, logout, updateProfile, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}