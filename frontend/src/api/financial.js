import api from './axios';

export const financialApi = {
  getAnalysis: () => api.get('/financial-analysis'),
  recalculate: () => api.post('/financial-analysis/recalculate'),
};
