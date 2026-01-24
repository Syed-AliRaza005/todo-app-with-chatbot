'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { getCurrentUser, authenticateUser, deauthenticateUser, registerUser } from '@/lib/auth';
import { authApi } from '@/lib/api';

interface User {
  id: string;
  email: string;
  name: string;
  created_at?: string;
  updated_at?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  signUp: (email: string, password: string, name: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isCancelled = false;

    const fetchUser = async () => {
      try {
        const userData = await getCurrentUser();
        if (!isCancelled) {
          setUser(userData);
        }
      } catch (error) {
        // Only log the error if it's not the "Not authenticated" error
        // This handles the case where a user visits a public page without being logged in
        if (error instanceof Error && error.message !== 'Not authenticated') {
          console.error('Failed to fetch user:', error);
        }
        if (!isCancelled) {
          // Set user to null when not authenticated, which is expected behavior
          setUser(null);
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    };

    fetchUser();

    return () => {
      isCancelled = true;
    };
  }, []);

  const signIn = async (email: string, password: string) => {
    // Sanitize and validate inputs
    const sanitizedEmail = email.trim().toLowerCase();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(sanitizedEmail)) {
      throw new Error('Invalid email format');
    }

    if (password.length < 6) {
      throw new Error('Password must be at least 6 characters');
    }

    try {
      // Try to authenticate with the API first
      const authResult = await authApi.signIn({ email: sanitizedEmail, password });

      // Store the user data and token
      if (typeof window !== 'undefined') {
        // Store token securely (in this case we'll continue using localStorage but with additional security)
        // For production, consider using httpOnly cookies with proper backend support
        localStorage.setItem('auth_token', authResult.access_token);

        // Get user info separately since the login response might not include full user details
        try {
          // Attempt to get user info after successful login
          const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';
          if (!API_BASE_URL) {
            throw new Error('API base URL is not configured');
          }

          // Validate the API base URL to prevent SSRF attacks
          if (!API_BASE_URL.startsWith('https://') && !API_BASE_URL.startsWith('http://')) {
            throw new Error('Invalid API base URL');
          }

          const userResponse = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
              'Authorization': `Bearer ${authResult.access_token}`,
              'Content-Type': 'application/json',
            }
          });

          if (userResponse.ok) {
            const userInfo = await userResponse.json();
            localStorage.setItem('user_data', JSON.stringify(userInfo));
            setUser(userInfo);
          } else {
            // If getting user info fails, use the user ID from the auth result
            const basicUserInfo = {
              id: authResult.user_id,
              email,
              name: email.split('@')[0] // Just for demo
            };
            localStorage.setItem('user_data', JSON.stringify(basicUserInfo));
            setUser(basicUserInfo);
          }
        } catch (userInfoError) {
          // Fallback to basic user info if fetching user info fails
          const basicUserInfo = {
            id: authResult.user_id,
            email,
            name: email.split('@')[0] // Just for demo
          };
          localStorage.setItem('user_data', JSON.stringify(basicUserInfo));
          setUser(basicUserInfo);
        }
      }
    } catch (error) {
      console.error('Sign in failed:', error);
      // Re-throw the error so the UI can handle it appropriately
      throw error;
    }
  };

  const signOut = async () => {
    try {
      await authApi.signOut();
      setUser(null);
    } catch (error) {
      console.error('Sign out failed:', error);
      // Even if the API call fails, we should clear the local state
      await deauthenticateUser();
      setUser(null);
    }
  };

  const signUp = async (email: string, password: string, name: string) => {
    // Sanitize and validate inputs
    const sanitizedEmail = email.trim().toLowerCase();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(sanitizedEmail)) {
      throw new Error('Invalid email format');
    }

    if (password.length < 6) {
      throw new Error('Password must be at least 6 characters');
    }

    if (!name.trim()) {
      throw new Error('Name is required');
    }

    try {
      // Try to sign up with the API first
      const authResult = await authApi.signUp({ email: sanitizedEmail, password, name: name.trim() });

      // Store the user data and token
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', authResult.access_token);

        // Get user info after successful signup
        try {
          // Attempt to get user info after successful signup
          const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';
          if (!API_BASE_URL) {
            throw new Error('API base URL is not configured');
          }

          // Validate the API base URL to prevent SSRF attacks
          if (!API_BASE_URL.startsWith('https://') && !API_BASE_URL.startsWith('http://')) {
            throw new Error('Invalid API base URL');
          }

          const userResponse = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
              'Authorization': `Bearer ${authResult.access_token}`,
              'Content-Type': 'application/json',
            }
          });

          if (userResponse.ok) {
            const userInfo = await userResponse.json();
            localStorage.setItem('user_data', JSON.stringify(userInfo));
            setUser(userInfo);
          } else {
            // If getting user info fails, use the user ID from the auth result
            const basicUserInfo = {
              id: authResult.user_id,
              email,
              name
            };
            localStorage.setItem('user_data', JSON.stringify(basicUserInfo));
            setUser(basicUserInfo);
          }
        } catch (userInfoError) {
          // Fallback to basic user info if fetching user info fails
          const basicUserInfo = {
            id: authResult.user_id,
            email,
            name
          };
          localStorage.setItem('user_data', JSON.stringify(basicUserInfo));
          setUser(basicUserInfo);
        }
      }
    } catch (error) {
      console.error('Sign up failed:', error);
      // Fallback to calling the backend API directly
      const userData = await registerUser(email, password, name);
      setUser(userData);
    }
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, signIn, signOut, signUp }}>
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