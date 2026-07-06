import api from './axios';

export const reportsApi = {
  downloadPdf: (reportType) => api.get(`/reports/${reportType}/pdf`, { responseType: 'blob' }),
  downloadCsv: (reportType) => api.get(`/reports/${reportType}/csv`, { responseType: 'blob' }),
};
