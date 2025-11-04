/**
 * Custom hook for automatic token refresh
 */
import { useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { authAPI } from '../services/api';

const TOKEN_REFRESH_INTERVAL = 20 * 60 * 1000; // 20 minutes
const TOKEN_EXPIRY_CHECK_INTERVAL = 60 * 1000; // Check every minute

export const useTokenRefresh = () => {
  const { user, logout } = useAuth();

  const refreshToken = useCallback(async () => {
    try {
      const rememberMe = localStorage.getItem('remember_me') === 'true';
      
      // Only auto-refresh if remember me is enabled
      if (!rememberMe) {
        return;
      }

      const refreshTokenValue = localStorage.getItem('refresh_token');
      if (!refreshTokenValue) {
        console.log('No refresh token available');
        return;
      }

      console.log('Auto-refreshing token...');
      const response = await authAPI.refreshToken(refreshTokenValue);
      const { access_token, refresh_token, user: userData } = response.data;

      // Update tokens
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      console.log('Token refreshed successfully');
    } catch (error) {
      console.error('Token refresh failed:', error);
      // If refresh fails, log out user
      logout();
    }
  }, [logout]);

  const checkTokenExpiry = useCallback(() => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      // Decode JWT to check expiry (without validation)
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );

      const payload = JSON.parse(jsonPayload);
      const exp = payload.exp * 1000; // Convert to milliseconds
      const now = Date.now();
      const timeUntilExpiry = exp - now;

      // If token expires in less than 5 minutes, refresh it
      if (timeUntilExpiry < 5 * 60 * 1000 && timeUntilExpiry > 0) {
        console.log('Token expiring soon, refreshing...');
        refreshToken();
      }

      // If token already expired, logout
      if (timeUntilExpiry <= 0) {
        console.log('Token expired, logging out...');
        logout();
      }
    } catch (error) {
      console.error('Error checking token expiry:', error);
    }
  }, [refreshToken, logout]);

  useEffect(() => {
    if (!user) return;

    // Set up periodic token refresh (only if remember me is enabled)
    const rememberMe = localStorage.getItem('remember_me') === 'true';
    if (rememberMe) {
      const refreshInterval = setInterval(refreshToken, TOKEN_REFRESH_INTERVAL);
      
      // Also check token expiry more frequently
      const expiryCheckInterval = setInterval(checkTokenExpiry, TOKEN_EXPIRY_CHECK_INTERVAL);

      return () => {
        clearInterval(refreshInterval);
        clearInterval(expiryCheckInterval);
      };
    }
  }, [user, refreshToken, checkTokenExpiry]);

  return { refreshToken };
};
