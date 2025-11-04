import React, { createContext, useState, useContext, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authAPI } from '../services/api-fetch';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const savedToken = await AsyncStorage.getItem('token');
      const savedUser = await AsyncStorage.getItem('user');
      
      if (savedToken && savedUser) {
        setToken(savedToken);
        const userData = JSON.parse(savedUser);
        // Convert string booleans to actual booleans
        if (userData.is_active) {
          userData.is_active = userData.is_active === 'true' || userData.is_active === true;
        }
        setUser(userData);
      }
    } catch (error) {
      console.error('Failed to load user:', error);
      // Clear corrupted data and reload
      await AsyncStorage.multiRemove(['token', 'user']);
    } finally {
      setLoading(false);
    }
  };

  const requestOTP = async (phone) => {
    try {
      const response = await authAPI.requestOTP(phone);
      return response.data;
    } catch (error) {
      throw error;
    }
  };

  const verifyOTP = async (phone, otp) => {
    try {
      const response = await authAPI.verifyOTP(phone, otp);
      const { access_token, user: userData } = response.data;
      
      // Convert string booleans to actual booleans
      if (userData.is_active) {
        userData.is_active = userData.is_active === 'true' || userData.is_active === true;
      }
      
      await AsyncStorage.setItem('token', access_token);
      await AsyncStorage.setItem('user', JSON.stringify(userData));
      
      setToken(access_token);
      setUser(userData);
      
      return response.data;
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await AsyncStorage.removeItem('token');
      await AsyncStorage.removeItem('user');
      setToken(null);
      setUser(null);
    } catch (error) {
      console.error('Failed to logout:', error);
    }
  };

  return (
    <AuthContext.Provider 
      value={{ 
        user, 
        token, 
        loading, 
        requestOTP, 
        verifyOTP, 
        logout,
        isAuthenticated: !!token 
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
