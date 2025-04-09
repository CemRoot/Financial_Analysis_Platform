import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import SessionTimeoutWarning from './auth/SessionTimeoutWarning';
import { getToken, clearTokens } from '../services/auth';
import { initializeInactivityTracking, clearInactivityTimer } from '../utils/sessionTimeout';

// AppWrapper component that handles session timeout functionality
const AppWrapper = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // Reset the authentication state when the location changes or on initial load
  useEffect(() => {
    const token = getToken();
    setIsAuthenticated(!!token);
  }, [location]);

  // Initialize inactivity tracking when the user is authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const handleTimeout = () => {
        console.log('Session timeout due to inactivity');
        clearTokens();
        navigate('/login?session_expired=true');
      };

      initializeInactivityTracking(handleTimeout);

      return () => {
        clearInactivityTimer();
      };
    }
  }, [isAuthenticated, navigate]);

  const handleResetTimeout = () => {
    // This will be called when the user clicks "Stay Logged In" in the warning dialog
    if (isAuthenticated) {
      const handleTimeout = () => {
        clearTokens();
        navigate('/login?session_expired=true');
      };
      
      // Reset the inactivity tracker
      clearInactivityTimer();
      initializeInactivityTracking(handleTimeout);
    }
  };

  return (
    <>
      {children}
      {isAuthenticated && (
        <SessionTimeoutWarning 
          isAuthenticated={isAuthenticated}
          onReset={handleResetTimeout}
          warningThreshold={60}  // Show warning 60 seconds before logout
          logoutTime={900}       // 15 minutes total (in seconds)
        />
      )}
    </>
  );
};

export default AppWrapper;
