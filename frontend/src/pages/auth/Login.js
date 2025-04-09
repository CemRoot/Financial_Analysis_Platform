// frontend/src/pages/auth/Login.js
import React, { useState, useContext } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { 
  Box, 
  TextField, 
  Button, 
  Typography,
  IconButton,
  CircularProgress,
  Alert,
  styled
} from '@mui/material';
import { GitHub, LinkedIn, Google, Facebook, Visibility } from '@mui/icons-material';
import { AuthContext } from '../../contexts/AuthContext';

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
  left: position === 'signIn' ? 0 : 0,
  width: '50%',
  zIndex: position === 'signIn' ? 2 : 1,
  opacity: position === 'signIn' ? 1 : 0,
  transform: active && position === 'signIn' ? 'translateX(100%)' : 
              active && position === 'signUp' ? 'translateX(100%)' : 'translateX(0)',
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

const CustomTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    backgroundColor: '#eee',
    borderRadius: '8px',
    '& fieldset': {
      border: 'none',
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

const Login = () => {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [active, setActive] = useState(false);
  
  const from = location.state?.from?.pathname || "/dashboard";

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter both email and password');
      return;
    }
    
    setError('');
    setIsLoading(true);
    
    try {
      await login(email, password);
      // Reset form
      setEmail('');
      setPassword('');
      navigate(from, { replace: true });
    } catch (error) {
      let errorMessage = 'Login failed';
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        errorMessage = error.response.data.detail || error.response.data.message || 'Invalid credentials';
      } else if (error.request) {
        // The request was made but no response was received
        errorMessage = 'No response from server. Please try again later.';
      } else {
        // Something happened in setting up the request that triggered an Error
        errorMessage = error.message;
      }
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Box className="auth-page">
      <Box id="particles-js"></Box>
      <Container className="container" active={active ? 'active' : ''}>
        <FormContainer position="signIn" active={active}>
          <Form onSubmit={handleSubmit}>
            <h1>Sign In</h1>
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
              or use your email password
            </Typography>
            
            {error && <Alert severity="error" sx={{ mb: 2, width: '100%' }}>{error}</Alert>}
            
            <CustomTextField
              placeholder="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              fullWidth
              size="small"
              inputProps={{ style: { fontSize: '14px' } }}
            />
            
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
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                fullWidth
                size="small"
                inputProps={{ 
                  style: { fontSize: '14px' } 
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '8px 0 0 8px',
                    '& fieldset': {
                      border: 'none',
                    },
                  },
                  '& .MuiInputBase-input': {
                    backgroundColor: '#eee',
                  },
                  margin: 0,
                }}
              />
              <IconButton
                onClick={() => setShowPassword(!showPassword)}
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
            
            <Link 
              to="/forgot-password" 
              style={{ 
                textDecoration: "none", 
                color: "#333",
                fontSize: '13px',
                margin: '15px 0 10px',
              }}
            >
              Forgot Your Password?
            </Link>
            
            <CustomButton 
              type="submit" 
              variant="primary" 
              disabled={isLoading}
            >
              {isLoading ? <CircularProgress size={24} color="inherit" /> : "Sign In"}
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
    </Box>
  );
};

export default Login;