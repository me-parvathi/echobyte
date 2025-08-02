import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { api } from '@/lib/api';
import type { 
  LeaveApplication, 
  LeaveApplicationCreate, 
  LeaveApplicationUpdate,
  LeaveType,
  LeaveBalanceSummary,
  LeaveDaysCalculation,
  TimesheetConflict,
  PaginatedLeaveResponse,
  LeaveFilterParams,
  PaginationParams
} from '@/lib/types';

interface UseLeaveOptions {
  employeeId?: number;
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
}

export function useLeaveManagement(options: UseLeaveOptions = {}) {
  const [leaveApplications, setLeaveApplications] = useState<LeaveApplication[]>([]);
  const [leaveTypes, setLeaveTypes] = useState<LeaveType[]>([]);
  const [leaveBalance, setLeaveBalance] = useState<LeaveBalanceSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const hasFetched = useRef(false);
  const isMounted = useRef(true);
  
  // Pagination state
  const [pagination, setPagination] = useState<PaginationParams>({
    skip: 0,
    limit: 5,
    page: 1
  });
  
  // Filter state
  const [filters, setFilters] = useState<LeaveFilterParams>({});
  
  // Pagination info
  const [paginationInfo, setPaginationInfo] = useState({
    total: 0,
    pages: 0,
    has_next: false,
    has_previous: false
  });

  const { employeeId, immediate = true, onSuccess, onError } = options;

  // Memoize the callbacks to prevent unnecessary re-renders
  const memoizedOnSuccess = useCallback(onSuccess || (() => {}), []);
  const memoizedOnError = useCallback(onError || (() => {}), []);

  // Fetch leave applications with pagination and filters
  const fetchLeaveApplications = useCallback(async (
    employeeId?: number,
    paginationParams?: PaginationParams,
    filterParams?: LeaveFilterParams
  ) => {
    console.log('🔄 useLeaveManagement fetch', { 
      employeeId, 
      paginationParams, 
      filterParams,
      hasFetched: hasFetched.current,
      isMounted: isMounted.current
    });
    
    if (hasFetched.current || !isMounted.current) {
      console.log('⏭️ Skipping leave applications fetch - already fetched or component unmounted');
      return;
    }
    
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      
      // Add pagination parameters
      const pagination = paginationParams || { skip: 0, limit: 10 };
      if (pagination.skip !== undefined) params.append('skip', pagination.skip.toString());
      if (pagination.limit !== undefined) params.append('limit', pagination.limit.toString());
      
      // Add filter parameters
      const filters = filterParams || {};
      if (employeeId) params.append('employee_id', employeeId.toString());
      if (filters.status_code) params.append('status_code', filters.status_code);
      if (filters.start_date) params.append('start_date', filters.start_date);
      if (filters.end_date) params.append('end_date', filters.end_date);
      if (filters.leave_type_id) params.append('leave_type_id', filters.leave_type_id.toString());
      
      const endpoint = `/api/leave/applications${params.toString() ? `?${params.toString()}` : ''}`;
      const result = await api.get<PaginatedLeaveResponse>(endpoint);
      
      // Update state unconditionally – React will ignore setState on an unmounted component during development strict-mode.
      setLeaveApplications(result.items);
      setPaginationInfo({
        total: result.total_count,
        pages: Math.ceil(result.total_count / (pagination.limit || 10)),
        has_next: result.has_next,
        has_previous: result.has_previous
      });
      memoizedOnSuccess(result);
      hasFetched.current = true;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch leave applications');
      
      setError(error);
      memoizedOnError(error);
    } finally {
      // Always clear loading state – even if the first render was un-mounted (React Strict-Mode).
      // The state update is safe because React silently ignores setState on an unmounted component in dev.
      setLoading(false);
    }
  }, [memoizedOnSuccess, memoizedOnError]);

  // Update pagination
  const updatePagination = useCallback((newPagination: PaginationParams) => {
    setPagination(newPagination);
    hasFetched.current = false;
    fetchLeaveApplications(employeeId, newPagination, filters);
  }, [employeeId, filters, fetchLeaveApplications]);

  // Update filters
  const updateFilters = useCallback((newFilters: LeaveFilterParams) => {
    setFilters(newFilters);
    hasFetched.current = false;
    fetchLeaveApplications(employeeId, pagination, newFilters);
  }, [employeeId, pagination, fetchLeaveApplications]);

  // Clear filters
  const clearFilters = useCallback(() => {
    setFilters({});
    hasFetched.current = false;
    fetchLeaveApplications(employeeId, pagination, {});
  }, [employeeId, pagination, fetchLeaveApplications]);

  // Navigation methods
  const nextPage = useCallback(() => {
    if (paginationInfo.has_next) {
      const newPagination = {
        ...pagination,
        skip: (pagination.skip || 0) + (pagination.limit || 10),
        page: (pagination.page || 1) + 1
      };
      updatePagination(newPagination);
    }
  }, [pagination, paginationInfo.has_next, updatePagination]);

  const previousPage = useCallback(() => {
    if (paginationInfo.has_previous) {
      const newPagination = {
        ...pagination,
        skip: Math.max(0, (pagination.skip || 0) - (pagination.limit || 10)),
        page: Math.max(1, (pagination.page || 1) - 1)
      };
      updatePagination(newPagination);
    }
  }, [pagination, paginationInfo.has_previous, updatePagination]);

  const goToPage = useCallback((page: number) => {
    const newPagination = {
      ...pagination,
      skip: (page - 1) * (pagination.limit || 10),
      page
    };
    updatePagination(newPagination);
  }, [pagination, updatePagination]);

  // Fetch leave types
  const fetchLeaveTypes = useCallback(async () => {
    try {
      const result = await api.get<LeaveType[]>('/api/leave/types');
      setLeaveTypes(result);
    } catch (err) {
      console.error('Failed to fetch leave types:', err);
    }
  }, []);

  // Fetch leave balance
  const fetchLeaveBalance = useCallback(async () => {
    try {
      const result = await api.get<LeaveBalanceSummary>('/api/leave/my/balance/summary');
      setLeaveBalance(result);
    } catch (err) {
      console.error('Failed to fetch leave balance:', err);
    }
  }, []);

  // Create leave application
  const createLeaveApplication = useCallback(async (application: LeaveApplicationCreate): Promise<LeaveApplication> => {
    try {
      const result = await api.post<LeaveApplication>('/api/leave/applications', application);
      // Refresh the list and balance after creating
      hasFetched.current = false;
      await Promise.all([
        fetchLeaveApplications(employeeId, pagination, filters),
        fetchLeaveBalance()
      ]);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to create leave application');
      throw error;
    }
  }, [employeeId, pagination, filters, fetchLeaveApplications, fetchLeaveBalance]);

  // Update leave application
  const updateLeaveApplication = useCallback(async (applicationId: number, updates: LeaveApplicationUpdate): Promise<LeaveApplication> => {
    try {
      const result = await api.put<LeaveApplication>(`/api/leave/applications/${applicationId}`, updates);
      // Refresh the list and balance after updating
      hasFetched.current = false;
      await Promise.all([
        fetchLeaveApplications(employeeId, pagination, filters),
        fetchLeaveBalance()
      ]);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to update leave application');
      throw error;
    }
  }, [employeeId, pagination, filters, fetchLeaveApplications, fetchLeaveBalance]);

  // Delete leave application
  const deleteLeaveApplication = useCallback(async (applicationId: number): Promise<void> => {
    try {
      await api.delete(`/api/leave/applications/${applicationId}`);
      // Refresh the list and balance after deleting
      hasFetched.current = false;
      await Promise.all([
        fetchLeaveApplications(employeeId, pagination, filters),
        fetchLeaveBalance()
      ]);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to delete leave application');
      throw error;
    }
  }, [employeeId, pagination, filters, fetchLeaveApplications, fetchLeaveBalance]);

  // Cancel leave application
  const cancelLeaveApplication = useCallback(async (applicationId: number): Promise<LeaveApplication> => {
    try {
      const result = await api.post<LeaveApplication>(`/api/leave/applications/${applicationId}/cancel`);
      // Refresh the list and balance after cancelling
      hasFetched.current = false;
      await Promise.all([
        fetchLeaveApplications(employeeId, pagination, filters),
        fetchLeaveBalance()
      ]);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to cancel leave application');
      throw error;
    }
  }, [employeeId, pagination, filters, fetchLeaveApplications, fetchLeaveBalance]);

  // Calculate leave days
  const calculateLeaveDays = useCallback(async (
    startDate: string,
    endDate: string,
    calculationType: string = 'business',
    excludeHolidays: boolean = true
  ): Promise<LeaveDaysCalculation> => {
    try {
      const params = new URLSearchParams();
      params.append('start_date', startDate);
      params.append('end_date', endDate);
      params.append('calculation_type', calculationType);
      params.append('exclude_holidays', excludeHolidays.toString());
      
      const result = await api.get<LeaveDaysCalculation>(`/api/leave/calculate-days?${params.toString()}`);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to calculate leave days');
      throw error;
    }
  }, []);

  // Check timesheet conflicts
  const checkTimesheetConflicts = useCallback(async (startDate: string, endDate: string, managerId?: number): Promise<TimesheetConflict> => {
    try {
      const params = new URLSearchParams();
      params.append('start_date', startDate);
      params.append('end_date', endDate);
      if (managerId) params.append('manager_id', managerId.toString());
      
      const result = await api.get<TimesheetConflict>(`/api/leave/check-conflicts?${params.toString()}`);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to check timesheet conflicts');
      throw error;
    }
  }, []);

  // Refresh data
  const refreshData = useCallback(async () => {
    hasFetched.current = false;
    await fetchLeaveApplications(employeeId, pagination, filters);
  }, [employeeId, pagination, filters, fetchLeaveApplications]);

  // Initial data fetch or when employee changes
  useEffect(() => {
    console.log('🔄 useLeaveManagement useEffect triggered', { immediate, hasFetched: hasFetched.current, employeeId });
    if (immediate) {
      // If employeeId just became available reset the fetched flag to ensure fresh data
      hasFetched.current = false;
      fetchLeaveApplications(employeeId, pagination, filters);
      fetchLeaveTypes();
      fetchLeaveBalance();
    }
  }, [immediate, employeeId, pagination, filters, fetchLeaveApplications, fetchLeaveTypes, fetchLeaveBalance]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMounted.current = false;
    };
  }, []);

  return {
    leaveApplications,
    leaveTypes,
    leaveBalance,
    loading,
    error,
    pagination,
    paginationInfo,
    filters,
    updatePagination,
    updateFilters,
    clearFilters,
    nextPage,
    previousPage,
    goToPage,
    createLeaveApplication,
    updateLeaveApplication,
    deleteLeaveApplication,
    cancelLeaveApplication,
    calculateLeaveDays,
    checkTimesheetConflicts,
    refreshData
  };
} 