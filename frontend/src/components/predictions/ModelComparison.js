// frontend/src/components/predictions/ModelComparison.js

import React, { useState, useEffect } from 'react';
import { 
  Box, Card, CardContent, Typography, Grid, Paper, 
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  CircularProgress, Divider, useTheme, Alert
} from '@mui/material';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, Scatter, ScatterChart
} from 'recharts';
import { modelComparisonAPI } from '../../services/api';

const ModelComparison = () => {
  const theme = useTheme();
  const [modelPerformance, setModelPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchModelPerformance = async () => {
      try {
        setLoading(true);
        const response = await modelComparisonAPI.compareModels();
        setModelPerformance(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching model performance:', err);
        setError('Failed to load model comparison data');
        
        // Set fallback data when API fails
        setModelPerformance({
          'LogisticRegression': {
            'accuracy': 0.76,
            'precision': 0.72,
            'recall': 0.68,
            'f1': 0.70,
            'execution_time': 0.15
          },
          'RandomForest': {
            'accuracy': 0.82,
            'precision': 0.79,
            'recall': 0.73,
            'f1': 0.76,
            'execution_time': 0.32
          },
          'LSTM': {
            'accuracy': 0.79,
            'precision': 0.77,
            'recall': 0.75,
            'f1': 0.76,
            'execution_time': 2.45
          },
          'BERT': {
            'accuracy': 0.85,
            'precision': 0.83,
            'recall': 0.81,
            'f1': 0.82,
            'execution_time': 3.71
          }
        });
        
        setLoading(false);
      }
    };

    fetchModelPerformance();
  }, []);

  // Transform performance metrics to chart data
  const prepareChartData = () => {
    if (!modelPerformance) return [];
    
    return Object.keys(modelPerformance).map(model => ({
      name: model,
      accuracy: modelPerformance[model].accuracy * 100,
      precision: modelPerformance[model].precision * 100,
      recall: modelPerformance[model].recall * 100,
      f1: modelPerformance[model].f1 * 100,
      executionTime: modelPerformance[model].execution_time
    }));
  };

  const chartData = prepareChartData();

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Model Performance Comparison
        </Typography>
        <Divider sx={{ mb: 3 }} />

        {error && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            {error} - Showing demo data instead
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Metrics Table */}
          <Grid item xs={12}>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Model</TableCell>
                    <TableCell align="right">Accuracy (%)</TableCell>
                    <TableCell align="right">Precision (%)</TableCell>
                    <TableCell align="right">Recall (%)</TableCell>
                    <TableCell align="right">F1 Score (%)</TableCell>
                    <TableCell align="right">Execution Time (s)</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {chartData.length > 0 ? (
                    chartData.map((row) => (
                      <TableRow key={row.name}>
                        <TableCell component="th" scope="row">
                          {row.name}
                        </TableCell>
                        <TableCell align="right">{row.accuracy.toFixed(2)}</TableCell>
                        <TableCell align="right">{row.precision.toFixed(2)}</TableCell>
                        <TableCell align="right">{row.recall.toFixed(2)}</TableCell>
                        <TableCell align="right">{row.f1.toFixed(2)}</TableCell>
                        <TableCell align="right">{row.executionTime.toFixed(3)}</TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={6} align="center">No model comparison data available</TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>

          {/* Performance Metrics Chart */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Performance Metrics
              </Typography>
              {chartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis label={{ value: 'Percentage (%)', angle: -90, position: 'insideLeft' }} />
                    <Tooltip formatter={(value) => value.toFixed(2) + '%'} />
                    <Legend />
                    <Bar dataKey="accuracy" name="Accuracy" fill={theme.palette.primary.main} />
                    <Bar dataKey="precision" name="Precision" fill={theme.palette.secondary.main} />
                    <Bar dataKey="recall" name="Recall" fill={theme.palette.success.main} />
                    <Bar dataKey="f1" name="F1 Score" fill={theme.palette.warning.main} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
                  <Typography color="text.secondary">No performance metrics data available</Typography>
                </Box>
              )}
            </Paper>
          </Grid>

          {/* Execution Time Chart */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Execution Time
              </Typography>
              {chartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" />
                    <Tooltip formatter={(value) => value.toFixed(3) + ' seconds'} />
                    <Legend />
                    <Bar dataKey="executionTime" name="Execution Time (s)" fill={theme.palette.primary.main} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
                  <Typography color="text.secondary">No execution time data available</Typography>
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default ModelComparison;