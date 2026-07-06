import { cn } from '@/utils/cn';

export function Badge({ children, variant = 'default', className }) {
  const variants = {
    default: 'bg-surface-100 dark:bg-surface-700 text-surface-600 dark:text-surface-300',
    primary: 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300',
    teal: 'bg-teal-100 dark:bg-teal-900/30 text-teal-700 dark:text-teal-300',
    success: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300',
    warning: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300',
    danger: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300',
    info: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300',
    orange: 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300',
  };
  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
