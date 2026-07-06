import api from './axios';

export const loansApi = {
  getLoans: (params) => api.get('/loans', { params }),
  getLoan: (id) => api.get(`/loans/${id}`),
  createLoan: (data) => api.post('/loans', data),
  updateLoan: (id, data) => api.put(`/loans/${id}`, data),
  deleteLoan: (id) => api.delete(`/loans/${id}`),
};
