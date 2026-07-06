import { Search } from 'lucide-react';
import { cn } from '@/utils/cn';
import { useEffect, useState } from 'react';

export function SearchBar({ value, onChange, placeholder = 'Search...', className, debounce = 300 }) {
  const [local, setLocal] = useState(value || '');

  useEffect(() => {
    const timer = setTimeout(() => {
      onChange(local);
    }, debounce);
    return () => clearTimeout(timer);
  }, [local, debounce, onChange]);

  useEffect(() => {
    setLocal(value || '');
  }, [value]);

  return (
    <div className={cn('relative', className)}>
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500" size={16} />
      <input
        type="text"
        value={local}
        onChange={(e) => setLocal(e.target.value)}
        placeholder={placeholder}
        className="w-full pl-9 pr-4 py-2.5 text-sm rounded-xl border border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-800 text-surface-900 dark:text-surface-100 placeholder-surface-400 dark:placeholder-surface-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
      />
    </div>
  );
}
