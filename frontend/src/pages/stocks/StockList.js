import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Box, 
  Typography, 
  TextField, 
  InputAdornment,
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper, 
  TablePagination,
  CircularProgress,
  Button,
  Chip,
  Tabs,
  Tab
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import { fetchStocks } from '../../services/api';

const StockList = () => {
  const [stocks, setStocks] = useState([]);
  const [filteredStocks, setFilteredStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  
  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // Tab state (for different market categories)
  const [activeTab, setActiveTab] = useState(0);
  const marketCategories = ['All', 'Technology', 'Healthcare', 'Finance', 'Consumer'];

  useEffect(() => {
    const getStocks = async () => {
      try {
        setLoading(true);
        const data = await fetchStocks();
        setStocks(data);
        setFilteredStocks(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load stocks data');
        setLoading(false);
      }
    };

    getStocks();
  }, []);

  useEffect(() => {
    // Filter stocks based on search and active tab
    let result = stocks;
    
    // Apply search filter
    if (search) {
      result = result.filter(stock => 
        stock.symbol.toLowerCase().includes(search.toLowerCase()) || 
        stock.name.toLowerCase().includes(search.toLowerCase())
      );
    }
    
    // Apply category filter (if not "All")
    if (activeTab > 0 && marketCategories[activeTab]) {
      result = result.filter(stock => 
        stock.sector === marketCategories[activeTab] || 
        stock.industry === marketCategories[activeTab]
      );
    }
    
    setFilteredStocks(result);
    setPage(0); // Reset to first page when filtering
  }, [search, stocks, activeTab]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSearchChange = (event) => {
    setSearch(event.target.value);
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const formatMarketCap = (marketCap) => {
    if (marketCap >= 1_000_000_000_000) {
      return `${(marketCap / 1_000_000_000_000).toFixed(2)}T`;
    } else if (marketCap >= 1_000_000_000) {
      return `${(marketCap / 1_000_000_000).toFixed(2)}B`;
    } else if (marketCap >= 1_000_000) {
      return `${(marketCap / 1_000_000).toFixed(2)}M`;
    }
    return formatCurrency(marketCap);
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
        <Typography color="error" variant="h6">{error}</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: { xs: 2, md: 3 } }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Stock Market
      </Typography>
      
      <Box sx={{ mb: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
          >
            {marketCategories.map((category, index) => (
              <Tab key={index} label={category} />
            ))}
          </Tabs>
        </Box>
        
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search by symbol or company name"
          value={search}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ mb: 2 }}
        />
      </Box>

      <TableContainer component={Paper} elevation={3}>
        <Table sx={{ minWidth: 650 }} aria-label="stock table">
          <TableHead>
            <TableRow>
              <TableCell>Symbol</TableCell>
              <TableCell>Company</TableCell>
              <TableCell align="right">Price</TableCell>
              <TableCell align="right">Change</TableCell>
              <TableCell align="right">% Change</TableCell>
              <TableCell align="right">Market Cap</TableCell>
              <TableCell align="center">Status</TableCell>
              <TableCell align="right">Action</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredStocks
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((stock) => {
                const isPositive = (stock.price_change || stock.change) > 0;
                const isNegative = (stock.price_change || stock.change) < 0;
                
                return (
                  <TableRow key={stock.symbol} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {stock.symbol}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{stock.name}</Typography>
                      {stock.sector && (
                        <Chip 
                          label={stock.sector} 
                          size="small" 
                          sx={{ fontSize: '0.7rem', mt: 0.5 }}
                        />
                      )}
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">{formatCurrency(stock.current_price || stock.price)}</Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                        {isPositive && <TrendingUpIcon color="success" fontSize="small" sx={{ mr: 0.5 }} />}
                        {isNegative && <TrendingDownIcon color="error" fontSize="small" sx={{ mr: 0.5 }} />}
                        <Typography 
                          variant="body2" 
                          color={isPositive ? 'success.main' : isNegative ? 'error.main' : 'text.primary'}
                        >
                          {stock.price_change > 0 ? '+' : ''}{(stock.price_change || stock.change).toFixed(2)}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <Typography 
                        variant="body2" 
                        color={isPositive ? 'success.main' : isNegative ? 'error.main' : 'text.primary'}
                      >
                        {stock.change_percent > 0 ? '+' : ''}{(stock.change_percent || stock.changePercent).toFixed(2)}%
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">{formatMarketCap(stock.market_cap || stock.marketCap)}</Typography>
                    </TableCell>
                    <TableCell align="center">
                      {stock.market_status ? (
                        <Chip 
                          label={stock.market_status.is_open ? 'Open' : 'Closed'} 
                          size="small"
                          color={stock.market_status.is_open ? 'success' : 'default'}
                          sx={{ fontSize: '0.7rem' }}
                        />
                      ) : (
                        <Typography variant="caption" color="text.secondary">
                          --
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell align="right">
                      <Button 
                        component={Link} 
                        to={`/stocks/${stock.symbol}`} 
                        variant="outlined" 
                        size="small"
                      >
                        Details
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}
            {filteredStocks.length === 0 && (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  <Typography variant="body1" sx={{ py: 2 }}>
                    No stocks found matching your criteria
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={filteredStocks.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>
    </Box>
  );
};

export default StockList;