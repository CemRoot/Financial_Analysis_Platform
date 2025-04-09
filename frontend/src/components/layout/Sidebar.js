// frontend/src/components/layout/Sidebar.js

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Box, 
  Drawer, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText, 
  Divider, 
  Typography,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { alpha } from '@mui/system';

// Icons
import DashboardIcon from '@mui/icons-material/Dashboard';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import ArticleIcon from '@mui/icons-material/Article';
import InsightsIcon from '@mui/icons-material/Insights';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import SettingsIcon from '@mui/icons-material/Settings';
import NotificationsIcon from '@mui/icons-material/Notifications';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

const navigationItems = [
  {
    title: 'Dashboard',
    icon: <DashboardIcon />,
    path: '/dashboard',
  },
  {
    title: 'Stocks',
    icon: <ShowChartIcon />,
    path: '/stocks',
  },
  {
    title: 'News',
    icon: <ArticleIcon />,
    path: '/news',
  },
  {
    title: 'ML Dashboard',
    icon: <InsightsIcon />,
    path: '/ml-dashboard',
  },
  {
    title: 'Sentiment Insights',
    icon: <TrendingUpIcon />,
    path: '/sentiment-insights',
  },
  {
    title: 'Watchlists',
    icon: <BookmarkIcon />,
    path: '/watchlists',
  },
  {
    title: 'Alerts',
    icon: <NotificationsIcon />,
    path: '/alerts',
  }
];

const userMenuItems = [
  {
    title: 'Profile',
    icon: <AccountCircleIcon />,
    path: '/profile',
  },
  {
    title: 'Settings',
    icon: <SettingsIcon />,
    path: '/settings',
  }
];

const Sidebar = ({ open, onClose, width = 240 }) => {
  const theme = useTheme();
  const location = useLocation();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'));

  const isActive = (path) => {
    return location.pathname === path;
  };

  const sidebarContent = (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Logo and brand */}
      <Box sx={{ 
        p: 2, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        borderBottom: `1px solid ${theme.palette.divider}`
      }}>
        <Typography variant="h6" component="h1" sx={{ fontWeight: 'bold' }}>
          Financial Analysis
        </Typography>
      </Box>

      {/* Main navigation */}
      <List component="nav" sx={{ flexGrow: 1, p: 1 }}>
        {navigationItems.map((item) => (
          <ListItem 
            button 
            component={Link} 
            to={item.path} 
            key={item.title}
            selected={isActive(item.path)}
            onClick={isSmallScreen ? onClose : undefined}
            sx={{ 
              mb: 0.5, 
              borderRadius: 1,
              color: isActive(item.path) ? theme.palette.primary.main : theme.palette.text.primary,
              backgroundColor: isActive(item.path) ? alpha(theme.palette.primary.main, 0.1) : 'transparent',
              '&:hover': {
                backgroundColor: alpha(theme.palette.primary.main, 0.05),
              },
              '&.Mui-selected': {
                backgroundColor: alpha(theme.palette.primary.main, 0.1),
                '&:hover': {
                  backgroundColor: alpha(theme.palette.primary.main, 0.15),
                },
              }
            }}
          >
            <ListItemIcon sx={{ 
              color: isActive(item.path) ? theme.palette.primary.main : theme.palette.text.primary,
              minWidth: 40
            }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText 
              primary={item.title} 
              primaryTypographyProps={{ 
                fontSize: 14,
                fontWeight: isActive(item.path) ? 'bold' : 'normal'
              }}
            />
          </ListItem>
        ))}
      </List>

      <Divider />

      {/* User menu */}
      <List component="nav" sx={{ p: 1 }}>
        {userMenuItems.map((item) => (
          <ListItem 
            button 
            component={Link} 
            to={item.path} 
            key={item.title}
            selected={isActive(item.path)}
            onClick={isSmallScreen ? onClose : undefined}
            sx={{ 
              mb: 0.5, 
              borderRadius: 1,
              color: isActive(item.path) ? theme.palette.primary.main : theme.palette.text.primary,
              backgroundColor: isActive(item.path) ? alpha(theme.palette.primary.main, 0.1) : 'transparent',
              '&:hover': {
                backgroundColor: alpha(theme.palette.primary.main, 0.05),
              },
              '&.Mui-selected': {
                backgroundColor: alpha(theme.palette.primary.main, 0.1),
                '&:hover': {
                  backgroundColor: alpha(theme.palette.primary.main, 0.15),
                },
              }
            }}
          >
            <ListItemIcon sx={{ 
              color: isActive(item.path) ? theme.palette.primary.main : theme.palette.text.primary,
              minWidth: 40
            }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText 
              primary={item.title} 
              primaryTypographyProps={{ 
                fontSize: 14,
                fontWeight: isActive(item.path) ? 'bold' : 'normal'
              }}
            />
          </ListItem>
        ))}
      </List>

      {/* User info at bottom */}
      <Box sx={{ p: 2, borderTop: `1px solid ${theme.palette.divider}` }}>
        <Typography variant="caption" color="text.secondary">
          2025 Financial Analysis Platform
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Box component="nav" sx={{ width: { md: width }, flexShrink: { md: 0 } }}>
      {/* Mobile drawer */}
      {isSmallScreen ? (
        <Drawer
          variant="temporary"
          open={open}
          onClose={onClose}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: width,
              borderRight: `1px solid ${theme.palette.divider}`
            },
          }}
        >
          {sidebarContent}
        </Drawer>
      ) : (
        /* Desktop permanent drawer */
        <Drawer
          variant="permanent"
          open
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: width,
              borderRight: `1px solid ${theme.palette.divider}`
            },
          }}
        >
          {sidebarContent}
        </Drawer>
      )}
    </Box>
  );
};

export default Sidebar;