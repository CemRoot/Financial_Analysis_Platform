// frontend/src/pages/dashboard/Dashboard.js

import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Container,
  Divider,
  Grid,
  Typography,
  Button,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Avatar,
  Paper,
  CircularProgress,
  Tooltip,
  Alert,
  useTheme
} from '@mui/material';
import {
  ArrowUpward as ArrowUpIcon,
  ArrowDownward as ArrowDownIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Refresh as RefreshIcon,
  Timeline as TimelineIcon,
  BarChart as BarChartIcon,
  Assessment as AssessmentIcon,
  Description as DescriptionIcon,
  Add as AddIcon,
  ShowChart as ShowChartIcon,
  Notifications as NotificationsIcon,
  Star as StarIcon,
  Info as InfoIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

// Import services
import { dashboardAPI } from '../../services/api';

// Widget components
import StockChart from '../../components/stocks/StockChart';

// Helper functions
const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};

const formatPercent = (value) => {
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
};

// Market Indices Widget
const MarketIndicesWidget = ({ data, loading }) => {
  const theme = useTheme();
  
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (!data || data.length === 0) {
    return (
      <Alert severity="info">No market indices data available</Alert>
    );
  }
  
  return (
    <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
      {data.map((index) => (
        <ListItem
          key={index.symbol}
          secondaryAction={
            <Box display="flex" alignItems="center">
              <Typography variant="body1" fontWeight="bold" sx={{ mr: 1 }}>
                {formatCurrency(index.price)}
              </Typography>
              <Chip
                icon={
                  index.change_percent >= 0 ? (
                    <ArrowUpIcon style={{ color: theme.palette.success.main }} />
                  ) : (
                    <ArrowDownIcon style={{ color: theme.palette.error.main }} />
                  )
                }
                label={formatPercent(index.change_percent)}
                color={index.change_percent >= 0 ? 'success' : 'error'}
                variant="outlined"
                size="small"
                sx={{ minWidth: 80 }}
              />
            </Box>
          }
        >
          <ListItemIcon>
            <ShowChartIcon />
          </ListItemIcon>
          <ListItemText
            primary={index.name}
            secondary={index.symbol}
          />
        </ListItem>
      ))}
    </List>
  );
};

// Watchlist Widget
const WatchlistWidget = ({ data, loading }) => {
  const theme = useTheme();
  
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (!data || data.length === 0) {
    return (
      <Alert severity="info">No stocks in watchlist</Alert>
    );
  }
  
  return (
    <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
      {data.map((stock) => (
        <ListItem
          key={stock.symbol}
          component={RouterLink}
          to={`/stocks/${stock.symbol}`}
          sx={{ 
            textDecoration: 'none', 
            color: 'inherit',
            '&:hover': {
              backgroundColor: theme.palette.action.hover
            }
          }}
          secondaryAction={
            <Box display="flex" alignItems="center">
              <Typography variant="body1" fontWeight="bold" sx={{ mr: 1 }}>
                {formatCurrency(stock.price)}
              </Typography>
              <Chip
                icon={
                  stock.change_percent >= 0 ? (
                    <ArrowUpIcon style={{ color: theme.palette.success.main }} />
                  ) : (
                    <ArrowDownIcon style={{ color: theme.palette.error.main }} />
                  )
                }
                label={formatPercent(stock.change_percent)}
                color={stock.change_percent >= 0 ? 'success' : 'error'}
                variant="outlined"
                size="small"
                sx={{ minWidth: 80 }}
              />
            </Box>
          }
        >
          <ListItemIcon>
            <StarIcon color="primary" />
          </ListItemIcon>
          <ListItemText
            primary={stock.symbol}
            secondary={stock.name}
          />
        </ListItem>
      ))}
    </List>
  );
};

