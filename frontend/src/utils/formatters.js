export const formatCurrency = (value) => {
  if (value == null || isNaN(value)) return '—';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(value);
};

/** Percentage formatter */
export const formatPercent = (value, decimals = 1) => {
  if (value == null || isNaN(value)) return '—';
  return `${Number(value).toFixed(decimals)}%`;
};

/** Date formatter */
export const formatDate = (dateStr, opts = {}) => {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  if (isNaN(d)) return '—';
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...opts,
  });
};

/** Relative time formatter */
export const formatRelativeTime = (dateStr) => {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  const now = new Date();
  const diff = now - d;
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 7) return formatDate(dateStr);
  if (days > 0) return `${days}d ago`;
  if (hours > 0) return `${hours}h ago`;
  if (minutes > 0) return `${minutes}m ago`;
  return 'just now';
};

/** Score color by value */
export const getScoreColor = (score) => {
  if (score >= 80) return 'text-emerald-500';
  if (score >= 60) return 'text-teal-500';
  if (score >= 40) return 'text-amber-500';
  return 'text-red-500';
};

/** Score label */
export const getScoreLabel = (score) => {
  if (score >= 80) return 'Excellent';
  if (score >= 60) return 'Good';
  if (score >= 40) return 'Fair';
  return 'Poor';
};

/** Risk level color */
export const getRiskColor = (level) => {
  switch (level?.toUpperCase()) {
    case 'LOW': return 'text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 dark:text-emerald-400';
    case 'MEDIUM': return 'text-amber-600 bg-amber-50 dark:bg-amber-900/20 dark:text-amber-400';
    case 'HIGH': return 'text-orange-600 bg-orange-50 dark:bg-orange-900/20 dark:text-orange-400';
    case 'CRITICAL': return 'text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400';
    default: return 'text-surface-500 bg-surface-100 dark:bg-surface-700';
  }
};

/** Settlement eligibility color */
export const getEligibilityColor = (eligibility) => {
  switch (eligibility?.toUpperCase()) {
    case 'ELIGIBLE': return 'text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 dark:text-emerald-400';
    case 'PARTIALLY_ELIGIBLE': return 'text-amber-600 bg-amber-50 dark:bg-amber-900/20 dark:text-amber-400';
    case 'NOT_ELIGIBLE': return 'text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400';
    default: return 'text-surface-500 bg-surface-100 dark:bg-surface-700';
  }
};

/** Difficulty color */
export const getDifficultyColor = (difficulty) => {
  switch (difficulty?.toUpperCase()) {
    case 'LOW': return 'text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 dark:text-emerald-400';
    case 'MEDIUM': return 'text-amber-600 bg-amber-50 dark:bg-amber-900/20 dark:text-amber-400';
    case 'HIGH': return 'text-orange-600 bg-orange-50 dark:bg-orange-900/20 dark:text-orange-400';
    case 'VERY_HIGH': return 'text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400';
    default: return 'text-surface-500 bg-surface-100 dark:bg-surface-700';
  }
};

/** Loan status color */
export const getLoanStatusColor = (status) => {
  switch (status?.toUpperCase()) {
    case 'ACTIVE': return 'text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 dark:text-emerald-400';
    case 'SETTLED': return 'text-teal-600 bg-teal-50 dark:bg-teal-900/20 dark:text-teal-400';
    case 'CLOSED': return 'text-surface-500 bg-surface-100 dark:bg-surface-700/50';
    case 'DEFAULTED': return 'text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400';
    default: return 'text-surface-500 bg-surface-100 dark:bg-surface-700';
  }
};

/** Truncate text */
export const truncate = (str, maxLength = 50) => {
  if (!str) return '';
  return str.length > maxLength ? `${str.slice(0, maxLength)}…` : str;
};
