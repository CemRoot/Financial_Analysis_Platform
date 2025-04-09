// frontend/src/services/user.js

import { api } from './api';

/**
 * Get user profile data
 * @param {string} userId - The user ID
 * @returns {Promise<Object>} User profile data
 */
export const getUserProfile = async (userId) => {
  try {
    const response = await api.get(`/api/users/${userId}/profile/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching user profile:', error);
    throw error;
  }
};

/**
 * Update user profile data
 * @param {string} userId - The user ID
 * @param {Object} profileData - The profile data to update
 * @returns {Promise<Object>} Updated user profile
 */
export const updateUserProfile = async (userId, profileData) => {
  try {
    const response = await api.put(`/api/users/${userId}/profile/`, profileData);
    return response.data;
  } catch (error) {
    console.error('Error updating user profile:', error);
    throw error;
  }
};

/**
 * Get user settings
 * @param {string} userId - The user ID
 * @returns {Promise<Object>} User settings data
 */
export const getUserSettings = async (userId) => {
  try {
    const response = await api.get(`/api/users/${userId}/settings/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching user settings:', error);
    throw error;
  }
};

/**
 * Update user settings
 * @param {string} userId - The user ID
 * @param {Object} settingsData - The settings data to update
 * @returns {Promise<Object>} Updated user settings
 */
export const updateUserSettings = async (userId, settingsData) => {
  try {
    const response = await api.put(`/api/users/${userId}/settings/`, settingsData);
    return response.data;
  } catch (error) {
    console.error('Error updating user settings:', error);
    throw error;
  }
};

/**
 * Get user activity log
 * @param {string} userId - The user ID
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} User activity data
 */
export const getUserActivity = async (userId, params = {}) => {
  try {
    const response = await api.get(`/api/users/${userId}/activity/`, { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching user activity:', error);
    throw error;
  }
};

/**
 * Get user notifications
 * @param {string} userId - The user ID
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} User notifications
 */
export const getUserNotifications = async (userId, params = {}) => {
  try {
    const response = await api.get(`/api/users/${userId}/notifications/`, { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching user notifications:', error);
    throw error;
  }
};

/**
 * Mark notification as read
 * @param {string} userId - The user ID
 * @param {string} notificationId - The notification ID
 * @returns {Promise<Object>} Updated notification
 */
export const markNotificationAsRead = async (userId, notificationId) => {
  try {
    const response = await api.patch(`/api/users/${userId}/notifications/${notificationId}/`, {
      read: true
    });
    return response.data;
  } catch (error) {
    console.error('Error marking notification as read:', error);
    throw error;
  }
};

/**
 * Update user preferences
 * @param {string} userId - The user ID
 * @param {Object} preferences - User preferences data
 * @returns {Promise<Object>} Updated preferences
 */
export const updateUserPreferences = async (userId, preferences) => {
  try {
    const response = await api.put(`/api/users/${userId}/preferences/`, preferences);
    return response.data;
  } catch (error) {
    console.error('Error updating user preferences:', error);
    throw error;
  }
};

export default {
  getUserProfile,
  updateUserProfile,
  getUserSettings,
  updateUserSettings,
  getUserActivity,
  getUserNotifications,
  markNotificationAsRead,
  updateUserPreferences
};