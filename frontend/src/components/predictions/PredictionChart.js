import React from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box,
  CircularProgress,
  useTheme
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';

const PredictionChart = ({ 
  data = [], 
  actualLabel = 'Actual', 
  predictedLabel = 'Predicted', 
  xAxisKey = 'date',
  title = 'Price Prediction',
  loading = false
}) => {
  const theme = useTheme();

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No prediction data available
        </Typography>
      </Box>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={data}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={xAxisKey} />
            <YAxis />
            <Tooltip />
            <Legend />
            <ReferenceLine x={data.findIndex(d => d.prediction)} label="Prediction Start" stroke="#666" />
            <Line
              type="monotone"
              dataKey="actual"
              name={actualLabel}
              stroke={theme.palette.primary.main}
              activeDot={{ r: 8 }}
              strokeWidth={2}
            />
            <Line
              type="monotone"
              dataKey="predicted"
              name={predictedLabel}
              stroke={theme.palette.secondary.main}
              strokeDasharray="5 5"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default PredictionChart;
