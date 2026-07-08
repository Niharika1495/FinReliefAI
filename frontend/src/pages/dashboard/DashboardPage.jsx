import { useDashboard } from '@/hooks/useDashboard';
import { StatCard } from '@/components/ui/StatCard';
import { Card, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { SkeletonCard } from '@/components/ui/Skeleton';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/context/AuthContext';
import { formatCurrency, formatPercent, formatRelativeTime, getRiskColor } from '@/utils/formatters';
import { CHART_COLORS } from '@/utils/constants';
import {
  IndianRupee, CreditCard, TrendingUp, Activity,
  RefreshCw, Brain, Handshake, AlertTriangle
} from 'lucide-react';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

function ScoreGauge({ score }) {
  const pct = Math.min(100, Math.max(0, score || 0));
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (pct / 100) * circumference;
  const color = pct >= 80 ? '#10b981' : pct >= 60 ? '#14B8A6' : pct >= 40 ? '#f59e0b' : '#ef4444';

  return (
    <div className="flex flex-col items-center justify-center py-2">
      <svg width="120" height="120" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="45" fill="none" stroke="currentColor" strokeWidth="8"
          className="text-surface-200 dark:text-surface-700" />
        <circle cx="50" cy="50" r="45" fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round" transform="rotate(-90 50 50)"
          style={{ transition: 'stroke-dashoffset 1s ease' }}
        />
        <text x="50" y="53" textAnchor="middle" fontSize="20" fontWeight="bold"
          fill="currentColor" className="text-surface-900 dark:text-surface-100">
          {Math.round(pct)}
        </text>
        <text x="50" y="66" textAnchor="middle" fontSize="8" fill="#64748b">SCORE</text>
      </svg>
    </div>
  );
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-xl px-3 py-2 shadow-lg text-xs">
      {label && <p className="font-medium text-surface-700 dark:text-surface-300 mb-1">{label}</p>}
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }} className="font-medium">
          {p.name}: {typeof p.value === 'number' && p.value > 100
            ? formatCurrency(p.value)
            : typeof p.value === 'number'
            ? `${p.value.toFixed(1)}%`
            : p.value}
        </p>
      ))}
    </div>
  );
};

