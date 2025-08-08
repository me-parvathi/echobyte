import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '@/lib/api';
import { Team, TeamListResponse, Department } from '@/lib/types';

interface UseTeamsOptions {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
}

interface TeamFilters {
  skip?: number;
  limit?: number;
  is_active?: boolean;
  department_id?: number;
}

export function useTeams(filters: TeamFilters = {}, options: UseTeamsOptions = {}) {
  const [data, setData] = useState<TeamListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const { immediate = true, onSuccess, onError } = options;

  const fetchTeams = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const queryParams = new URLSearchParams();
      if (filters.skip !== undefined) queryParams.append('skip', filters.skip.toString());
      if (filters.limit !== undefined) queryParams.append('limit', filters.limit.toString());
      if (filters.is_active !== undefined) queryParams.append('is_active', filters.is_active.toString());
      if (filters.department_id !== undefined) queryParams.append('department_id', filters.department_id.toString());

      const endpoint = `/teams/?${queryParams.toString()}`;
      const result = await api.get<TeamListResponse>(endpoint);
      setData(result);
      onSuccess?.(result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch teams');
      setError(error);
      onError?.(error);
    } finally {
      setLoading(false);
    }
  }, [filters, onSuccess, onError]);

  const refetch = useCallback(() => {
    fetchTeams();
  }, [fetchTeams]);

  useEffect(() => {
    if (immediate) {
      fetchTeams();
    }
  }, [immediate, fetchTeams]);

  return {
    data,
    loading,
    error,
    refetch,
  };
}

export function useTeam(teamId: number | null, options: UseTeamsOptions = {}) {
  const [data, setData] = useState<Team | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const { immediate = true, onSuccess, onError } = options;

  const fetchTeam = useCallback(async () => {
    if (!teamId) return;
    
    setLoading(true);
    setError(null);

    try {
      const result = await api.get<Team>(`/teams/${teamId}`);
      setData(result);
      onSuccess?.(result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch team');
      setError(error);
      onError?.(error);
    } finally {
      setLoading(false);
    }
  }, [teamId, onSuccess, onError]);

  const refetch = useCallback(() => {
    fetchTeam();
  }, [fetchTeam]);

  useEffect(() => {
    if (immediate && teamId) {
      fetchTeam();
    }
  }, [immediate, teamId, fetchTeam]);

  return {
    data,
    loading,
    error,
    refetch,
  };
}

export function useTeamMembers(teamId: number | null, options: UseTeamsOptions = {}) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const { immediate = true, onSuccess, onError } = options;

  const fetchTeamMembers = useCallback(async () => {
    if (!teamId) return;
    
    setLoading(true);
    setError(null);

    try {
      const result = await api.get<any[]>(`/teams/${teamId}/members`);
      setData(result);
      onSuccess?.(result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch team members');
      setError(error);
      onError?.(error);
    } finally {
      setLoading(false);
    }
  }, [teamId, onSuccess, onError]);

  const refetch = useCallback(() => {
    fetchTeamMembers();
  }, [fetchTeamMembers]);

  useEffect(() => {
    if (immediate && teamId) {
      fetchTeamMembers();
    }
  }, [immediate, teamId, fetchTeamMembers]);

  return {
    data,
    loading,
    error,
    refetch,
  };
} 

export function useTeamsAndDepartments(options: UseTeamsOptions = {}) {
  const [teamsData, setTeamsData] = useState<TeamListResponse | null>(null);
  const [departmentsData, setDepartmentsData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const hasFetched = useRef(false);
  const isMounted = useRef(true);

  const { immediate = true, onSuccess, onError } = options;

  // Memoize the callbacks to prevent unnecessary re-renders
  const memoizedOnSuccess = useCallback(onSuccess || (() => {}), []);
  const memoizedOnError = useCallback(onError || (() => {}), []);

  const fetchData = useCallback(async () => {
    console.log('🔄 useTeamsAndDepartments fetch', { hasFetched: hasFetched.current, isMounted: isMounted.current });
    
    if (hasFetched.current || !isMounted.current) {
      console.log('⏭️ Skipping teams/departments fetch - already fetched or component unmounted');
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      // Fetch teams and departments in parallel
      const [teamsResult, departmentsResult] = await Promise.all([
        api.get<TeamListResponse>('/teams'),
        api.get<any>('/departments')
      ]);
      
      // Only update state if component is still mounted
      if (isMounted.current) {
        setTeamsData(teamsResult);
        setDepartmentsData(departmentsResult);
        memoizedOnSuccess({ teams: teamsResult, departments: departmentsResult });
        hasFetched.current = true;
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch teams and departments');
      
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
  }, [memoizedOnSuccess, memoizedOnError]);

  const refetch = useCallback(() => { 
    console.log('🔄 Manual teams/departments refetch requested');
    hasFetched.current = false;
    fetchData(); 
  }, [fetchData]);

  useEffect(() => {
    console.log('🔄 useTeamsAndDepartments useEffect triggered', { immediate, hasFetched: hasFetched.current });
    if (immediate) { 
      fetchData(); 
    }
  }, [immediate, fetchData]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMounted.current = false;
    };
  }, []);

  return { 
    teamsData, 
    departmentsData, 
    loading, 
    error, 
    refetch 
  };
} 