import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/utils/cn';

export function StatCard({ title, value, subtitle, icon: Icon, trend, trendValue, color = 'primary', className }) {
  const colors = {
    primary: {
      bg: 'bg-primary-50 dark:bg-primary-900/20',
      icon: 'text-primary-600 dark:text-primary-400',
      border: 'border-primary-100 dark:border-primary-800/40',
    },
    teal: {
      bg: 'bg-teal-50 dark:bg-teal-900/20',
      icon: 'text-teal-600 dark:text-teal-400',
      border: 'border-teal-100 dark:border-teal-800/40',
    },
    emerald: {
      bg: 'bg-emerald-50 dark:bg-emerald-900/20',
      icon: 'text-emerald-600 dark:text-emerald-400',
      border: 'border-emerald-100 dark:border-emerald-800/40',
    },
    amber: {
      bg: 'bg-amber-50 dark:bg-amber-900/20',
      icon: 'text-amber-600 dark:text-amber-400',
      border: 'border-amber-100 dark:border-amber-800/40',
    },
    red: {
      bg: 'bg-red-50 dark:bg-red-900/20',
      icon: 'text-red-600 dark:text-red-400',
      border: 'border-red-100 dark:border-red-800/40',
    },
  };
  const c = colors[color] || colors.primary;

  const trendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;
  const TrendIcon = trendIcon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn(
        'bg-white dark:bg-surface-800 border rounded-2xl p-5 flex flex-col gap-3 shadow-card hover:shadow-card-hover transition-shadow duration-200',
        c.border,
        className
      )}
    >
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-surface-500 dark:text-surface-400">{title}</p>
        {Icon && (
          <div className={cn('p-2.5 rounded-xl', c.bg)}>
            <Icon size={18} className={c.icon} />
          </div>
        )}
      </div>
      <div>
        <p className="text-2xl font-bold text-surface-900 dark:text-surface-100 tracking-tight">{value}</p>
        {subtitle && (
          <p className="text-xs text-surface-400 dark:text-surface-500 mt-0.5">{subtitle}</p>
        )}
      </div>
      {trend && trendValue && (
        <div className={cn(
          'flex items-center gap-1 text-xs font-medium',
          trend === 'up' ? 'text-emerald-600 dark:text-emerald-400' :
          trend === 'down' ? 'text-red-500 dark:text-red-400' :
          'text-surface-400'
        )}>
          <TrendIcon size={12} />
          <span>{trendValue}</span>
        </div>
      )}
    </motion.div>
  );
}
