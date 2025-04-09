// frontend/src/components/stocks/StockChart.js

import React, { useState, useEffect, useCallback } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LineChart,
  Line,
  Bar,
  BarChart,
  ComposedChart
} from 'recharts';
import { 
  Box, 
  Card, 
  CardContent, 
  CardHeader, 
  Typography, 
  ButtonGroup, 
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  useTheme,
  Alert
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

// Services
import { chartService } from '../../services/chart';
import { getToken } from '../../services/auth';

// Time periods
const TIME_PERIODS = [
  { label: '1D', value: '1d', interval: '5m' },
  { label: '1W', value: '5d', interval: '15m' },
  { label: '1M', value: '1mo', interval: '1h' },
  { label: '3M', value: '3mo', interval: '1d' },
  { label: '6M', value: '6mo', interval: '1d' },
  { label: '1Y', value: '1y', interval: '1d' },
  { label: '5Y', value: '5y', interval: '1wk' },
];

// Chart types
const CHART_TYPES = [
  { label: 'Area', value: 'area' },
  { label: 'Line', value: 'line' },
  { label: 'Candlestick', value: 'candlestick' },
  { label: 'OHLC', value: 'ohlc' },
];

// Price formatters
const formatPrice = (price) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(price);
};

const formatChangePercent = (percent) => {
  return percent > 0 ? `+${percent.toFixed(2)}%` : `${percent.toFixed(2)}%`;
};

// Custom tooltip
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <Card sx={{ p: 1, border: '1px solid #ddd', boxShadow: 2, maxWidth: 200 }}>
        <Typography variant="body2" color="textSecondary">
          {label}
        </Typography>
        <Typography variant="body1" color="textPrimary" fontWeight="bold">
          {formatPrice(payload[0].value)}
        </Typography>
        {payload[0].payload.open && (
          <Box>
            <Typography variant="caption" display="block">
              Open: {formatPrice(payload[0].payload.open)}
            </Typography>
            <Typography variant="caption" display="block">
              High: {formatPrice(payload[0].payload.high)}
            </Typography>
            <Typography variant="caption" display="block">
              Low: {formatPrice(payload[0].payload.low)}
            </Typography>
            <Typography variant="caption" display="block">
              Close: {formatPrice(payload[0].payload.close)}
            </Typography>
            <Typography variant="caption" display="block">
              Volume: {new Intl.NumberFormat().format(payload[0].payload.volume)}
            </Typography>
          </Box>
        )}
      </Card>
    );
  }
  return null;
};

// Candlestick chart component
const CandlestickChart = ({ data, theme }) => {
  const isUp = (d) => d.close >= d.open;
  
  return (
    <ResponsiveContainer width="100%" height={400}>
      <ComposedChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <XAxis dataKey="date" />
        <YAxis domain={['dataMin', 'dataMax']} />
        <Tooltip content={<CustomTooltip />} />
        <CartesianGrid strokeDasharray="3 3" />
        <Legend />
        
        {/* Candlestick bars */}
        {data.map((d, index) => (
          <Bar
            key={`candle-${index}`}
            dataKey="high"
            fill="transparent"
            stroke="transparent"
            barSize={8}
            yAxisId={0}
          >
            {data.map((entry, i) => (
              <rect
                key={`candle-bar-${i}`}
                x={i * 8}
                y={entry.high > entry.low ? entry.high : entry.low}
                width={8}
                height={Math.abs(entry.high - entry.low)}
                fill="transparent"
                stroke={isUp(entry) ? theme.palette.success.main : theme.palette.error.main}
              />
            ))}
          </Bar>
        ))}
        
        {/* Wicks */}
        {data.map((d, index) => (
          <Line
            key={`wick-${index}`}
            type="monotone"
            dataKey="high"
            stroke={isUp(d) ? theme.palette.success.main : theme.palette.error.main}
            dot={false}
            activeDot={false}
            yAxisId={0}
          />
        ))}
        
        {/* Real Bodies */}
        {data.map((d, index) => (
          <Bar
            key={`body-${index}`}
            dataKey={isUp(d) ? 'close' : 'open'}
            barSize={20}
            fill={isUp(d) ? theme.palette.success.main : theme.palette.error.main}
            stroke={isUp(d) ? theme.palette.success.main : theme.palette.error.main}
            yAxisId={0}
          />
        ))}
      </ComposedChart>
    </ResponsiveContainer>
  );
};

