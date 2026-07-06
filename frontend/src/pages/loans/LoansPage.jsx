import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Pencil, Trash2, Eye, ChevronLeft, ChevronRight, AlertTriangle, CreditCard } from 'lucide-react';
import toast from 'react-hot-toast';
import { useLoans } from '@/hooks/useLoans';
import { loansApi } from '@/api/loans';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { SearchBar } from '@/components/ui/SearchBar';
import { Select } from '@/components/ui/Select';
import { Modal } from '@/components/ui/Modal';
import { SkeletonTable } from '@/components/ui/Skeleton';
import { LoanForm } from './LoanForm';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { formatCurrency, formatPercent, formatDate, getLoanStatusColor } from '@/utils/formatters';
import { LOAN_TYPES, LOAN_STATUSES } from '@/utils/constants';
import { cn } from '@/utils/cn';

const TYPE_LABELS = Object.fromEntries(LOAN_TYPES.map((t) => [t.value, t.label]));

const statusVariant = {
  ACTIVE: 'success', SETTLED: 'teal', CLOSED: 'default', DEFAULTED: 'danger',
};

export default function LoansPage() {
  const {
    loans, allLoans, isLoading, error, search, setSearch,
    filterType, setFilterType, filterStatus, setFilterStatus,
    page, setPage, totalPages, refetch, deleteLoan,
  } = useLoans();

  const [showAddModal, setShowAddModal] = useState(false);
  const [editLoan, setEditLoan] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleAddLoan = async (data) => {
    setIsSubmitting(true);
    try {
      await loansApi.createLoan({
        lender_name: data.lender_name,
        loan_type: data.loan_type,
        outstanding_amount: data.outstanding_amount,
        interest_rate: data.interest_rate,
        emi: data.emi,
        overdue_months: data.overdue_months,
      });
      toast.success('Loan added successfully');
      setShowAddModal(false);
      refetch();
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to add loan');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEditLoan = async (data) => {
    setIsSubmitting(true);
    try {
      await loansApi.updateLoan(editLoan.id, {
        lender_name: data.lender_name,
        loan_type: data.loan_type,
        outstanding_amount: data.outstanding_amount,
        interest_rate: data.interest_rate,
        emi: data.emi,
        overdue_months: data.overdue_months,
        loan_status: data.loan_status,
      });
      toast.success('Loan updated');
      setEditLoan(null);
      refetch();
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to update loan');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    await deleteLoan(deleteTarget.id);
    setDeleteTarget(null);
    setIsDeleting(false);
  };

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-surface-900 dark:text-surface-100">Loan Management</h1>
          <p className="text-sm text-surface-500 dark:text-surface-400 mt-0.5">
            {allLoans.length} loan{allLoans.length !== 1 ? 's' : ''} on record
          </p>
        </div>
        <Button onClick={() => setShowAddModal(true)} id="add-loan-button">
          <Plus size={16} /> Add Loan
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <SearchBar
          value={search}
          onChange={setSearch}
          placeholder="Search by lender, type..."
          className="flex-1"
        />
        <Select
          value={filterType}
          onChange={(e) => { setFilterType(e.target.value); setPage(1); }}
          options={LOAN_TYPES}
          placeholder="All Types"
          className="sm:w-44"
        />
        <Select
          value={filterStatus}
          onChange={(e) => { setFilterStatus(e.target.value); setPage(1); }}
          options={LOAN_STATUSES}
          placeholder="All Statuses"
          className="sm:w-40"
        />
      </div>

      {/* Table */}
      <div className="bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700/60 rounded-2xl overflow-hidden shadow-card">
        {isLoading ? (
          <SkeletonTable rows={6} cols={6} />
        ) : error ? (
          <div className="flex flex-col items-center gap-3 py-16">
            <AlertTriangle size={32} className="text-amber-500" />
            <p className="text-sm text-surface-500">{error}</p>
          </div>
        ) : loans.length === 0 ? (
          <div className="flex flex-col items-center gap-3 py-16">
            <CreditCard size={36} className="text-surface-300 dark:text-surface-600" />
            <p className="text-sm font-medium text-surface-500 dark:text-surface-400">No loans found</p>
            <p className="text-xs text-surface-400 dark:text-surface-500">Add your first loan to get started</p>
            <Button onClick={() => setShowAddModal(true)} size="sm" variant="outline">
              <Plus size={14} /> Add Loan
            </Button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Lender</th>
                  <th>Type</th>
                  <th>Outstanding</th>
                  <th>EMI</th>
                  <th>Interest</th>
                  <th>Status</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {loans.map((loan) => (
                  <tr key={loan.id} className="group">
                    <td>
                      <div>
                        <p className="font-medium text-surface-900 dark:text-surface-100">{loan.lender_name}</p>
                        <p className="text-xs text-surface-400 dark:text-surface-500">{formatDate(loan.created_at)}</p>
                      </div>
                    </td>
                    <td className="text-surface-600 dark:text-surface-400">
                      {TYPE_LABELS[loan.loan_type] || loan.loan_type}
                    </td>
                    <td className="font-semibold text-surface-900 dark:text-surface-100">
                      {formatCurrency(loan.outstanding_amount)}
                    </td>
                    <td className="text-surface-600 dark:text-surface-400">
                      {formatCurrency(loan.emi)}
                    </td>
                    <td className="text-surface-600 dark:text-surface-400">
                      {formatPercent(loan.interest_rate)}
                    </td>
                    <td>
                      <Badge variant={statusVariant[loan.loan_status] || 'default'}>
                        {loan.loan_status}
                      </Badge>
                    </td>
                    <td>
                      <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Link to={`/loans/${loan.id}`}>
                          <Button variant="ghost" size="icon" title="View details">
                            <Eye size={14} />
                          </Button>
                        </Link>
                        <Button
                          variant="ghost"
                          size="icon"
                          title="Edit"
                          onClick={() => setEditLoan(loan)}
                        >
                          <Pencil size={14} />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          title="Delete"
                          onClick={() => setDeleteTarget(loan)}
                          className="text-red-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                        >
                          <Trash2 size={14} />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-surface-100 dark:border-surface-700/50">
            <p className="text-xs text-surface-400 dark:text-surface-500">
              Page {page} of {totalPages}
            </p>
            <div className="flex gap-2">
              <Button
                variant="ghost" size="sm"
                disabled={page === 1}
                onClick={() => setPage((p) => p - 1)}
              >
                <ChevronLeft size={16} /> Prev
              </Button>
              <Button
                variant="ghost" size="sm"
                disabled={page === totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next <ChevronRight size={16} />
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Add Loan Modal */}
      <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} title="Add New Loan" size="md">
        <LoanForm onSubmit={handleAddLoan} isLoading={isSubmitting} onCancel={() => setShowAddModal(false)} />
      </Modal>

      {/* Edit Loan Modal */}
      <Modal isOpen={!!editLoan} onClose={() => setEditLoan(null)} title="Edit Loan" size="md">
        <LoanForm
          initialValues={editLoan}
          onSubmit={handleEditLoan}
          isLoading={isSubmitting}
          onCancel={() => setEditLoan(null)}
        />
      </Modal>

      {/* Delete Confirm */}
      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        isLoading={isDeleting}
        title="Delete Loan"
        message={`Are you sure you want to delete the loan from "${deleteTarget?.lender_name}"? This action cannot be undone.`}
        confirmLabel="Delete"
        variant="danger"
      />
    </div>
  );
}
