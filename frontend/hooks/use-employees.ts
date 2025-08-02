import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { api } from '@/lib/api';
import { Employee, EmployeeListResponse, ManagerTeamOverviewResponse, EmployeeFeedbackTargetResponse } from '@/lib/types';

/**
 * Simple in-memory caches so that multiple instances of the hook share the same
 * network request and response when they ask for the exact same endpoint.
 * This eliminates the three duplicate 42-second `/api/employees` calls that
 * were happening when the Leave page loaded through the Dashboard layout.
 */
const employeesResultCache = new Map<string, EmployeeListResponse>();
const employeesPromiseCache = new Map<string, Promise<EmployeeListResponse>>();

interface UseEmployeesOptions {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
}

interface EmployeeFilters {
  skip?: number;
  limit?: number;
  team_id?: number;
  department_id?: number;
  search?: string;
}

export function useEmployees(filters: EmployeeFilters = {}, options: UseEmployeesOptions = {}) {
  const [data, setData] = useState<EmployeeListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const hasFetched = useRef(false);
  const fetchCount = useRef(0);
  const isMounted = useRef(true);

  const { immediate = true, onSuccess, onError } = options;

  // Memoize the filters object to prevent unnecessary re-renders
  const memoizedFilters = useMemo(() => filters, [
    filters.skip,
    filters.limit,
    filters.team_id,
    filters.department_id,
    filters.search
  ]);

  // Memoize the callbacks to prevent unnecessary re-renders
  const memoizedOnSuccess = useCallback(onSuccess || (() => {}), []);
  const memoizedOnError = useCallback(onError || (() => {}), []);

  const fetchEmployees = useCallback(async () => {
    fetchCount.current += 1;
    console.log(`🔄 useEmployees fetch #${fetchCount.current}`, { 
      filters: memoizedFilters, 
      hasFetched: hasFetched.current,
      immediate,
      isMounted: isMounted.current
    });
    
    if (hasFetched.current || !isMounted.current) {
      console.log('⏭️ Skipping fetch - already fetched or component unmounted');
      return;
    }
    
    setLoading(true);
    setError(null);

    try {
      const queryParams = new URLSearchParams();
      if (memoizedFilters.skip !== undefined) queryParams.append('skip', memoizedFilters.skip.toString());
      if (memoizedFilters.limit !== undefined) queryParams.append('limit', memoizedFilters.limit.toString());
      if (memoizedFilters.team_id !== undefined) queryParams.append('team_id', memoizedFilters.team_id.toString());
      if (memoizedFilters.department_id !== undefined) queryParams.append('department_id', memoizedFilters.department_id.toString());
      if (memoizedFilters.search) queryParams.append('search', memoizedFilters.search);

      const endpoint = `/employees/?${queryParams.toString()}`;
      console.log('Fetching employees from:', endpoint);

      // 1) serve from cache if already fetched
      if (employeesResultCache.has(endpoint)) {
        console.log('✅ Employees served from cache');
        const cached = employeesResultCache.get(endpoint)!;
        if (isMounted.current) {
          setData(cached);
          memoizedOnSuccess(cached);
          hasFetched.current = true;
          setLoading(false);
        }
        return;
      }

      // 2) if a request is already in-flight for this endpoint, wait for it
      let requestPromise: Promise<EmployeeListResponse>;
      if (employeesPromiseCache.has(endpoint)) {
        console.log('⏳ Waiting for ongoing employees request');
        requestPromise = employeesPromiseCache.get(endpoint)!;
      } else {
        console.log('🌐 Sending employees request to API');
        requestPromise = api.get<EmployeeListResponse>(endpoint);
        employeesPromiseCache.set(endpoint, requestPromise);
      }

      const result = await requestPromise;
      employeesResultCache.set(endpoint, result); // store final response
      employeesPromiseCache.delete(endpoint);
      console.log('Employees response:', result);
      
      // Only update state if component is still mounted
      if (isMounted.current) {
        setData(result);
        memoizedOnSuccess(result);
        hasFetched.current = true;
      }
    } catch (err) {
      console.error('Error fetching employees:', err);
      const error = err instanceof Error ? err : new Error('Failed to fetch employees');
      
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
  }, [memoizedFilters, memoizedOnSuccess, memoizedOnError]);

  const refetch = useCallback(() => {
    console.log('🔄 Manual refetch requested');
    hasFetched.current = false;
    fetchEmployees();
  }, [fetchEmployees]);

  useEffect(() => {
    console.log('🔄 useEmployees useEffect triggered', { immediate, hasFetched: hasFetched.current });
    if (immediate) {
      fetchEmployees();
    }
  }, [immediate, fetchEmployees]);

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
    refetch,
  };
}

