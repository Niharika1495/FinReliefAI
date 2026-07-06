import { useState, useEffect, useCallback } from 'react';
import { dashboardApi } from '@/api/dashboard';

export function useDashboard() {
  const [overview, setOverview] = useState(null);
  const [charts, setCharts] = useState(null);
  const [financialSummary, setFinancialSummary] = useState(null);
  const [loanAnalytics, setLoanAnalytics] = useState(null);
  const [settlementAnalytics, setSettlementAnalytics] = useState(null);
  const [aiAnalytics, setAIAnalytics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAll = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [ov, ch, fs, la, sa, ai] = await Promise.allSettled([
        dashboardApi.getOverview(),
        dashboardApi.getCharts(),
        dashboardApi.getFinancialSummary(),
        dashboardApi.getLoanAnalytics(),
        dashboardApi.getSettlementAnalytics(),
        dashboardApi.getAIAnalytics(),
      ]);

      const unwrap = (res) => res.status === 'fulfilled' ? (res.value.data?.data || res.value.data) : null;

      setOverview(unwrap(ov));
      setCharts(unwrap(ch));
      setFinancialSummary(unwrap(fs));
      setLoanAnalytics(unwrap(la));
      setSettlementAnalytics(unwrap(sa));
      setAIAnalytics(unwrap(ai));
    } catch (err) {
      setError('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  return {
    overview,
    charts,
    financialSummary,
    loanAnalytics,
    settlementAnalytics,
    aiAnalytics,
    isLoading,
    error,
    refetch: fetchAll,
  };
}
