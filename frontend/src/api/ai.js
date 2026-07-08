import api from './axios';

// Helper to recursively replace all literal '$' with '₹' in string values
const replaceDollars = (obj) => {
  if (typeof obj === 'string') {
    return obj.replace(/\$/g, '₹');
  }
  if (Array.isArray(obj)) {
    return obj.map(replaceDollars);
  }
  if (obj !== null && typeof obj === 'object') {
    const newObj = {};
    for (const key in obj) {
      newObj[key] = replaceDollars(obj[key]);
    }
    return newObj;
  }
  return obj;
};

export const aiApi = {
  generateNegotiationStrategy: async (loanId, customHardship, geminiKey) => {
    const headers = geminiKey ? { 'x-gemini-api-key': geminiKey } : {};
    const res = await api.post('/ai/negotiation-strategy', {
      loan_id: loanId,
      custom_hardship_description: customHardship || null
    }, { headers });
    res.data = replaceDollars(res.data);
    return res;
  },
  generateSettlementLetter: async (loanId, customHardship, geminiKey) => {
    const headers = geminiKey ? { 'x-gemini-api-key': geminiKey } : {};
    const res = await api.post('/ai/settlement-letter', {
      loan_id: loanId,
      custom_hardship_description: customHardship || null
    }, { headers });
    res.data = replaceDollars(res.data);
    return res;
  },
  generateNegotiationEmail: async (loanId, customHardship, geminiKey) => {
    const headers = geminiKey ? { 'x-gemini-api-key': geminiKey } : {};
    const res = await api.post('/ai/negotiation-email', {
      loan_id: loanId,
      custom_hardship_description: customHardship || null
    }, { headers });
    res.data = replaceDollars(res.data);
    return res;
  },
  generateFinancialExplanation: async (geminiKey) => {
    const headers = geminiKey ? { 'x-gemini-api-key': geminiKey } : {};
    const res = await api.post('/ai/financial-explanation', {}, { headers });
    res.data = replaceDollars(res.data);
    return res;
  },
  getHistory: async () => {
    const res = await api.get('/ai/history');
    res.data = replaceDollars(res.data);
    return res;
  },
  getHistoryDetail: async (id) => {
    const res = await api.get(`/ai/history/${id}`);
    res.data = replaceDollars(res.data);
    return res;
  },
};
