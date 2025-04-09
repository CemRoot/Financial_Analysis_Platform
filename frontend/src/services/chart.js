// frontend/src/services/chart.js

import { api } from './api';
import { getToken } from './auth';

/**
 * Chart services for handling stock and market data visualization
 */
export const chartService = {
  /**
   * Get historical stock data for charting
   * @param {string} symbol - Stock ticker symbol
   * @param {string} period - Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 5y)
   * @param {string} interval - Data interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk)
   * @returns {Promise<Array>} Array of stock price data points
   */
  async getHistoricalData(symbol, period = '1y', interval = '1d') {
    try {
      console.log(`ChartService: Fetching historical data for ${symbol} (${period}, ${interval})`);
      console.log(`ChartService: API Base URL: ${api.defaults.baseURL}`);
      console.log(`ChartService: Token exists: ${!!getToken()}`);
      
      // Log full URL being requested
      const endpoint = `/stocks/${symbol}/historical/`;
      const fullUrl = `${api.defaults.baseURL}${endpoint}?period=${period}&interval=${interval}`;
      console.log(`ChartService: Full URL: ${fullUrl}`);
      
      const response = await api.get(`/stocks/${symbol}/historical/`, {
        params: { period, interval }
      });
      
      // Log response status and data length
      console.log(`ChartService: Response status: ${response.status}`);
      console.log(`ChartService: Received ${response.data.length} data points`);
      
      if (!response.data || response.data.length === 0) {
        console.warn('ChartService: Received empty data array');
        return [];
      }
      
      // Process data for charts
      return response.data.map(item => ({
        date: new Date(item.date).toLocaleDateString(),
        open: parseFloat(item.open),
        high: parseFloat(item.high),
        low: parseFloat(item.low),
        close: parseFloat(item.close),
        volume: parseInt(item.volume, 10),
        value: parseFloat(item.close), // For area chart
      }));
    } catch (error) {
      console.error('ChartService: Error fetching historical data:', error);
      
      // Log detailed error information
      if (error.response) {
        console.error(`ChartService: Server responded with status ${error.response.status}`);
        console.error('ChartService: Response data:', error.response.data);
        
        // Handle specific error cases
        if (error.response.status === 401) {
          console.error('ChartService: Authentication error - token may be invalid or expired');
        } else if (error.response.status === 404) {
          console.error(`ChartService: Endpoint not found - check API URL configuration`);
        }
      } else if (error.request) {
        console.error('ChartService: No response received from server');
        console.error('ChartService: Network error or CORS issue may be preventing the request');
      } else {
        console.error(`ChartService: Error setting up request: ${error.message}`);
      }
      
      // Re-throw the error for component handling
      throw error;
    }
  },

  /**
   * Get technical indicators for a stock
   * @param {string} symbol - Stock ticker symbol
   * @param {string} indicator - Technical indicator name
   * @returns {Promise<Object>} Technical indicator data
   */
  async getTechnicalIndicator(symbol, indicator) {
    try {
      console.log(`ChartService: Fetching ${indicator} indicator for ${symbol}`);
      
      const response = await api.get(`/stocks/${symbol}/indicators/${indicator}/`);
      console.log(`${indicator} indicator response:`, response.data);
      
      return response.data;
    } catch (error) {
      console.error(`ChartService: Error fetching ${indicator} data:`, error);
      
      // Log detailed error information
      if (error.response) {
        console.error(`ChartService: Server responded with status ${error.response.status}`);
        console.error('ChartService: Response data:', error.response.data);
        
        // Handle specific error cases
        if (error.response.status === 401) {
          console.error('ChartService: Authentication error - token may be invalid or expired');
        } else if (error.response.status === 404) {
          console.error(`ChartService: Endpoint not found - check API URL configuration`);
        }
      } else if (error.request) {
        console.error('ChartService: No response received from server');
        console.error('ChartService: Network error or CORS issue may be preventing the request');
      } else {
        console.error(`ChartService: Error setting up request: ${error.message}`);
      }
      
      // Re-throw the error for component handling
      throw error;
    }
  },

  /**
   * Get all technical indicators for a stock
   * @param {string} symbol - Stock ticker symbol
   * @returns {Promise<Array>} Array of technical indicators
   */
  async getAllIndicators(symbol) {
    try {
      console.log(`ChartService: Fetching all indicators for ${symbol}`);
      
      const response = await api.get(`/stocks/${symbol}/indicators/`);
      console.log('All indicators response:', response.data);
      
      return response.data;
    } catch (error) {
      console.error('ChartService: Error fetching technical indicators:', error);
      
      // Log detailed error information
      if (error.response) {
        console.error(`ChartService: Server responded with status ${error.response.status}`);
        console.error('ChartService: Response data:', error.response.data);
        
        // Handle specific error cases
        if (error.response.status === 401) {
          console.error('ChartService: Authentication error - token may be invalid or expired');
        } else if (error.response.status === 404) {
          console.error(`ChartService: Endpoint not found - check API URL configuration`);
        }
      } else if (error.request) {
        console.error('ChartService: No response received from server');
        console.error('ChartService: Network error or CORS issue may be preventing the request');
      } else {
        console.error(`ChartService: Error setting up request: ${error.message}`);
      }
      
      // Re-throw the error for component handling
      throw error;
    }
  },

  /**
   * Get market index data
   * @returns {Promise<Array>} Array of market indices data
   */
  async getMarketIndices() {
    try {
      console.log('ChartService: Fetching market indices');
      
      const response = await api.get('/stocks/market/indices/');
      console.log('Market indices response:', response.data);
      
      return response.data;
    } catch (error) {
      console.error('ChartService: Error fetching market indices:', error);
      
      // Log detailed error information
      if (error.response) {
        console.error(`ChartService: Server responded with status ${error.response.status}`);
        console.error('ChartService: Response data:', error.response.data);
        
        // Handle specific error cases
        if (error.response.status === 401) {
          console.error('ChartService: Authentication error - token may be invalid or expired');
        } else if (error.response.status === 404) {
          console.error(`ChartService: Endpoint not found - check API URL configuration`);
        }
      } else if (error.request) {
        console.error('ChartService: No response received from server');
        console.error('ChartService: Network error or CORS issue may be preventing the request');
      } else {
        console.error(`ChartService: Error setting up request: ${error.message}`);
      }
      
      // Re-throw the error for component handling
      throw error;
    }
  },

  /**
   * Get sector performance data
   * @returns {Promise<Array>} Array of sector performance data
   */
  async getSectorPerformance() {
    try {
      console.log('ChartService: Fetching sector performance');
      
      const response = await api.get('/stocks/market/sectors/');
      console.log('Sector performance response:', response.data);
      
      return response.data;
    } catch (error) {
      console.error('ChartService: Error fetching sector performance:', error);
      
      // Log detailed error information
      if (error.response) {
        console.error(`ChartService: Server responded with status ${error.response.status}`);
        console.error('ChartService: Response data:', error.response.data);
        
        // Handle specific error cases
        if (error.response.status === 401) {
          console.error('ChartService: Authentication error - token may be invalid or expired');
        } else if (error.response.status === 404) {
          console.error(`ChartService: Endpoint not found - check API URL configuration`);
        }
      } else if (error.request) {
        console.error('ChartService: No response received from server');
        console.error('ChartService: Network error or CORS issue may be preventing the request');
      } else {
        console.error(`ChartService: Error setting up request: ${error.message}`);
      }
      
      // Re-throw the error for component handling
      throw error;
    }
  },

  /**
   * Get market movers (top gainers and losers)
   * @returns {Promise<Object>} Market movers data
   */
  async getMarketMovers() {
    try {
      console.log('ChartService: Fetching market movers');
      
      const response = await api.get('/stocks/market/movers/');
      console.log('Market movers response:', response.data);
      
      return response.data;
    } catch (error) {
      console.error('ChartService: Error fetching market movers:', error);
      
      // Log detailed error information
      if (error.response) {
        console.error(`ChartService: Server responded with status ${error.response.status}`);
        console.error('ChartService: Response data:', error.response.data);
        
        // Handle specific error cases
        if (error.response.status === 401) {
          console.error('ChartService: Authentication error - token may be invalid or expired');
        } else if (error.response.status === 404) {
          console.error(`ChartService: Endpoint not found - check API URL configuration`);
        }
      } else if (error.request) {
        console.error('ChartService: No response received from server');
        console.error('ChartService: Network error or CORS issue may be preventing the request');
      } else {
        console.error(`ChartService: Error setting up request: ${error.message}`);
      }
      
      // Re-throw the error for component handling
      throw error;
    }
  },

  /**
   * Get chart configuration for different chart types
   * @param {string} chartType - Chart type (area, line, candlestick, etc.)
   * @param {Object} theme - Material UI theme object
   * @returns {Object} Chart configuration
   */
  getChartConfig: (chartType, theme) => {
    const baseConfig = {
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          label: {
            backgroundColor: theme.palette.primary.main
          }
        }
      }
    };

    switch (chartType) {
      case 'area':
        return {
          ...baseConfig,
          series: {
            type: 'line',
            smooth: true,
            lineStyle: {
              width: 2
            },
            areaStyle: {
              opacity: 0.8,
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: theme.palette.primary.main
                  },
                  {
                    offset: 1,
                    color: theme.palette.background.default
                  }
                ]
              }
            }
          }
        };

      case 'candlestick':
        return {
          ...baseConfig,
          xAxis: {
            type: 'category',
            boundaryGap: false,
            axisLine: { lineStyle: { color: theme.palette.text.secondary } }
          },
          yAxis: {
            scale: true,
            splitLine: { lineStyle: { color: theme.palette.divider } }
          },
          series: {
            type: 'candlestick',
            itemStyle: {
              color: theme.palette.error.main,
              color0: theme.palette.success.main,
              borderColor: theme.palette.error.main,
              borderColor0: theme.palette.success.main
            }
          }
        };

      case 'line':
      default:
        return {
          ...baseConfig,
          series: {
            type: 'line',
            smooth: true,
            symbolSize: 4,
            lineStyle: {
              width: 2
            }
          }
        };
    }
  },

  /**
   * Format chart data based on chart type
   * @param {Array} data - Raw chart data
   * @param {string} chartType - Chart type
   * @returns {Array} Formatted chart data
   */
  formatChartData: (data, chartType) => {
    if (!data || !Array.isArray(data)) return [];

    switch (chartType) {
      case 'candlestick':
        return data.map(item => ({
          value: [item.open, item.close, item.low, item.high],
          date: item.date
        }));

      case 'volume':
        return data.map(item => ({
          value: item.volume,
          date: item.date
        }));

      case 'area':
      case 'line':
      default:
        return data.map(item => ({
          value: item.close,
          date: item.date
        }));
    }
  },

  /**
   * Apply technical analysis and generate signals
   * @param {Array} data - Historical price data
   * @param {Array} indicators - Technical indicators
   * @returns {Object} Analysis results with buy/sell signals
   */
  analyzeChart: (data, indicators) => {
    // This is a simplified example
    if (!data || !indicators) return { signals: [] };

    const signals = [];
    // Example: Detect crossovers of moving averages
    for (let i = 1; i < data.length; i++) {
      const prevSMA20 = indicators[i - 1]?.sma_20;
      const prevSMA50 = indicators[i - 1]?.sma_50;
      const currSMA20 = indicators[i]?.sma_20;
      const currSMA50 = indicators[i]?.sma_50;

      // Golden Cross (SMA20 crosses above SMA50)
      if (prevSMA20 < prevSMA50 && currSMA20 > currSMA50) {
        signals.push({
          date: data[i].date,
          type: 'buy',
          reason: 'Golden Cross: SMA20 crossed above SMA50',
          price: data[i].close
        });
      }
      // Death Cross (SMA20 crosses below SMA50)
      else if (prevSMA20 > prevSMA50 && currSMA20 < currSMA50) {
        signals.push({
          date: data[i].date,
          type: 'sell',
          reason: 'Death Cross: SMA20 crossed below SMA50',
          price: data[i].close
        });
      }
    }

    return {
      signals,
      summary: {
        buySignals: signals.filter(s => s.type === 'buy').length,
        sellSignals: signals.filter(s => s.type === 'sell').length
      }
    };
  }
};

export default chartService;
