import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  Button,
  CircularProgress,
  Divider,
  Chip,
  Paper,
  Grid,
  useTheme
} from '@mui/material';
import SentimentVeryDissatisfiedIcon from '@mui/icons-material/SentimentVeryDissatisfied';
import SentimentSatisfiedIcon from '@mui/icons-material/SentimentSatisfied';
import SentimentVerySatisfiedIcon from '@mui/icons-material/SentimentVerySatisfied';
import { sentimentAPI } from '../../services/api';

const SentimentAnalysis = () => {
  const theme = useTheme();
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyzeSentiment = async () => {
    if (!text.trim()) return;

    try {
      setLoading(true);
      setError(null);
      
      // Call sentiment analysis API
      const response = await sentimentAPI.analyzeSentiment([text]);
      setResult(response.data[0] || null);
    } catch (err) {
      console.error('Error analyzing sentiment:', err);
      setError('Failed to analyze sentiment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderSentimentResult = () => {
    if (!result) return null;

    const { sentiment_label, sentiment_score } = result;
    
    const getColor = () => {
      if (sentiment_label === 'positive') return theme.palette.success.main;
      if (sentiment_label === 'negative') return theme.palette.error.main;
      return theme.palette.warning.main;
    };

    const getIcon = () => {
      if (sentiment_label === 'positive') return <SentimentVerySatisfiedIcon fontSize="large" />;
      if (sentiment_label === 'negative') return <SentimentVeryDissatisfiedIcon fontSize="large" />;
      return <SentimentSatisfiedIcon fontSize="large" />;
    };

    return (
      <Paper elevation={2} sx={{ p: 3, mt: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item>
            <Box sx={{ color: getColor() }}>
              {getIcon()}
            </Box>
          </Grid>
          <Grid item>
            <Typography variant="h6">
              Sentiment: 
              <Chip 
                label={sentiment_label.charAt(0).toUpperCase() + sentiment_label.slice(1)}
                sx={{ ml: 1, bgcolor: getColor(), color: '#fff' }}
              />
            </Typography>
            <Typography variant="body2">
              Score: {sentiment_score.toFixed(2)}
            </Typography>
          </Grid>
        </Grid>
        
        {result.features && (
          <Box sx={{ mt: 2 }}>
            <Divider sx={{ my: 1 }} />
            <Typography variant="subtitle2">Key Features:</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
              {result.features.positive_count > 0 && (
                <Chip 
                  size="small" 
                  label={`${result.features.positive_count} Positive Words`}
                  color="success"
                />
              )}
              {result.features.negative_count > 0 && (
                <Chip 
                  size="small" 
                  label={`${result.features.negative_count} Negative Words`}
                  color="error"
                />
              )}
              {result.features.word_count && (
                <Chip 
                  size="small" 
                  label={`${result.features.word_count} Words`}
                  color="default"
                />
              )}
            </Box>
          </Box>
        )}
      </Paper>
    );
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Sentiment Analysis
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <Box>
          <Typography variant="body1" gutterBottom>
            Enter text to analyze sentiment:
          </Typography>
          <TextField
            multiline
            rows={4}
            fullWidth
            placeholder="Enter financial news, report excerpt, or any text..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            variant="outlined"
            sx={{ mb: 2 }}
          />
          <Button
            variant="contained"
            color="primary"
            onClick={analyzeSentiment}
            disabled={loading || !text.trim()}
          >
            {loading ? <CircularProgress size={24} /> : 'Analyze Sentiment'}
          </Button>
          
          {error && (
            <Typography color="error" sx={{ mt: 2 }}>
              {error}
            </Typography>
          )}
          
          {renderSentimentResult()}
        </Box>
      </CardContent>
    </Card>
  );
};

export default SentimentAnalysis;
