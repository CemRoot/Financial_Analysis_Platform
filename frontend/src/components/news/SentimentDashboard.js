// frontend/src/components/news/SentimentDashboard.js

import React, { useState, useEffect } from 'react';
import { 
  Box, Card, CardContent, Typography, Grid, Paper, 
  CircularProgress, Divider, Chip, Button,
  useTheme, Alert
} from '@mui/material';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell
} from 'recharts';
import { sentimentAPI } from '../../services/api';

const SentimentDashboard = ({ articleId }) => {
  const theme = useTheme();
  const [sentimentData, setSentimentData] = useState(null);
  const [timeRange, setTimeRange] = useState('7d'); // 1d, 7d, 1m, 3m options
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSentimentData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // If articleId is provided, get sentiment for a specific article
        // Otherwise, get general sentiment over time
        let response;
        if (articleId) {
          response = await sentimentAPI.getSentimentOverTime(timeRange, articleId);
        } else {
          response = await sentimentAPI.getSentimentOverTime(timeRange);
        }
        
        setSentimentData(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching sentiment data:', err);
        setError(`Failed to load sentiment data: ${err.message}. Please contact support.`);
        setLoading(false);
      }
    };

    fetchSentimentData();
  }, [timeRange, articleId]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button 
          variant="outlined" 
          color="primary" 
          onClick={() => window.location.reload()}
          sx={{ mt: 1 }}
        >
          Retry
        </Button>
      </Box>
    );
  }

  if (!sentimentData) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert severity="info">
          No sentiment data available at this time.
        </Alert>
      </Box>
    );
  }

  // Define color scheme
  const COLORS = [theme.palette.success.main, theme.palette.warning.light, theme.palette.error.main]; // positive, neutral, negative

  // Prepare data for sentiment distribution pie chart
  const sentimentDistribution = [
    { name: 'Positive', value: sentimentData?.sentiment_counts?.positive || 0 },
    { name: 'Neutral', value: sentimentData?.sentiment_counts?.neutral || 0 },
    { name: 'Negative', value: sentimentData?.sentiment_counts?.negative || 0 }
  ];

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Market Sentiment Analysis
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          <Button
            variant={timeRange === '1d' ? 'contained' : 'outlined'}
            size="small"
            sx={{ mr: 1 }}
            onClick={() => setTimeRange('1d')}
          >
            1 Day
          </Button>
          <Button
            variant={timeRange === '7d' ? 'contained' : 'outlined'}
            size="small"
            sx={{ mr: 1 }}
            onClick={() => setTimeRange('7d')}
          >
            7 Days
          </Button>
          <Button
            variant={timeRange === '1m' ? 'contained' : 'outlined'}
            size="small"
            sx={{ mr: 1 }}
            onClick={() => setTimeRange('1m')}
          >
            1 Month
          </Button>
          <Button
            variant={timeRange === '3m' ? 'contained' : 'outlined'}
            size="small"
            onClick={() => setTimeRange('3m')}
          >
            3 Months
          </Button>
        </Box>
        
        <Grid container spacing={3}>
          {/* Sentiment Distribution Pie Chart */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Sentiment Distribution
              </Typography>
              <Box sx={{ height: 250, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={sentimentDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      fill="#8884d8"
                      paddingAngle={2}
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
                    >
                      {sentimentDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [value, 'Articles']} />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </Paper>
          </Grid>
          
          {/* Overall Sentiment */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Overall Market Sentiment
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="h4" component="span" sx={{ mr: 2 }}>
                  {sentimentData?.overall_sentiment || 'Neutral'}
                </Typography>
                <Chip 
                  label={sentimentData?.overall_sentiment || 'Neutral'} 
                  color={
                    sentimentData?.overall_sentiment === 'Positive' ? 'success' : 
                    sentimentData?.overall_sentiment === 'Negative' ? 'error' : 'warning'
                  }
                  size="small"
                  sx={{ ml: 1 }}
                />
              </Box>
              <Typography variant="body2" sx={{ mt: 1 }}>
                Total News Articles: {sentimentData?.total_articles || 0}
              </Typography>
            </Paper>
          </Grid>
          
          {/* Sentiment Over Time Chart */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Sentiment Over Time
              </Typography>
              {sentimentData?.sentiment_over_time?.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={sentimentData.sentiment_over_time}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="positive" stroke={theme.palette.success.main} name="Positive" />
                    <Line type="monotone" dataKey="neutral" stroke={theme.palette.warning.light} name="Neutral" />
                    <Line type="monotone" dataKey="negative" stroke={theme.palette.error.main} name="Negative" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
                  <Typography color="text.secondary">No sentiment data available</Typography>
                </Box>
              )}
            </Paper>
          </Grid>
          
          {/* Most Positive Headlines */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Most Positive Headlines
              </Typography>
              <Box sx={{ maxHeight: 250, overflow: 'auto' }}>
                {sentimentData?.top_positive?.length > 0 ? (
                  sentimentData.top_positive.map((item, index) => (
                    <Box key={index} sx={{ mb: 1, p: 1, borderRadius: 1, bgcolor: theme.palette.background.default }}>
                      <Typography variant="body2">{item.headline}</Typography>
                      <Typography variant="caption" color="success.main">
                        Score: {item.score.toFixed(2)}
                      </Typography>
                    </Box>
                  ))
                ) : (
                  <Typography color="text.secondary" sx={{ textAlign: 'center' }}>
                    No positive headlines data available
                  </Typography>
                )}
              </Box>
            </Paper>
          </Grid>
          
          {/* Most Negative Headlines */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Most Negative Headlines
              </Typography>
              <Box sx={{ maxHeight: 250, overflow: 'auto' }}>
                {sentimentData?.top_negative?.length > 0 ? (
                  sentimentData.top_negative.map((item, index) => (
                    <Box key={index} sx={{ mb: 1, p: 1, borderRadius: 1, bgcolor: theme.palette.background.default }}>
                      <Typography variant="body2">{item.headline}</Typography>
                      <Typography variant="caption" color="error.main">
                        Score: {item.score.toFixed(2)}
                      </Typography>
                    </Box>
                  ))
                ) : (
                  <Typography color="text.secondary" sx={{ textAlign: 'center' }}>
                    No negative headlines data available
                  </Typography>
                )}
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SentimentDashboard;