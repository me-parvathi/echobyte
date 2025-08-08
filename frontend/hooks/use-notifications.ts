import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '@/lib/api';
import { Notification } from '@/lib/types';

// Unread count response interface
interface UnreadCountResponse {
  count: number;
}

// Hook state interface
interface NotificationsState {
  notifications: Notification[];
  unreadCount: number;
  loading: boolean;
  error: string | null;
  hasMore: boolean;
  offset: number;
}

// Hook return interface
interface UseNotificationsReturn extends NotificationsState {
  refetch: () => Promise<void>;
  markAsRead: (notificationId: string) => Promise<void>;
  loadMore: () => Promise<void>;
  clearError: () => void;
}

// Hook options interface
interface UseNotificationsOptions {
  autoPoll?: boolean;
  pollInterval?: number;
  initialLimit?: number;
  loadMoreLimit?: number;
  enabled?: boolean; // New option to control when the hook should be active
}

const DEFAULT_OPTIONS: Required<UseNotificationsOptions> = {
  autoPoll: true,
  pollInterval: 30000, // 30 seconds
  initialLimit: 10,
  loadMoreLimit: 10,
  enabled: true,
};

export function useNotifications(
  options: UseNotificationsOptions = {}
): UseNotificationsReturn {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  
  // State management
  const [state, setState] = useState<NotificationsState>({
    notifications: [],
    unreadCount: 0,
    loading: false,
    error: null,
    hasMore: true,
    offset: 0,
  });

  // Refs for managing polling and preventing race conditions
  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const isInitialLoadRef = useRef(true);
  const isMountedRef = useRef(true);

  // Fetch notifications with pagination
  const fetchNotifications = useCallback(async (
    limit: number = opts.initialLimit,
    offset: number = 0,
    append: boolean = false
  ) => {
    // Don't fetch if hook is disabled or component is unmounted
    if (!opts.enabled || !isMountedRef.current) {
      return;
    }

    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    abortControllerRef.current = new AbortController();

    try {
      setState(prev => ({ ...prev, loading: true, error: null }));

      const response = await api.get<Notification[]>(
        `/api/notifications/?limit=${limit}&offset=${offset}`,
        { signal: abortControllerRef.current.signal }
      );

      // Check if component is still mounted before updating state
      if (!isMountedRef.current) {
        return;
      }

      setState(prev => ({
        ...prev,
        notifications: append ? [...prev.notifications, ...response] : response,
        offset: offset + response.length,
        hasMore: response.length === limit,
        loading: false,
      }));
    } catch (error) {
      // Don't set error if request was aborted or component is unmounted
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Notification fetch aborted - this is normal during navigation');
        return;
      }

      if (!isMountedRef.current) {
        return;
      }

      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch notifications',
      }));
    }
  }, [opts.initialLimit, opts.enabled]);

  // Fetch unread count
  const fetchUnreadCount = useCallback(async () => {
    if (!opts.enabled || !isMountedRef.current) {
      return;
    }

    try {
      const response = await api.get<UnreadCountResponse>('/api/notifications/unread-count');
      
      if (!isMountedRef.current) {
        return;
      }

      setState(prev => ({ ...prev, unreadCount: response.count }));
    } catch (error) {
      // Don't set error for unread count failures, just log
      if (error instanceof Error && error.name !== 'AbortError') {
        console.warn('Failed to fetch unread count:', error);
      }
    }
  }, [opts.enabled]);

  // Mark notification as read with optimistic update
  const markAsRead = useCallback(async (notificationId: string) => {
    if (!isMountedRef.current) {
      return;
    }

    // Optimistic update
    setState(prev => ({
      ...prev,
      notifications: prev.notifications.map(notification =>
        notification.id === notificationId
          ? { ...notification, is_read: true, read_at: new Date().toISOString() }
          : notification
      ),
      unreadCount: Math.max(0, prev.unreadCount - 1),
    }));

    try {
      await api.post(`/api/notifications/${notificationId}/read`);
    } catch (error) {
      if (!isMountedRef.current) {
        return;
      }

      // Revert optimistic update on error
      setState(prev => ({
        ...prev,
        notifications: prev.notifications.map(notification =>
          notification.id === notificationId
            ? { ...notification, is_read: false, read_at: undefined }
            : notification
        ),
        unreadCount: prev.unreadCount + 1,
        error: 'Failed to mark notification as read',
      }));
    }
  }, []);

  // Load more notifications
  const loadMore = useCallback(async () => {
    if (state.loading || !state.hasMore || !opts.enabled) return;
    
    await fetchNotifications(opts.loadMoreLimit, state.offset, true);
  }, [state.loading, state.hasMore, state.offset, fetchNotifications, opts.loadMoreLimit, opts.enabled]);

  // Refetch all data
  const refetch = useCallback(async () => {
    if (!opts.enabled) return;

    setState(prev => ({ ...prev, offset: 0, hasMore: true }));
    await Promise.all([
      fetchNotifications(opts.initialLimit, 0, false),
      fetchUnreadCount(),
    ]);
  }, [fetchNotifications, fetchUnreadCount, opts.initialLimit, opts.enabled]);

  // Clear error state
  const clearError = useCallback(() => {
    if (!isMountedRef.current) return;
    
    setState(prev => ({ ...prev, error: null }));
  }, []);

  // Setup polling
  useEffect(() => {
    if (!opts.autoPoll || !opts.enabled) return;

    const startPolling = () => {
      pollingRef.current = setInterval(async () => {
        // Skip if already loading, unmounted, or previous request is pending
        if (state.loading || !isMountedRef.current || abortControllerRef.current) {
          return;
        }

        try {
          // Create new abort controller for this polling cycle
          abortControllerRef.current = new AbortController();
          
          await fetchUnreadCount();
          
          // Check for new notifications by fetching first page
          try {
            const response = await api.get<Notification[]>(
              `/api/notifications/?limit=${opts.initialLimit}&offset=0`
            );
            
            if (!isMountedRef.current) return;
            
            // If we have new notifications, update the list
            if (response.length > 0) {
              const firstExistingId = state.notifications[0]?.id;
              const newNotifications = response.filter(
                notification => notification.id !== firstExistingId
              );
              
              if (newNotifications.length > 0) {
                setState(prev => ({
                  ...prev,
                  notifications: [...newNotifications, ...prev.notifications],
                  unreadCount: prev.unreadCount + newNotifications.filter(n => !n.is_read).length,
                }));
              }
            }
          } catch (error) {
            if (error instanceof Error && error.name !== 'AbortError') {
              console.warn('Failed to check for new notifications:', error);
            }
          }
        } catch (error) {
          if (error instanceof Error && error.name !== 'AbortError') {
            console.warn('Failed to fetch unread count:', error);
          }
        } finally {
          // Clear abort controller after requests complete
          abortControllerRef.current = null;
        }
      }, opts.pollInterval);
    };

    startPolling();

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    };
  }, [opts.autoPoll, opts.pollInterval, opts.initialLimit, opts.enabled, state.loading, state.notifications, fetchUnreadCount]);

  // Initial data fetch - only when enabled and component is mounted
  useEffect(() => {
    if (isInitialLoadRef.current && opts.enabled && isMountedRef.current) {
      refetch();
      isInitialLoadRef.current = false;
    }
  }, [refetch, opts.enabled]);

  // Cleanup on unmount
  useEffect(() => {
    isMountedRef.current = true;
    
    return () => {
      isMountedRef.current = false;
      
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    ...state,
    refetch,
    markAsRead,
    loadMore,
    clearError,
  };
} 