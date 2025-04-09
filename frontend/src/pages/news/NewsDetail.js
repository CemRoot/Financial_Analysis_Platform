import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  Box, 
  Typography, 
  Paper, 
  Chip, 
  Grid, 
  Divider, 
  CircularProgress,
  Avatar,
  Card
} from '@mui/material';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import SourceIcon from '@mui/icons-material/Source';
import SentimentSatisfiedAltIcon from '@mui/icons-material/SentimentSatisfiedAlt';
import SentimentDissatisfiedIcon from '@mui/icons-material/SentimentDissatisfied';
import SentimentNeutralIcon from '@mui/icons-material/SentimentNeutral';
import SentimentDashboard from '../../components/news/SentimentDashboard';
import { fetchNewsArticle } from '../../services/api';

const NewsDetail = () => {
  const { id } = useParams();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getArticle = async () => {
      try {
        setLoading(true);
        const data = await fetchNewsArticle(id);
        setArticle(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load article details');
        setLoading(false);
      }
    };

    getArticle();
  }, [id]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography color="error" variant="h6">{error}</Typography>
      </Box>
    );
  }

  if (!article) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h6">Article not found</Typography>
      </Box>
    );
  }

  // In a real app, this would come from the API
  const getSentimentIcon = (sentiment) => {
    if (!sentiment) return <SentimentNeutralIcon />;
    
    const score = typeof sentiment === 'string' 
      ? sentiment.toLowerCase() 
      : sentiment.score;
      
    if (score === 'positive' || score > 0.5) return <SentimentSatisfiedAltIcon color="success" />;
    if (score === 'negative' || score < 0) return <SentimentDissatisfiedIcon color="error" />;
    return <SentimentNeutralIcon color="warning" />;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown date';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Box sx={{ p: { xs: 2, md: 3 } }}>
      <Paper elevation={3} sx={{ p: { xs: 2, md: 4 }, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {article.title}
        </Typography>
        
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <AccessTimeIcon fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                {formatDate(article.published_at)}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <SourceIcon fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                {article.source || 'Unknown source'}
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {article.image_url && (
          <Box sx={{ mb: 4, width: '100%', height: { xs: 200, md: 400 } }}>
            <img 
              src={article.image_url} 
              alt={article.title} 
              style={{ 
                width: '100%', 
                height: '100%', 
                objectFit: 'cover',
                borderRadius: '8px'
              }} 
            />
          </Box>
        )}

        <Box sx={{ mb: 3 }}>
          <Chip 
            icon={getSentimentIcon(article.sentiment)} 
            label={`Sentiment: ${article.sentiment || 'Neutral'}`} 
            color={
              article.sentiment === 'positive' ? 'success' : 
              article.sentiment === 'negative' ? 'error' : 'default'
            }
            sx={{ mr: 1, mb: 1 }}
          />
          
          {article.categories && article.categories.map((category, index) => (
            <Chip key={index} label={category} sx={{ mr: 1, mb: 1 }} />
          ))}
        </Box>

        <Divider sx={{ mb: 3 }} />

        <Typography variant="body1" component="div" sx={{ mb: 4, lineHeight: 1.8 }}>
          {article.content || 'No content available for this article.'}
        </Typography>

        {article.related_stocks && article.related_stocks.length > 0 && (
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom>Related Stocks</Typography>
            <Grid container spacing={2}>
              {article.related_stocks.map((stock, index) => (
                <Grid item xs={6} sm={4} md={3} key={index}>
                  <Card sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Avatar sx={{ bgcolor: 'primary.main' }}>{stock.symbol.charAt(0)}</Avatar>
                      <Box>
                        <Typography variant="subtitle2">{stock.symbol}</Typography>
                        <Typography variant="caption" color="text.secondary">{stock.name}</Typography>
                      </Box>
                    </Box>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </Paper>

      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom>Sentiment Analysis</Typography>
        <SentimentDashboard articleId={id} />
      </Box>
    </Box>
  );
};

export default NewsDetail;