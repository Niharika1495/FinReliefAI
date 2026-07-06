import { forwardRef } from 'react';
import { cn } from '@/utils/cn';

export const Select = forwardRef(function Select(
  { label, error, options = [], placeholder, className, id, ...props },
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
      <select
        ref={ref}
        id={inputId}
        className={cn(
          'w-full rounded-xl border bg-white dark:bg-surface-800 text-surface-900 dark:text-surface-100',
          'px-3.5 py-2.5 text-sm transition-all duration-150 cursor-pointer',
          'border-surface-300 dark:border-surface-600',
          'focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          error && 'border-red-500',
          className
        )}
        {...props}
      >
        {placeholder && <option value="">{placeholder}</option>}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
});
