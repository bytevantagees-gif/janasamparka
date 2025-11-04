import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create the main API client
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('[API] Request with token to:', config.url, 'Token length:', token.length, 'Full URL:', config.baseURL + config.url);
    } else if (!config.url.includes('/auth/')) {
      console.warn('[API] No token found for request to:', config.url);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => {
    console.log('[API] Response success for:', response.config.url, 'Status:', response.status);
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url.includes('/auth/')) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          console.log('[API] Attempting to refresh token...');
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken
          });
          
          const { access_token, refresh_token } = response.data;
          
          if (access_token) {
            localStorage.setItem('access_token', access_token);
            if (refresh_token) {
              localStorage.setItem('refresh_token', refresh_token);
            }
            
            // Update the Authorization header
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            
            // Retry the original request
            return api(originalRequest);
          }
        }
      } catch (refreshError) {
        console.error('[API] Token refresh failed:', refreshError);
        // Clear auth data and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => {
    console.log('[API] Response success for:', response.config.url, 'Status:', response.status);
    return response;
  },
  async (error) => {
    console.error('[API] Response error for:', error.config?.url, 'Status:', error.response?.status, 'Message:', error.message);
    
    const originalRequest = error.config;

    // If error is 401 and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      console.log('[API] 401 error, attempting token refresh...');
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          console.log('[API] Refreshing token...');
          // Try to refresh the token using authAxios (no interceptor loop)
          const response = await authAxios.post('/api/auth/refresh', {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token: new_refresh_token } = response.data;

          // Store new tokens
          localStorage.setItem('access_token', access_token);
          if (new_refresh_token) {
            localStorage.setItem('refresh_token', new_refresh_token);
          }

          console.log('[API] Token refreshed successfully');

          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } else {
          console.warn('[API] No refresh token available');
        }
      } catch (refreshError) {
        console.error('[API] Token refresh failed:', refreshError);
        // If refresh fails, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Constituencies API
export const constituenciesAPI = {
  getAll: (activeOnly = true) =>
    api.get(`/api/constituencies/?active_only=${activeOnly}`),
  
  getById: (id) =>
    api.get(`/api/constituencies/${id}`),
  
  getStats: (id) =>
    api.get(`/api/constituencies/${id}/stats`),
  
  create: (data) =>
    api.post('/api/constituencies/', data),
  
  update: (id, data) =>
    api.patch(`/api/constituencies/${id}`, data),
  
  deactivate: (id) =>
    api.delete(`/api/constituencies/${id}`),
  
  activate: (id) =>
    api.post(`/api/constituencies/${id}/activate`),
  
  compare: () =>
    api.get('/api/constituencies/compare/all'),
};

// Complaints API
export const complaintsAPI = {
  getAll: (params) =>
    api.get('/api/complaints/', { params }),
  
  getMyAssigned: (params) =>
    api.get('/api/complaints/my-assigned', { params }),
  
  getById: (id) =>
    api.get(`/api/complaints/${id}`),
  
  create: (data) =>
    api.post('/api/complaints/', data),
  
  assign: (id, data) =>
    api.post(`/api/complaints/${id}/assign`, data),
  
  subAssign: (id, data) =>
    api.post(`/api/complaints/${id}/sub-assign`, data),
  
  updateStatus: (id, data) =>
    api.patch(`/api/complaints/${id}/status`, data),
  
  getStats: () =>
    api.get('/api/complaints/stats/summary'),

  getAdvancedStats: () =>
    api.get('/api/complaints/stats/advanced'),

  getUsersByRole: (roles, constituencyId) =>
    api.get('/api/users/', { 
      params: { 
        roles: roles.join(','), 
        constituency_id: constituencyId 
      } 
    }),
  
  updateComplaintNotes: (id, data) =>
    api.patch(`/api/complaints/${id}/notes`, data),
};

// Create a separate axios instance for auth requests
const authAxios = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to add auth token
authAxios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle the auth response data structure
authAxios.interceptors.response.use(
  (response) => {
    // Don't modify the response for OTP verification
    if (response.config.url.includes('/verify-otp')) {
      return response;
    }
    
    // For /me endpoint, ensure we have the expected structure
    if (response.config.url.includes('/auth/me')) {
      // If the response is already in the expected format, return as is
      if (response.data && (response.data.id || response.data.user)) {
        return response;
      }
      // Otherwise, ensure it's wrapped in a data property
      return {
        ...response,
        data: response.data || {}
      };
    }
    
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          console.log('[API] Attempting to refresh token...');
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken
          });
          
          const { access_token, refresh_token } = response.data;
          
          if (access_token) {
            localStorage.setItem('access_token', access_token);
            if (refresh_token) {
              localStorage.setItem('refresh_token', refresh_token);
            }
            
            // Update the Authorization header
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            
            // Retry the original request
            return api(originalRequest);
          }
        }
      } catch (refreshError) {
        console.error('[API] Token refresh failed:', refreshError);
        // Clear auth data and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  requestOTP: (phone) =>
    authAxios.post('/api/auth/request-otp', { phone }),
  
  verifyOTP: (phone, otp) =>
    authAxios.post('/api/auth/verify-otp', { phone, otp }),
  
  getCurrentUser: async () => {
    const response = await authAxios.get('/api/auth/me');
    // The backend returns the user object directly, not wrapped in a data.user property
    return response;
  },
  
  refreshToken: (refreshToken) =>
    authAxios.post('/api/auth/refresh', { refresh_token: refreshToken }),
  
  resetUserAccess: (userId) =>
    api.post('/api/auth/admin/reset-user-access', { user_id: userId }),
  
  loginWithCode: (accessCode) =>
    authAxios.post('/api/auth/login-with-code', { access_code: accessCode }),
};

