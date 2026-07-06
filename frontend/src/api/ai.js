import api from './axios';

export const aiApi = {
  generateNegotiationStrategy: (loanId, customHardship, geminiKey) => {
    const headers = geminiKey ? { 'x-gemini-api-key': geminiKey } : {};
    return api.post('/ai/negotiation-strategy', {
      loan_id: loanId,
      custom_hardship_description: customHardship || null
    }, { headers });
  },
  generateSettlementLetter: (loanId, customHardship, geminiKey) => {
    const headers = geminiKey ? { 'x-gemini-api-key': geminiKey } : {};
    return api.post('/ai/settlement-letter', {
      loan_id: loanId,
      custom_hardship_description: customHardship || null
    }, { headers });
  },
  generateNegotiationEmail: (loanId, customHardship, geminiKey) => {
    const headers = geminiKey ? { 'x-gemini-api-key': geminiKey } : {};
    return api.post('/ai/negotiation-email', {
      loan_id: loanId,
      custom_hardship_description: customHardship || null
    }, { headers });
  },
  generateFinancialExplanation: (geminiKey) => {
    const headers = geminiKey ? { 'x-gemini-api-key': geminiKey } : {};
    return api.post('/ai/financial-explanation', {}, { headers });
  },
  getHistory: () => api.get('/ai/history'),
  getHistoryDetail: (id) => api.get(`/ai/history/${id}`),
};
