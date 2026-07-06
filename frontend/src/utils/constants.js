export const API_BASE_URL = '/api/v1';

export const ROUTES = {
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  LOANS: '/loans',
  LOAN_DETAIL: '/loans/:id',
  ANALYSIS: '/analysis',
  SETTLEMENT: '/settlement',
  PROFILE: '/profile',
  NOTIFICATIONS: '/notifications',
};

export const LOAN_TYPES = [
  { value: 'CREDIT_CARD', label: 'Credit Card' },
  { value: 'PERSONAL_LOAN', label: 'Personal Loan' },
  { value: 'HOME_LOAN', label: 'Home Loan' },
  { value: 'AUTO_LOAN', label: 'Auto Loan' },
  { value: 'STUDENT_LOAN', label: 'Student Loan' },
  { value: 'BUSINESS_LOAN', label: 'Business Loan' },
  { value: 'MEDICAL_LOAN', label: 'Medical Loan' },
  { value: 'OTHER', label: 'Other' },
];

export const LOAN_STATUSES = [
  { value: 'ACTIVE', label: 'Active' },
  { value: 'SETTLED', label: 'Settled' },
  { value: 'CLOSED', label: 'Closed' },
  { value: 'DEFAULTED', label: 'Defaulted' },
];

export const QUERY_KEYS = {
  ME: ['auth', 'me'],
  DASHBOARD_OVERVIEW: ['dashboard', 'overview'],
  DASHBOARD_CHARTS: ['dashboard', 'charts'],
  DASHBOARD_FINANCIAL_SUMMARY: ['dashboard', 'financial-summary'],
  DASHBOARD_LOAN_ANALYTICS: ['dashboard', 'loan-analytics'],
  DASHBOARD_SETTLEMENT_ANALYTICS: ['dashboard', 'settlement-analytics'],
  DASHBOARD_AI_ANALYTICS: ['dashboard', 'ai-analytics'],
  LOANS: ['loans'],
  LOAN_DETAIL: (id) => ['loans', id],
  ANALYSIS: ['financial-analysis'],
  SETTLEMENT: ['settlement'],
  SETTLEMENT_SUMMARY: ['settlement', 'summary'],
  PROFILE: ['financial-profile'],
  NOTIFICATIONS: ['notifications'],
};

export const CHART_COLORS = [
  '#7C3AED',
  '#14B8A6',
  '#f59e0b',
  '#ef4444',
  '#3b82f6',
  '#ec4899',
  '#22c55e',
  '#8b5cf6',
];
