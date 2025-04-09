import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import SentimentDashboard from '../../components/news/SentimentDashboard';

const SentimentInsights = () => {
  return (
    <Container maxWidth="xl">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Sentiment Insights
        </Typography>
        
        <SentimentDashboard />
      </Box>
    </Container>
  );
};

export default SentimentInsights;
