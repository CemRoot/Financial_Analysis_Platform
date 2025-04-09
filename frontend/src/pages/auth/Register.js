import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  TextField,
  Button,
  Typography,
  IconButton,
  Alert,
  Checkbox,
  FormControlLabel,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  styled
} from '@mui/material';
import { GitHub, LinkedIn, Google, Facebook, Visibility, Person, Email } from '@mui/icons-material';
import { register } from '../../services/auth';
import { TERMS_OF_SERVICE, PRIVACY_POLICY } from '../../constants/legal';

// Styled components
const Container = styled(Box)(({ theme }) => ({
  backgroundColor: '#fff',
  borderRadius: '30px',
  boxShadow: '0 5px 15px rgba(0, 0, 0, 0.35)',
  position: 'relative',
  overflow: 'hidden',
  width: '768px',
  maxWidth: '100%',
  minHeight: '480px',
}));

const FormContainer = styled(Box)(({ theme, position, active }) => ({
  position: 'absolute',
  top: 0,
  height: '100%',
  transition: 'all 0.6s ease-in-out',
  left: position === 'signUp' ? 0 : 0,
  width: '50%',
  zIndex: position === 'signUp' ? 5 : 1,
  opacity: position === 'signUp' ? 1 : 0,
  transform: active && position === 'signUp' ? 'translateX(100%)' : 'translateX(0)',
}));

const Form = styled('form')(({ theme }) => ({
  backgroundColor: '#fff',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  flexDirection: 'column',
  padding: '0 40px',
  height: '100%',
  width: '100%',
}));

const SocialContainer = styled(Box)(({ theme }) => ({
  margin: '20px 0',
  display: 'flex',
}));

const SocialIcon = styled(IconButton)(({ theme }) => ({
  border: '1px solid #ccc',
  borderRadius: '20%',
  display: 'inline-flex',
  justifyContent: 'center',
  alignItems: 'center',
  margin: '0 3px',
  width: '40px',
  height: '40px',
  color: '#333',
}));

const CustomTextField = styled(TextField)(({ theme, error }) => ({
  '& .MuiOutlinedInput-root': {
    backgroundColor: '#eee',
    borderRadius: '8px',
    '& fieldset': {
      border: error ? '1px solid #f44336' : 'none',
    },
  },
  margin: '8px 0',
  width: '100%',
}));

const CustomButton = styled(Button)(({ theme, variant }) => ({
  backgroundColor: variant === 'primary' ? '#512da8' : 'transparent',
  color: '#fff',
  fontSize: '12px',
  padding: '10px 45px',
  border: variant === 'primary' ? '1px solid transparent' : '1px solid #fff',
  borderRadius: '8px',
  fontWeight: 600,
  letterSpacing: '0.5px',
  textTransform: 'uppercase',
  marginTop: '10px',
  cursor: 'pointer',
  '&:hover': {
    backgroundColor: variant === 'primary' ? '#4527a0' : 'rgba(255, 255, 255, 0.1)',
  },
}));

const ToggleContainer = styled(Box)(({ theme, active }) => ({
  position: 'absolute',
  top: 0,
  left: '50%',
  width: '50%',
  height: '100%',
  overflow: 'hidden',
  transition: 'all 0.6s ease-in-out',
  borderRadius: active ? '0 150px 100px 0' : '150px 0 0 100px',
  zIndex: 1000,
  transform: active ? 'translateX(-100%)' : 'translateX(0)',
}));

const Toggle = styled(Box)(({ theme, active }) => ({
  backgroundColor: '#512da8',
  background: 'linear-gradient(to right, #5c6bc0, #512da8)',
  color: '#fff',
  position: 'relative',
  left: '-100%',
  height: '100%',
  width: '200%',
  transform: active ? 'translateX(50%)' : 'translateX(0)',
  transition: 'all 0.6s ease-in-out',
}));

