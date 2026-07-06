import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, CreditCard, Pencil, Trash2, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';
import { loansApi } from '@/api/loans';
import { settlementApi } from '@/api/settlement';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader } from '@/components/ui/Card';
import { Modal } from '@/components/ui/Modal';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { SkeletonCard } from '@/components/ui/Skeleton';
import { LoanForm } from './LoanForm';
import { formatCurrency, formatPercent, formatDate, getLoanStatusColor } from '@/utils/formatters';
import { LOAN_TYPES } from '@/utils/constants';

const TYPE_LABELS = Object.fromEntries(LOAN_TYPES.map((t) => [t.value, t.label]));
const statusVariant = { ACTIVE: 'success', SETTLED: 'teal', CLOSED: 'default', DEFAULTED: 'danger' };
const eligibilityVariant = { ELIGIBLE: 'success', PARTIALLY_ELIGIBLE: 'warning', NOT_ELIGIBLE: 'danger' };

export default function LoanDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loan, setLoan] = useState(null);
  const [settlement, setSettlement] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const fetch = async () => {
      setIsLoading(true);
      try {
        const [loanRes, settlRes] = await Promise.allSettled([
          loansApi.getLoan(id),
          settlementApi.getByLoan(id),
        ]);
        if (loanRes.status === 'fulfilled') {
          const d = loanRes.value.data;
          setLoan(d.data || d);
        }
        if (settlRes.status === 'fulfilled') {
          const d = settlRes.value.data;
          setSettlement(d.data || d);
        }
      } catch {
        toast.error('Failed to load loan details');
      } finally {
        setIsLoading(false);
      }
    };
    fetch();
  }, [id]);

  const handleEdit = async (data) => {
    setIsSubmitting(true);
    try {
      const res = await loansApi.updateLoan(id, data);
      const d = res.data;
      setLoan(d.data || d);
      toast.success('Loan updated');
      setEditOpen(false);
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to update loan');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await loansApi.deleteLoan(id);
      toast.success('Loan deleted');
      navigate('/loans');
    } catch {
      toast.error('Failed to delete loan');
    } finally {
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <SkeletonCard />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <SkeletonCard /><SkeletonCard />
        </div>
      </div>
    );
  }

  if (!loan) {
    return (
      <div className="flex flex-col items-center gap-4 py-20">
        <AlertTriangle size={40} className="text-amber-500" />
        <p className="text-surface-500">Loan not found</p>
        <Link to="/loans"><Button variant="outline">Back to Loans</Button></Link>
      </div>
    );
  }

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/loans">
            <Button variant="ghost" size="icon" title="Back"><ArrowLeft size={16} /></Button>
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-surface-900 dark:text-surface-100">{loan.lender_name}</h1>
              <Badge variant={statusVariant[loan.loan_status] || 'default'}>{loan.loan_status}</Badge>
            </div>
            <p className="text-sm text-surface-500 dark:text-surface-400">
              {TYPE_LABELS[loan.loan_type] || loan.loan_type} · Added {formatDate(loan.created_at)}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => setEditOpen(true)} id="edit-loan-button">
            <Pencil size={14} /> Edit
          </Button>
          <Button variant="danger" size="sm" onClick={() => setDeleteOpen(true)} id="delete-loan-button">
            <Trash2 size={14} /> Delete
          </Button>
        </div>
      </div>

      {/* Loan Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card padding="p-5">
          <CardHeader title="Loan Details" icon={CreditCard} />
          <dl className="space-y-3">
            {[
              { label: 'Outstanding Amount', value: formatCurrency(loan.outstanding_amount) },
              { label: 'Monthly EMI', value: formatCurrency(loan.emi) },
              { label: 'Interest Rate', value: formatPercent(loan.interest_rate) },
              { label: 'Overdue Months', value: loan.overdue_months > 0 ? `${loan.overdue_months} months` : 'None' },
              { label: 'Last Updated', value: formatDate(loan.updated_at) },
            ].map(({ label, value }) => (
              <div key={label} className="flex justify-between items-center py-1.5 border-b border-surface-100 dark:border-surface-700/50 last:border-0">
                <dt className="text-sm text-surface-500 dark:text-surface-400">{label}</dt>
                <dd className="text-sm font-semibold text-surface-800 dark:text-surface-200">{value}</dd>
              </div>
            ))}
          </dl>
        </Card>

        {/* Settlement recommendation */}
        {settlement ? (
          <Card padding="p-5">
            <CardHeader
              title="Settlement Recommendation"
              action={
                <Badge variant={eligibilityVariant[settlement.eligibility] || 'default'}>
                  {settlement.eligibility?.replace('_', ' ')}
                </Badge>
              }
            />
            <dl className="space-y-3">
              {[
                { label: 'Settlement %', value: formatPercent(settlement.settlement_percentage) },
                { label: 'Recommended Amount', value: formatCurrency(settlement.recommended_amount) },
                { label: 'Estimated Savings', value: formatCurrency(settlement.estimated_savings) },
                { label: 'Payoff Timeline', value: `${settlement.estimated_payoff_months} months` },
                { label: 'Priority Score', value: `${settlement.priority_score?.toFixed(1)}/100` },
                { label: 'Negotiation Difficulty', value: settlement.negotiation_difficulty },
              ].map(({ label, value }) => (
                <div key={label} className="flex justify-between items-center py-1.5 border-b border-surface-100 dark:border-surface-700/50 last:border-0">
                  <dt className="text-sm text-surface-500 dark:text-surface-400">{label}</dt>
                  <dd className="text-sm font-semibold text-surface-800 dark:text-surface-200">{value}</dd>
                </div>
              ))}
            </dl>
            <div className="mt-4">
              <Link to="/settlement">
                <Button variant="outline" size="sm" className="w-full">View Full Settlement Plan</Button>
              </Link>
            </div>
          </Card>
        ) : (
          <Card padding="p-5">
            <CardHeader title="Settlement Recommendation" />
            <div className="flex flex-col items-center justify-center h-32 gap-2">
              <p className="text-sm text-surface-400">No settlement data available for this loan.</p>
              <Link to="/settlement">
                <Button variant="outline" size="sm">Generate Settlement Plan</Button>
              </Link>
            </div>
          </Card>
        )}
      </div>

      <Modal isOpen={editOpen} onClose={() => setEditOpen(false)} title="Edit Loan" size="md">
        <LoanForm initialValues={loan} onSubmit={handleEdit} isLoading={isSubmitting} onCancel={() => setEditOpen(false)} />
      </Modal>

      <ConfirmDialog
        isOpen={deleteOpen}
        onClose={() => setDeleteOpen(false)}
        onConfirm={handleDelete}
        isLoading={isDeleting}
        title="Delete Loan"
        message={`Delete loan from "${loan.lender_name}"? This action is irreversible.`}
        confirmLabel="Delete"
        variant="danger"
      />
    </div>
  );
}
