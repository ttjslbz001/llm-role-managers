import axios, { AxiosRequestConfig } from 'axios';

const API_BASE_URL = '/api'; // Using proxy in package.json to redirect to backend

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for API calls
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const message = 
      error.response?.data?.message || 
      'An unexpected error occurred';
    console.error('API Error:', message);
    return Promise.reject(error);
  }
);

export const setAuthToken = (token: string) => {
  apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
};

export const clearAuthToken = () => {
  delete apiClient.defaults.headers.common['Authorization'];
};

export default apiClient; 