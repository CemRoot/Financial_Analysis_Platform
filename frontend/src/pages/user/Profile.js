import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Avatar,
  Button,
  TextField,
  Box,
  Divider,
  Alert,
  CircularProgress,
  Snackbar
} from '@mui/material';
import { Edit, Save, Cancel } from '@mui/icons-material';
import { getUserProfile, updateUserProfile } from '../../services/user';
import { useAuth } from '../../contexts/AuthContext';

const Profile = () => {
  const { currentUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    bio: ''
  });
  
  const [formErrors, setFormErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const data = await getUserProfile(currentUser.id);
        setProfile(data);
        // Initialize form data
        setFormData({
          firstName: data.firstName || '',
          lastName: data.lastName || '',
          email: data.email || '',
          phone: data.phone || '',
          bio: data.bio || ''
        });
      } catch (err) {
        setError(err.message || 'Failed to load profile data');
      } finally {
        setLoading(false);
      }
    };

    if (currentUser) {
      fetchProfile();
    }
  }, [currentUser]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    // Clear error for this field
    if (formErrors[name]) {
      setFormErrors({
        ...formErrors,
        [name]: null
      });
    }
  };

  const validateForm = () => {
    const errors = {};
    let isValid = true;
    
    if (!formData.firstName.trim()) {
      errors.firstName = 'First name is required';
      isValid = false;
    }
    
    if (!formData.lastName.trim()) {
      errors.lastName = 'Last name is required';
      isValid = false;
    }
    
    if (!formData.email.trim()) {
      errors.email = 'Email is required';
      isValid = false;
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Email is invalid';
      isValid = false;
    }
    
    if (formData.phone && !/^\+?[0-9]{10,15}$/.test(formData.phone.replace(/[-()\s]/g, ''))) {
      errors.phone = 'Phone number is invalid';
      isValid = false;
    }
    
    if (formData.bio && formData.bio.length > 500) {
      errors.bio = 'Bio should not exceed 500 characters';
      isValid = false;
    }
    
    setFormErrors(errors);
    return isValid;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      const updatedProfile = await updateUserProfile(currentUser.id, formData);
      setProfile(updatedProfile);
      setEditMode(false);
      setSubmitSuccess(true);
    } catch (err) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEditToggle = () => {
    if (editMode) {
      // Cancel edit - reset form data to original values
      setFormData({
        firstName: profile.firstName || '',
        lastName: profile.lastName || '',
        email: profile.email || '',
        phone: profile.phone || '',
        bio: profile.bio || ''
      });
      setFormErrors({});
    }
    setEditMode(!editMode);
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

  if (error && !profile) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  const getInitials = () => {
    if (!profile) return '';
    return `${profile.firstName?.charAt(0) || ''}${profile.lastName?.charAt(0) || ''}`.toUpperCase();
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Snackbar
        open={submitSuccess}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        message="Profile updated successfully"
      />
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3, borderRadius: 2 }}>
            <Box 
              component="form" 
              onSubmit={handleSubmit}
              sx={{ 
                display: 'flex', 
                flexDirection: { xs: 'column', md: 'row' },
                alignItems: { xs: 'center', md: 'flex-start' },
                gap: 4
              }}
            >
              <Box 
                sx={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center',
                  minWidth: { md: '200px' }
                }}
              >
                <Avatar 
                  sx={{ 
                    width: 120, 
                    height: 120, 
                    fontSize: '2.5rem', 
                    bgcolor: 'primary.main',
                    mb: 2
                  }}
                >
                  {getInitials()}
                </Avatar>
                
                <Typography variant="h5" gutterBottom>
                  {profile?.firstName} {profile?.lastName}
                </Typography>
                
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Member since {new Date(profile?.createdAt).toLocaleDateString()}
                </Typography>
                
                {!editMode && (
                  <Button 
                    variant="outlined" 
                    startIcon={<Edit />} 
                    onClick={handleEditToggle}
                    sx={{ mt: 2 }}
                  >
                    Edit Profile
                  </Button>
                )}
              </Box>
              
              <Divider orientation="vertical" flexItem sx={{ display: { xs: 'none', md: 'block' } }} />
              <Divider sx={{ width: '100%', display: { xs: 'block', md: 'none' }, my: 2 }} />
              
              <Box sx={{ flex: 1 }}>
                {error && (
                  <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                  </Alert>
                )}
                
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="First Name"
                      name="firstName"
                      value={formData.firstName}
                      onChange={handleInputChange}
                      disabled={!editMode || isSubmitting}
                      error={!!formErrors.firstName}
                      helperText={formErrors.firstName}
                      required
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Last Name"
                      name="lastName"
                      value={formData.lastName}
                      onChange={handleInputChange}
                      disabled={!editMode || isSubmitting}
                      error={!!formErrors.lastName}
                      helperText={formErrors.lastName}
                      required
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      disabled={!editMode || isSubmitting}
                      error={!!formErrors.email}
                      helperText={formErrors.email}
                      required
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Phone"
                      name="phone"
                      value={formData.phone}
                      onChange={handleInputChange}
                      disabled={!editMode || isSubmitting}
                      error={!!formErrors.phone}
                      helperText={formErrors.phone}
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Bio"
                      name="bio"
                      multiline
                      rows={4}
                      value={formData.bio}
                      onChange={handleInputChange}
                      disabled={!editMode || isSubmitting}
                      error={!!formErrors.bio}
                      helperText={formErrors.bio || 'Brief description about yourself'}
                    />
                  </Grid>
                  
                  {editMode && (
                    <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 2 }}>
                      <Button 
                        variant="outlined" 
                        startIcon={<Cancel />} 
                        onClick={handleEditToggle}
                        disabled={isSubmitting}
                      >
                        Cancel
                      </Button>
                      
                      <Button 
                        type="submit" 
                        variant="contained" 
                        startIcon={<Save />}
                        disabled={isSubmitting}
                      >
                        {isSubmitting ? 'Saving...' : 'Save Changes'}
                      </Button>
                    </Grid>
                  )}
                </Grid>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Profile;