import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import { Box, Button, TextField, Typography, Paper, Checkbox, FormControlLabel, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions } from '@mui/material';
import { authAPI } from '../services/api';
import { TERMS_OF_SERVICE, PRIVACY_POLICY } from '../constants/legal';

const Register = () => {
  const history = useHistory();
  const [formData, setFormData] = useState({ firstName: '', lastName: '', email: '', password: '' });
  const [agree, setAgree] = useState(false);
  const [error, setError] = useState('');
  const [tosOpen, setTosOpen] = useState(false);
  const [privacyOpen, setPrivacyOpen] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!agree) {
      setError('You must agree to the Terms of Service and Privacy Policy.');
      return;
    }
    setError('');
    try {
      await authAPI.register(formData);
      history.push('/login');
    } catch (err) {
      setError(err.response && err.response.data ? err.response.data.message : 'Registration failed.');
    }
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      height="100vh"
      bgcolor="#f5f5f5"
      sx={{ overflow: 'hidden' }}
    >
      <Paper elevation={6} sx={{ 
        padding: '2rem', 
        maxWidth: '500px', 
        width: '100%',
        maxHeight: '90vh',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem'
      }}>
        <Typography variant="h4" align="center" gutterBottom>
          Register
        </Typography>
        {error && (
          <Typography color="error" align="center">{error}</Typography>
        )}
        <form onSubmit={handleSubmit} noValidate>
          <TextField
            label="First Name"
            variant="outlined"
            margin="normal"
            fullWidth
            name="firstName"
            value={formData.firstName}
            onChange={handleChange}
            required
          />
          <TextField
            label="Last Name"
            variant="outlined"
            margin="normal"
            fullWidth
            name="lastName"
            value={formData.lastName}
            onChange={handleChange}
            required
          />
          <TextField
            label="Email"
            variant="outlined"
            margin="normal"
            fullWidth
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
          />
          <TextField
            label="Password"
            type="password"
            variant="outlined"
            margin="normal"
            fullWidth
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
          <FormControlLabel
            control={<Checkbox checked={agree} onChange={(e) => setAgree(e.target.checked)} color="primary" />}
            label={
              <span>
                I agree to the{' '}
                <Button color="primary" onClick={() => setTosOpen(true)}>Terms of Service</Button>{' '}
                and{' '}
                <Button color="primary" onClick={() => setPrivacyOpen(true)}>Privacy Policy</Button>
              </span>
            }
          />
          <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2, py: 1 }}>
            Register
          </Button>
        </form>
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
      </Paper>
    </Box>
  );
};

export default Register;