// Main StockChart component
const StockChart = ({ symbol, initialPeriod = '1y', showHeader = true, height = 400 }) => {
  const theme = useTheme();
  const [period, setPeriod] = useState(initialPeriod);
  const [chartType, setChartType] = useState('area');
  const [chartData, setChartData] = useState([]);
  const [stockInfo, setStockInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Debug info state
  const [debugInfo, setDebugInfo] = useState({
    hasToken: false,
    lastApiCall: null,
    lastError: null,
    dataPoints: 0
  });
  
  // Handle period change
  const handlePeriodChange = (newPeriod) => {
    console.log(`Changing period to: ${newPeriod}`);
    setPeriod(newPeriod);
  };
  
  // Get stock data with period/interval
  const fetchStockData = useCallback(async () => {
    if (!symbol) return;
    
    setLoading(true);
    setError(null);
    
    // Get current time period config
    const currentPeriod = TIME_PERIODS.find(p => p.value === period) || TIME_PERIODS[5]; // Default to 1Y
    
    try {
      // Debug: Check if token exists
      const token = getToken();
      setDebugInfo(prev => ({
        ...prev,
        hasToken: !!token,
        lastApiCall: `${symbol}/historical/?period=${currentPeriod.value}&interval=${currentPeriod.interval}`
      }));
      
      console.log(`StockChart: Fetching data for ${symbol} with period=${currentPeriod.value}, interval=${currentPeriod.interval}`);
      console.log(`StockChart: Authentication token exists: ${!!token}`);
      
      // Load stock details
      const stockDetails = await chartService.getStockDetails(symbol);
      setStockInfo({
        currentPrice: stockDetails.current_price,
        change: stockDetails.price_change,
        changePercent: stockDetails.change_percent,
        marketCap: stockDetails.market_cap,
        volume: stockDetails.volume,
        high: stockDetails.high,
        low: stockDetails.low,
        open: stockDetails.open,
        previousClose: stockDetails.previous_close
      });
      
      // Load historical data
      const historicalData = await chartService.getHistoricalData(symbol, currentPeriod.value, currentPeriod.interval);
      console.log(`StockChart: Received ${historicalData.length} historical data points`);
      
      // Update debug info
      setDebugInfo(prev => ({
        ...prev,
        dataPoints: historicalData.length
      }));
      
      setChartData(historicalData);
    } catch (err) {
      console.error('Error fetching stock data:', err);
      setError(`Failed to load chart data: ${err.message}`);
      
      // Update debug info
      setDebugInfo(prev => ({
        ...prev,
        lastError: err.message
      }));
    } finally {
      setLoading(false);
    }
  }, [symbol, period]);
  
  // Load data on mount and when period changes
  useEffect(() => {
    fetchStockData();
  }, [fetchStockData]);
  
  // Helper for price color
  const getChangeColor = (change) => {
    return change >= 0 ? theme.palette.success.main : theme.palette.error.main;
  };

  // Render chart based on type
  const renderChart = () => {
    if (loading) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" height={height}>
          <CircularProgress />
        </Box>
      );
    }
    
    if (error) {
      return (
        <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" height={height}>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
          
          {/* Debug information */}
          <Box mt={2} p={2} sx={{ backgroundColor: '#f5f5f5', borderRadius: 1, width: '100%' }}>
            <Typography variant="subtitle2" gutterBottom>Debug Information:</Typography>
            <Typography variant="body2">Symbol: {symbol}</Typography>
            <Typography variant="body2">Valid Token: {debugInfo.hasToken ? 'Yes' : 'No'}</Typography>
            <Typography variant="body2">API Call: {debugInfo.lastApiCall}</Typography>
            <Typography variant="body2">Error: {debugInfo.lastError}</Typography>
          </Box>
          
          <Button 
            variant="contained" 
            color="primary" 
            onClick={fetchStockData} 
            sx={{ mt: 2 }}
          >
            Retry
          </Button>
        </Box>
      );
    }
    
    if (!chartData || chartData.length === 0) {
      return (
        <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" height={height}>
          <Alert severity="warning">
            No data available for this stock and time period.
          </Alert>
          
          {/* Debug information */}
          <Box mt={2} p={2} sx={{ backgroundColor: '#f5f5f5', borderRadius: 1, width: '100%' }}>
            <Typography variant="subtitle2" gutterBottom>Debug Information:</Typography>
            <Typography variant="body2">Symbol: {symbol}</Typography>
            <Typography variant="body2">Valid Token: {debugInfo.hasToken ? 'Yes' : 'No'}</Typography>
            <Typography variant="body2">API Call: {debugInfo.lastApiCall}</Typography>
            <Typography variant="body2">Data Points: {debugInfo.dataPoints}</Typography>
          </Box>
        </Box>
      );
    }

    switch (chartType) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={['dataMin', 'dataMax']} tickFormatter={tick => formatPrice(tick)} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line
                type="monotone"
                dataKey="close"
                stroke={theme.palette.primary.main}
                activeDot={{ r: 8 }}
                name="Price"
              />
            </LineChart>
          </ResponsiveContainer>
        );
        
      case 'candlestick':
        return <CandlestickChart data={chartData} theme={theme} />;
        
      case 'ohlc':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={['dataMin', 'dataMax']} tickFormatter={tick => formatPrice(tick)} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar dataKey="high" name="High" fill={theme.palette.success.light} />
              <Bar dataKey="low" name="Low" fill={theme.palette.error.light} />
              <Line type="monotone" dataKey="open" name="Open" stroke={theme.palette.info.main} />
              <Line type="monotone" dataKey="close" name="Close" stroke={theme.palette.primary.main} />
            </ComposedChart>
          </ResponsiveContainer>
        );
        
      case 'area':
      default:
        return (
          <ResponsiveContainer width="100%" height={height}>
            <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                  <stop
                    offset="5%"
                    stopColor={stockInfo && stockInfo.change >= 0 ? theme.palette.success.main : theme.palette.error.main}
                    stopOpacity={0.8}
                  />
                  <stop
                    offset="95%"
                    stopColor={stockInfo && stockInfo.change >= 0 ? theme.palette.success.main : theme.palette.error.main}
                    stopOpacity={0}
                  />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={['dataMin', 'dataMax']} tickFormatter={tick => formatPrice(tick)} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Area
                type="monotone"
                dataKey="close"
                stroke={stockInfo && stockInfo.change >= 0 ? theme.palette.success.main : theme.palette.error.main}
                fillOpacity={1}
                fill="url(#colorPrice)"
                name="Price"
              />
            </AreaChart>
          </ResponsiveContainer>
        );
    }
  };

  return (
    <Card>
      {showHeader && (
        <CardHeader
          title={
            <Box display="flex" alignItems="center">
              <Typography variant="h6" component="div">
                {symbol}
              </Typography>
              {stockInfo && (
                <Box ml={2} display="flex" alignItems="center">
                  <Typography variant="h6" color={getChangeColor(stockInfo.change)}>
                    {formatPrice(stockInfo.currentPrice)}
                  </Typography>
                  <Box ml={1} display="flex" alignItems="center">
                    {stockInfo.change >= 0 ? (
                      <TrendingUpIcon sx={{ color: theme.palette.success.main }} />
                    ) : (
                      <TrendingDownIcon sx={{ color: theme.palette.error.main }} />
                    )}
                    <Typography
                      variant="body2"
                      color={getChangeColor(stockInfo.change)}
                      sx={{ ml: 0.5 }}
                    >
                      {formatChangePercent(stockInfo.changePercent)}
                    </Typography>
                  </Box>
                </Box>
              )}
            </Box>
          }
          action={
            <Box display="flex" alignItems="center">
              <FormControl variant="outlined" size="small" sx={{ minWidth: 120, mr: 2 }}>
                <InputLabel id="chart-type-label">Chart Type</InputLabel>
                <Select
                  labelId="chart-type-label"
                  id="chart-type"
                  value={chartType}
                  onChange={(e) => setChartType(e.target.value)}
                  label="Chart Type"
                >
                  {CHART_TYPES.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <ButtonGroup size="small" aria-label="time period">
                {TIME_PERIODS.map((timePeriod) => (
                  <Button
                    key={timePeriod.value}
                    onClick={() => handlePeriodChange(timePeriod.value)}
                    variant={period === timePeriod.value ? 'contained' : 'outlined'}
                  >
                    {timePeriod.label}
                  </Button>
                ))}
              </ButtonGroup>
            </Box>
          }
        />
      )}
      <CardContent>
        {renderChart()}
      </CardContent>
    </Card>
  );
};

export default StockChart;
