import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

// Create the auth context
const AuthContext = createContext();

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Set up axios with the token
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Token ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Fetch user data if token exists
  useEffect(() => {
    const fetchUserData = async () => {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        // First, get the user data from djoser endpoint
        const userResponse = await axios.get('/api/auth/users/me/');
        if (userResponse.data) {
          const userData = userResponse.data;
          
          // Then, try to get profile data if needed
          try {
            const profileResponse = await axios.get('/api/profile/');
            if (profileResponse.data && profileResponse.data.length > 0) {
              // Combine user and profile data
              setUser({
                ...userData,
                ...profileResponse.data[0]
              });
            } else {
              setUser(userData);
            }
          } catch (profileError) {
            // If profile fetch fails, just use the base user data
            setUser(userData);
          }
          
          setIsAuthenticated(true);
        } else {
          // Invalid token or no user data
          logout();
        }
      } catch (error) {
        console.error('Error fetching user data:', error);
        logout();
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [token]);

  // Login function
  const login = async (username, password) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/auth/token/login/', { username, password });
      
      if (response.data.auth_token) {
        localStorage.setItem('token', response.data.auth_token);
        setToken(response.data.auth_token);
        return true;
      }
    } catch (error) {
      console.error('Login error:', error);
      setError(error.response?.data?.non_field_errors?.[0] || 'Login failed. Please check your credentials.');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Register function
  const register = async (username, email, password) => {
    setLoading(true);
    setError(null);

    try {
      // Djoser uses a different endpoint structure
      const response = await axios.post('/api/auth/users/', {
        username,
        email,
        password
      });

      if (response.status === 201) {
        // Auto-login after registration
        return await login(username, password);
      }
    } catch (error) {
      console.error('Registration error:', error);
      
      // Better error handling for Djoser's error format
      if (error.response?.data) {
        // Flatten all error messages into a single string
        const errorMessages = Object.entries(error.response.data)
          .map(([field, messages]) => {
            if (Array.isArray(messages)) {
              return `${field}: ${messages.join(', ')}`;
            }
            return `${field}: ${messages}`;
          })
          .join('; ');
        
        setError(errorMessages || 'Registration failed. Please try again.');
      } else {
        setError('Registration failed. Please try again.');
      }
      
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = async () => {
    if (token) {
      try {
        // Call Djoser logout endpoint to invalidate the token
        await axios.post('/api/auth/token/logout/');
      } catch (error) {
        console.error('Logout error:', error);
        // Continue with local logout even if API logout fails
      }
    }
    
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    // Clear auth header
    delete axios.defaults.headers.common['Authorization'];
  };

  // Check if user has completed survey
  const hasCompletedSurvey = () => {
    return user?.survey_completed || false;
  };

  // Context value
  const value = {
    user,
    token,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout,
    hasCompletedSurvey
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}; 