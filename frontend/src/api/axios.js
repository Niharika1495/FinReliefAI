import axios from 'axios';
import toast from 'react-hot-toast';
import { API_BASE_URL } from '@/utils/constants';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor — attach JWT token
api.interceptors.request.use(
  (config) => {
    const adminToken = localStorage.getItem('finrelief_admin_token');
    const userToken = localStorage.getItem('finrelief_token');
    const token = config.url.startsWith('/admin') && adminToken ? adminToken : userToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    const message = error?.response?.data?.detail || error?.response?.data?.message || error.message;

    if (status === 401) {
      if (window.location.pathname.startsWith('/admin')) {
        localStorage.removeItem('finrelief_admin_token');
        if (window.location.pathname !== '/admin/login') {
          toast.error('Admin session expired. Please log in again.');
          window.location.href = '/admin/login';
        }
      } else {
        // Auto-logout
        localStorage.removeItem('finrelief_token');
        localStorage.removeItem('finrelief_user');
        // Redirect to login if not already there
        if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
          toast.error('Session expired. Please log in again.');
          window.location.href = '/login';
        }
      }
    } else if (status === 403) {
      toast.error('You do not have permission to perform this action.');
    } else if (status === 422) {
      // Validation errors — let form handlers deal with them
    } else if (status >= 500) {
      toast.error('Server error. Please try again later.');
    }

    return Promise.reject(error);
  }
);

export default api;