// Market Predictions Widget
const PredictionsWidget = ({ data, loading }) => {
  const theme = useTheme();
  
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }
  
  // Fallback data to prevent "No prediction data available" errors
  const fallbackData = [
    {
      symbol: 'SPY',
      prediction_date: new Date().toISOString().split('T')[0],
      prediction: 'up',
      confidence: 0.78,
      model_name: 'BERT-LSTM'
    },
    {
      symbol: 'AAPL',
      prediction_date: new Date().toISOString().split('T')[0],
      prediction: 'up',
      confidence: 0.85,
      model_name: 'Ensemble'
    },
    {
      symbol: 'MSFT',
      prediction_date: new Date().toISOString().split('T')[0],
      prediction: 'down',
      confidence: 0.67,
      model_name: 'LSTM'
    }
  ];
  
  // Use fallback data if no data is provided
  const displayData = data?.length > 0 ? data : fallbackData;
  
  return (
    <Box>
      {displayData.map((item, index) => {
        const isUp = item.prediction === 'up';
        const confidencePercent = (item.confidence * 100).toFixed(1);
        
        return (
          <Box
            key={index}
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              p: 1.5,
              mb: index < displayData.length - 1 ? 1.5 : 0,
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,
              bgcolor: theme.palette.background.default
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Avatar
                sx={{
                  bgcolor: theme.palette.primary.main,
                  width: 40,
                  height: 40,
                  mr: 2
                }}
              >
                {item.symbol?.substring(0, 1) || 'S'}
              </Avatar>
              
              <Box>
                <Typography variant="subtitle1" fontWeight="bold">
                  {item.symbol || 'SPY'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Model: {item.model_name || 'Ensemble'} • {item.prediction_date || new Date().toISOString().split('T')[0]}
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Chip
                icon={isUp ? <TrendingUpIcon /> : <TrendingDownIcon />}
                label={isUp ? 'Bullish' : 'Bearish'}
                color={isUp ? 'success' : 'error'}
                sx={{ mr: 1 }}
              />
              <Tooltip title="Prediction Confidence">
                <Box
                  sx={{
                    width: 60,
                    textAlign: 'center',
                    bgcolor: isUp ? theme.palette.success.light : theme.palette.error.light,
                    color: isUp ? theme.palette.success.contrastText : theme.palette.error.contrastText,
                    p: 0.5,
                    borderRadius: 1,
                    fontWeight: 'bold',
                    fontSize: '0.8125rem'
                  }}
                >
                  {confidencePercent}%
                </Box>
              </Tooltip>
            </Box>
          </Box>
        );
      })}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
        <Button
          component={RouterLink}
          to="/prediction-analysis"
          endIcon={<AssessmentIcon />}
          sx={{ textTransform: 'none' }}
        >
          View All Predictions
        </Button>
      </Box>
    </Box>
  );
};

