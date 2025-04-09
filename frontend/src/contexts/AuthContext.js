// frontend/src/contexts/AuthContext.js

import React, { createContext, useState, useEffect, useContext } from 'react';
import { authAPI } from '../services/api';
import { 
  getToken, 
  saveTokens, 
  clearTokens, 
  isAuthenticated as checkAuthStatus,
  parseJwt
} from '../services/auth';

// Auth context
export const AuthContext = createContext();

// Custom hook for using auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is logged in on initial load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        setIsLoading(true);
        
        if (checkAuthStatus()) {
          // Try to get user profile if token exists
          try {
            const response = await authAPI.getProfile();
            setUser(response.data);
            setIsAuthenticated(true);
          } catch (profileError) {
            console.error('Failed to fetch user profile:', profileError);
            // If token is invalid, clear authentication
            clearTokens();
            setUser(null);
            setIsAuthenticated(false);
          }
        } else {
          setUser(null);
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Auth check error:', error);
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  // Login function
  const login = async (credentials) => {
    try {
      const response = await authAPI.login(credentials);
      const { access, refresh } = response.data;
      
      // Save tokens to localStorage
      saveTokens(access, refresh);
      
      // Get user profile
      const userResponse = await authAPI.getProfile();
      setUser(userResponse.data);
      setIsAuthenticated(true);
      
      return userResponse.data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  // Register function
  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData);
      return response.data;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  // Logout function
  const logout = () => {
    clearTokens();
    setUser(null);
    setIsAuthenticated(false);
  };

  // Update profile function
  const updateProfile = async (profileData) => {
    try {
      const response = await authAPI.updateProfile(profileData);
      setUser(response.data);
      return response.data;
    } catch (error) {
      console.error('Profile update error:', error);
      throw error;
    }
  };

  // Change password function
  const changePassword = async (passwordData) => {
    try {
      const response = await authAPI.changePassword(passwordData);
      return response.data;
    } catch (error) {
      console.error('Password change error:', error);
      throw error;
    }
  };

  // Forgot password function
  const forgotPassword = async (email) => {
    try {
      const response = await authAPI.requestPasswordReset(email);
      return response.data;
    } catch (error) {
      console.error('Forgot password error:', error);
      throw error;
    }
  };

  // Reset password function
  const resetPassword = async (tokenData) => {
    try {
      const response = await authAPI.resetPassword(tokenData);
      return response.data;
    } catch (error) {
      console.error('Reset password error:', error);
      throw error;
    }
  };

  // Get current user from token
  const getUserFromToken = () => {
    const token = getToken();
    if (!token) return null;
    
    const payload = parseJwt(token);
    return payload;
  };

  // Context value
  const contextValue = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    register,
    updateProfile,
    changePassword,
    forgotPassword,
    resetPassword,
    getUserFromToken
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};
