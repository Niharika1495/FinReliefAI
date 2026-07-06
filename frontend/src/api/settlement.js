import api from './axios';

export const settlementApi = {
  getSettlements: () => api.get('/settlement'),
  getSummary: () => api.get('/settlement/summary'),
  getByLoan: (loanId) => api.get(`/settlement/${loanId}`),
  recalculate: () => api.post('/settlement/recalculate'),
};
