import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI, api } from '../services/api';
import { saveTokens } from '../services/auth';
import '../styles/auth.css';

const AuthPage = () => {
  const navigate = useNavigate();
  const containerRef = useRef(null);
  
  // Login state
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  
  // Register state
  const [registerName, setRegisterName] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  
  // UI state
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Initialize particles.js
    if (window.particlesJS) {
      window.particlesJS('particles-js', {
        particles: {
          number: {
            value: 80,
            density: {
              enable: true,
              value_area: 800
            }
          },
          color: {
            value: "#ffffff"
          },
          shape: {
            type: "circle",
            stroke: {
              width: 0,
              color: "#000000"
            },
            polygon: {
              nb_sides: 5
            },
            image: {
              src: "img/github.svg",
              width: 100,
              height: 100
            }
          },
          opacity: {
            value: 0.5,
            random: false,
            anim: {
              enable: false,
              speed: 1,
              opacity_min: 0.1,
              sync: false
            }
          },
          size: {
            value: 3,
            random: true,
            anim: {
              enable: false,
              speed: 40,
              size_min: 0.1,
              sync: false
            }
          },
          line_linked: {
            enable: true,
            distance: 150,
            color: "#ffffff",
            opacity: 0.4,
            width: 1
          },
          move: {
            enable: true,
            speed: 6,
            direction: "none",
            random: false,
            straight: false,
            out_mode: "out",
            attract: {
              enable: false,
              rotateX: 600,
              rotateY: 1200
            }
          }
        },
        interactivity: {
          detect_on: "canvas",
          events: {
            onhover: {
              enable: true,
              mode: "repulse"
            },
            onclick: {
              enable: true,
              mode: "push"
            },
            resize: true
          },
          modes: {
            grab: {
              distance: 400,
              line_linked: {
                opacity: 1
              }
            },
            bubble: {
              distance: 400,
              size: 40,
              duration: 2,
              opacity: 8,
              speed: 3
            },
            repulse: {
              distance: 200
            },
            push: {
              particles_nb: 4
            },
            remove: {
              particles_nb: 2
            }
          }
        },
        retina_detect: true
      });
    } else {
      console.error("particles.js not loaded");
    }
  }, []);

  const handleRegisterClick = () => {
    setIsActive(true);
    setError('');
  };

  const handleLoginClick = () => {
    setIsActive(false);
    setError('');
  };

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    if (!loginEmail || !loginPassword) {
      setError('Please enter both email and password');
      setLoading(false);
      return;
    }
    
    try {
      // Debug message
      console.log('Login attempt in AuthPage for:', loginEmail);
      
      // First try standard login with token endpoint
      let response;
      try {
        // Use the updated login method that calls /api/token/
        response = await authAPI.login({ 
          email: loginEmail, 
          password: loginPassword
        });
        console.log('Token login successful:', response);
      } catch (tokenError) {
        console.error('Token login failed, trying direct login:', tokenError);
        
        // Fall back to direct login if token login fails
        response = await authAPI.loginDirect({ 
          email: loginEmail, 
          password: loginPassword
        });
        console.log('Direct login successful:', response);
      }
      
      // Reset form
      setLoginEmail('');
      setLoginPassword('');
      
      // Navigate to dashboard
      window.location.href = '/dashboard';
    } catch (err) {
      console.error('Login error:', err);
      
      if (err.response) {
        console.log('Error response status:', err.response.status);
        console.log('Error response data:', err.response.data);
        
        // Format error message based on response
        if (err.response.status === 401) {
          setError('Invalid email or password');
        } else if (err.response.status === 404) {
          setError('Account not found. Please check your email or create an account.');
        } else if (err.response.data && err.response.data.error) {
          setError(err.response.data.error);
        } else if (err.response.data && err.response.data.detail) {
          setError(err.response.data.detail);
        } else {
          setError('An error occurred during login. Please try again.');
        }
      } else if (err.request) {
        console.log('No response received:', err.request);
        setError('Unable to connect to the server. Please check your internet connection.');
      } else {
        setError(err.message || 'Login failed. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    if (!registerName || !registerEmail || !registerPassword) {
      setError('Please fill in all fields');
      setLoading(false);
      return;
    }

    console.log('Attempting registration with data:', {
      name: registerName,
      email: registerEmail,
      password: '********'
    });
    
    try {
      // Call the register API function with the correct endpoint
      const response = await authAPI.register({
        name: registerName,
        email: registerEmail,
        password: registerPassword
      });
      
      console.log('Registration successful, response:', response);
      
      // Clear form fields
      setRegisterName('');
      setRegisterEmail('');
      setRegisterPassword('');
      
      // Show success message and switch to login
      alert('Registration successful! Please login with your new account.');
      handleLoginClick();
    } catch (err) {
      console.error('Registration error:', err);
      
      if (err.response) {
        console.log('Error response status:', err.response.status);
        console.log('Error response data:', err.response.data);
        
        if (err.response.status === 409) {
          setError('An account with this email already exists.');
        } else if (err.response.status === 400) {
          // Handle validation errors
          if (typeof err.response.data === 'object') {
            const errorMessages = [];
            for (const field in err.response.data) {
              if (Array.isArray(err.response.data[field])) {
                errorMessages.push(`${field}: ${err.response.data[field].join(', ')}`);
              } else {
                errorMessages.push(`${field}: ${err.response.data[field]}`);
              }
            }
            setError(errorMessages.join('\n'));
          } else if (typeof err.response.data === 'string') {
            setError(err.response.data);
          } else {
            setError('Invalid data. Please check your inputs and try again.');
          }
        } else {
          setError(err.response.data?.message || err.response.data?.error || 'Registration failed. Please try again.');
        }
      } else if (err.request) {
        console.log('No response received:', err.request);
        setError('Unable to connect to the server. Please check your internet connection.');
      } else {
        setError(err.message || 'Registration failed. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div id="particles-js"></div>
      
      <div className={`container ${isActive ? 'active' : ''}`} ref={containerRef}>
        <div className="form-container sign-up">
          <form onSubmit={handleRegisterSubmit}>
            <h1>Create Account</h1>
            <div className="social-icons">
              <a href="#" className="icon"><i className="fa-brands fa-google"></i></a>
              <a href="#" className="icon"><i className="fa-brands fa-facebook-f"></i></a>
              <a href="#" className="icon"><i className="fa-brands fa-github"></i></a>
              <a href="#" className="icon"><i className="fa-brands fa-linkedin-in"></i></a>
            </div>
            <span>or use your email for registration</span>
            
            {error && <div className="error-message">{error}</div>}
            
            <input 
              type="text" 
              placeholder="Name" 
              value={registerName} 
              onChange={(e) => setRegisterName(e.target.value)}
              required
            />
            <input 
              type="email" 
              placeholder="Email" 
              value={registerEmail} 
              onChange={(e) => setRegisterEmail(e.target.value)}
              required
            />
            <input 
              type="password" 
              placeholder="Password" 
              value={registerPassword} 
              onChange={(e) => setRegisterPassword(e.target.value)}
              required
            />
            <p className="terms-info">
              By signing up, you agree to our{" "}
              <Link to="/terms" className="terms-link">Terms of Service</Link>{" "}
              and{" "}
              <Link to="/privacy" className="terms-link">Privacy Policy</Link>
            </p>
            <button type="submit" disabled={loading}>
              {loading ? 'Processing...' : 'Sign Up'}
            </button>
          </form>
        </div>
        
        <div className="form-container sign-in">
          <form onSubmit={handleLoginSubmit}>
            <h1>Sign In</h1>
            <div className="social-icons">
              <a href="#" className="icon"><i className="fa-brands fa-google"></i></a>
              <a href="#" className="icon"><i className="fa-brands fa-facebook-f"></i></a>
              <a href="#" className="icon"><i className="fa-brands fa-github"></i></a>
              <a href="#" className="icon"><i className="fa-brands fa-linkedin-in"></i></a>
            </div>
            <span>or use your email password</span>
            
            {error && <div className="error-message">{error}</div>}
            
            <input 
              type="email" 
              placeholder="Email" 
              value={loginEmail} 
              onChange={(e) => setLoginEmail(e.target.value)}
              required
            />
            <input 
              type="password" 
              placeholder="Password" 
              value={loginPassword} 
              onChange={(e) => setLoginPassword(e.target.value)}
              required
            />
            <a href="/forgot-password">Forgot Your Password?</a>
            <button type="submit" disabled={loading}>
              {loading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>
        </div>
        
        <div className="toggle-container">
          <div className="toggle">
            <div className="toggle-panel toggle-left">
              <h1>Welcome Back!</h1>
              <p>Enter your personal details to use all of site features</p>
              <button className="hidden" onClick={handleLoginClick}>Sign In</button>
            </div>
            <div className="toggle-panel toggle-right">
              <h1>Hello, Friend!</h1>
              <p>Register with your personal details to use all of site features</p>
              <button className="hidden" onClick={handleRegisterClick}>Sign Up</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;