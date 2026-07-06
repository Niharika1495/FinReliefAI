import { cn } from '@/utils/cn';
import { motion } from 'framer-motion';

export function Card({ children, className, hover = false, padding = 'p-5', ...props }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={cn(
        'bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700/60 rounded-2xl shadow-card',
        hover && 'hover:shadow-card-hover transition-shadow duration-200 cursor-pointer',
        padding,
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  );
}

export function CardHeader({ title, subtitle, action, className }) {
  return (
    <div className={cn('flex items-start justify-between mb-4', className)}>
      <div>
        <h3 className="text-sm font-semibold text-surface-900 dark:text-surface-100">{title}</h3>
        {subtitle && <p className="text-xs text-surface-500 dark:text-surface-400 mt-0.5">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}
