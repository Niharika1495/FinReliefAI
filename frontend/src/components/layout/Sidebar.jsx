import { NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard, CreditCard, BarChart3, Handshake,
  User, Bell, ChevronLeft, ChevronRight, TrendingUp,
  Shield, Menu, X, FileUp, FileText, Sparkles
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { useNotifications } from '@/hooks/useNotifications';

const NAV_ITEMS = [
  { label: 'Dashboard',   path: '/dashboard',    icon: LayoutDashboard },
  { label: 'Loans',       path: '/loans',         icon: CreditCard },
  { label: 'Analysis',    path: '/analysis',      icon: BarChart3 },
  { label: 'Settlement',  path: '/settlement',    icon: Handshake },
  { label: 'AI Workspace', path: '/ai',            icon: Sparkles },
  { label: 'OCR Upload',  path: '/documents',     icon: FileUp },
  { label: 'Reports',     path: '/reports',       icon: FileText },
  { label: 'Profile',     path: '/profile',       icon: User },
  { label: 'Notifications', path: '/notifications', icon: Bell, badge: true },
];

export function Sidebar({ collapsed, setCollapsed, mobileOpen, setMobileOpen }) {
  const location = useLocation();
  const { unreadCount } = useNotifications();

  const SidebarLink = ({ item }) => {
    const Icon = item.icon;
    const isActive = location.pathname.startsWith(item.path);

    return (
      <NavLink
        to={item.path}
        onClick={() => setMobileOpen(false)}
        className={({ isActive: na }) => cn(
          'group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 relative',
          (isActive || na)
            ? 'bg-primary-600 text-white shadow-sm'
            : 'text-surface-600 dark:text-surface-400 hover:bg-surface-100 dark:hover:bg-surface-700/50 hover:text-surface-900 dark:hover:text-surface-100'
        )}
      >
        <div className="relative flex-shrink-0">
          <Icon size={18} />
          {item.badge && unreadCount > 0 && (
            <span className="absolute -top-1.5 -right-1.5 h-4 w-4 flex items-center justify-center rounded-full bg-red-500 text-white text-[9px] font-bold">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </div>
        {!collapsed && (
          <span className="truncate">{item.label}</span>
        )}
        {!collapsed && item.badge && unreadCount > 0 && (
          <span className="ml-auto text-xs bg-red-500 text-white px-1.5 py-0.5 rounded-full font-medium">
            {unreadCount}
          </span>
        )}
      </NavLink>
    );
  };

  const sidebarContent = (
    <div className="flex flex-col h-full">
      {/* Brand */}
      <div className={cn(
        'flex items-center px-4 py-5 border-b border-surface-200 dark:border-surface-700/60',
        collapsed ? 'justify-center' : 'justify-between'
      )}>
        {!collapsed && (
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-primary-500 to-teal-500 flex items-center justify-center flex-shrink-0">
              <TrendingUp size={16} className="text-white" />
            </div>
            <div>
              <p className="text-sm font-bold text-surface-900 dark:text-surface-100 leading-tight">FinRelief AI</p>
              <p className="text-[10px] text-surface-400 dark:text-surface-500">Debt Relief Platform</p>
            </div>
          </div>
        )}
        {collapsed && (
          <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-primary-500 to-teal-500 flex items-center justify-center">
            <TrendingUp size={16} className="text-white" />
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="hidden lg:flex p-1.5 rounded-lg text-surface-400 hover:text-surface-600 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* Nav items */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {NAV_ITEMS.map((item) => (
          <SidebarLink key={item.path} item={item} />
        ))}
      </nav>

      {/* Footer badge */}
      {!collapsed && (
        <div className="px-4 py-4 border-t border-surface-200 dark:border-surface-700/60">
          <div className="flex items-center gap-2 text-xs text-surface-400 dark:text-surface-500">
            <Shield size={12} />
            <span>Bank-grade security</span>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <motion.aside
        animate={{ width: collapsed ? 72 : 240 }}
        transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
        className="hidden lg:flex flex-col flex-shrink-0 bg-white dark:bg-surface-900 border-r border-surface-200 dark:border-surface-700/60 overflow-hidden"
      >
        {sidebarContent}
      </motion.aside>

      {/* Mobile drawer */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
              onClick={() => setMobileOpen(false)}
            />
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
              className="fixed left-0 top-0 bottom-0 z-50 w-[240px] bg-white dark:bg-surface-900 border-r border-surface-200 dark:border-surface-700 flex flex-col lg:hidden"
            >
              <div className="flex items-center justify-between px-4 py-5 border-b border-surface-200 dark:border-surface-700">
                <div className="flex items-center gap-2.5">
                  <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-primary-500 to-teal-500 flex items-center justify-center">
                    <TrendingUp size={16} className="text-white" />
                  </div>
                  <p className="text-sm font-bold text-surface-900 dark:text-surface-100">FinRelief AI</p>
                </div>
                <button onClick={() => setMobileOpen(false)} className="p-1.5 rounded-lg text-surface-400 hover:bg-surface-100 dark:hover:bg-surface-700">
                  <X size={18} />
                </button>
              </div>
              <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
                {NAV_ITEMS.map((item) => (
                  <SidebarLink key={item.path} item={item} />
                ))}
              </nav>
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
