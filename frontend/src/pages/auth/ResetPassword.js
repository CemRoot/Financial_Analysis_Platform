import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Link,
  Paper,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { resetPassword, validateResetToken } from '../../services/auth';

const ResetPassword = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [token, setToken] = useState('');
  const [isValidToken, setIsValidToken] = useState(false);
  const [isValidatingToken, setIsValidatingToken] = useState(true);
  const [tokenError, setTokenError] = useState(null);
  
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [confirmPasswordError, setConfirmPasswordError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  useEffect(() => {
    // Extract token from URL query params
    const query = new URLSearchParams(location.search);
    const resetToken = query.get('token');
    
    if (!resetToken) {
      setTokenError('Reset token is missing. Please use the link provided in the email.');
      setIsValidatingToken(false);
      return;
    }
    
    setToken(resetToken);
    
    // Validate the token
    const checkToken = async () => {
      try {
        await validateResetToken(resetToken);
        setIsValidToken(true);
      } catch (error) {
        setTokenError(
          error.response?.data?.message || 
          'Invalid or expired reset token. Please request a new password reset link.'
        );
      } finally {
        setIsValidatingToken(false);
      }
    };
    
    checkToken();
  }, [location.search]);

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };
  
  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
    setPasswordError('');
    setConfirmPasswordError('');
  };
  
  const handleConfirmPasswordChange = (e) => {
    setConfirmPassword(e.target.value);
    setConfirmPasswordError('');
  };

  const validateForm = () => {
    let isValid = true;
    
    if (!password) {
      setPasswordError('Password is required');
      isValid = false;
    } else if (password.length < 8) {
      setPasswordError('Password must be at least 8 characters long');
      isValid = false;
    }
    
    if (!confirmPassword) {
      setConfirmPasswordError('Please confirm your password');
      isValid = false;
    } else if (password !== confirmPassword) {
      setConfirmPasswordError('Passwords do not match');
      isValid = false;
    }
    
    return isValid;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    setSubmitError(null);
    
    try {
      await resetPassword(token, password);
      setSubmitSuccess(true);
      
      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (error) {
      setSubmitError(
        error.response?.data?.message || 
        'Failed to reset password. Please try again or request a new reset link.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Container component="main" maxWidth="sm">
      <Paper elevation={3} sx={{ p: { xs: 3, md: 4 }, mt: 8 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <Typography component="h1" variant="h4" gutterBottom>
            Reset Your Password
          </Typography>
          
          {isValidatingToken ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', my: 4 }}>
              <CircularProgress size={40} />
              <Typography variant="body1" sx={{ mt: 2 }}>
                Validating your reset token...
              </Typography>
            </Box>
          ) : !isValidToken ? (
            <Box sx={{ width: '100%', mt: 2 }}>
              <Alert severity="error" sx={{ mb: 3 }}>
                {tokenError}
              </Alert>
              <Button 
                component={RouterLink} 
                to="/forgot-password" 
                variant="contained" 
                fullWidth
                sx={{ mt: 2 }}
              >
                Request New Reset Link
              </Button>
            </Box>
          ) : submitSuccess ? (
            <Alert severity="success" sx={{ width: '100%', mb: 3 }}>
              Your password has been successfully reset. You will be redirected to the login page momentarily.
            </Alert>
          ) : (
            <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%', mt: 2 }}>
              {submitError && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {submitError}
                </Alert>
              )}
              
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="New Password"
                type={showPassword ? 'text' : 'password'}
                id="password"
                autoComplete="new-password"
                value={password}
                onChange={handlePasswordChange}
                error={!!passwordError}
                helperText={passwordError}
                disabled={isSubmitting}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label="toggle password visibility"
                        onClick={togglePasswordVisibility}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              
              <TextField
                margin="normal"
                required
                fullWidth
                name="confirmPassword"
                label="Confirm New Password"
                type={showConfirmPassword ? 'text' : 'password'}
                id="confirmPassword"
                autoComplete="new-password"
                value={confirmPassword}
                onChange={handleConfirmPasswordChange}
                error={!!confirmPasswordError}
                helperText={confirmPasswordError}
                disabled={isSubmitting}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label="toggle confirm password visibility"
                        onClick={toggleConfirmPasswordVisibility}
                        edge="end"
                      >
                        {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2, py: 1.5 }}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <CircularProgress size={24} sx={{ mr: 1 }} />
                    Resetting Password...
                  </Box>
                ) : (
                  'Reset Password'
                )}
              </Button>
              
              <Box sx={{ mt: 2 }}>
                <Link component={RouterLink} to="/login" variant="body2" underline="hover">
                  Return to Login
                </Link>
              </Box>
            </Box>
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default ResetPassword;