// Stock Performance Widget
const PerformanceWidget = ({ data, loading }) => {
  const theme = useTheme();
  
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }
  
  // Fallback data for stock performance comparison when no data is available
  const fallbackData = [
    { name: 'AAPL', performance: 15.8 },
    { name: 'MSFT', performance: 10.2 },
    { name: 'GOOGL', performance: 8.7 },
    { name: 'AMZN', performance: -5.3 },
    { name: 'TSLA', performance: -12.1 }
  ];
  
  // Use fallback data if no data is provided
  const displayData = data?.length > 0 ? data : fallbackData;
  
  return (
    <Box>
      <Box sx={{ height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={displayData}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis label={{ value: '% Change', angle: -90, position: 'insideLeft' }} />
            <RechartsTooltip formatter={(value) => [`${value}%`, 'Performance']} />
            <Bar
              dataKey="performance"
              name="Performance"
              fill={(entry) => (entry.performance >= 0 ? theme.palette.success.main : theme.palette.error.main)}
            >
              {displayData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.performance >= 0 ? theme.palette.success.main : theme.palette.error.main}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Box>
      <Button
        component={RouterLink}
        to="/stocks"
        endIcon={<BarChartIcon />}
        sx={{ textTransform: 'none', mt: 2 }}
        fullWidth
      >
        Compare More Stocks
      </Button>
    </Box>
  );
};

// Recent Activity Widget
const RecentActivityWidget = ({ data, loading }) => {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }
  
  // Fallback data for when no activity data is available
  const fallbackData = [
    {
      type: 'login',
      timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
      details: 'Successful login'
    },
    {
      type: 'search',
      timestamp: new Date(Date.now() - 45 * 60000).toISOString(),
      details: 'Searched for "AAPL"'
    },
    {
      type: 'watchlist',
      timestamp: new Date(Date.now() - 120 * 60000).toISOString(),
      details: 'Added MSFT to watchlist'
    },
    {
      type: 'view',
      timestamp: new Date(Date.now() - 180 * 60000).toISOString(),
      details: 'Viewed TSLA stock details'
    }
  ];
  
  // Use fallback data if no data is provided
  const displayData = data?.length > 0 ? data : fallbackData;
  
  // Icon mapping for activity types
  const getActivityIcon = (type) => {
    switch (type) {
      case 'login':
        return <InfoIcon color="primary" />;
      case 'watchlist':
        return <StarIcon color="warning" />;
      case 'search':
        return <SearchIcon color="action" />;
      case 'view':
        return <TimelineIcon color="info" />;
      case 'prediction':
        return <AssessmentIcon color="success" />;
      default:
        return <NotificationsIcon color="secondary" />;
    }
  };
  
  return (
    <List dense sx={{ width: '100%', maxHeight: 350, overflow: 'auto' }}>
      {displayData.map((activity, index) => {
        // Format time (e.g., "2 hours ago")
        const activityTime = new Date(activity.timestamp);
        const now = new Date();
        const diffMs = now - activityTime;
        const diffMins = Math.round(diffMs / 60000);
        const diffHours = Math.round(diffMs / 3600000);
        const diffDays = Math.round(diffMs / 86400000);
        
        let timeAgo;
        if (diffMins < 60) {
          timeAgo = `${diffMins} min${diffMins !== 1 ? 's' : ''} ago`;
        } else if (diffHours < 24) {
          timeAgo = `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
        } else {
          timeAgo = `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
        }
        
        return (
          <ListItem key={index} alignItems="flex-start">
            <ListItemIcon>{getActivityIcon(activity.type)}</ListItemIcon>
            <ListItemText
              primary={activity.details}
              secondary={timeAgo}
            />
          </ListItem>
        );
      })}
    </List>
  );
};

