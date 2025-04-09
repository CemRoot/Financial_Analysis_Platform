import React from 'react';
import { Box, Button } from '@mui/material';
import GoogleIcon from '@mui/icons-material/Google';
import { useNavigate } from 'react-router-dom';

const GoogleLogin = ({ onSuccess, onError }) => {
  const navigate = useNavigate();

  const handleGoogleLogin = async () => {
    try {
      // In a real implementation, this would redirect to Google OAuth
      // For now, we're simulating a successful login with a direct backend call
      const response = await fetch('http://localhost:8000/api/accounts/oauth/google/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // In a real OAuth flow, this would be handled by the OAuth provider
        // This is just a placeholder for demonstration
        body: JSON.stringify({ 
          code: 'simulated_auth_code',
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.access && data.refresh) {
          // Store the tokens
          localStorage.setItem('financial_platform_access_token', data.access);
          localStorage.setItem('financial_platform_refresh_token', data.refresh);
          
          // Fetch user profile
          const userResponse = await fetch('http://localhost:8000/api/accounts/users/me/', {
            headers: {
              'Authorization': `Bearer ${data.access}`
            }
          });
          
          if (userResponse.ok) {
            const userData = await userResponse.json();
            localStorage.setItem('financial_platform_user', JSON.stringify(userData));
            
            if (onSuccess) onSuccess(userData);
            navigate('/dashboard');
          }
        }
      } else {
        throw new Error('Google login failed');
      }
    } catch (error) {
      console.error('Google login error:', error);
      if (onError) onError(error.message || 'Failed to authenticate with Google');
    }
  };

  return (
    <Box mt={2} width="100%">
      <Button
        startIcon={<GoogleIcon />}
        variant="outlined"
        fullWidth
        onClick={handleGoogleLogin}
        sx={{
          borderColor: '#4285F4',
          color: '#4285F4',
          '&:hover': {
            borderColor: '#4285F4',
            backgroundColor: 'rgba(66, 133, 244, 0.04)',
          }
        }}
      >
        Continue with Google
      </Button>
    </Box>
  );
};

export default GoogleLogin;
