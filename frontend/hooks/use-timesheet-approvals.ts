import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { api } from '@/lib/api';
import type { 
  Timesheet
} from '@/lib/types';

interface UseTimesheetApprovalsOptions {
  skip?: number;
  limit?: number;
  statusCode?: string;
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
}

export function useTimesheetApprovals(options: UseTimesheetApprovalsOptions = {}) {
  const [data, setData] = useState<{
    items: Timesheet[];
    total_count: number;
    page: number;
    size: number;
    has_next: boolean;
    has_previous: boolean;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const hasFetched = useRef(false);
  const isMounted = useRef(true);

  const { skip = 0, limit = 10, statusCode, onSuccess, onError } = options;

  // Memoize the options to prevent unnecessary re-renders
  const memoizedOptions = useMemo(() => ({
    skip,
    limit,
    statusCode
  }), [skip, limit, statusCode]);

  // Memoize the callbacks to prevent unnecessary re-renders
  const memoizedOnSuccess = useCallback(onSuccess || (() => {}), []);
  const memoizedOnError = useCallback(onError || (() => {}), []);

  const fetchApprovals = useCallback(async () => {
    console.log('🔄 useTimesheetApprovals fetch', { 
      options: memoizedOptions, 
      hasFetched: hasFetched.current,
      isMounted: isMounted.current
    });
    
    if (hasFetched.current || !isMounted.current) {
      console.log('⏭️ Skipping timesheet approvals fetch - already fetched or component unmounted');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      params.append('skip', memoizedOptions.skip.toString());
      params.append('limit', memoizedOptions.limit.toString());
      if (memoizedOptions.statusCode) {
        params.append('status_code', memoizedOptions.statusCode);
      }
      
      const result = await api.get<{
        items: Timesheet[];
        total_count: number;
        page: number;
        size: number;
        has_next: boolean;
        has_previous: boolean;
      }>(`/api/timesheets/manager/subordinates?${params.toString()}`);
      
      // Only update state if component is still mounted
      if (isMounted.current) {
        setData(result);
        memoizedOnSuccess(result);
        hasFetched.current = true;
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch timesheet approvals');
      
      // Only update state if component is still mounted
      if (isMounted.current) {
        setError(error);
        memoizedOnError(error);
      }
    } finally {
      // Only update loading state if component is still mounted
      if (isMounted.current) {
        setLoading(false);
      }
    }
  }, [memoizedOptions, memoizedOnSuccess, memoizedOnError]);

  const refetch = useCallback(() => {
    console.log('🔄 Manual timesheet approvals refetch requested');
    hasFetched.current = false;
    fetchApprovals();
  }, [fetchApprovals]);

  useEffect(() => {
    console.log('🔄 useTimesheetApprovals useEffect triggered', { hasFetched: hasFetched.current });
    fetchApprovals();
  }, [fetchApprovals]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMounted.current = false;
    };
  }, []);

  return {
    data,
    loading,
    error,
    refetch
  };
} 