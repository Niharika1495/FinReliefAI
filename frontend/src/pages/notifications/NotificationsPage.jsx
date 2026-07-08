import { Bell, Check, CheckCheck, AlertCircle, Info, IndianRupee } from 'lucide-react';
import { useNotifications } from '@/hooks/useNotifications';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { SkeletonCard } from '@/components/ui/Skeleton';
import { formatRelativeTime } from '@/utils/formatters';
import { cn } from '@/utils/cn';
import { motion } from 'framer-motion';
import { useState } from 'react';

const TYPE_ICON = {
  ALERT: AlertCircle,
  REMINDER: Bell,
  INFO: Info,
  PAYMENT: IndianRupee,
};

const TYPE_COLOR = {
  ALERT: 'text-red-500 bg-red-50 dark:bg-red-900/20',
  REMINDER: 'text-amber-500 bg-amber-50 dark:bg-amber-900/20',
  INFO: 'text-blue-500 bg-blue-50 dark:bg-blue-900/20',
  PAYMENT: 'text-emerald-500 bg-emerald-50 dark:bg-emerald-900/20',
};

export default function NotificationsPage() {
  const { notifications, isLoading, unreadCount, markRead, markAllRead } = useNotifications();
  const [filter, setFilter] = useState('all'); // 'all' | 'unread'

  const displayed = filter === 'unread'
    ? notifications.filter((n) => !n.is_read)
    : notifications;

  return (
    <div className="space-y-5 animate-fade-in max-w-3xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-surface-900 dark:text-surface-100">Notifications</h1>
          <p className="text-sm text-surface-500 dark:text-surface-400 mt-0.5">
            {unreadCount > 0 ? `${unreadCount} unread notifications` : 'All caught up!'}
          </p>
        </div>
        {unreadCount > 0 && (
          <Button onClick={markAllRead} variant="outline" size="sm" id="mark-all-read">
            <CheckCheck size={14} /> Mark all read
          </Button>
        )}
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2">
        {[
          { key: 'all', label: 'All' },
          { key: 'unread', label: `Unread (${unreadCount})` },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={cn(
              'px-4 py-1.5 rounded-full text-sm font-medium transition-all',
              filter === tab.key
                ? 'bg-primary-600 text-white'
                : 'bg-surface-100 dark:bg-surface-700/50 text-surface-600 dark:text-surface-400 hover:bg-surface-200 dark:hover:bg-surface-700'
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Notifications list */}
      {isLoading ? (
        <div className="space-y-3">
          {Array(4).fill(0).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : displayed.length === 0 ? (
        <div className="flex flex-col items-center gap-3 py-20">
          <div className="h-14 w-14 rounded-2xl bg-surface-100 dark:bg-surface-700/50 flex items-center justify-center">
            <Bell size={24} className="text-surface-400" />
          </div>
          <p className="text-sm font-medium text-surface-500 dark:text-surface-400">No notifications</p>
        </div>
      ) : (
        <div className="space-y-2">
          {displayed.map((notif, i) => {
            const Icon = TYPE_ICON[notif.type] || Bell;
            const colorClass = TYPE_COLOR[notif.type] || 'text-surface-500 bg-surface-100 dark:bg-surface-700';

            return (
              <motion.div
                key={notif.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                className={cn(
                  'flex items-start gap-3.5 p-4 rounded-2xl border transition-all cursor-pointer group',
                  notif.is_read
                    ? 'bg-white dark:bg-surface-800 border-surface-200 dark:border-surface-700/50'
                    : 'bg-primary-50/50 dark:bg-primary-900/10 border-primary-200 dark:border-primary-800/40'
                )}
                onClick={() => !notif.is_read && markRead(notif.id)}
              >
                <div className={cn('h-9 w-9 rounded-xl flex items-center justify-center flex-shrink-0', colorClass)}>
                  <Icon size={16} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <p className={cn(
                      'text-sm font-medium',
                      notif.is_read ? 'text-surface-700 dark:text-surface-300' : 'text-surface-900 dark:text-surface-100'
                    )}>
                      {notif.title}
                    </p>
                    <div className="flex items-center gap-1.5 flex-shrink-0">
                      {!notif.is_read && (
                        <span className="h-2 w-2 rounded-full bg-primary-500 flex-shrink-0" />
                      )}
                      <span className="text-[10px] text-surface-400 dark:text-surface-500 whitespace-nowrap">
                        {formatRelativeTime(notif.created_at)}
                      </span>
                    </div>
                  </div>
                  <p className="text-xs text-surface-500 dark:text-surface-400 mt-0.5 line-clamp-2">{notif.message}</p>
                  {notif.type && (
                    <Badge className="mt-1.5" variant="default">{notif.type}</Badge>
                  )}
                </div>
                {!notif.is_read && (
                  <button
                    onClick={(e) => { e.stopPropagation(); markRead(notif.id); }}
                    className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-lg text-surface-400 hover:text-surface-600 hover:bg-surface-100 dark:hover:bg-surface-700"
                    title="Mark as read"
                  >
                    <Check size={14} />
                  </button>
                )}
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
