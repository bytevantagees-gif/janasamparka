import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      const refreshToken = localStorage.getItem('refresh_token');
      const userData = localStorage.getItem('user');
      
      if (token && userData) {
        try {
          // Try to validate the current token by making a test request
          await authAPI.getCurrentUser();
          setUser(JSON.parse(userData));
        } catch (error) {
          // If token is invalid, try to refresh
          if (refreshToken) {
            try {
              const response = await authAPI.refreshToken(refreshToken);
              const { access_token, refresh_token, user: newUserData } = response.data;
              
              localStorage.setItem('access_token', access_token);
              localStorage.setItem('refresh_token', refresh_token);
              localStorage.setItem('user', JSON.stringify(newUserData));
              
              setUser(newUserData);
            } catch (refreshError) {
              // If refresh fails, clear stored data
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              localStorage.removeItem('user');
            }
          } else {
            // No refresh token, clear stored data
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
          }
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const requestOTP = async (phone) => {
    try {
      setError(null);
      const response = await authAPI.requestOTP(phone);
      return response.data;
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to request OTP';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  };

  const verifyOTP = async (phone, otp) => {
    try {
      setError(null);
      const response = await authAPI.verifyOTP(phone, otp);
      
      // The response should contain access_token, refresh_token, and user data
      const { access_token, refresh_token, user } = response.data;
      
      if (!access_token || !refresh_token || !user) {
        console.error('Invalid login response:', response.data);
        throw new Error('Invalid response from server: Missing required data');
      }
      
      // Extract user data
      const userData = {
        id: user.id,
        name: user.name,
        phone: user.phone,
        role: user.role,
        constituency_id: user.constituency_id,
        // Include any other required user fields
        ...user
      };
      
      // Store tokens and user data with constituency info
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      // Log for debugging multi-tenancy and token storage
      console.log('User logged in:', {
        name: userData.name,
        role: userData.role,
        constituency_id: userData.constituency_id,
        token_length: access_token.length,
        token_preview: access_token.substring(0, 20) + '...'
      });
      
      setUser(userData);
      return userData;
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to verify OTP';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const updateUser = (userData) => {
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  };

  const value = {
    user,
    loading,
    error,
    requestOTP,
    verifyOTP,
    logout,
    updateUser,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