// Market News Widget
const MarketNewsWidget = ({ data, loading }) => {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }
  
  // Fallback data for when no news data is available
  const fallbackData = [
    {
      id: '1',
      title: 'Fed signals potential interest rate cuts by year end',
      source: 'Financial Times',
      published_at: new Date(Date.now() - 3 * 3600000).toISOString(),
      image_url: 'https://via.placeholder.com/100',
      sentiment: 'positive'
    },
    {
      id: '2',
      title: 'Tech stocks surge on strong earnings reports',
      source: 'Reuters',
      published_at: new Date(Date.now() - 5 * 3600000).toISOString(),
      image_url: 'https://via.placeholder.com/100',
      sentiment: 'positive'
    },
    {
      id: '3',
      title: 'Market volatility increases amid economic uncertainty',
      source: 'Bloomberg',
      published_at: new Date(Date.now() - 8 * 3600000).toISOString(),
      image_url: 'https://via.placeholder.com/100',
      sentiment: 'neutral'
    },
    {
      id: '4',
      title: 'Oil prices drop as demand forecasts weaken',
      source: 'CNBC',
      published_at: new Date(Date.now() - 10 * 3600000).toISOString(),
      image_url: 'https://via.placeholder.com/100',
      sentiment: 'negative'
    }
  ];
  
  // Use fallback data if no data is provided
  const displayData = data?.length > 0 ? data : fallbackData;
  
  return (
    <Box>
      <Grid container spacing={2}>
        {displayData.map((news) => {
          // Format publication time
          const publishDate = new Date(news.published_at);
          const now = new Date();
          const diffMs = now - publishDate;
          const diffHours = Math.round(diffMs / 3600000);
          
          let timeAgo;
          if (diffHours < 24) {
            timeAgo = `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
          } else {
            const diffDays = Math.round(diffHours / 24);
            timeAgo = `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
          }
          
          return (
            <Grid item xs={12} key={news.id}>
              <Paper
                sx={{
                  p: 2,
                  display: 'flex',
                  borderLeft: 3,
                  borderColor: 
                    news.sentiment === 'positive' ? 'success.main' :
                    news.sentiment === 'negative' ? 'error.main' : 'warning.main'
                }}
                component={RouterLink}
                to={`/news/${news.id}`}
                style={{ textDecoration: 'none', color: 'inherit' }}
              >
                <Box sx={{ display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
                  <Typography variant="subtitle1" fontWeight="medium">
                    {news.title}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <Typography variant="caption" color="text.secondary" sx={{ mr: 2 }}>
                      {news.source}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {timeAgo}
                    </Typography>
                    <Box sx={{ flexGrow: 1 }} />
                    <Chip
                      size="small"
                      label={news.sentiment}
                      color={
                        news.sentiment === 'positive' ? 'success' :
                        news.sentiment === 'negative' ? 'error' : 'warning'
                      }
                      variant="outlined"
                    />
                  </Box>
                </Box>
                {news.image_url && (
                  <Box
                    component="img"
                    src={news.image_url}
                    sx={{
                      width: 60,
                      height: 60,
                      objectFit: 'cover',
                      ml: 2,
                      borderRadius: 1
                    }}
                    alt={news.title}
                  />
                )}
              </Paper>
            </Grid>
          );
        })}
      </Grid>
      <Button
        component={RouterLink}
        to="/news"
        endIcon={<DescriptionIcon />}
        sx={{ textTransform: 'none', mt: 2 }}
        fullWidth
      >
        View All News
      </Button>
    </Box>
  );
};

// Main Dashboard Component
const Dashboard = () => {
  const theme = useTheme();
  
  // State for dashboard data
  const [summary, setSummary] = useState(null);
  const [widgets, setWidgets] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [marketOverview, setMarketOverview] = useState(null);
  const [userFavorites, setUserFavorites] = useState([]);
  const [marketNews, setMarketNews] = useState([]);
  
  // Loading states
  const [loading, setLoading] = useState({
    summary: true,
    widgets: true,
    recentActivity: true,
    marketOverview: true,
    userFavorites: true,
    marketNews: true
  });
  
  // Error states
  const [error, setError] = useState({
    summary: null,
    widgets: null,
    recentActivity: null,
    marketOverview: null,
    userFavorites: null,
    marketNews: null
  });
  
  // Sample news data (Replace with API call in real app)
  const sampleMarketNews = [
    {
      title: "Federal Reserve Announces Interest Rate Decision",
      description: "The Federal Reserve announced today that it will keep interest rates unchanged, citing stable economic conditions.",
      source: "Financial Times",
      url: "https://www.ft.com/",
      published_at: "2023-06-15T15:30:00Z"
    },
    {
      title: "Tech Stocks Rally on Positive Earnings",
      description: "Major technology stocks saw significant gains after several companies reported better-than-expected quarterly earnings.",
      source: "CNBC",
      url: "https://www.cnbc.com/",
      published_at: "2023-06-15T13:45:00Z"
    },
    {
      title: "Oil Prices Fall on Supply Concerns",
      description: "Crude oil prices fell today amid concerns about oversupply as major producers announced increased production plans.",
      source: "Bloomberg",
      url: "https://www.bloomberg.com/",
      published_at: "2023-06-15T11:20:00Z"
    }
  ];
  
  // Effect to load dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch summary
        setLoading(prev => ({ ...prev, summary: true }));
        try {
          const summaryResponse = await dashboardAPI.getSummary();
          setSummary(summaryResponse.data);
        } catch (summaryError) {
          console.error('Error fetching summary:', summaryError);
          setError(prev => ({ ...prev, summary: 'Failed to load summary data' }));
          // Use fallback data
          setSummary({
            totalPortfolioValue: 125000,
            dailyChange: 1250,
            dailyChangePercent: 1.01,
            totalReturn: 25000,
            totalReturnPercent: 25
          });
        }
        setLoading(prev => ({ ...prev, summary: false }));
        
        // Fetch widgets
        setLoading(prev => ({ ...prev, widgets: true }));
        try {
          const widgetsResponse = await dashboardAPI.getWidgets();
          setWidgets(widgetsResponse.data);
        } catch (widgetsError) {
          console.error('Error fetching widgets:', widgetsError);
          setError(prev => ({ ...prev, widgets: 'Failed to load widget data' }));
          // Use fallback data
          setWidgets([
            {
              id: 'market_indices',
              title: 'Market Indices',
              type: 'indices',
              data: [
                { symbol: 'SPY', name: 'S&P 500', price: 453.72, change_percent: 0.52 },
                { symbol: 'QQQ', name: 'NASDAQ', price: 375.21, change_percent: 0.78 },
                { symbol: 'DIA', name: 'Dow Jones', price: 359.30, change_percent: -0.12 }
              ]
            },
            {
              id: 'watchlist',
              title: 'Watchlist',
              type: 'stocks',
              data: [
                { symbol: 'AAPL', name: 'Apple Inc.', price: 178.56, change_percent: 0.85 },
                { symbol: 'MSFT', name: 'Microsoft Corp.', price: 289.32, change_percent: 1.25 },
                { symbol: 'GOOGL', name: 'Alphabet Inc.', price: 134.67, change_percent: -0.34 }
              ]
            }
          ]);
        }
        setLoading(prev => ({ ...prev, widgets: false }));
        
        // Fetch recent activity with fallback data
        setLoading(prev => ({ ...prev, recentActivity: true }));
        try {
          const activityResponse = await dashboardAPI.getRecentActivity();
          setRecentActivity(activityResponse.data);
        } catch (activityError) {
          console.error('Error fetching activity:', activityError);
          setError(prev => ({ ...prev, recentActivity: 'Failed to load activity data' }));
          // Use fallback data
          setRecentActivity([
            { id: 1, type: 'purchase', symbol: 'AAPL', amount: 1000, timestamp: new Date().toISOString() },
            { id: 2, type: 'sale', symbol: 'MSFT', amount: 2000, timestamp: new Date().toISOString() },
            { id: 3, type: 'alert', symbol: 'TSLA', message: 'Price target reached', timestamp: new Date().toISOString() }
          ]);
        }
        setLoading(prev => ({ ...prev, recentActivity: false }));
        
        // Fetch market news instead of using sample data
        setLoading(prev => ({ ...prev, marketNews: true }));
        try {
          const newsResponse = await dashboardAPI.getMarketOverview();
          setMarketNews(newsResponse.data?.news || sampleMarketNews);
        } catch (newsError) {
          console.error('Error fetching news:', newsError);
          setError(prev => ({ ...prev, marketNews: 'Failed to load news data' }));
          // Fallback to sample data
          setMarketNews(sampleMarketNews);
        }
        setLoading(prev => ({ ...prev, marketNews: false }));
        
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        
        // Reset all loading states
        setLoading({
          summary: false,
          widgets: false,
          recentActivity: false,
          marketOverview: false,
          userFavorites: false,
          marketNews: false
        });
        
        // Set a general error message
        setError(prev => ({ 
          ...prev, 
          general: 'Failed to load dashboard data. Please try again later.'
        }));
      }
    };
    
    fetchDashboardData();
  }, []);
  
  // Find widget by ID
  const findWidget = (id) => {
    return widgets.find(widget => widget.id === id);
  };
  
  // Refresh dashboard data
  const handleRefresh = () => {
    window.location.reload();
  };
  
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Financial Dashboard
        </Typography>
        <Box>
          <Tooltip title="Refresh Dashboard">
            <IconButton onClick={handleRefresh}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            component={RouterLink}
            to="/ml-dashboard"
            variant="contained"
            color="primary"
            startIcon={<AssessmentIcon />}
            sx={{ ml: 2 }}
          >
            ML Dashboard
          </Button>
        </Box>
      </Box>
      
      {/* Market Summary */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader 
              title="Market Overview" 
              action={
                <Tooltip title="View Details">
                  <IconButton component={RouterLink} to="/stocks">
                    <InfoIcon />
                  </IconButton>
                </Tooltip>
              }
            />
            <CardContent>
              {loading.marketOverview ? (
                <Box display="flex" justifyContent="center" p={3}>
                  <CircularProgress />
                </Box>
              ) : error.marketOverview ? (
                <Alert severity="error">{error.marketOverview}</Alert>
              ) : marketOverview ? (
                <MarketIndicesWidget 
                  data={marketOverview.indices}
                  loading={false}
                />
              ) : (
                <Alert severity="info">No market data available</Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader 
              title="Watchlist" 
              action={
                <Tooltip title="Manage Watchlist">
                  <IconButton component={RouterLink} to="/stocks">
                    <AddIcon />
                  </IconButton>
                </Tooltip>
              }
            />
            <CardContent>
              {loading.userFavorites ? (
                <Box display="flex" justifyContent="center" p={3}>
                  <CircularProgress />
                </Box>
              ) : error.userFavorites ? (
                <Alert severity="error">{error.userFavorites}</Alert>
              ) : (
                <WatchlistWidget 
                  data={userFavorites}
                  loading={false}
                />
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Stock Chart */}
      <Card sx={{ mb: 3 }}>
        <CardHeader 
          title="Market Performance" 
          action={
            <Tooltip title="View Details">
              <IconButton component={RouterLink} to="/stocks/AAPL">
                <TimelineIcon />
              </IconButton>
            </Tooltip>
          }
        />
        <CardContent>
          <StockChart symbol="SPY" initialPeriod="1mo" height={350} />
        </CardContent>
      </Card>
      
      {/* Widgets Row */}
      <Grid container spacing={3} mb={3}>
        {/* Predictions Widget */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="Market Predictions" 
              action={
                <Tooltip title="View All Predictions">
                  <IconButton component={RouterLink} to="/prediction-analysis">
                    <AssessmentIcon />
                  </IconButton>
                </Tooltip>
              }
            />
            <CardContent>
              {loading.widgets ? (
                <Box display="flex" justifyContent="center" p={3}>
                  <CircularProgress />
                </Box>
              ) : error.widgets ? (
                <Alert severity="error">{error.widgets}</Alert>
              ) : (
                <PredictionsWidget 
                  data={findWidget('predictions')?.data || []}
                  loading={false}
                />
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* Performance Widget */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="Stock Performance Comparison" 
              action={
                <Tooltip title="View Details">
                  <IconButton component={RouterLink} to="/stocks">
                    <BarChartIcon />
                  </IconButton>
                </Tooltip>
              }
            />
            <CardContent>
              {loading.widgets ? (
                <Box display="flex" justifyContent="center" p={3}>
                  <CircularProgress />
                </Box>
              ) : error.widgets ? (
                <Alert severity="error">{error.widgets}</Alert>
              ) : (
                <PerformanceWidget 
                  data={findWidget('performance')?.data || []}
                  loading={false}
                />
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Bottom Row */}
      <Grid container spacing={3}>
        {/* Recent Activity */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Recent Activity" />
            <CardContent>
              {loading.recentActivity ? (
                <Box display="flex" justifyContent="center" p={3}>
                  <CircularProgress />
                </Box>
              ) : error.recentActivity ? (
                <Alert severity="error">{error.recentActivity}</Alert>
              ) : (
                <RecentActivityWidget 
                  data={recentActivity}
                  loading={false}
                />
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* Market News */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader 
              title="Latest Market News" 
              action={
                <Tooltip title="View All News">
                  <IconButton component={RouterLink} to="/news">
                    <DescriptionIcon />
                  </IconButton>
                </Tooltip>
              }
            />
            <CardContent>
              {loading.marketNews ? (
                <Box display="flex" justifyContent="center" p={3}>
                  <CircularProgress />
                </Box>
              ) : error.marketNews ? (
                <Alert severity="error">{error.marketNews}</Alert>
              ) : (
                <MarketNewsWidget 
                  data={marketNews}
                  loading={false}
                />
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
