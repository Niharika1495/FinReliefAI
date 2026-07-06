import { useLocation, Link } from 'react-router-dom';
import { Sun, Moon, Bell, Menu, ChevronRight, LogOut, User } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '@/context/AuthContext';
import { useTheme } from '@/context/ThemeContext';
import { useNotifications } from '@/hooks/useNotifications';
import { cn } from '@/utils/cn';

const BREADCRUMB_MAP = {
  '/dashboard':     ['Dashboard'],
  '/loans':         ['Loans'],
  '/analysis':      ['Financial Analysis'],
  '/settlement':    ['Settlement'],
  '/profile':       ['Profile'],
  '/notifications': ['Notifications'],
};

export function Navbar({ onMenuClick }) {
  const location = useLocation();
  const { user, logout } = useAuth();
  const { isDark, toggleDark } = useTheme();
  const { unreadCount } = useNotifications();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const breadcrumbs = BREADCRUMB_MAP[location.pathname] || [];

  const initials = user?.name
    ? user.name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    : user?.email?.[0]?.toUpperCase() || 'U';

  return (
    <header className="flex items-center justify-between h-16 px-4 lg:px-6 bg-white dark:bg-surface-900 border-b border-surface-200 dark:border-surface-700/60 flex-shrink-0">
      {/* Left: mobile menu + breadcrumbs */}
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-lg text-surface-400 hover:text-surface-600 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
          aria-label="Open menu"
        >
          <Menu size={20} />
        </button>

        {breadcrumbs.length > 0 && (
          <nav className="flex items-center gap-1.5 text-sm">
            <span className="text-surface-400 dark:text-surface-500 hidden sm:block">Home</span>
            {breadcrumbs.map((crumb, i) => (
              <span key={i} className="flex items-center gap-1.5">
                <ChevronRight size={14} className="text-surface-300 dark:text-surface-600 hidden sm:block" />
                <span className="font-medium text-surface-700 dark:text-surface-200">{crumb}</span>
              </span>
            ))}
          </nav>
        )}
      </div>

      {/* Right: actions */}
      <div className="flex items-center gap-2">
        {/* Dark mode toggle */}
        <button
          onClick={toggleDark}
          className="p-2 rounded-lg text-surface-400 hover:text-surface-600 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
          aria-label="Toggle dark mode"
          id="dark-mode-toggle"
        >
          {isDark ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        {/* Notifications bell */}
        <Link
          to="/notifications"
          className="relative p-2 rounded-lg text-surface-400 hover:text-surface-600 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
          aria-label="Notifications"
          id="notifications-bell"
        >
          <Bell size={18} />
          {unreadCount > 0 && (
            <span className="absolute top-1 right-1 h-4 w-4 flex items-center justify-center rounded-full bg-red-500 text-white text-[9px] font-bold">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </Link>

        {/* User menu */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2.5 pl-3 pr-2 py-1.5 rounded-xl hover:bg-surface-100 dark:hover:bg-surface-700/50 transition-colors"
            id="user-menu-button"
          >
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-primary-500 to-teal-500 flex items-center justify-center text-white text-xs font-bold">
              {initials}
            </div>
            <span className="text-sm font-medium text-surface-700 dark:text-surface-200 hidden sm:block max-w-[120px] truncate">
              {user?.name || user?.email}
            </span>
          </button>

          <AnimatePresence>
            {dropdownOpen && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95, y: -8 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: -8 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 top-full mt-2 w-52 bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-xl shadow-lg z-50 overflow-hidden"
              >
                <div className="px-4 py-3 border-b border-surface-100 dark:border-surface-700">
                  <p className="text-sm font-semibold text-surface-900 dark:text-surface-100 truncate">
                    {user?.name || 'User'}
                  </p>
                  <p className="text-xs text-surface-400 dark:text-surface-500 truncate">{user?.email}</p>
                </div>
                <div className="py-1">
                  <Link
                    to="/profile"
                    onClick={() => setDropdownOpen(false)}
                    className="flex items-center gap-2.5 px-4 py-2.5 text-sm text-surface-700 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-700/50 transition-colors"
                  >
                    <User size={15} /> My Profile
                  </Link>
                  <button
                    onClick={() => { setDropdownOpen(false); logout(); }}
                    className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                    id="logout-button"
                  >
                    <LogOut size={15} /> Sign Out
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  );
}
