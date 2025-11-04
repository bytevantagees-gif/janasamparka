import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'http://192.168.29.35:8000/api';

// Helper function to make fetch requests
const fetchAPI = async (endpoint, options = {}) => {
  const token = await AsyncStorage.getItem('token');
  
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  if (options.headers) {
    Object.assign(headers, options.headers);
  }
  
  const config = {
    ...options,
    headers: headers,
  };

  console.log('Fetch Request:', `${API_URL}${endpoint}`, config);

  try {
    const response = await fetch(`${API_URL}${endpoint}`, config);
    console.log('Fetch Response Status:', response.status);
    console.log('Fetch Response Headers:', response.headers);
    
    const responseText = await response.text();
    console.log('Fetch Response Text (first 500 chars):', responseText.substring(0, 500));
    
    let data;
    try {
      data = JSON.parse(responseText);
      console.log('Fetch Response Data:', data);
    } catch (parseError) {
      console.error('JSON Parse Error. Response was:', responseText.substring(0, 1000));
      throw new Error(`Server returned non-JSON response: ${responseText.substring(0, 200)}`);
    }
    
    if (!response.ok) {
      throw {
        response: {
          status: response.status,
          data: data,
        },
      };
    }
    
    return { data };
  } catch (error) {
    console.error('Fetch Error:', error);
    throw error;
  }
};

// Auth API
export const authAPI = {
  requestOTP: (phone) => 
    fetchAPI('/auth/request-otp', {
      method: 'POST',
      body: JSON.stringify({ phone }),
    }),
  verifyOTP: (phone, otp) => 
    fetchAPI('/auth/verify-otp', {
      method: 'POST',
      body: JSON.stringify({ phone, otp }),
    }),
};

// Complaints API
export const complaintsAPI = {
  getAll: (filters) => {
    const params = new URLSearchParams(filters).toString();
    return fetchAPI(`/complaints${params ? `?${params}` : ''}`);
  },
  getById: (id) => fetchAPI(`/complaints/${id}`),
  create: async (data) => {
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
    
    const token = await AsyncStorage.getItem('token');
    
    return fetch(`${API_URL}/complaints`, {
      method: 'POST',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: formData,
    }).then(res => res.json()).then(data => ({ data }));
  },
  updateStatus: (id, status, comment) => 
    fetchAPI(`/complaints/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status, comment }),
    }),
  addComment: (id, comment) => 
    fetchAPI(`/complaints/${id}/comments`, {
      method: 'POST',
      body: JSON.stringify({ comment }),
    }),
};

// Constituencies API
export const constituenciesAPI = {
  getAll: () => fetchAPI('/constituencies'),
  getById: (id) => fetchAPI(`/constituencies/${id}`),
};

// Wards API
export const wardsAPI = {
  getAll: () => fetchAPI('/wards'),
  getByConstituency: (constituencyId) => 
    fetchAPI(`/wards?constituency_id=${constituencyId}`),
};

// Departments API
export const departmentsAPI = {
  getAll: () => fetchAPI('/departments'),
  getById: (id) => fetchAPI(`/departments/${id}`),
};

// User API
export const userAPI = {
  getProfile: () => fetchAPI('/users/me'),
  updateProfile: (data) => 
    fetchAPI('/users/me', {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
};

export default { authAPI, complaintsAPI, constituenciesAPI, wardsAPI, departmentsAPI, userAPI };
