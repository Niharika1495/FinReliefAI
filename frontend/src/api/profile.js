import api from './axios';

export const profileApi = {
  getProfile: () => api.get('/financial-profile'),
  createProfile: (data) => api.post('/financial-profile', data),
  updateProfile: (data) => api.put('/financial-profile', data),
};
