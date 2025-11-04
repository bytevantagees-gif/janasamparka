import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Update this to your backend URL
// For local development: use your computer's IP address (not localhost)
// Example: http://192.168.1.100:8000/api
const API_URL = 'http://192.168.29.35:8000/api';

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  requestOTP: (phone) => api.post('/auth/request-otp', { phone }),
  verifyOTP: (phone, otp) => api.post('/auth/verify-otp', { phone, otp }),
};

// Complaints API
export const complaintsAPI = {
  getAll: (filters) => api.get('/complaints', { params: filters }),
  getById: (id) => api.get(`/complaints/${id}`),
  create: (data) => {
    const formData = new FormData();
    
    // Add text fields
    Object.keys(data).forEach(key => {
      if (key !== 'images' && data[key] !== null && data[key] !== undefined) {
        formData.append(key, data[key]);
      }
    });
    
    // Add images
    if (data.images && data.images.length > 0) {
      data.images.forEach((image, index) => {
        const uri = image.uri;
        const uriParts = uri.split('.');
        const fileType = uriParts[uriParts.length - 1];
        
        formData.append('images', {
          uri: uri,
          name: `photo_${index}.${fileType}`,
          type: `image/${fileType}`,
        });
      });
    }
    
    return api.post('/complaints', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  updateStatus: (id, status, comment) => 
    api.patch(`/complaints/${id}/status`, { status, comment }),
  addComment: (id, comment) => 
    api.post(`/complaints/${id}/comments`, { comment }),
};

// Constituencies API
export const constituenciesAPI = {
  getAll: () => api.get('/constituencies'),
  getById: (id) => api.get(`/constituencies/${id}`),
};

// Wards API
export const wardsAPI = {
  getAll: () => api.get('/wards'),
  getByConstituency: (constituencyId) => 
    api.get(`/wards?constituency_id=${constituencyId}`),
};

// Departments API
export const departmentsAPI = {
  getAll: () => api.get('/departments'),
  getById: (id) => api.get(`/departments/${id}`),
};

// User API
export const userAPI = {
  getProfile: () => api.get('/users/me'),
  updateProfile: (data) => api.patch('/users/me', data),
};

export default api;
