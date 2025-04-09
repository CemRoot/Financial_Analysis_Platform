/**
 * API Service Module
 * 
 * This module provides a centralized API client for the application, handling
 * authentication, request/response interceptors, and exposing endpoints for
 * different features of the application. It uses axios for HTTP requests and
 * implements JWT token authentication with automatic token refresh.
 * 
 * Key features:
 * - Centralized API client with base configuration
 * - Authentication token management
 * - Automatic token refresh on 401 errors
 * - Organized API endpoints for different modules
 * - Error handling and logging
 */

// frontend/src/services/api.js
import axios from 'axios';
import { getToken, getRefreshToken, saveTokens, clearTokens, isTokenExpired } from './auth';

/**
 * Create axios instance with base URL and default configuration
 * This ensures consistent configuration across all API requests
 */
const api = axios.create({
  baseURL: 'http://localhost:8002/api',
  headers: {
    'Content-Type': 'application/json',
  },
  // Enable sending cookies in cross-domain requests
  withCredentials: true,
});

// Export the base api instance
export { api };

/**
 * Request interceptor for authentication
 * 
 * Automatically adds the JWT token to all outgoing requests
 * if a token exists in storage
 */
api.interceptors.request.use(
  (config) => {
    // Add token to requests if it exists
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor for token refresh
 * 
 * Handles 401 Unauthorized errors by attempting to refresh the token
 * and retrying the original request with the new token
 */
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 (Unauthorized) and we haven't tried refreshing yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true; // Mark that we've tried refreshing for this request
      
      try {
        // Try to refresh the token
        const refreshToken = getRefreshToken();
        if (!refreshToken || isTokenExpired(refreshToken)) {
          // If no refresh token or it's expired, logout
          clearTokens();
          window.location.href = '/login';
          return Promise.reject(error);
        }
        
        const response = await axios.post(
          `${api.defaults.baseURL}/token/refresh/`,
          { refresh: refreshToken }
        );
        
        // Save new tokens
        const { access } = response.data;
        saveTokens(access, refreshToken);
        
        // Update authorization header and retry the original request
        api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
        originalRequest.headers.Authorization = `Bearer ${access}`;
        
        return api(originalRequest);
      } catch (refreshError) {
        // If token refresh fails, logout and redirect to login
        console.error('Token refresh failed:', refreshError);
        clearTokens();
        window.location.href = '/login?expired=true';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

/**
 * Authentication API endpoints
 * 
 * Handles user registration, login, token refresh, and profile management
 */
export const authAPI = {
  /**
   * Register a new user
   * 
   * @param {Object} userData - User registration data (email, password, name)
   * @returns {Promise} - Response with tokens and user data on success
   */
  register: (userData) => {
    console.log('Attempting to register user:', {
      ...userData,
      password: '********' // Don't log the actual password
    });
    
    // Use the correct URL path with /api prefix
    return axios.post('http://localhost:8002/api/accounts/register/', userData, { withCredentials: true })
      .then(response => {
        console.log('Registration response:', response);
        
        // If we have tokens in the response, save them
        if (response.data && response.data.access) {
          saveTokens(response.data.access, response.data.refresh);
        } else if (response.data && response.data.token) {
          localStorage.setItem('authToken', response.data.token);
        }
        
        return response;
      })
      .catch(error => {
        console.error('Registration error:', error);
        
        // Log detailed error information for debugging
        if (error.response) {
          console.error('Error status:', error.response.status);
          console.error('Error data:', error.response.data);
          
          // Check if it's a 404 (endpoint not found)
          if (error.response.status === 404) {
            throw new Error('Registration endpoint not available. Please contact support.');
          }
          
          // If we have validation errors, format them nicely
          if (error.response.status === 400 && error.response.data) {
            const errorMessages = [];
            const errorData = error.response.data;
            
            Object.keys(errorData).forEach(key => {
              if (Array.isArray(errorData[key])) {
                errorMessages.push(`${key}: ${errorData[key].join(', ')}`);
              } else {
                errorMessages.push(`${key}: ${errorData[key]}`);
              }
            });
            
            if (errorMessages.length > 0) {
              throw new Error(errorMessages.join('\n'));
            }
          }
        } else if (error.request) {
          console.error('No response received:', error.request);
          throw new Error('Server not responding. Please check your connection and try again.');
        }
        
        throw error;
      });
  },
  
  /**
   * Login user and get tokens
   * 
   * @param {Object} credentials - User login credentials (email, password)
   * @returns {Promise} - Response with tokens and user data on success
   */
  login: (credentials) => {
    console.log('Attempting login with credentials:', credentials);
    
    // The token endpoint expects the field name to match the USERNAME_FIELD in the user model
    // In our CustomUser model, we set USERNAME_FIELD = 'email'
    const loginData = { 
      email: credentials.email,
      password: credentials.password
    };
    
    console.log('Sending login data:', { email: loginData.email, password: '********' });
    
    // Use /api/token/ as per the backend URL configuration
    return axios.post('http://localhost:8002/api/token/', loginData, { withCredentials: true })
      .then(response => {
        console.log('Login response:', response);
        
        // If we have tokens in the response, save them
        if (response.data && response.data.access) {
          saveTokens(response.data.access, response.data.refresh);
        }
        
        return response;
      })
      .catch(error => {
        console.error('Login error from token endpoint:', error);
        
        // Check if it's a 404 (user not found in public.accounts_customuser)
        if (error.response && error.response.status === 404) {
          // Try direct login as fallback
          return authAPI.loginDirect(credentials);
        }
        
        // Check if it's a 401 (invalid credentials)
        if (error.response && error.response.status === 401) {
          throw new Error('Invalid email or password. Please try again.');
        }
        
        throw error;
      });
  },
  
  /**
   * Direct login method as fallback
   * 
   * Used when the token endpoint fails, attempts login through a custom endpoint
   * 
   * @param {Object} credentials - User login credentials (email, password)
   * @returns {Promise} - Response with tokens and user data on success
   */
  loginDirect: (credentials) => {
    console.log('Attempting direct login with credentials:', { email: credentials.email, password: '********' });
    
    const loginData = {
      email: credentials.email,
      password: credentials.password
    };
    
    // Detailed logging
    console.log('Direct login request URL:', 'http://localhost:8002/api/accounts/direct-login/');
    console.log('Direct login request headers:', { 'Content-Type': 'application/json', 'withCredentials': true });
    
    // Use the accounts direct login endpoint
    return axios.post('http://localhost:8002/api/accounts/direct-login/', loginData, {
      headers: {
        'Content-Type': 'application/json'
      },
      withCredentials: true
    })
      .then(response => {
        console.log('Direct login successful:', response);
        
        if (response.data && response.data.access) {
          saveTokens(response.data.access, response.data.refresh);
        } else if (response.data && response.data.token) {
          localStorage.setItem('authToken', response.data.token);
        }
        
        return response;
      })
      .catch(error => {
        console.error('Login error from direct login:', error);
        
        // Log detailed error information
        if (error.response) {
          console.error('Direct login error status:', error.response.status);
          console.error('Direct login error data:', error.response.data);
        }
        
        throw error;
      });
  },
  
  // Refresh access token
  refreshToken: (refreshToken) => api.post('/token/refresh/', { refresh: refreshToken }),
  
  // Get current user profile
  getProfile: () => api.get('/accounts/users/me/'),
  
  // Update user profile
  updateProfile: (userData) => api.patch('/accounts/users/update_me/', userData),
  
  // Change password
  changePassword: (passwordData) => api.post('/accounts/change-password/', passwordData),
  
  // Request password reset
  requestPasswordReset: (email) => api.post('/accounts/password-reset/', { email }),
  
  // Reset password with token
  resetPassword: (tokenData) => api.post('/accounts/password-reset/confirm/', tokenData),
  
  // Check if user exists in database
  checkUserExists: (email) => api.get(`/accounts/check-user/?email=${encodeURIComponent(email)}`),
};

/**
 * Watchlist API endpoints
 * 
 * Handles user watchlists and watchlist items management
 */
export const watchlistAPI = {
  // Get all user watchlists
  getWatchlists: () => api.get('/watchlists/'),
  
  // Get specific watchlist
  getWatchlist: (id) => api.get(`/watchlists/${id}/`),
  
  // Create new watchlist
  createWatchlist: (watchlistData) => api.post('/watchlists/', watchlistData),
  
  // Update watchlist
  updateWatchlist: (id, watchlistData) => api.put(`/watchlists/${id}/`, watchlistData),
  
  // Delete watchlist
  deleteWatchlist: (id) => api.delete(`/watchlists/${id}/`),
  
  // Get watchlist items
  getWatchlistItems: (watchlistId) => api.get(`/watchlist-items/?watchlist=${watchlistId}`),
  
  // Add item to watchlist
  addToWatchlist: (itemData) => api.post('/watchlist-items/', itemData),
  
  // Remove item from watchlist
  removeFromWatchlist: (itemId) => api.delete(`/watchlist-items/${itemId}/`),
};

/**
 * User preferences API endpoints
 * 
 * Handles user preferences management
 */
export const preferencesAPI = {
  // Get user preferences
  getPreferences: () => api.get('/preferences/'),
  
  // Update user preferences
  updatePreferences: (preferencesData) => api.patch('/preferences/', preferencesData),
};

/**
 * Stock API endpoints
 * 
 * Handles stock data retrieval and analysis
 */
export const stockAPI = {
  getStocks: (query) => api.get('/stocks/', { params: { q: query } }),
  getStockDetails: (symbol, params) => api.get(`/stocks/${symbol}/`, { params }),
  getHistoricalData: (symbol, period, interval) => 
    api.get(`/stocks/${symbol}/historical/`, { params: { period, interval } }),
  getMarketMovers: () => api.get('/stocks/market/movers/'),
  getSectorPerformance: () => api.get('/stocks/market/sectors/'),
  getMarketIndices: () => api.get('/stocks/market/indices/'),
  getTechnicalIndicators: (symbol) => api.get(`/stocks/${symbol}/indicators/`),
  getIndicatorDetail: (symbol, indicator) => 
    api.get(`/stocks/${symbol}/indicators/${indicator}/`),
  getDividends: (symbol) => api.get(`/stocks/${symbol}/dividends/`),
  getFinancialData: (symbol) => api.get(`/stocks/${symbol}/financials/`),
  getWatchlist: () => api.get('/stocks/watchlist/'),
  addToWatchlist: (data) => api.post('/stocks/watchlist/add/', data),
  removeFromWatchlist: (data) => api.post('/stocks/watchlist/remove/', data),
};

/**
 * News API endpoints
 * 
 * Handles financial news retrieval and analysis
 */
export const newsAPI = {
  getNews: (page, category) => 
    api.get('/news/', { 
      params: { page, category },
      headers: {
        'Content-Type': 'application/json',
        // Ensure auth token is present on each request
        'Authorization': `Bearer ${getToken()}`
      }
    }),
  getNewsDetail: (id) => api.get(`/news/${id}/`),
  getNewsCategories: () => api.get('/news/categories/'),
  getStockNews: (symbol, page) => 
    api.get(`/news/stocks/${symbol}/`, { params: { page } }),
  searchNews: (query) => api.get('/news/search/', { params: { q: query } }),
  getSentimentAnalysis: () => api.get('/news/sentiment-analysis/'),
  getSentimentTrends: () => api.get('/news/sentiment-trends/'),
  getNewsPreferences: () => api.get('/news/preferences/'),
  updateNewsPreferences: (data) => api.patch('/news/preferences/', data),
};

/**
 * Dashboard API endpoints
 * 
 * Handles dashboard data retrieval and customization
 */
export const dashboardAPI = {
  getSummary: () => api.get('/dashboard/summary/'),
  getWidgets: () => api.get('/dashboard/widgets/'),
  getRecentActivity: () => api.get('/dashboard/recent-activity/'),
  getMarketOverview: () => api.get('/dashboard/market-overview/'),
  getUserFavorites: () => api.get('/dashboard/user-favorites/'),
  customizeDashboard: (data) => api.post('/dashboard/customize/', data),
};

/**
 * ML Model Comparison API endpoints
 * 
 * Handles machine learning model comparison and testing
 */
export const modelComparisonAPI = {
  compareModels: () => api.get('/predictions/compare-models/'),
  testModels: (data) => api.post('/predictions/model-comparison/test_models/', data),
  getModelPerformance: () => api.get('/predictions/metrics/'),
};

/**
 * Sentiment Analysis API endpoints
 * 
 * Handles sentiment analysis of news and text
 */
export const sentimentAPI = {
  analyzeSentiment: (texts) => api.post('/predictions/analyze-sentiment/', { texts }),
  getSentimentOverTime: (timeRange) => api.get('/predictions/sentiment-over-time/', { 
    params: { time_range: timeRange } 
  }),
};

/**
 * Market Prediction API endpoints
 * 
 * Handles market prediction using machine learning models
 */
export const marketPredictionAPI = {
  predictDirection: (texts, modelType) => api.post('/predictions/predict-market-direction/', { 
    texts, 
    model_type: modelType 
  }),
  getLatestPredictions: (symbol, days) => api.get('/predictions/predictions/latest/', { 
    params: { symbol, days } 
  }),
  predictStockPrice: (symbol, daysAhead, modelType) => 
    api.get('/predictions/predict-stock-price/', {
      params: { symbol, days_ahead: daysAhead, model_type: modelType }
    }),
};

/**
 * Fetch stocks list with optional query parameter
 * 
 * @param {string} query - Optional search query
 * @returns {Promise<Array>} List of stocks
 */
export const fetchStocks = async (query) => {
  try {
    const response = await stockAPI.getStocks(query);
    return response.data;
  } catch (error) {
    console.error('Error fetching stocks:', error);
    throw error;
  }
};

/**
 * Fetch detailed information for a specific stock
 * 
 * @param {string} symbol - Stock symbol
 * @returns {Promise<Object>} Stock details
 */
export const fetchStockDetails = async (symbol) => {
  try {
    console.log(`Fetching real-time data for ${symbol}...`);
    const response = await stockAPI.getStockDetails(symbol);
    
    // Format and normalize the data
    const stockData = response.data;
    
    // Verify market status data is present
    if (!stockData.market_status) {
      console.warn(`Market status information missing for ${symbol}`);
    }
    
    // Format timestamp if present
    if (stockData.last_updated) {
      stockData.last_updated_formatted = new Date(stockData.last_updated).toLocaleString();
    }
    
    return stockData;
  } catch (error) {
    console.error(`Error fetching stock details for ${symbol}:`, error);
    
    // If we get a specific error about rate limiting or service unavailability
    if (error.response && 
        (error.response.status === 429 || error.response.status === 503)) {
      console.log(`Retrying with fallback data for ${symbol}...`);
      try {
        // Add a query param to indicate we want fallback data
        const fallbackResponse = await stockAPI.getStockDetails(symbol, { use_fallback: true });
        const fallbackData = fallbackResponse.data;
        fallbackData.is_fallback = true;
        return fallbackData;
      } catch (fallbackError) {
        console.error(`Fallback data fetch also failed for ${symbol}:`, fallbackError);
        throw fallbackError;
      }
    }
    
    throw error;
  }
};

/**
 * Fetch price history for a stock
 * 
 * @param {string} symbol - Stock symbol
 * @param {string} period - Time period (1d, 1w, 1m, 3m, 6m, 1y, etc.)
 * @param {string} interval - Time interval between data points
 * @returns {Promise<Array>} Price history data
 */
export const fetchStockPriceHistory = async (symbol, period = '1y', interval = '1d') => {
  try {
    const response = await stockAPI.getHistoricalData(symbol, period, interval);
    return response.data;
  } catch (error) {
    console.error(`Error fetching price history for ${symbol}:`, error);
    throw error;
  }
};

/**
 * Fetch news list with optional category filter
 * 
 * @param {string} category - Optional category filter
 * @param {number} page - Page number for pagination
 * @returns {Promise<Object>} News data with articles and pagination info
 */
export const fetchNewsList = async (category = null, page = 1) => {
  try {
    // Ensure token is available
    const token = getToken();
    if (!token) {
      console.error('No authentication token available');
      throw new Error('Authentication required. Please log in again.');
    }

    const response = await newsAPI.getNews(page, category);
    
    // Check if the response contains expected data structure
    if (!response.data || !response.data.articles) {
      console.warn('News API response missing expected data structure:', response.data);
      throw new Error('Unexpected API response format');
    }
    
    return response.data;
  } catch (error) {
    // Handle specific error cases
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      if (error.response.status === 401) {
        console.error('Authentication error when fetching news. Token may be expired.');
        clearTokens();
        // Use window.location directly rather than through the API to ensure immediate redirect
        window.location.href = '/login?session_expired=true';
        throw new Error('Your session has expired. Please log in again.');
      } else if (error.response.status === 403) {
        throw new Error('You do not have permission to access this resource.');
      } else if (error.response.status === 500) {
        console.error('Server error details:', error.response.data);
        throw new Error('Server error. The team has been notified.');
      }
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received from news API:', error.request);
      throw new Error('Unable to connect to the server. Please check your internet connection.');
    }
    
    console.error('Error fetching news list:', error);
    throw error;
  }
};

/**
 * Fetch detailed information for a specific news article
 * 
 * @param {string} id - News article ID
 * @returns {Promise<Object>} News article details
 */
export const fetchNewsArticle = async (id) => {
  try {
    // Ensure token is available
    const token = getToken();
    if (!token) {
      console.error('No authentication token available');
      throw new Error('Authentication required. Please log in again.');
    }
    
    const response = await newsAPI.getNewsDetail(id);
    return response.data;
  } catch (error) {
    // Handle specific error cases
    if (error.response) {
      if (error.response.status === 401) {
        console.error('Authentication error when fetching news article. Token may be expired.');
        clearTokens();
        window.location.href = '/login?session_expired=true';
        throw new Error('Your session has expired. Please log in again.');
      } else if (error.response.status === 404) {
        throw new Error('News article not found.');
      } else if (error.response.status === 500) {
        console.error('Server error details:', error.response.data);
        throw new Error('Server error. The team has been notified.');
      }
    } else if (error.request) {
      console.error('No response received from news API:', error.request);
      throw new Error('Unable to connect to the server. Please check your internet connection.');
    }
    
    console.error(`Error fetching news article ${id}:`, error);
    throw error;
  }
};

/**
 * Fetch news related to a specific stock
 * 
 * @param {string} symbol - Stock symbol
 * @param {number} page - Page number for pagination
 * @returns {Promise<Array>} Stock news articles
 */
export const fetchStockNews = async (symbol, page = 1) => {
  try {
    const response = await newsAPI.getStockNews(symbol, page);
    return response.data;
  } catch (error) {
    console.error(`Error fetching news for ${symbol}:`, error);
    throw error;
  }
};

/**
 * Fetch financial data for a specific stock
 * 
 * @param {string} symbol - Stock symbol
 * @returns {Promise<Object>} Financial data
 */
export const fetchStockFinancials = async (symbol) => {
  try {
    const response = await stockAPI.getFinancialData(symbol);
    return response.data;
  } catch (error) {
    console.error(`Error fetching financials for ${symbol}:`, error);
    throw error;
  }
};

/**
 * Export a default object with all APIs for convenience
 */
export default {
  auth: authAPI,
  stocks: stockAPI,
  news: newsAPI,
  dashboard: dashboardAPI,
  modelComparison: modelComparisonAPI,
  sentiment: sentimentAPI,
  marketPrediction: marketPredictionAPI,
  watchlist: watchlistAPI,
  preferences: preferencesAPI,
  fetchStocks,
  fetchStockDetails,
  fetchStockPriceHistory,
  fetchStockNews,
  fetchStockFinancials,
  fetchNewsArticle,
  fetchNewsList
};
