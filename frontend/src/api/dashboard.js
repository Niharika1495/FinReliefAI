import api from './axios';

export const dashboardApi = {
  getOverview: () => api.get('/dashboard/overview'),
  getCharts: () => api.get('/dashboard/charts'),
  getFinancialSummary: () => api.get('/dashboard/financial-summary'),
  getLoanAnalytics: () => api.get('/dashboard/loan-analytics'),
  getSettlementAnalytics: () => api.get('/dashboard/settlement-analytics'),
  getAIAnalytics: () => api.get('/dashboard/ai-analytics'),
};
