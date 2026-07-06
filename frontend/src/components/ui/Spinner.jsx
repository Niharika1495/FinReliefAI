import { cn } from '@/utils/cn';

export function Spinner({ size = 'md', className }) {
  const sizes = { sm: 'h-4 w-4', md: 'h-6 w-6', lg: 'h-10 w-10', xl: 'h-16 w-16' };
  return (
    <svg
      className={cn('animate-spin text-primary-500', sizes[size], className)}
      viewBox="0 0 24 24"
      fill="none"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
  );
}

export function FullPageSpinner() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-surface-50 dark:bg-[#09101d]">
      <div className="text-center space-y-4">
        <Spinner size="xl" />
        <p className="text-sm text-surface-500 dark:text-surface-400">Loading FinRelief AI...</p>
      </div>
    </div>
  );
}
