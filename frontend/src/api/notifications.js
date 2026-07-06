import api from './axios';

export const notificationsApi = {
  getNotifications: (params) => api.get('/notifications', { params }),
  markRead: (id) => api.put(`/notifications/${id}/read`),
};
