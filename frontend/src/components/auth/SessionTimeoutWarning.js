import React, { useState, useEffect } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button, LinearProgress } from '@mui/material';
import { clearTokens } from '../../services/auth';
import { useNavigate } from 'react-router-dom';

// Session timeout warning component that displays a warning dialog when the user's session is about to expire
const SessionTimeoutWarning = ({ 
  warningThreshold = 60, // seconds before timeout to show warning
  logoutTime = 900,     // total seconds until logout (15 minutes)
  onReset,              // callback to reset the timeout
  isAuthenticated = false
}) => {
  const [open, setOpen] = useState(false);
  const [timeLeft, setTimeLeft] = useState(warningThreshold);
  const [progress, setProgress] = useState(100);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) return;

    let warningTimer = null;
    let intervalTimer = null;
    let logoutTimer = null;

    // Set the timer to show the warning dialog
    warningTimer = setTimeout(() => {
      setOpen(true);
      
      // Start the countdown interval
      intervalTimer = setInterval(() => {
        setTimeLeft(prev => {
          const newValue = prev - 1;
          setProgress((newValue / warningThreshold) * 100);
          return newValue;
        });
      }, 1000);
      
      // Set the timer to logout
      logoutTimer = setTimeout(() => {
        handleLogout();
      }, warningThreshold * 1000);
    }, (logoutTime - warningThreshold) * 1000);

    return () => {
      clearTimeout(warningTimer);
      clearTimeout(logoutTimer);
      clearInterval(intervalTimer);
    };
  }, [isAuthenticated]);

  const handleStayLoggedIn = () => {
    setOpen(false);
    setTimeLeft(warningThreshold);
    setProgress(100);
    if (onReset) onReset();
  };

  const handleLogout = () => {
    setOpen(false);
    clearTokens();
    navigate('/login');
  };

  return (
    <Dialog
      open={open}
      onClose={handleStayLoggedIn}
      aria-labelledby="session-timeout-title"
      aria-describedby="session-timeout-description"
    >
      <DialogTitle id="session-timeout-title">Session Timeout Warning</DialogTitle>
      <DialogContent>
        <DialogContentText id="session-timeout-description">
          Your session is about to expire due to inactivity. You will be logged out in {timeLeft} seconds.
        </DialogContentText>
        <LinearProgress 
          variant="determinate" 
          value={progress} 
          color="warning"
          sx={{ mt: 2, mb: 1 }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={handleLogout} color="secondary">
          Logout Now
        </Button>
        <Button onClick={handleStayLoggedIn} color="primary" variant="contained" autoFocus>
          Stay Logged In
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default SessionTimeoutWarning;
