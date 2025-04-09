import React, { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Link,
  Paper,
  Alert,
  AlertTitle,
  CircularProgress
} from '@mui/material';
import { sendPasswordResetEmail } from '../../services/auth';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  const handleEmailChange = (e) => {
    setEmail(e.target.value);
    setEmailError('');
  };

  const validateEmail = () => {
    if (!email) {
      setEmailError('Email is required');
      return false;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setEmailError('Please enter a valid email address');
      return false;
    }
    
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateEmail()) {
      return;
    }
    
    setIsSubmitting(true);
    setSubmitError(null);
    
    try {
      await sendPasswordResetEmail(email);
      setSubmitSuccess(true);
    } catch (error) {
      setSubmitError(
        error.response?.data?.message || 
        'Failed to send password reset email. Please try again.'
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
          
          <Typography variant="body1" textAlign="center" sx={{ mb: 4 }}>
            Enter the email address associated with your account,
            and we'll send you a link to reset your password.
          </Typography>
          
          {submitSuccess ? (
            <Alert severity="success" sx={{ width: '100%', mb: 3 }}>
              <AlertTitle>Email Sent</AlertTitle>
              We've sent a password reset link to <strong>{email}</strong>. 
              Please check your inbox and follow the instructions to reset your password.
              <Box sx={{ mt: 2 }}>
                <Button 
                  component={RouterLink} 
                  to="/login" 
                  variant="outlined" 
                  color="success"
                  size="small"
                >
                  Return to Login
                </Button>
              </Box>
            </Alert>
          ) : (
            <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
              {submitError && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {submitError}
                </Alert>
              )}
              
              <TextField
                margin="normal"
                required
                fullWidth
                id="email"
                label="Email Address"
                name="email"
                autoComplete="email"
                autoFocus
                value={email}
                onChange={handleEmailChange}
                error={!!emailError}
                helperText={emailError}
                disabled={isSubmitting}
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
                    Sending...
                  </Box>
                ) : (
                  'Send Reset Link'
                )}
              </Button>
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                <Link component={RouterLink} to="/login" variant="body2" underline="hover">
                  Back to Login
                </Link>
                <Link component={RouterLink} to="/register" variant="body2" underline="hover">
                  Create an account
                </Link>
              </Box>
            </Box>
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default ForgotPassword;