// Users API
export const usersAPI = {
  getAll: (params) =>
    api.get('/api/users/', { params }),
    
  getUser: (userId) =>
    api.get(`/api/users/${userId}`),
    
  updateUser: (userId, data) =>
    api.patch(`/api/users/${userId}`, data),
    
  createUser: (data) =>
    api.post('/api/users/', data),
    
  deleteUser: (userId) =>
    api.delete(`/api/users/${userId}`),
};

export const analyticsAPI = {
  getDashboard: () =>
    api.get('/api/analytics/dashboard'),

  getSatisfaction: () =>
    api.get('/api/analytics/satisfaction'),

  getTrends: (params) =>
    api.get('/api/analytics/trends', { params }),

  getAlerts: () =>
    api.get('/api/analytics/alerts'),
  
  getMLAPerformanceComparison: (params) =>
    api.get('/api/analytics/mla/performance-comparison', { params }),
  
  getSatisfactionAggregated: (params) =>
    api.get('/api/analytics/satisfaction/aggregated', { params }),
};

export const interventionsAPI = {
  createIntervention: (data) =>
    api.post('/api/interventions', data),
  
  getInterventions: (params) =>
    api.get('/api/interventions', { params }),
  
  updateIntervention: (id, data) =>
    api.patch(`/api/interventions/${id}`, data),
  
  completeIntervention: (id, data) =>
    api.post(`/api/interventions/${id}/complete`, data),
};

// Polls API
export const pollsAPI = {
  getAll: (params) =>
    api.get('/api/polls/', { params }),
  
  getById: (id) =>
    api.get(`/api/polls/${id}`),
  
  getMyVotes: () =>
    api.get('/api/polls/my-votes'),
  
  vote: (pollId, optionId) =>
    api.post(`/api/polls/${pollId}/vote`, { option_id: optionId }),
  
  create: (data) =>
    api.post('/api/polls/', data),
  
  update: (id, data) =>
    api.patch(`/api/polls/${id}`, data),
};

// Wards API
export const wardsAPI = {
  getAll: (params) =>
    api.get('/api/wards/', { params }),
  
  getById: (id) =>
    api.get(`/api/wards/${id}`),
  
  getStats: (id) =>
    api.get(`/api/wards/${id}/stats`),
  
  getMyWard: () =>
    api.get('/api/wards/my-ward'),
  
  create: (data) =>
    api.post('/api/wards/', data),
  
  update: (id, data) =>
    api.patch(`/api/wards/${id}`, data),
};

// Panchayats API
export const panchayatsAPI = {
  // Zilla Panchayat (District) APIs
  getAllZP: (params) =>
    api.get('/api/panchayats/zilla', { params }),
  
  getZP: (id) =>
    api.get(`/api/panchayats/zilla/${id}`),
  
  createZP: (data) =>
    api.post('/api/panchayats/zilla', data),
  
  updateZP: (id, data) =>
    api.patch(`/api/panchayats/zilla/${id}`, data),
  
  deleteZP: (id) =>
    api.delete(`/api/panchayats/zilla/${id}`),

  // Taluk Panchayat (Block) APIs
  getAllTP: (params) =>
    api.get('/api/panchayats/taluk', { params }),
  
  getTP: (id) =>
    api.get(`/api/panchayats/taluk/${id}`),
  
  createTP: (data) =>
    api.post('/api/panchayats/taluk', data),
  
  updateTP: (id, data) =>
    api.patch(`/api/panchayats/taluk/${id}`, data),
  
  deleteTP: (id) =>
    api.delete(`/api/panchayats/taluk/${id}`),

  // Gram Panchayat (Village) APIs
  getAllGP: (params) =>
    api.get('/api/panchayats/gram', { params }),
  
  getGP: (id) =>
    api.get(`/api/panchayats/gram/${id}`),
  
  createGP: (data) =>
    api.post('/api/panchayats/gram', data),
  
  updateGP: (id, data) =>
    api.patch(`/api/panchayats/gram/${id}`, data),
  
  deleteGP: (id) =>
    api.delete(`/api/panchayats/gram/${id}`),
  
  // Hierarchy
  getHierarchy: (constituencyId) =>
    api.get(`/api/panchayats/hierarchy/${constituencyId}`),
};

export default api;

