// frontend/src/contexts/ThemeContext.js
import React, { createContext, useState, useEffect, useContext } from 'react';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { lightTheme, darkTheme } from '../theme';

export const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [mode, setMode] = useState(() => {
    // Get theme preference from local storage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark' || savedTheme === 'light' || savedTheme === 'system') {
      return savedTheme;
    }
    // Default to system preference
    return 'system';
  });

  const [darkMode, setDarkMode] = useState(() => {
    const savedTheme = localStorage.getItem('theme');
    return savedTheme === 'dark' || 
           (savedTheme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
  });

  // Save theme preference to local storage
  useEffect(() => {
    localStorage.setItem('theme', mode);
    
    // Set dark mode based on mode and system preference
    if (mode === 'dark') {
      setDarkMode(true);
    } else if (mode === 'light') {
      setDarkMode(false);
    } else if (mode === 'system') {
      setDarkMode(window.matchMedia('(prefers-color-scheme: dark)').matches);
    }
  }, [mode]);

  // Toggle theme function
  const toggleTheme = () => {
    setDarkMode(!darkMode);
    setMode(darkMode ? 'light' : 'dark');
  };

  // Change theme function
  const changeTheme = (newMode) => {
    if (['light', 'dark', 'system'].includes(newMode)) {
      setMode(newMode);
    }
  };

  return (
    <ThemeContext.Provider value={{ darkMode, mode, toggleTheme, changeTheme }}>
      <MuiThemeProvider theme={darkMode ? darkTheme : lightTheme}>
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};

// Custom hook to use the theme context
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};