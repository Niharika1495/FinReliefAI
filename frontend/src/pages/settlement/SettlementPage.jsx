import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { settlementApi } from '@/api/settlement';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader } from '@/components/ui/Card';
import { StatCard } from '@/components/ui/StatCard';
import { SkeletonCard } from '@/components/ui/Skeleton';
import { formatCurrency, formatPercent } from '@/utils/formatters';
import { RefreshCw, Handshake, DollarSign, TrendingDown, CheckCircle, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

const eligibilityVariant = { ELIGIBLE: 'success', PARTIALLY_ELIGIBLE: 'warning', NOT_ELIGIBLE: 'danger' };
const difficultyVariant = { LOW: 'success', MEDIUM: 'warning', HIGH: 'orange', VERY_HIGH: 'danger' };

export default function SettlementPage() {
  const [settlements, setSettlements] = useState([]);
  const [summary, setSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRecalculating, setIsRecalculating] = useState(false);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [settRes, sumRes] = await Promise.allSettled([
        settlementApi.getSettlements(),
        settlementApi.getSummary(),
      ]);
      if (settRes.status === 'fulfilled') {
        const d = settRes.value.data;
        setSettlements(Array.isArray(d) ? d : (d.data || []));
      }
      if (sumRes.status === 'fulfilled') {
        const d = sumRes.value.data;
        setSummary(d.data || d);
      }
    } catch {
      toast.error('Failed to load settlement data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRecalculate = async () => {
    setIsRecalculating(true);
    try {
      const res = await settlementApi.recalculate();
      const d = res.data;
      setSettlements(Array.isArray(d) ? d : (d.data || []));
      // Refresh summary too
      const sumRes = await settlementApi.getSummary();
      const sd = sumRes.data;
      setSummary(sd.data || sd);
      toast.success('Settlement recommendations updated!');
    } catch {
      toast.error('Recalculation failed');
    } finally {
      setIsRecalculating(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array(4).fill(0).map((_, i) => <SkeletonCard key={i} />)}
        </div>
        <SkeletonCard />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-surface-900 dark:text-surface-100">Settlement Plan</h1>
          <p className="text-sm text-surface-500 dark:text-surface-400">AI-powered debt settlement recommendations</p>
        </div>
        <Button onClick={handleRecalculate} isLoading={isRecalculating} variant="outline" size="sm" id="settlement-recalculate">
          <RefreshCw size={14} /> Recalculate
        </Button>
      </div>

      {/* Summary Stats */}
      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Eligible Loans"
            value={`${summary.eligible_loans} loans`}
            icon={Handshake}
            color="emerald"
          />
          <StatCard
            title="Avg. Settlement %"
            value={formatPercent(summary.average_settlement_percentage)}
            icon={TrendingDown}
            color="primary"
          />
          <StatCard
            title="Total Est. Savings"
            value={formatCurrency(summary.total_savings)}
            icon={DollarSign}
            color="teal"
            subtitle="If settled today"
          />
          <StatCard
            title="Total Settlement"
            value={formatCurrency(summary.total_recommended_settlement)}
            icon={DollarSign}
            color="amber"
            subtitle="Recommended offer"
          />
        </div>
      )}

      {/* Recommendations list */}
      {summary?.recommendations?.length > 0 && (
        <Card padding="p-5">
          <CardHeader title="Action Plan" subtitle="Prioritized settlement recommendations" />
          <ul className="space-y-2">
            {summary.recommendations.map((rec, i) => (
              <li key={i} className="flex items-start gap-2.5">
                <CheckCircle size={16} className="text-teal-500 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-surface-700 dark:text-surface-300">{rec}</p>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Per-loan settlement cards */}
      {settlements.length === 0 ? (
        <div className="flex flex-col items-center gap-4 py-16">
          <Handshake size={40} className="text-surface-300 dark:text-surface-600" />
          <p className="text-sm text-surface-500">No settlement data. Add active loans first.</p>
          <Link to="/loans">
            <Button variant="outline" size="sm">Go to Loans</Button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {settlements.map((s, i) => (
            <motion.div
              key={s.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06 }}
              className="bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700/60 rounded-2xl p-5 shadow-card"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className="h-9 w-9 rounded-xl bg-primary-50 dark:bg-primary-900/20 flex items-center justify-center">
                    <Handshake size={18} className="text-primary-500" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-surface-900 dark:text-surface-100">
                      Loan #{s.loan_id}
                    </p>
                    <p className="text-xs text-surface-400">Settlement Recommendation</p>
                  </div>
                </div>
                <Badge variant={eligibilityVariant[s.eligibility] || 'default'}>
                  {s.eligibility?.replace('_', ' ')}
                </Badge>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: 'Settlement %', value: formatPercent(s.settlement_percentage) },
                  { label: 'Offer Amount', value: formatCurrency(s.recommended_amount) },
                  { label: 'Est. Savings', value: formatCurrency(s.estimated_savings) },
                  { label: 'Payoff', value: `${s.estimated_payoff_months} mo.` },
                  { label: 'Priority', value: `${s.priority_score?.toFixed(1)}/100` },
                  { label: 'Difficulty', value: (
                    <Badge variant={difficultyVariant[s.negotiation_difficulty] || 'default'}>
                      {s.negotiation_difficulty}
                    </Badge>
                  )},
                ].map(({ label, value }) => (
                  <div key={label} className="bg-surface-50 dark:bg-surface-700/40 rounded-xl p-2.5">
                    <p className="text-[10px] text-surface-400 dark:text-surface-500 font-medium uppercase tracking-wide">{label}</p>
                    <div className="text-sm font-semibold text-surface-800 dark:text-surface-200 mt-0.5">{value}</div>
                  </div>
                ))}
              </div>

              <div className="mt-3">
                <Link to={`/loans/${s.loan_id}`}>
                  <Button variant="ghost" size="sm" className="w-full text-primary-500">View Loan Details</Button>
                </Link>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
