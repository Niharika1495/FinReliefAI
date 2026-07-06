import { TrendingUp } from 'lucide-react';

export function Footer() {
  return (
    <footer className="flex items-center justify-between px-6 py-3 border-t border-surface-200 dark:border-surface-700/60 bg-white dark:bg-surface-900 text-xs text-surface-400 dark:text-surface-500">
      <div className="flex items-center gap-2">
        <div className="h-4 w-4 rounded bg-gradient-to-br from-primary-500 to-teal-500 flex items-center justify-center">
          <TrendingUp size={10} className="text-white" />
        </div>
        <span>FinRelief AI © 2025</span>
      </div>
      <span className="hidden sm:block">AI-Powered Debt Relief & Financial Recovery</span>
      <span className="text-primary-400 dark:text-primary-500 font-medium">v1.0.0</span>
    </footer>
  );
}
