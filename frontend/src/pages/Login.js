import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Button, TextField, Typography, Paper, Divider, Link } from '@mui/material';
import { authAPI } from '../services/api';
import GoogleLogin from '../components/auth/GoogleLogin';

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await authAPI.login({ email, password });
      navigate('/dashboard');
    } catch (err) {
      setError(err.response && err.response.data ? err.response.data.message : 'Login failed.');
    }
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      height="100vh"
      bgcolor="#f5f5f5"
      sx={{ overflow: 'hidden' }}
    >
      <Paper elevation={6} sx={{ 
        padding: '2rem', 
        maxWidth: '400px', 
        width: '100%',
        maxHeight: '90vh',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem'
      }}>
        <Typography variant="h4" align="center" gutterBottom>
          Financial Platform
        </Typography>
        <Typography variant="subtitle1" align="center" color="textSecondary" gutterBottom>
          Log in to your account
        </Typography>
        {error && (
          <Typography color="error" align="center" gutterBottom>{error}</Typography>
        )}
        <form onSubmit={handleSubmit} noValidate>
          <TextField
            label="Email"
            variant="outlined"
            margin="normal"
            fullWidth
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoFocus
            type="email"
            placeholder="your.email@example.com"
          />
          <TextField
            label="Password"
            type="password"
            variant="outlined"
            margin="normal"
            fullWidth
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <Button 
            type="submit" 
            variant="contained" 
            color="primary" 
            fullWidth 
            sx={{ mt: 2, py: 1 }}
            size="large"
          >
            Log In
          </Button>
        </form>
        
        <Box mt={2} mb={2}>
          <Divider>
            <Typography variant="body2" color="textSecondary">
              OR
            </Typography>
          </Divider>
        </Box>
        
        <GoogleLogin 
          onSuccess={() => navigate('/dashboard')}
          onError={(msg) => setError(msg)}
        />
        
        <Box mt={2} textAlign="center">
          <Typography variant="body2">
            Don't have an account?{' '}
            <Link href="/register" color="primary">
              Register now
            </Link>
          </Typography>
        </Box>
        
        <Box mt={1} textAlign="center">
          <Link href="/forgot-password" variant="body2">
            Forgot password?
          </Link>
        </Box>
      </Paper>
    </Box>
  );
};

export default Login;
