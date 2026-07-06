import { useState, useEffect, useCallback } from 'react';
import { notificationsApi } from '@/api/notifications';
import toast from 'react-hot-toast';

export function useNotifications() {
  const [notifications, setNotifications] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchNotifications = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await notificationsApi.getNotifications();
      const data = Array.isArray(res.data) ? res.data : (res.data?.data || []);
      setNotifications(data);
      setUnreadCount(data.filter((n) => !n.is_read).length);
    } catch {
      // Silently fail — notifications are non-critical
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  const markRead = async (id) => {
    try {
      await notificationsApi.markRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((c) => Math.max(0, c - 1));
    } catch {
      toast.error('Failed to mark notification as read');
    }
  };

  const markAllRead = async () => {
    const unread = notifications.filter((n) => !n.is_read);
    await Promise.allSettled(unread.map((n) => notificationsApi.markRead(n.id)));
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    setUnreadCount(0);
  };

  return {
    notifications,
    unreadCount,
    isLoading,
    markRead,
    markAllRead,
    refetch: fetchNotifications,
  };
}
