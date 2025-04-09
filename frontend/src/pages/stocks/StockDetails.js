import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  Box, 
  Typography, 
  Grid, 
  Paper, 
  Tabs, 
  Tab, 
  Divider, 
  CircularProgress,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import InfoIcon from '@mui/icons-material/Info';
import NewspaperIcon from '@mui/icons-material/Newspaper';
import DescriptionIcon from '@mui/icons-material/Description';
import AssessmentIcon from '@mui/icons-material/Assessment';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { fetchStockDetails, fetchStockPriceHistory, fetchStockNews, fetchStockFinancials } from '../../services/api';

const StockDetails = () => {
  const { symbol } = useParams();
  const [stock, setStock] = useState(null);
  const [priceHistory, setPriceHistory] = useState([]);
  const [news, setNews] = useState([]);
  const [financials, setFinancials] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    const fetchStockData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch all stock data in parallel
        const [stockData, historyData, newsData, financialsData] = await Promise.all([
          fetchStockDetails(symbol),
          fetchStockPriceHistory(symbol),
          fetchStockNews(symbol),
          fetchStockFinancials(symbol)
        ]);

        setStock(stockData);
        setPriceHistory(historyData);
        setNews(newsData);
        setFinancials(financialsData);
        setLoading(false);
      } catch (err) {
        setError(`Failed to load data for ${symbol}`);
        setLoading(false);
      }
    };

    fetchStockData();
  }, [symbol]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const formatCurrency = (value) => {
    if (value === undefined || value === null) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const formatLargeNumber = (num) => {
    if (num === undefined || num === null) return 'N/A';
    if (num >= 1_000_000_000_000) {
      return `${(num / 1_000_000_000_000).toFixed(2)}T`;
    } else if (num >= 1_000_000_000) {
      return `${(num / 1_000_000_000).toFixed(2)}B`;
    } else if (num >= 1_000_000) {
      return `${(num / 1_000_000).toFixed(2)}M`;
    }
    return num.toLocaleString();
  };

  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

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
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  // Price change data
  const priceChange = stock?.price_change || 0;
  const priceChangePercent = stock?.change_percent || 0;
  const isPositive = priceChange > 0;
  const isNegative = priceChange < 0;
  const priceChangeColor = isPositive ? 'success.main' : isNegative ? 'error.main' : 'text.primary';

  return (
    <Box sx={{ p: { xs: 2, md: 3 } }}>
      {/* Stock Header */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <Typography variant="h4" component="h1">
              {stock?.name} ({symbol})
            </Typography>
            {stock?.sector && (
              <Chip 
                label={stock.sector} 
                size="small" 
                sx={{ mr: 1, mt: 1 }}
              />
            )}
            {stock?.industry && (
              <Chip 
                label={stock.industry} 
                size="small" 
                sx={{ mt: 1 }}
              />
            )}
            {/* Market Status Indicator */}
            {stock?.market_status && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Chip 
                  label={stock.market_status.is_open ? 'Market Open' : 'Market Closed'} 
                  color={stock.market_status.is_open ? 'success' : 'default'}
                  size="small" 
                  sx={{ mr: 1 }}
                />
                <Typography variant="caption" color="text.secondary">
                  {stock.market_status.is_open 
                    ? `Closes at ${stock.market_status.closing_time}` 
                    : stock.market_status.reason === 'Weekend' || stock.market_status.reason === 'Holiday or Trading Halt'
                      ? `${stock.market_status.reason} - Reopens ${formatDate(stock.market_status.next_open)}`
                      : `Outside trading hours - Opens ${stock.market_status.next_open}`
                  }
                </Typography>
              </Box>
            )}
          </Grid>
          <Grid item xs={12} md={6} sx={{ textAlign: { xs: 'left', md: 'right' } }}>
            <Typography variant="h3" component="p" sx={{ fontWeight: 'bold' }}>
              {formatCurrency(stock?.current_price)}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: { xs: 'flex-start', md: 'flex-end' } }}>
              {isPositive && <TrendingUpIcon color="success" sx={{ mr: 0.5 }} />}
              {isNegative && <TrendingDownIcon color="error" sx={{ mr: 0.5 }} />}
              <Typography variant="h6" color={priceChangeColor} sx={{ mr: 1 }}>
                {priceChange > 0 ? '+' : ''}{priceChange.toFixed(2)}
              </Typography>
              <Typography variant="h6" color={priceChangeColor}>
                ({priceChangePercent > 0 ? '+' : ''}{priceChangePercent.toFixed(2)}%)
              </Typography>
            </Box>
            {/* Last updated timestamp */}
            {stock?.market_status && (
              <Typography variant="caption" color="text.secondary">
                Last updated: {stock.market_status.current_time}
                {stock.is_fallback && " (Fallback Data)"}
              </Typography>
            )}
          </Grid>
        </Grid>
      </Paper>

      {/* Tabs Navigation */}
      <Box sx={{ mb: 3 }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<AssessmentIcon />} label="Chart" />
          <Tab icon={<InfoIcon />} label="Overview" />
          <Tab icon={<DescriptionIcon />} label="Financials" />
          <Tab icon={<NewspaperIcon />} label="News" />
        </Tabs>
      </Box>

      {/* Tab Panels */}
      <Box sx={{ mb: 3 }}>
        {/* Chart Tab */}
        {activeTab === 0 && (
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" component="h2" gutterBottom>
              Stock Price History
            </Typography>
            <Box sx={{ height: 400, mt: 3 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={priceHistory}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={(tick) => new Date(tick).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                  />
                  <YAxis domain={['auto', 'auto']} />
                  <Tooltip 
                    formatter={(value) => [formatCurrency(value), 'Price']}
                    labelFormatter={(label) => formatDate(label)}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="price" 
                    stroke="#2196f3" 
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 8 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        )}

        {/* Overview Tab */}
        {activeTab === 1 && (
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" component="h2" gutterBottom>
              Company Overview
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TableContainer>
                  <Table>
                    <TableBody>
                      <TableRow>
                        <TableCell component="th">Market Cap</TableCell>
                        <TableCell align="right">{formatLargeNumber(stock?.marketCap)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th">P/E Ratio</TableCell>
                        <TableCell align="right">{stock?.pe?.toFixed(2) || 'N/A'}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th">Dividend Yield</TableCell>
                        <TableCell align="right">{stock?.dividendYield ? `${(stock.dividendYield * 100).toFixed(2)}%` : 'N/A'}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th">52-Week High</TableCell>
                        <TableCell align="right">{formatCurrency(stock?.high52Week)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th">52-Week Low</TableCell>
                        <TableCell align="right">{formatCurrency(stock?.low52Week)}</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Grid>
              <Grid item xs={12} md={6}>
                <TableContainer>
                  <Table>
                    <TableBody>
                      <TableRow>
                        <TableCell component="th">Average Volume</TableCell>
                        <TableCell align="right">{formatLargeNumber(stock?.avgVolume)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th">Volume</TableCell>
                        <TableCell align="right">{formatLargeNumber(stock?.volume)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th">EPS</TableCell>
                        <TableCell align="right">{formatCurrency(stock?.eps)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th">Beta</TableCell>
                        <TableCell align="right">{stock?.beta?.toFixed(2) || 'N/A'}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th">Exchange</TableCell>
                        <TableCell align="right">{stock?.exchange || 'N/A'}</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Grid>
            </Grid>

            {stock?.description && (
              <Box sx={{ mt: 4 }}>
                <Typography variant="h6" component="h3" gutterBottom>
                  About {stock.name}
                </Typography>
                <Typography variant="body1" paragraph>
                  {stock.description}
                </Typography>
              </Box>
            )}
          </Paper>
        )}

        {/* Financials Tab */}
        {activeTab === 2 && (
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" component="h2" gutterBottom>
              Financial Statements
            </Typography>
            {financials ? (
              <Box>
                <Typography variant="subtitle1" gutterBottom>
                  Income Statement Highlights
                </Typography>
                <TableContainer component={Paper} variant="outlined" sx={{ mb: 4 }}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Metric</TableCell>
                        {financials.incomeStatementDates.map(date => (
                          <TableCell key={date} align="right">{formatDate(date)}</TableCell>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <TableRow>
                        <TableCell component="th">Total Revenue</TableCell>
                        {financials.revenue.map((val, idx) => (
                          <TableCell key={idx} align="right">{formatLargeNumber(val)}</TableCell>
                        ))}
                      </TableRow>
                      <TableRow>
                        <TableCell component="th">Gross Profit</TableCell>
                        {financials.grossProfit.map((val, idx) => (
                          <TableCell key={idx} align="right">{formatLargeNumber(val)}</TableCell>
                        ))}
                      </TableRow>
                      <TableRow>
                        <TableCell component="th">Operating Income</TableCell>
                        {financials.operatingIncome.map((val, idx) => (
                          <TableCell key={idx} align="right">{formatLargeNumber(val)}</TableCell>
                        ))}
                      </TableRow>
                      <TableRow>
                        <TableCell component="th">Net Income</TableCell>
                        {financials.netIncome.map((val, idx) => (
                          <TableCell key={idx} align="right">{formatLargeNumber(val)}</TableCell>
                        ))}
                      </TableRow>
                      <TableRow>
                        <TableCell component="th">EPS</TableCell>
                        {financials.eps.map((val, idx) => (
                          <TableCell key={idx} align="right">{val?.toFixed(2) || 'N/A'}</TableCell>
                        ))}
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>

                <Typography variant="subtitle1" gutterBottom>
                  Balance Sheet Highlights
                </Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Metric</TableCell>
                        {financials.balanceSheetDates.map(date => (
                          <TableCell key={date} align="right">{formatDate(date)}</TableCell>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <TableRow>
                        <TableCell component="th">Total Assets</TableCell>
                        {financials.totalAssets.map((val, idx) => (
                          <TableCell key={idx} align="right">{formatLargeNumber(val)}</TableCell>
                        ))}
                      </TableRow>
                      <TableRow>
                        <TableCell component="th">Total Liabilities</TableCell>
                        {financials.totalLiabilities.map((val, idx) => (
                          <TableCell key={idx} align="right">{formatLargeNumber(val)}</TableCell>
                        ))}
                      </TableRow>
                      <TableRow>
                        <TableCell component="th">Total Equity</TableCell>
                        {financials.totalEquity.map((val, idx) => (
                          <TableCell key={idx} align="right">{formatLargeNumber(val)}</TableCell>
                        ))}
                      </TableRow>
                      <TableRow>
                        <TableCell component="th">Cash and Equivalents</TableCell>
                        {financials.cashAndEquivalents.map((val, idx) => (
                          <TableCell key={idx} align="right">{formatLargeNumber(val)}</TableCell>
                        ))}
                      </TableRow>
                      <TableRow>
                        <TableCell component="th">Debt</TableCell>
                        {financials.debt.map((val, idx) => (
                          <TableCell key={idx} align="right">{formatLargeNumber(val)}</TableCell>
                        ))}
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            ) : (
              <Alert severity="info">Financial data is not available for this stock</Alert>
            )}
          </Paper>
        )}

        {/* News Tab */}
        {activeTab === 3 && (
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" component="h2" gutterBottom>
              Latest News
            </Typography>
            {news && news.length > 0 ? (
              <Grid container spacing={2}>
                {news.map((article, index) => (
                  <Grid item xs={12} key={index}>
                    <Paper elevation={1} sx={{ p: 2, '&:hover': { boxShadow: 3 } }}>
                      <Typography variant="h6" component="h3" gutterBottom>
                        {article.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {formatDate(article.date)} • {article.source}
                      </Typography>
                      <Typography variant="body2" paragraph>
                        {article.summary}
                      </Typography>
                      <Button 
                        variant="outlined" 
                        size="small" 
                        href={article.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                      >
                        Read More
                      </Button>
                    </Paper>
                    {index < news.length - 1 && <Divider sx={{ my: 2 }} />}
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Alert severity="info">No recent news for this stock</Alert>
            )}
          </Paper>
        )}
      </Box>
    </Box>
  );
};

export default StockDetails;