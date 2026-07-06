import { useState, useEffect, useCallback } from 'react';
import { loansApi } from '@/api/loans';
import toast from 'react-hot-toast';

export function useLoans() {
  const [loans, setLoans] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const fetchLoans = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = {};
      if (search) params.search = search;
      if (filterType) params.loan_type = filterType;
      if (filterStatus) params.status = filterStatus;
      const res = await loansApi.getLoans(params);
      const rawData = res.data?.data || res.data;
      if (Array.isArray(rawData)) {
        setLoans(rawData);
      } else if (rawData && Array.isArray(rawData.items)) {
        setLoans(rawData.items);
      } else {
        setLoans([]);
      }
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to load loans');
    } finally {
      setIsLoading(false);
    }
  }, [search, filterType, filterStatus]);

  useEffect(() => {
    fetchLoans();
  }, [fetchLoans]);

  const deleteLoan = async (id) => {
    try {
      await loansApi.deleteLoan(id);
      toast.success('Loan deleted successfully');
      fetchLoans();
    } catch {
      toast.error('Failed to delete loan');
    }
  };

  // Pagination
  const totalPages = Math.ceil(loans.length / pageSize);
  const paginated = loans.slice((page - 1) * pageSize, page * pageSize);

  return {
    loans: paginated,
    allLoans: loans,
    isLoading,
    error,
    search,
    setSearch,
    filterType,
    setFilterType,
    filterStatus,
    setFilterStatus,
    page,
    setPage,
    totalPages,
    refetch: fetchLoans,
    deleteLoan,
  };
}
