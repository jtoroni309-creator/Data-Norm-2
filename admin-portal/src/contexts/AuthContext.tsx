import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI, type UserDetail } from '../services/api';

interface AuthContextType {
  user: UserDetail | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  error: string | null;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserDetail | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if user is already logged in
    const initAuth = async () => {
      const storedToken = localStorage.getItem('admin_token');
      if (storedToken) {
        try {
          // Verify token is still valid by fetching user info
          const response = await fetch(
            `${import.meta.env.VITE_IDENTITY_API_URL || 'http://identity:8000'}/auth/me`,
            {
              headers: {
                Authorization: `Bearer ${storedToken}`,
              },
            }
          );

          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
            setToken(storedToken);
          } else {
            // Token is invalid, clear it
            localStorage.removeItem('admin_token');
          }
        } catch (error) {
          console.error('Auth init error:', error);
          localStorage.removeItem('admin_token');
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await authAPI.login(email, password);

      setToken(response.token);
      setUser(response.user);
      localStorage.setItem('admin_token', response.token);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setToken(null);
      localStorage.removeItem('admin_token');
    }
  };

  const clearError = () => {
    setError(null);
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!user && !!token,
    isLoading,
    login,
    logout,
    error,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