export default function DashboardPage() {
  const { user } = useAuth();
  const {
    overview, charts, financialSummary, loanAnalytics,
    settlementAnalytics, aiAnalytics, isLoading, error, refetch
  } = useDashboard();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          {Array(4).fill(0).map((_, i) => <SkeletonCard key={i} />)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {Array(3).fill(0).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <AlertTriangle size={40} className="text-amber-500" />
        <p className="text-surface-600 dark:text-surface-400">{error}</p>
        <Button onClick={refetch} variant="outline" size="sm">
          <RefreshCw size={14} /> Retry
        </Button>
      </div>
    );
  }

  const riskVariant = {
    LOW: 'success', MEDIUM: 'warning', HIGH: 'orange', CRITICAL: 'danger',
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Welcome header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-surface-900 dark:text-surface-100">
            Welcome back, {overview?.user_name?.split(' ')[0] || user?.name?.split(' ')[0] || 'there'} 👋
          </h1>
          <p className="text-sm text-surface-500 dark:text-surface-400 mt-0.5">
            Here's your financial snapshot for today.
          </p>
        </div>
        <Button onClick={refetch} variant="ghost" size="sm" id="dashboard-refresh">
          <RefreshCw size={14} /> Refresh
        </Button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          title="Monthly Income"
          value={formatCurrency(overview?.monthly_income)}
          icon={IndianRupee}
          color="emerald"
          subtitle="Gross monthly earnings"
        />
        <StatCard
          title="Monthly Expenses"
          value={formatCurrency(overview?.monthly_expenses)}
          icon={Activity}
          color="amber"
          subtitle={`Surplus: ${formatCurrency(overview?.monthly_surplus)}`}
        />
        <StatCard
          title="Total EMI"
          value={formatCurrency(overview?.total_monthly_emi)}
          icon={CreditCard}
          color="primary"
          subtitle={`${overview?.total_active_loans || 0} active loans`}
        />
        <StatCard
          title="Total Outstanding"
          value={formatCurrency(overview?.total_outstanding_amount)}
          icon={TrendingUp}
          color="red"
          subtitle={`Est. savings: ${formatCurrency(overview?.estimated_savings)}`}
        />
      </div>

      {/* Health score + Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

        {/* Financial Health Score */}
        <Card padding="p-5">
          <CardHeader title="Financial Health Score" subtitle="Based on DTI, EMI & surplus analysis" />
          <ScoreGauge score={overview?.financial_health_score} />
          <div className="mt-3 space-y-2.5">
            <div className="flex justify-between items-center">
              <span className="text-xs text-surface-500">Risk Level</span>
              <Badge variant={riskVariant[overview?.risk_level] || 'default'}>
                {overview?.risk_level || '—'}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-surface-500">Repayment Capacity</span>
              <span className="text-xs font-medium text-surface-700 dark:text-surface-300">
                {overview?.repayment_capacity || '—'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-surface-500">Eligible Settlements</span>
              <span className="text-xs font-semibold text-primary-600 dark:text-primary-400">
                {overview?.eligible_settlements || 0} loans
              </span>
            </div>
          </div>
          <div className="mt-4">
            <Link to="/analysis">
              <Button variant="outline" size="sm" className="w-full">View Full Analysis</Button>
            </Link>
          </div>
        </Card>

        {/* Loan Type Distribution */}
        <Card padding="p-5">
          <CardHeader title="Loan Type Distribution" />
          {charts?.loan_type_pie_chart?.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={charts.loan_type_pie_chart}
                  cx="50%" cy="50%"
                  innerRadius={55} outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {charts.loan_type_pie_chart.map((_, i) => (
                    <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend
                  iconType="circle" iconSize={8}
                  formatter={(v) => <span className="text-xs text-surface-600 dark:text-surface-400">{v}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[220px] text-surface-400 text-sm">
              No loan data available
            </div>
          )}
        </Card>

        {/* Settlement eligibility */}
        <Card padding="p-5">
          <CardHeader title="Settlement Eligibility" />
          {charts?.settlement_eligibility_chart?.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie
                    data={charts.settlement_eligibility_chart}
                    cx="50%" cy="50%"
                    outerRadius={75} paddingAngle={3}
                    dataKey="value"
                  >
                    {charts.settlement_eligibility_chart.map((entry, i) => {
                      const c = entry.name === 'ELIGIBLE' ? '#10b981'
                        : entry.name === 'PARTIALLY_ELIGIBLE' ? '#f59e0b' : '#ef4444';
                      return <Cell key={i} fill={c} />;
                    })}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-2 mt-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-emerald-500 inline-block" />Eligible</span>
                  <span className="font-medium">{settlementAnalytics?.eligible_loans || 0} loans</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-amber-500 inline-block" />Partial</span>
                  <span className="font-medium">{settlementAnalytics?.partially_eligible_loans || 0} loans</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-red-500 inline-block" />Not Eligible</span>
                  <span className="font-medium">{settlementAnalytics?.not_eligible_loans || 0} loans</span>
                </div>
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-[220px] text-surface-400 text-sm">
              No settlement data
            </div>
          )}
        </Card>
      </div>

      {/* Interest Rate Bar Chart + Financial Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card padding="p-5">
          <CardHeader title="Interest Rates by Lender" subtitle="Annual interest rate (%)" />
          {charts?.interest_rate_bar_chart?.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={charts.interest_rate_bar_chart} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                <XAxis dataKey="lender_name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} unit="%" />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="interest_rate" name="Interest Rate" fill="#7C3AED" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[220px] text-surface-400 text-sm">
              No lender data
            </div>
          )}
        </Card>

        <Card padding="p-5">
          <CardHeader title="Financial Summary" />
          <div className="space-y-3">
            {[
              { label: 'Monthly Income', value: formatCurrency(financialSummary?.income), pct: null },
              { label: 'Monthly Expenses', value: formatCurrency(financialSummary?.expenses), pct: null },
              { label: 'Total EMI', value: formatCurrency(financialSummary?.emi), pct: null },
              { label: 'Net Surplus', value: formatCurrency(financialSummary?.surplus), pct: null },
              { label: 'DTI Ratio', value: formatPercent(financialSummary?.dti), pct: financialSummary?.dti },
              { label: 'EMI Ratio', value: formatPercent(financialSummary?.emi_ratio), pct: financialSummary?.emi_ratio },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between">
                <span className="text-sm text-surface-500 dark:text-surface-400">{item.label}</span>
                <div className="flex items-center gap-2">
                  {item.pct != null && (
                    <div className="w-24 h-1.5 bg-surface-200 dark:bg-surface-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary-500 rounded-full"
                        style={{ width: `${Math.min(100, item.pct)}%` }}
                      />
                    </div>
                  )}
                  <span className="text-sm font-semibold text-surface-800 dark:text-surface-200 min-w-[70px] text-right">
                    {item.value}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 pt-3 border-t border-surface-100 dark:border-surface-700/50">
            <div className="flex justify-between items-center">
              <span className="text-xs font-medium text-surface-500">Financial Health Score</span>
              <span className={`text-base font-bold ${
                (financialSummary?.financial_score || 0) >= 70 ? 'text-emerald-500' :
                (financialSummary?.financial_score || 0) >= 50 ? 'text-amber-500' : 'text-red-500'
              }`}>
                {Math.round(financialSummary?.financial_score || 0)}/100
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* AI Activity + Outstanding by Lender */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* AI Activity */}
        <Card padding="p-5">
          <CardHeader
            title="Recent AI Activity"
            subtitle={`${aiAnalytics?.total_ai_requests || 0} total requests`}
            action={
              <div className="flex items-center gap-1.5 text-xs text-primary-500">
                <Brain size={14} /> AI Engine
              </div>
            }
          />
          {aiAnalytics?.recent_ai_activities?.length > 0 ? (
            <div className="space-y-3">
              {aiAnalytics.recent_ai_activities.slice(0, 4).map((item) => (
                <div key={item.id} className="flex gap-3 items-start">
                  <div className="h-7 w-7 rounded-lg bg-primary-50 dark:bg-primary-900/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Brain size={13} className="text-primary-500" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs font-medium text-surface-700 dark:text-surface-300 capitalize">
                      {item.prompt_type?.replace(/_/g, ' ')}
                    </p>
                    <p className="text-xs text-surface-400 dark:text-surface-500 truncate">{item.prompt}</p>
                    <p className="text-[10px] text-surface-300 dark:text-surface-600 mt-0.5">
                      {formatRelativeTime(item.created_at)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-28 gap-2">
              <Brain size={28} className="text-surface-300 dark:text-surface-600" />
              <p className="text-xs text-surface-400">No AI activity yet</p>
            </div>
          )}
        </Card>

        {/* Outstanding by lender */}
        <Card padding="p-5">
          <CardHeader title="Outstanding by Lender" subtitle="Total outstanding amount" />
          {charts?.outstanding_amount_by_lender?.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart
                data={charts.outstanding_amount_by_lender}
                margin={{ top: 4, right: 4, left: 10, bottom: 0 }}
                layout="vertical"
              >
                <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k`} />
                <YAxis type="category" dataKey="lender_name" tick={{ fontSize: 11 }} width={80} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="outstanding_amount" name="Outstanding" fill="#14B8A6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[220px] text-surface-400 text-sm">No data</div>
          )}
        </Card>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Add a Loan', path: '/loans', icon: CreditCard, color: 'primary' },
          { label: 'View Analysis', path: '/analysis', icon: TrendingUp, color: 'teal' },
          { label: 'Settlement Plan', path: '/settlement', icon: Handshake, color: 'emerald' },
          { label: 'Update Profile', path: '/profile', icon: Activity, color: 'amber' },
        ].map((action) => (
          <Link key={action.path} to={action.path}>
            <motion.div
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`flex flex-col items-center gap-2 p-4 rounded-2xl border cursor-pointer transition-all bg-white dark:bg-surface-800 border-surface-200 dark:border-surface-700 hover:border-primary-300 dark:hover:border-primary-700 hover:shadow-card`}
            >
              <action.icon size={22} className="text-primary-500" />
              <span className="text-xs font-medium text-surface-700 dark:text-surface-300 text-center">{action.label}</span>
            </motion.div>
          </Link>
        ))}
      </div>
    </div>
  );
}
