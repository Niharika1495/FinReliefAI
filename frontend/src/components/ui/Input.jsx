import { forwardRef } from 'react';
import { cn } from '@/utils/cn';

export const Input = forwardRef(function Input(
  { label, error, hint, leftIcon: LeftIcon, rightIcon: RightIcon, className, id, ...props },
  ref
) {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-surface-700 dark:text-surface-300">
          {label}
          {props.required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <div className="relative">
        {LeftIcon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500 pointer-events-none">
            <LeftIcon size={16} />
          </div>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            'w-full rounded-xl border bg-white dark:bg-surface-800 text-surface-900 dark:text-surface-100 placeholder-surface-400 dark:placeholder-surface-500',
            'px-3.5 py-2.5 text-sm transition-all duration-150',
            'border-surface-300 dark:border-surface-600',
            'focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            error && 'border-red-500 focus:ring-red-500/40',
            LeftIcon && 'pl-9',
            RightIcon && 'pr-9',
            className
          )}
          {...props}
        />
        {RightIcon && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500">
            <RightIcon size={16} />
          </div>
        )}
      </div>
      {error && <p className="text-xs text-red-500 flex items-center gap-1">{error}</p>}
      {hint && !error && <p className="text-xs text-surface-400 dark:text-surface-500">{hint}</p>}
    </div>
  );
});
