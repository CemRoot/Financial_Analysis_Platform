// frontend/src/services/auth.js

/**
 * Utility functions for authentication and token management
 */
import axios from 'axios';

// Token storage keys
const ACCESS_TOKEN_KEY = 'financial_analysis_access_token';
const REFRESH_TOKEN_KEY = 'financial_analysis_refresh_token';

/**
 * Save tokens to localStorage
 * @param {string} accessToken - JWT access token
 * @param {string} refreshToken - JWT refresh token
 */
export const saveTokens = (accessToken, refreshToken) => {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
};

/**
 * Get access token from localStorage
 * @returns {string|null} The access token or null if not found
 */
export const getToken = () => {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
};

/**
 * Get refresh token from localStorage
 * @returns {string|null} The refresh token or null if not found
 */
export const getRefreshToken = () => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

/**
 * Clear tokens from localStorage (logout)
 */
export const clearTokens = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

/**
 * Check if user is authenticated (has valid token)
 * @returns {boolean} True if token exists
 */
export const isAuthenticated = () => {
  const token = getToken();
  return !!token;
};

/**
 * Parse a JWT token to get payload data
 * @param {string} token - JWT token
 * @returns {Object} Decoded payload
 */
export const parseJwt = (token) => {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch (e) {
    return null;
  }
};

/**
 * Check if token is expired
 * @param {string} token - JWT token
 * @returns {boolean} True if token is expired
 */
export const isTokenExpired = (token) => {
  if (!token) return true;
  
  const payload = parseJwt(token);
  if (!payload) return true;
  
  const now = Date.now() / 1000;
  return payload.exp < now;
};

/**
 * Register a new user
 * @param {Object} userData - User registration data
 * @returns {Promise<Object>} Registration response
 */
export const register = async (userData) => {
  try {
    const response = await axios.post('/api/accounts/register/', userData);
    return response.data;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
};

/**
 * Send password reset email
 * @param {string} email - User email
 * @returns {Promise<Object>} Password reset response
 */
export const sendPasswordResetEmail = async (email) => {
  try {
    const response = await axios.post('/api/accounts/password-reset/', { email });
    return response.data;
  } catch (error) {
    console.error('Password reset request error:', error);
    throw error;
  }
};

/**
 * Validate reset token
 * @param {string} token - Password reset token
 * @returns {Promise<boolean>} Token validity
 */
export const validateResetToken = async (token) => {
  try {
    const response = await axios.get(`/api/accounts/password-reset/validate/${token}/`);
    return response.data.valid;
  } catch (error) {
    console.error('Token validation error:', error);
    return false;
  }
};

/**
 * Reset password with token
 * @param {Object} tokenData - Token and new password data
 * @returns {Promise<Object>} Password reset response
 */
export const resetPassword = async (tokenData) => {
  try {
    const response = await axios.post('/api/accounts/password-reset/confirm/', tokenData);
    return response.data;
  } catch (error) {
    console.error('Password reset error:', error);
    throw error;
  }
};
