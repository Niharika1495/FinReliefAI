import { cn } from '@/utils/cn';
import { motion } from 'framer-motion';

const variants = {
  primary: 'bg-primary-600 hover:bg-primary-700 active:bg-primary-800 text-white shadow-sm hover:shadow-glow-primary',
  secondary: 'bg-teal-500 hover:bg-teal-600 active:bg-teal-700 text-white shadow-sm hover:shadow-glow-teal',
  outline: 'border border-primary-300 dark:border-primary-700 text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20',
  ghost: 'text-surface-600 dark:text-surface-400 hover:bg-surface-100 dark:hover:bg-surface-700/50',
  danger: 'bg-red-600 hover:bg-red-700 active:bg-red-800 text-white shadow-sm',
  success: 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm',
};

const sizes = {
  xs: 'px-2.5 py-1.5 text-xs rounded-lg',
  sm: 'px-3 py-2 text-sm rounded-lg',
  md: 'px-4 py-2.5 text-sm rounded-xl',
  lg: 'px-5 py-3 text-base rounded-xl',
  icon: 'p-2 rounded-xl',
};

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  className,
  onClick,
  type = 'button',
  ...props
}) {
  return (
    <motion.button
      whileTap={{ scale: 0.97 }}
      type={type}
      disabled={disabled || isLoading}
      onClick={onClick}
      className={cn(
        'inline-flex items-center justify-center gap-2 font-medium transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:ring-offset-2 dark:focus:ring-offset-surface-900 disabled:opacity-50 disabled:cursor-not-allowed',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {isLoading ? (
        <>
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
          </svg>
          <span>Loading...</span>
        </>
      ) : children}
    </motion.button>
  );
}
