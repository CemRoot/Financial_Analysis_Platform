// frontend/src/layouts/AuthLayout.js

import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Box, Container, Paper, Typography } from '@mui/material';
import { useTheme } from '@mui/material/styles';

const AuthLayout = () => {
  const theme = useTheme();
  const location = useLocation();
  
  // If the current route is /auth, render the outlet directly
  // without any wrapper to allow full-screen design
  if (location.pathname === '/auth') {
    return <Outlet />;
  }
  
  // For other auth routes (forgot password, etc.) use the default layout
  return (
    <Box
      sx={{
        display: 'flex',
        minHeight: '100vh',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: theme.palette.background.default,
        py: 4
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={6}
          sx={{
            p: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <Typography
            component="h1"
            variant="h4"
            color="primary"
            sx={{ mb: 4, fontWeight: 'bold' }}
          >
            Financial Analysis Platform
          </Typography>
          
          <Outlet />
        </Paper>
      </Container>
    </Box>
  );
};

export default AuthLayout;