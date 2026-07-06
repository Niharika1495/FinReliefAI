import api from './axios';

export const adminApi = {
  login: (username, password) => api.post('/admin/login', { username, password }),
  getDashboard: () => api.get('/admin/dashboard'),
  getUsers: () => api.get('/admin/users'),
  getLoans: () => api.get('/admin/loans'),
  getAuditLogs: () => api.get('/admin/audit-logs'),
};
