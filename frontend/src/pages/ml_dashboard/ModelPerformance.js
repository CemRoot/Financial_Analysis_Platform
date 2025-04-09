// frontend/src/pages/ml_dashboard/ModelPerformance.js

import React from 'react';
import { Container, Typography, Box, Grid, Paper, Tab, Tabs } from '@mui/material';
import ModelComparison from '../../components/predictions/ModelComparison';
import SentimentDashboard from '../../components/news/SentimentDashboard';
import MarketPrediction from '../../components/predictions/MarketPrediction';

const ModelPerformance = () => {
  const [tabValue, setTabValue] = React.useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          ML Model Dashboard
        </Typography>
        
        <Paper sx={{ mb: 3 }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            variant="fullWidth"
            indicatorColor="primary"
            textColor="primary"
          >
            <Tab label="Model Comparison" />
            <Tab label="Sentiment Analysis" />
            <Tab label="Market Prediction" />
          </Tabs>
        </Paper>

        {tabValue === 0 && (
          <ModelComparison />
        )}
        
        {tabValue === 1 && (
          <SentimentDashboard />
        )}
        
        {tabValue === 2 && (
          <MarketPrediction />
        )}
      </Box>
    </Container>
  );
};

export default ModelPerformance;