export function useCurrentEmployee(options: UseEmployeesOptions = {}) {
  const [data, setData] = useState<Employee | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const { immediate = true, onSuccess, onError } = options;

  const fetchCurrentEmployee = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await api.get<Employee>('/employees/profile/current');
      setData(result);
      onSuccess?.(result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch current employee');
      setError(error);
      onError?.(error);
    } finally {
      setLoading(false);
    }
  }, [onSuccess, onError]);

  const refetch = useCallback(() => {
    fetchCurrentEmployee();
  }, [fetchCurrentEmployee]);

  useEffect(() => {
    if (immediate) {
      fetchCurrentEmployee();
    }
  }, [immediate, fetchCurrentEmployee]);

  return {
    data,
    loading,
    error,
    refetch,
  };
}

export function useManagerTeamOverview(options: UseEmployeesOptions = {}) {
  const [data, setData] = useState<ManagerTeamOverviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const { immediate = true, onSuccess, onError } = options;

  const fetchTeamOverview = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await api.get<ManagerTeamOverviewResponse>('/employees/manager/team-overview');
      setData(result);
      onSuccess?.(result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch team overview');
      setError(error);
      onError?.(error);
    } finally {
      setLoading(false);
    }
  }, [onSuccess, onError]);

  const refetch = useCallback(() => {
    fetchTeamOverview();
  }, [fetchTeamOverview]);

  useEffect(() => {
    if (immediate) {
      fetchTeamOverview();
    }
  }, [immediate, fetchTeamOverview]);

  return {
    data,
    loading,
    error,
    refetch,
  };
}

export function useFeedbackTargets(options: UseEmployeesOptions = {}) {
  const [data, setData] = useState<EmployeeFeedbackTargetResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const { immediate = true, onSuccess, onError } = options;

  const fetchFeedbackTargets = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await api.get<EmployeeFeedbackTargetResponse[]>('/employees/feedback-targets');
      setData(result);
      onSuccess?.(result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch feedback targets');
      setError(error);
      onError?.(error);
    } finally {
      setLoading(false);
    }
  }, [onSuccess, onError]);

  const refetch = useCallback(() => {
    fetchFeedbackTargets();
  }, [fetchFeedbackTargets]);

  useEffect(() => {
    if (immediate) {
      fetchFeedbackTargets();
    }
  }, [immediate, fetchFeedbackTargets]);

  return {
    data,
    loading,
    error,
    refetch,
  };
}

export function useCurrentEmployeeHierarchy(options: UseEmployeesOptions = {}) {
  const [data, setData] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const { immediate = true, onSuccess, onError } = options;

  const fetchHierarchy = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // First get current employee to get their ID
      const currentEmployee = await api.get<Employee>('/employees/profile/current');
      if (!currentEmployee) {
        throw new Error('Current employee not found');
      }

      // Then get their hierarchy
      const result = await api.get<Employee[]>(`/employees/${currentEmployee.EmployeeID}/hierarchy`);
      setData(result);
      onSuccess?.(result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch employee hierarchy');
      setError(error);
      onError?.(error);
    } finally {
      setLoading(false);
    }
  }, [onSuccess, onError]);

  const refetch = useCallback(() => {
    fetchHierarchy();
  }, [fetchHierarchy]);

  useEffect(() => {
    if (immediate) {
      fetchHierarchy();
    }
  }, [immediate, fetchHierarchy]);

  return {
    data,
    loading,
    error,
    refetch,
  };
} 