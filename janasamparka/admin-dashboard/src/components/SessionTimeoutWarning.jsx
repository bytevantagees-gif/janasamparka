/**
 * Session Timeout Warning Component
 * Shows a warning when the session is about to expire
 */
import { useState, useEffect } from 'react';
import { AlertCircle, Clock, LogOut } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { authAPI } from '../services/api';

const SessionTimeoutWarning = () => {
  const [showWarning, setShowWarning] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const { logout } = useAuth();

  useEffect(() => {
    const checkSession = () => {
      const token = localStorage.getItem('access_token');
      const rememberMe = localStorage.getItem('remember_me') === 'true';

      // Don't show warning if remember me is enabled (auto-refresh handles it)
      if (rememberMe) {
        setShowWarning(false);
        return;
      }

      if (!token) {
        setShowWarning(false);
        return;
      }

      try {
        // Decode JWT
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(
          atob(base64)
            .split('')
            .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
            .join('')
        );

        const payload = JSON.parse(jsonPayload);
        const exp = payload.exp * 1000;
        const now = Date.now();
        const remaining = exp - now;

        setTimeRemaining(Math.floor(remaining / 1000));

        // Show warning if less than 2 minutes remaining
        if (remaining < 2 * 60 * 1000 && remaining > 0) {
          setShowWarning(true);
        } else if (remaining <= 0) {
          // Session expired, logout
          logout();
        } else {
          setShowWarning(false);
        }
      } catch (error) {
        console.error('Error checking session:', error);
      }
    };

    // Check every 10 seconds
    checkSession();
    const interval = setInterval(checkSession, 10000);

    return () => clearInterval(interval);
  }, [logout]);

  const handleExtendSession = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) return;

      const response = await authAPI.refreshToken(refreshToken);
      const { access_token, refresh_token: newRefreshToken, user } = response.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', newRefreshToken);
      localStorage.setItem('user', JSON.stringify(user));

      setShowWarning(false);
    } catch (error) {
      console.error('Failed to extend session:', error);
      logout();
    }
  };

  const handleLogoutNow = () => {
    logout();
  };

  if (!showWarning) return null;

  const minutes = Math.floor(timeRemaining / 60);
  const seconds = timeRemaining % 60;

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-md">
      <div className="bg-yellow-50 border-2 border-yellow-400 rounded-lg shadow-lg p-4">
        <div className="flex items-start">
          <AlertCircle className="h-6 w-6 text-yellow-600 mt-0.5" />
          <div className="ml-3 flex-1">
            <h3 className="text-sm font-medium text-yellow-800">
              Session Expiring Soon
            </h3>
            <p className="mt-1 text-sm text-yellow-700">
              Your session will expire in{' '}
              <strong>
                {minutes}:{seconds.toString().padStart(2, '0')}
              </strong>
            </p>
            <div className="mt-3 flex gap-2">
              <button
                onClick={handleExtendSession}
                className="flex items-center px-3 py-2 bg-yellow-600 text-white text-sm font-medium rounded-lg hover:bg-yellow-700"
              >
                <Clock className="mr-1.5 h-4 w-4" />
                Extend Session
              </button>
              <button
                onClick={handleLogoutNow}
                className="flex items-center px-3 py-2 bg-white border border-yellow-600 text-yellow-700 text-sm font-medium rounded-lg hover:bg-yellow-50"
              >
                <LogOut className="mr-1.5 h-4 w-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SessionTimeoutWarning;
