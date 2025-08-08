import { useState, useCallback } from 'react';
import { api } from '@/lib/api';
import type { 
  Timesheet, 
  TimesheetApprovalRequest
} from '@/lib/types';

interface UseTimesheetApprovalOptions {
  approverId?: number;
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
}

export function useTimesheetApproval(options: UseTimesheetApprovalOptions = {}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const { approverId, onSuccess, onError } = options;

  // Approve or reject timesheet
  const approveTimesheet = useCallback(async (
    timesheetId: number, 
    approval: TimesheetApprovalRequest
  ): Promise<Timesheet> => {
    setLoading(true);
    setError(null);

    try {
      const result = await api.post<Timesheet>(
        `/api/timesheets/${timesheetId}/approve`,
        approval
      );
      
      onSuccess?.(result);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to approve timesheet');
      setError(error);
      onError?.(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [onSuccess, onError]);

  return {
    loading,
    error,
    approveTimesheet,
  };
} 