const TogglePanel = styled(Box)(({ theme, position, active }) => ({
  position: 'absolute',
  width: '50%',
  height: '100%',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  flexDirection: 'column',
  padding: '0 30px',
  textAlign: 'center',
  top: 0,
  transform: position === 'left' 
    ? active ? 'translateX(0)' : 'translateX(-200%)'
    : active ? 'translateX(200%)' : 'translateX(0)',
  transition: 'all 0.6s ease-in-out',
  right: position === 'right' ? 0 : 'auto',
}));

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false
  });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [active, setActive] = useState(true);
  const [tosOpen, setTosOpen] = useState(false);
  const [privacyOpen, setPrivacyOpen] = useState(false);

  const handleChange = (e) => {
    const { name, value, checked } = e.target;
    const val = name === 'agreeToTerms' ? checked : value;
    
    setFormData({
      ...formData,
      [name]: val
    });
    
    // Clear error for this field if exists
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: ''
      });
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };

  const validateForm = () => {
    const newErrors = {};
    
    // Validate first name
    if (!formData.firstName.trim()) {
      newErrors.firstName = 'First name is required';
    }
    
    // Validate last name
    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Last name is required';
    }
    
    // Validate email
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    // Validate password
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long';
    }
    
    // Validate confirm password
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    // Validate terms agreement
    if (!formData.agreeToTerms) {
      newErrors.agreeToTerms = 'You must agree to the terms and conditions';
    }
    
    setErrors(newErrors);
    
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    
    try {
      // Prepare data for the API
      const userData = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        password: formData.password
      };
      
      await register(userData);
      alert('Registration successful! Please log in.');
      setActive(false);
    } catch (error) {
      if (error.response && error.response.data) {
        const serverErrors = error.response.data;
        const newErrors = {};
        
        Object.keys(serverErrors).forEach(key => {
          newErrors[key === 'email' ? 'email' : 
                   key === 'password' ? 'password' : 
                   key === 'first_name' ? 'firstName' : 
                   key === 'last_name' ? 'lastName' : key] = serverErrors[key][0];
        });
        
        setErrors(newErrors);
      } else {
        alert('Registration failed. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box className="auth-page">
      <Box id="particles-js"></Box>
      <Container className="container" active={active ? 'active' : ''}>
        <FormContainer position="signUp" active={active}>
          <Form onSubmit={handleSubmit}>
            <h1>Create Account</h1>
            <SocialContainer>
              <SocialIcon>
                <Google fontSize="small" />
              </SocialIcon>
              <SocialIcon>
                <Facebook fontSize="small" />
              </SocialIcon>
              <SocialIcon>
                <GitHub fontSize="small" />
              </SocialIcon>
              <SocialIcon>
                <LinkedIn fontSize="small" />
              </SocialIcon>
            </SocialContainer>
            
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              or use your email for registration
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 1, width: '100%' }}>
              <CustomTextField
                placeholder="First Name"
                name="firstName"
                value={formData.firstName}
                onChange={handleChange}
                required
                size="small"
                error={!!errors.firstName}
                InputProps={{
                  startAdornment: (
                    <Person fontSize="small" sx={{ color: 'rgba(0,0,0,0.54)', mr: 1 }} />
                  ),
                }}
                sx={{ flex: 1 }}
              />
              
              <CustomTextField
                placeholder="Last Name"
                name="lastName"
                value={formData.lastName}
                onChange={handleChange}
                required
                size="small"
                error={!!errors.lastName}
                InputProps={{
                  startAdornment: (
                    <Person fontSize="small" sx={{ color: 'rgba(0,0,0,0.54)', mr: 1 }} />
                  ),
                }}
                sx={{ flex: 1 }}
              />
            </Box>
            
            {(errors.firstName || errors.lastName) && (
              <Typography variant="caption" color="error" sx={{ alignSelf: 'flex-start', mb: 1 }}>
                {errors.firstName || errors.lastName}
              </Typography>
            )}
            
            <CustomTextField
              placeholder="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              required
              size="small"
              error={!!errors.email}
              InputProps={{
                startAdornment: (
                  <Email fontSize="small" sx={{ color: 'rgba(0,0,0,0.54)', mr: 1 }} />
                ),
              }}
            />
            
            {errors.email && (
              <Typography variant="caption" color="error" sx={{ alignSelf: 'flex-start', mb: 1 }}>
                {errors.email}
              </Typography>
            )}
            
            {/* Password Field */}
            <Box sx={{ 
              position: 'relative',
              width: '100%',
              margin: '8px 0',
              display: 'flex',
              alignItems: 'center',
              backgroundColor: '#eee',
              borderRadius: '8px',
            }}>
              <TextField
                placeholder="Password"
                type={showPassword ? "text" : "password"}
                value={formData.password}
                onChange={handleChange}
                name="password"
                required
                fullWidth
                size="small"
                error={!!errors.password}
                inputProps={{ 
                  style: { fontSize: '14px' } 
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '8px 0 0 8px',
                    '& fieldset': {
                      border: !!errors.password ? '1px solid #f44336' : 'none',
                    },
                  },
                  '& .MuiInputBase-input': {
                    backgroundColor: '#eee',
                  },
                  margin: 0,
                }}
              />
              <IconButton
                onClick={togglePasswordVisibility}
                sx={{ 
                  height: '40px',
                  width: '40px',
                  backgroundColor: '#eee',
                  borderRadius: '0 8px 8px 0',
                  padding: 0,
                  '&:hover': { 
                    backgroundColor: '#e0e0e0' 
                  }
                }}
                aria-label="show password"
              >
                <Visibility fontSize="small" />
              </IconButton>
            </Box>
            {errors.password && (
              <Typography variant="caption" color="error" sx={{ alignSelf: 'flex-start', mb: 1 }}>
                {errors.password}
              </Typography>
            )}

            {/* Confirm Password Field */}
            <Box sx={{ 
              position: 'relative',
              width: '100%',
              margin: '8px 0',
              display: 'flex',
              alignItems: 'center',
              backgroundColor: '#eee',
              borderRadius: '8px',
            }}>
              <TextField
                placeholder="Confirm Password"
                type={showConfirmPassword ? "text" : "password"}
                value={formData.confirmPassword}
                onChange={handleChange}
                name="confirmPassword"
                required
                fullWidth
                size="small"
                error={!!errors.confirmPassword}
                inputProps={{ 
                  style: { fontSize: '14px' } 
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '8px 0 0 8px',
                    '& fieldset': {
                      border: !!errors.confirmPassword ? '1px solid #f44336' : 'none',
                    },
                  },
                  '& .MuiInputBase-input': {
                    backgroundColor: '#eee',
                  },
                  margin: 0,
                }}
              />
              <IconButton
                onClick={toggleConfirmPasswordVisibility}
                sx={{ 
                  height: '40px',
                  width: '40px',
                  backgroundColor: '#eee',
                  borderRadius: '0 8px 8px 0',
                  padding: 0,
                  '&:hover': { 
                    backgroundColor: '#e0e0e0' 
                  }
                }}
                aria-label="show confirm password"
              >
                <Visibility fontSize="small" />
              </IconButton>
            </Box>
            {errors.confirmPassword && (
              <Typography variant="caption" color="error" sx={{ alignSelf: 'flex-start', mb: 1 }}>
                {errors.confirmPassword}
              </Typography>
            )}
            
            <FormControlLabel
              control={
                <Checkbox 
                  checked={formData.agreeToTerms} 
                  onChange={handleChange}
                  name="agreeToTerms"
                  color="primary"
                />
              }
              label={
                <Box component="span" sx={{ fontSize: '12px' }}>
                  I agree to the{' '}
                  <Box 
                    component="span" 
                    onClick={() => setTosOpen(true)}
                    sx={{ 
                      color: '#512da8', 
                      cursor: 'pointer',
                      textDecoration: 'underline',
                      fontWeight: 600,
                      mx: 0.5
                    }}
                  >
                    Terms of Service
                  </Box>{' '}
                  and{' '}
                  <Box 
                    component="span" 
                    onClick={() => setPrivacyOpen(true)}
                    sx={{ 
                      color: '#512da8', 
                      cursor: 'pointer',
                      textDecoration: 'underline',
                      fontWeight: 600,
                      mx: 0.5
                    }}
                  >
                    Privacy Policy
                  </Box>
                </Box>
              }
              sx={{ 
                mt: 1,
                color: errors.agreeToTerms ? '#f44336' : 'inherit',
                alignItems: 'flex-start',
                '.MuiFormControlLabel-label': {
                  mt: 0.5  // Align text with checkbox
                }
              }}
            />
            {errors.agreeToTerms && (
              <Typography variant="caption" color="error" sx={{ alignSelf: 'flex-start', mb: 1 }}>
                {errors.agreeToTerms}
              </Typography>
            )}
            
            <CustomButton 
              type="submit" 
              variant="primary"
              disabled={loading}
              sx={{ mt: 1 }}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : "Sign Up"}
            </CustomButton>
          </Form>
        </FormContainer>
        
        <ToggleContainer active={active}>
          <Toggle active={active}>
            <TogglePanel position="left" active={active}>
              <Typography variant="h5" sx={{ fontWeight: 600, color: '#fff' }}>
                Hi there,
              </Typography>
              <Typography variant="body2" sx={{ my: 3, color: '#fff' }}>
                Enter your personal details to use all of site features
              </Typography>
              <CustomButton variant="transparent" onClick={() => setActive(false)}>
                Sign In
              </CustomButton>
            </TogglePanel>
            
            <TogglePanel position="right" active={active}>
              <Typography variant="h5" sx={{ fontWeight: 600, color: '#fff' }}>
                Hello, Friend!
              </Typography>
              <Typography variant="body2" sx={{ my: 3, color: '#fff' }}>
                Register with your personal details to use all of site features
              </Typography>
              <CustomButton variant="transparent" onClick={() => setActive(true)}>
                Sign Up
              </CustomButton>
            </TogglePanel>
          </Toggle>
        </ToggleContainer>
      </Container>

      {/* Terms of Service Dialog */}
      <Dialog open={tosOpen} onClose={() => setTosOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>Terms of Service</DialogTitle>
        <DialogContent>
          <DialogContentText component="div">
            <div dangerouslySetInnerHTML={{ __html: TERMS_OF_SERVICE.replace(/\n/g, '<br>') }} />
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTosOpen(false)} color="primary">
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Privacy Policy Dialog */}
      <Dialog open={privacyOpen} onClose={() => setPrivacyOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>Privacy Policy</DialogTitle>
        <DialogContent>
          <DialogContentText component="div">
            <div dangerouslySetInnerHTML={{ __html: PRIVACY_POLICY.replace(/\n/g, '<br>') }} />
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPrivacyOpen(false)} color="primary">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Register;