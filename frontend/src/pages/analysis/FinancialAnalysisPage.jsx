import { useState, useEffect } from 'react';
import { financialApi } from '@/api/financial';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader } from '@/components/ui/Card';
import { StatCard } from '@/components/ui/StatCard';
import { SkeletonCard } from '@/components/ui/Skeleton';
import { formatCurrency, formatPercent, getRiskColor } from '@/utils/formatters';
import { RefreshCw, TrendingUp, Activity, AlertTriangle, CheckCircle, DollarSign, BarChart3 } from 'lucide-react';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';

const riskVariant = { LOW: 'success', MEDIUM: 'warning', HIGH: 'orange', CRITICAL: 'danger' };
const capacityVariant = { GOOD: 'success', MODERATE: 'teal', WEAK: 'warning', VERY_WEAK: 'danger' };

function HealthGauge({ score }) {
  const pct = Math.min(100, Math.max(0, score || 0));
  const circumference = 2 * Math.PI * 60;
  const offset = circumference - (pct / 100) * circumference;
  const color = pct >= 80 ? '#10b981' : pct >= 60 ? '#14B8A6' : pct >= 40 ? '#f59e0b' : '#ef4444';
  const label = pct >= 80 ? 'Excellent' : pct >= 60 ? 'Good' : pct >= 40 ? 'Fair' : 'Poor';

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width="160" height="160" viewBox="0 0 130 130">
        <circle cx="65" cy="65" r="60" fill="none" stroke="currentColor" strokeWidth="10"
          className="text-surface-200 dark:text-surface-700" />
        <circle cx="65" cy="65" r="60" fill="none" stroke={color} strokeWidth="10"
          strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round" transform="rotate(-90 65 65)"
          style={{ transition: 'stroke-dashoffset 1.2s ease' }}
        />
        <text x="65" y="60" textAnchor="middle" fontSize="28" fontWeight="bold" fill={color}>{Math.round(pct)}</text>
        <text x="65" y="76" textAnchor="middle" fontSize="11" fill="#64748b" fontWeight="500">/ 100</text>
        <text x="65" y="91" textAnchor="middle" fontSize="11" fill={color} fontWeight="600">{label}</text>
      </svg>
    </div>
  );
}

export default function FinancialAnalysisPage() {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRecalculating, setIsRecalculating] = useState(false);

  const fetchAnalysis = async () => {
    setIsLoading(true);
    try {
      const res = await financialApi.getAnalysis();
      const d = res.data;
      setData(d.data || d);
    } catch (err) {
      toast.error('Failed to load financial analysis');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRecalculate = async () => {
    setIsRecalculating(true);
    try {
      const res = await financialApi.recalculate();
      const d = res.data;
      setData(d.data || d);
      toast.success('Analysis recalculated!');
    } catch {
      toast.error('Recalculation failed');
    } finally {
      setIsRecalculating(false);
    }
  };

  useEffect(() => { fetchAnalysis(); }, []);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array(4).fill(0).map((_, i) => <SkeletonCard key={i} />)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <SkeletonCard /><SkeletonCard />
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex flex-col items-center gap-4 py-20">
        <AlertTriangle size={40} className="text-amber-500" />
        <p className="text-surface-500">No analysis data available. Add some loans first.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-surface-900 dark:text-surface-100">Financial Analysis</h1>
          <p className="text-sm text-surface-500 dark:text-surface-400">Rule-based health analysis across all your loans</p>
        </div>
        <Button onClick={handleRecalculate} isLoading={isRecalculating} variant="outline" size="sm" id="recalculate-button">
          <RefreshCw size={14} /> Recalculate
        </Button>
      </div>

      {/* Score + badges */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card padding="p-6" className="flex flex-col items-center">
          <p className="text-sm font-semibold text-surface-600 dark:text-surface-400 mb-4">Financial Health Score</p>
          <HealthGauge score={data.financial_health_score} />
          <div className="flex gap-3 mt-4">
            <Badge variant={riskVariant[data.risk_level] || 'default'}>
              Risk: {data.risk_level}
            </Badge>
            <Badge variant={capacityVariant[data.repayment_capacity] || 'default'}>
              {data.repayment_capacity?.replace('_', ' ')}
            </Badge>
          </div>
        </Card>

        <div className="lg:col-span-2 grid grid-cols-2 gap-4 content-start">
          <StatCard title="Monthly Surplus" value={formatCurrency(data.monthly_surplus)}
            icon={DollarSign} color={data.monthly_surplus >= 0 ? 'emerald' : 'red'} />
          <StatCard title="DTI Ratio" value={formatPercent(data.dti_ratio)}
            icon={BarChart3} color={data.dti_ratio < 35 ? 'emerald' : data.dti_ratio < 50 ? 'amber' : 'red'}
            subtitle="Debt-to-Income" />
          <StatCard title="EMI Ratio" value={formatPercent(data.emi_ratio)}
            icon={Activity} color={data.emi_ratio < 30 ? 'emerald' : data.emi_ratio < 45 ? 'amber' : 'red'}
            subtitle="EMI-to-Income" />
          <StatCard title="Avg. Interest Rate" value={formatPercent(data.average_interest_rate)}
            icon={TrendingUp} color="primary"
            subtitle={`Max: ${formatPercent(data.highest_interest_rate)}`} />
        </div>
      </div>

      {/* Detailed metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card padding="p-5">
          <CardHeader title="Loan Portfolio Overview" />
          <dl className="space-y-3">
            {[
              { label: 'Active Loans', value: data.total_active_loans },
              { label: 'Total Outstanding', value: formatCurrency(data.total_outstanding) },
              { label: 'Total Monthly EMI', value: formatCurrency(data.total_monthly_emi) },
              { label: 'Monthly Income', value: formatCurrency(data.monthly_income) },
              { label: 'Monthly Expenses', value: formatCurrency(data.monthly_expenses) },
              { label: 'Max Overdue Months', value: data.maximum_overdue_months > 0 ? `${data.maximum_overdue_months} months` : 'None' },
            ].map(({ label, value }) => (
              <div key={label} className="flex justify-between items-center py-1.5 border-b border-surface-100 dark:border-surface-700/50 last:border-0">
                <dt className="text-sm text-surface-500 dark:text-surface-400">{label}</dt>
                <dd className="text-sm font-semibold text-surface-800 dark:text-surface-200">{value}</dd>
              </div>
            ))}
          </dl>
        </Card>

        <Card padding="p-5">
          <CardHeader title="AI Recommendations" />
          {data.recommendations?.length > 0 ? (
            <ul className="space-y-3">
              {data.recommendations.map((rec, i) => (
                <motion.li
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="flex gap-3 items-start"
                >
                  <CheckCircle size={16} className="text-teal-500 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-surface-700 dark:text-surface-300">{rec}</p>
                </motion.li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-surface-400 mt-4">No recommendations at this time.</p>
          )}
        </Card>
      </div>
    </div>
  );
}
