// frontend/src/layouts/MainLayout.js

import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Box, Toolbar, IconButton, useTheme, AppBar } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import Sidebar from '../components/layout/Sidebar';

const MainLayout = () => {
  const theme = useTheme();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Top AppBar */}
      <AppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          {/* You can add header components here: search, notifications, profile menu, etc. */}
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Sidebar 
        open={mobileOpen} 
        onClose={handleDrawerToggle} 
      />

      {/* Main content */}
      <Box component="main" sx={{ 
        flexGrow: 1, 
        p: 3, 
        width: { md: `calc(100% - 240px)` },
        marginTop: '64px', // AppBar height
        backgroundColor: theme.palette.background.default
      }}>
        <Outlet />
      </Box>
    </Box>
  );
};

export default MainLayout;