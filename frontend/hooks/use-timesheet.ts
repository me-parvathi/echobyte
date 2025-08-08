import { useState, useEffect, useCallback } from 'react';
import { TimesheetApiService } from '@/lib/timesheet-api';
import { 
  TimesheetBatchResponse, 
  Timesheet, 
  TimesheetDetail, 
  DailyEntryFormData,
  BulkSaveResponse,
  TimesheetSubmissionResponse
} from '@/lib/types';
import { formatDate, isCurrentWeek, isPastWeek } from '@/lib/timesheet-utils';

// Hook for fetching timesheet batch data
export function useTimesheetBatch(
  weekStartDate?: string,
  includeHistory: boolean = true,
  historyLimit: number = 10
) {
  const [data, setData] = useState<TimesheetBatchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await TimesheetApiService.getMyTimesheetBatch(
        weekStartDate,
        includeHistory,
        historyLimit
      );
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch timesheet data'));
    } finally {
      setLoading(false);
    }
  }, [weekStartDate, includeHistory, historyLimit]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refetch: fetchData
  };
}

// Hook for paginated timesheet history
export function useTimesheetHistoryPagination(pageSize: number = 10) {
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
  const [currentPage, setCurrentPage] = useState(1);

  const fetchData = useCallback(async (page: number = 1) => {
    setLoading(true);
    setError(null);
    
    const skip = (page - 1) * pageSize;
    
    try {
      const result = await TimesheetApiService.getMyTimesheetHistory(skip, pageSize);
      setData(result);
      setCurrentPage(page);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch timesheet history'));
    } finally {
      setLoading(false);
    }
  }, [pageSize]);

  const goToPage = useCallback((page: number) => {
    if (page >= 1) {
      fetchData(page);
    }
  }, [fetchData]);

  const nextPage = useCallback(() => {
    if (data?.has_next) {
      goToPage(currentPage + 1);
    }
  }, [data?.has_next, currentPage, goToPage]);

  const previousPage = useCallback(() => {
    if (data?.has_previous) {
      goToPage(currentPage - 1);
    }
  }, [data?.has_previous, currentPage, goToPage]);

  useEffect(() => {
    fetchData(1);
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    currentPage,
    totalPages: data ? Math.ceil(data.total_count / pageSize) : 0,
    goToPage,
    nextPage,
    previousPage,
    refetch: () => fetchData(currentPage)
  };
}

// Hook for daily entry
export function useDailyEntry(workDate: string) {
  const [data, setData] = useState<TimesheetDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await TimesheetApiService.getMyDailyEntry(workDate);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch daily entry'));
    } finally {
      setLoading(false);
    }
  }, [workDate]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refetch: fetchData
  };
}

// Hook for timesheet status polling
export function useTimesheetStatus(
  timesheetId: number | null,
  pollInterval: number = 5000
) {
  const [status, setStatus] = useState<Timesheet['StatusCode'] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchStatus = useCallback(async () => {
    if (!timesheetId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await TimesheetApiService.getTimesheetStatus(timesheetId);
      setStatus(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch timesheet status'));
    } finally {
      setLoading(false);
    }
  }, [timesheetId]);

  useEffect(() => {
    if (!timesheetId) return;

    fetchStatus();

    // Only poll if timesheet is submitted (not approved/rejected)
    if (status === 'Submitted') {
      const interval = setInterval(fetchStatus, pollInterval);
      return () => clearInterval(interval);
    }
  }, [timesheetId, status, pollInterval, fetchStatus]);

  return {
    status,
    loading,
    error,
    refetch: fetchStatus
  };
}

// Hook for saving daily entry
export function useSaveDailyEntry() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [success, setSuccess] = useState(false);

  const saveEntry = useCallback(async (entryData: DailyEntryFormData) => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    
    try {
      await TimesheetApiService.createMyDailyEntry(entryData);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to save daily entry'));
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    saveEntry,
    loading,
    error,
    success
  };
}

// Hook for bulk saving entries
export function useBulkSaveEntries() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [success, setSuccess] = useState(false);
  const [progress, setProgress] = useState(0);

  const bulkSave = useCallback(async (entries: DailyEntryFormData[]) => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    setProgress(0);
    
    try {
      const result = await TimesheetApiService.bulkSaveDailyEntries(entries);
      
      if (result.success) {
        setSuccess(true);
        setProgress(100);
      } else {
        setError(new Error(`Failed to save some entries: ${result.errors.join(', ')}`));
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to bulk save entries'));
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    bulkSave,
    loading,
    error,
    success,
    progress
  };
}

// Hook for submitting timesheet
export function useSubmitTimesheet() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [success, setSuccess] = useState(false);

  const submitTimesheet = useCallback(async (timesheetId: number) => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    
    try {
      await TimesheetApiService.submitMyTimesheet(timesheetId);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to submit timesheet'));
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    submitTimesheet,
    loading,
    error,
    success
  };
} 