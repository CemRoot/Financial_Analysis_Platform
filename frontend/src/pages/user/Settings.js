import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Switch,
  FormControlLabel,
  Button,
  Divider,
  Box,
  Alert,
  CircularProgress,
  Snackbar,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  FormHelperText
} from '@mui/material';
import { Save, NotificationsActive, Security, Language, ColorLens, Sync } from '@mui/icons-material';
import { getUserSettings, updateUserSettings } from '../../services/user';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';

const Settings = () => {
  const { currentUser } = useAuth();
  const { mode, changeTheme } = useTheme();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  
  const [settings, setSettings] = useState({
    notifications: {
      email: true,
      push: true,
      stockAlerts: true,
      newsAlerts: true,
      marketSummary: true
    },
    preferences: {
      language: 'en',
      theme: 'system',
      dataRefreshInterval: 5
    },
    privacy: {
      shareUsageData: true,
      saveSearchHistory: true
    }
  });
  
  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true);
        const data = await getUserSettings(currentUser.id);
        if (data) {
          setSettings(data);
        }
      } catch (err) {
        setError(err.message || 'Failed to load settings');
      } finally {
        setLoading(false);
      }
    };

    if (currentUser) {
      fetchSettings();
    }
  }, [currentUser]);

  const handleNotificationChange = (event) => {
    const { name, checked } = event.target;
    setSettings({
      ...settings,
      notifications: {
        ...settings.notifications,
        [name]: checked
      }
    });
  };

  const handlePreferenceChange = (event) => {
    const { name, value } = event.target;
    
    const newSettings = {
      ...settings,
      preferences: {
        ...settings.preferences,
        [name]: value
      }
    };
    
    setSettings(newSettings);
    
    // If theme is changed, apply it immediately
    if (name === 'theme') {
      changeTheme(value);
    }
  };

  const handlePrivacyChange = (event) => {
    const { name, checked } = event.target;
    setSettings({
      ...settings,
      privacy: {
        ...settings.privacy,
        [name]: checked
      }
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    
    try {
      await updateUserSettings(currentUser.id, settings);
      setSubmitSuccess(true);
    } catch (err) {
      setError(err.message || 'Failed to update settings');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSnackbarClose = () => {
    setSubmitSuccess(false);
  };

  if (loading) {
    return (
      <Container sx={{ mt: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Container>
    );
  }

  const refreshIntervals = [
    { value: 1, label: '1 minute' },
    { value: 5, label: '5 minutes' },
    { value: 15, label: '15 minutes' },
    { value: 30, label: '30 minutes' },
    { value: 60, label: '1 hour' }
  ];

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'zh', name: 'Chinese' },
    { code: 'ja', name: 'Japanese' }
  ];

  const themes = [
    { value: 'light', label: 'Light' },
    { value: 'dark', label: 'Dark' },
    { value: 'system', label: 'System' }
  ];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Snackbar
        open={submitSuccess}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        message="Settings saved successfully"
      />
      
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Box component="form" onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          {/* Notification Settings */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3, borderRadius: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <NotificationsActive color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Notification Settings</Typography>
              </Box>
              
              <Divider sx={{ mb: 3 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.notifications.email}
                        onChange={handleNotificationChange}
                        name="email"
                        color="primary"
                      />
                    }
                    label="Email Notifications"
                  />
                  <FormHelperText>Receive important updates via email</FormHelperText>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.notifications.push}
                        onChange={handleNotificationChange}
                        name="push"
                        color="primary"
                      />
                    }
                    label="Push Notifications"
                  />
                  <FormHelperText>Receive notifications in your browser</FormHelperText>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.notifications.stockAlerts}
                        onChange={handleNotificationChange}
                        name="stockAlerts"
                        color="primary"
                      />
                    }
                    label="Stock Price Alerts"
                  />
                  <FormHelperText>Get notified when stocks hit your target prices</FormHelperText>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.notifications.newsAlerts}
                        onChange={handleNotificationChange}
                        name="newsAlerts"
                        color="primary"
                      />
                    }
                    label="News Alerts"
                  />
                  <FormHelperText>Get important news about your watchlist stocks</FormHelperText>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.notifications.marketSummary}
                        onChange={handleNotificationChange}
                        name="marketSummary"
                        color="primary"
                      />
                    }
                    label="Daily Market Summary"
                  />
                  <FormHelperText>Receive a daily digest of market performance</FormHelperText>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
          
          {/* Preferences */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3, borderRadius: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ColorLens color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Application Preferences</Typography>
              </Box>
              
              <Divider sx={{ mb: 3 }} />
              
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6} md={4}>
                  <FormControl fullWidth>
                    <InputLabel id="language-select-label">Language</InputLabel>
                    <Select
                      labelId="language-select-label"
                      value={settings.preferences.language}
                      name="language"
                      label="Language"
                      onChange={handlePreferenceChange}
                      startAdornment={<Language sx={{ mr: 1, ml: -0.5 }} />}
                    >
                      {languages.map((lang) => (
                        <MenuItem key={lang.code} value={lang.code}>
                          {lang.name}
                        </MenuItem>
                      ))}
                    </Select>
                    <FormHelperText>Select your preferred language</FormHelperText>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} sm={6} md={4}>
                  <FormControl fullWidth>
                    <InputLabel id="theme-select-label">Theme</InputLabel>
                    <Select
                      labelId="theme-select-label"
                      value={settings.preferences.theme}
                      name="theme"
                      label="Theme"
                      onChange={handlePreferenceChange}
                      startAdornment={<ColorLens sx={{ mr: 1, ml: -0.5 }} />}
                    >
                      {themes.map((theme) => (
                        <MenuItem key={theme.value} value={theme.value}>
                          {theme.label}
                        </MenuItem>
                      ))}
                    </Select>
                    <FormHelperText>Choose your preferred theme</FormHelperText>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} sm={6} md={4}>
                  <FormControl fullWidth>
                    <InputLabel id="refresh-select-label">Data Refresh Interval</InputLabel>
                    <Select
                      labelId="refresh-select-label"
                      value={settings.preferences.dataRefreshInterval}
                      name="dataRefreshInterval"
                      label="Data Refresh Interval"
                      onChange={handlePreferenceChange}
                      startAdornment={<Sync sx={{ mr: 1, ml: -0.5 }} />}
                    >
                      {refreshIntervals.map((interval) => (
                        <MenuItem key={interval.value} value={interval.value}>
                          {interval.label}
                        </MenuItem>
                      ))}
                    </Select>
                    <FormHelperText>How often to refresh market data</FormHelperText>
                  </FormControl>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
          
          {/* Privacy Settings */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3, borderRadius: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Security color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Privacy Settings</Typography>
              </Box>
              
              <Divider sx={{ mb: 3 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.privacy.shareUsageData}
                        onChange={handlePrivacyChange}
                        name="shareUsageData"
                        color="primary"
                      />
                    }
                    label="Share Usage Data"
                  />
                  <FormHelperText>
                    Allow us to collect anonymous usage data to improve our service
                  </FormHelperText>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.privacy.saveSearchHistory}
                        onChange={handlePrivacyChange}
                        name="saveSearchHistory"
                        color="primary"
                      />
                    }
                    label="Save Search History"
                  />
                  <FormHelperText>
                    Save your search history for quicker access to previous searches
                  </FormHelperText>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
          
          <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
            <Button 
              type="submit" 
              variant="contained" 
              color="primary" 
              startIcon={<Save />}
              disabled={isSubmitting}
              sx={{ minWidth: 150 }}
            >
              {isSubmitting ? 'Saving...' : 'Save Settings'}
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Settings;