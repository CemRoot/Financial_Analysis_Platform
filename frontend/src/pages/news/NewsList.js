// frontend/src/pages/news/NewsList.js
import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  CardMedia, 
  Chip, 
  CircularProgress, 
  InputAdornment,
  TextField,
  Button,
  Paper,
  Divider,
  Alert,
  Tab,
  Tabs
} from '@mui/material';
import { Link } from 'react-router-dom';
import SearchIcon from '@mui/icons-material/Search';
import SentimentSatisfiedAltIcon from '@mui/icons-material/SentimentSatisfiedAlt';
import SentimentNeutralIcon from '@mui/icons-material/SentimentNeutral';
import SentimentDissatisfiedIcon from '@mui/icons-material/SentimentDissatisfied';
import SentimentDashboard from '../../components/news/SentimentDashboard';
import { fetchNewsList } from '../../services/api';

const NewsList = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [category, setCategory] = useState('all');
  const [showSentimentDashboard, setShowSentimentDashboard] = useState(true);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchNewsList(category !== 'all' ? category : null);
        setNews(data.articles || []);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching news:", err);
        setError(`Failed to load news articles: ${err.message}. Please contact support.`);
        setNews([]);
        setLoading(false);
      }
    };

    fetchNews();
  }, [category]);

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleCategoryChange = (event, newValue) => {
    setCategory(newValue);
  };

  const getSentimentIcon = (sentiment) => {
    switch(sentiment) {
      case 'positive':
        return <SentimentSatisfiedAltIcon color="success" />;
      case 'negative':
        return <SentimentDissatisfiedIcon color="error" />;
      default:
        return <SentimentNeutralIcon color="warning" />;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown date';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredNews = news.filter(article => 
    article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (article.summary && article.summary.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Financial News
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={showSentimentDashboard ? 8 : 12}>
          <Paper sx={{ mb: 3, p: 2 }}>
            <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2, mb: 2 }}>
              <TextField
                label="Search News"
                variant="outlined"
                fullWidth
                value={searchTerm}
                onChange={handleSearchChange}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
                sx={{ flexGrow: 1 }}
              />
              <Button 
                variant="outlined"
                onClick={() => setShowSentimentDashboard(!showSentimentDashboard)}
                sx={{ minWidth: 180 }}
              >
                {showSentimentDashboard ? 'Hide' : 'Show'} Sentiment Dashboard
              </Button>
            </Box>
            
            <Tabs 
              value={category} 
              onChange={handleCategoryChange}
              variant="scrollable"
              scrollButtons="auto"
              sx={{ mb: 2 }}
            >
              <Tab value="all" label="All News" />
              <Tab value="markets" label="Markets" />
              <Tab value="stocks" label="Stocks" />
              <Tab value="economy" label="Economy" />
              <Tab value="business" label="Business" />
            </Tabs>
          </Paper>
          
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : filteredNews.length > 0 ? (
            <Grid container spacing={3}>
              {filteredNews.map((article) => (
                <Grid item xs={12} key={article.id}>
                  <Card 
                    component={Link} 
                    to={`/news/${article.id}`}
                    sx={{ 
                      display: 'flex', 
                      flexDirection: { xs: 'column', sm: 'row' },
                      textDecoration: 'none',
                      height: '100%',
                      transition: 'transform 0.2s',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: 3
                      }
                    }}
                  >
                    {article.image_url && (
                      <CardMedia
                        component="img"
                        sx={{ 
                          width: { xs: '100%', sm: 200 },
                          height: { xs: 200, sm: 'auto' }
                        }}
                        image={article.image_url}
                        alt={article.title}
                      />
                    )}
                    <CardContent sx={{ flex: '1 1 auto', p: 3 }}>
                      <Typography 
                        variant="h6" 
                        component="div"
                        sx={{ 
                          color: 'text.primary',
                          mb: 2,
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                          lineHeight: 1.4
                        }}
                      >
                        {article.title}
                      </Typography>
                      
                      <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                        <Chip 
                          size="small" 
                          label={article.source} 
                          sx={{ mr: 1 }}
                        />
                        {article.sentiment && (
                          <Chip 
                            size="small" 
                            icon={getSentimentIcon(article.sentiment)}
                            label={article.sentiment} 
                            color={
                              article.sentiment === 'positive' ? 'success' : 
                              article.sentiment === 'negative' ? 'error' : 'default'
                            }
                          />
                        )}
                      </Box>
                      
                      <Typography 
                        variant="body2" 
                        color="text.secondary"
                        sx={{ 
                          mb: 2,
                          display: '-webkit-box',
                          WebkitLineClamp: 3,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                          lineHeight: 1.6
                        }}
                      >
                        {article.summary || article.content?.substring(0, 150) + '...' || 'No summary available.'}
                      </Typography>
                      
                      <Typography variant="caption" color="text.secondary">
                        {formatDate(article.published_at)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary" gutterBottom>No news articles found</Typography>
              {!error && (
                <Typography variant="body2" color="text.secondary">
                  Try changing your search criteria or check back later for updates.
                </Typography>
              )}
            </Paper>
          )}
        </Grid>
        
        {showSentimentDashboard && (
          <Grid item xs={12} md={4}>
            <Box sx={{ position: { md: 'sticky' }, top: { md: 24 } }}>
              <SentimentDashboard />
            </Box>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default NewsList;