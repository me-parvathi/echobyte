import { useState, useEffect, useCallback, useRef, useMemo } from "react";
import { api } from "@/lib/api";
import {
  Employee,
  EmployeeListResponse,
  ManagerTeamOverviewResponse,
  EmployeeFeedbackTargetResponse,
} from "@/lib/types";

/**
 * Simple in-memory caches so that multiple instances of the hook share the same
 * network request and response when they ask for the exact same endpoint.
 * This eliminates the three duplicate 42-second `/api/employees` calls that
 * were happening when the Leave page loaded through the Dashboard layout.
 */
type TimedPromise<T> = { promise: Promise<T>; startedAt: number };
const employeesResultCache = new Map<string, EmployeeListResponse>();
const employeesPromiseCache = new Map<
  string,
  TimedPromise<EmployeeListResponse>
>();
const INFLIGHT_TTL_MS = 10000; // 10s safety to avoid stale promises after Fast Refresh/runtime errors

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

/** 🔧 Helper to build a stable endpoint string from filters */
const buildEmployeesEndpoint = (f: EmployeeFilters) => {
  const qp = new URLSearchParams();
  if (f.skip !== undefined) qp.append("skip", String(f.skip));
  if (f.limit !== undefined) qp.append("limit", String(f.limit));
  if (f.team_id !== undefined) qp.append("team_id", String(f.team_id));
  if (f.department_id !== undefined)
    qp.append("department_id", String(f.department_id));
  if (f.search) qp.append("search", f.search);
  return `/employees/?${qp.toString()}`;
};

export function useEmployees(
  filters: EmployeeFilters = {},
  options: UseEmployeesOptions = {}
) {
  const [data, setData] = useState<EmployeeListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // ✅ keep a single "already handled this endpoint" guard
  const hasFetched = useRef(false);
  const fetchCount = useRef(0);

  // ✅ used only to prevent setState after unmount/replace (StrictMode-safe)
  const abortedRef = useRef(false);

  const { immediate = true, onSuccess, onError } = options;

  // Memoize the filters object to prevent unnecessary re-renders
  const memoizedFilters = useMemo(
    () => filters,
    [
      filters.skip,
      filters.limit,
      filters.team_id,
      filters.department_id,
      filters.search,
    ]
  );

  // ✅ computed endpoint from filters (stable key for caches/guards)
  const endpoint = useMemo(
    () => buildEmployeesEndpoint(memoizedFilters),
    [memoizedFilters]
  );

  // ✅ Reset the guard whenever the endpoint changes (new filters => new fetch)
  useEffect(() => {
    hasFetched.current = false;
  }, [endpoint]);

  // Memoize the callbacks to prevent unnecessary re-renders
  const memoizedOnSuccess = useCallback(onSuccess || (() => {}), []);
  const memoizedOnError = useCallback(onError || (() => {}), []);

  const fetchEmployees = useCallback(async () => {
    fetchCount.current += 1;
    console.log(`🔄 useEmployees fetch #${fetchCount.current}`, {
      endpoint,
      hasFetched: hasFetched.current,
      immediate,
    });

    // Only skip when we truly have fetched for THIS endpoint already
    if (hasFetched.current) {
      console.log("⏭️ Skipping fetch - already fetched for this endpoint");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 1) serve from cache if already fetched
      if (employeesResultCache.has(endpoint)) {
        console.log("✅ Employees served from cache");
        const cached = employeesResultCache.get(endpoint)!;
        if (!abortedRef.current) {
          setData(cached);
          memoizedOnSuccess(cached);
          hasFetched.current = true;
          setLoading(false);
        }
        return;
      }

      // 2) if a request is already in-flight for this endpoint, wait for it — unless it went stale
      const timed = employeesPromiseCache.get(endpoint);
      const now = Date.now();
      let requestPromise: Promise<EmployeeListResponse>;

      if (timed && now - timed.startedAt < INFLIGHT_TTL_MS) {
        console.log("⏳ Waiting for ongoing employees request", endpoint);
        requestPromise = timed.promise;
      } else {
        if (timed) {
          console.warn(
            "⏱️ Stale employees request detected — refetching",
            endpoint
          );
          employeesPromiseCache.delete(endpoint);
        }
        console.log("🌐 Sending employees request to API", endpoint);
        requestPromise = api.get<EmployeeListResponse>(endpoint);
        employeesPromiseCache.set(endpoint, {
          promise: requestPromise,
          startedAt: now,
        });
      }

      const result = await requestPromise;
      employeesResultCache.set(endpoint, result); // store final response
      employeesPromiseCache.delete(endpoint);

      if (!abortedRef.current) {
        setData(result);
        memoizedOnSuccess(result);
        hasFetched.current = true;
      }
    } catch (err) {
      console.error("Error fetching employees:", err);
      const e =
        err instanceof Error ? err : new Error("Failed to fetch employees");
      if (!abortedRef.current) {
        setError(e);
        memoizedOnError(e);
      }
    } finally {
      if (!abortedRef.current) setLoading(false);
    }
  }, [endpoint, immediate, memoizedOnSuccess, memoizedOnError]);

  const refetch = useCallback(() => {
    console.log("🔄 Manual refetch requested");
    hasFetched.current = false;
    fetchEmployees();
  }, [fetchEmployees]);

  useEffect(() => {
    console.log("🔄 useEmployees useEffect triggered", {
      immediate,
      hasFetched: hasFetched.current,
      endpoint,
    });

    if (!immediate) return;

    abortedRef.current = false;
    fetchEmployees();

    // StrictMode cleanup guard (prevents setState after unmount)
    return () => {
      abortedRef.current = true;
    };
  }, [immediate, endpoint, fetchEmployees]);

  // Dev helper to recover after a bad HMR state
  if (typeof window !== "undefined") {
    // @ts-ignore
    (window as any).__clearEmployeesCaches = () => {
      employeesResultCache.clear();
      employeesPromiseCache.clear();
      console.log("🧹 Cleared employees caches");
    };
  }

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
      const result = await api.get<Employee>("/employees/profile/current");
      setData(result);
      onSuccess?.(result);
    } catch (err) {
      const error =
        err instanceof Error
          ? err
          : new Error("Failed to fetch current employee");
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
      const result = await api.get<ManagerTeamOverviewResponse>(
        "/employees/manager/team-overview"
      );
      setData(result);
      onSuccess?.(result);
    } catch (err) {
      const error =
        err instanceof Error ? err : new Error("Failed to fetch team overview");
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
      const result = await api.get<EmployeeFeedbackTargetResponse[]>(
        "/employees/feedback-targets"
      );
      setData(result);
      onSuccess?.(result);
    } catch (err) {
      const error =
        err instanceof Error
          ? err
          : new Error("Failed to fetch feedback targets");
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
      const currentEmployee = await api.get<Employee>(
        "/employees/profile/current"
      );
      if (!currentEmployee) {
        throw new Error("Current employee not found");
      }

      // Then get their hierarchy
      const result = await api.get<Employee[]>(
        `/employees/${currentEmployee.EmployeeID}/hierarchy`
      );
      setData(result);
      onSuccess?.(result);
    } catch (err) {
      const error =
        err instanceof Error
          ? err
          : new Error("Failed to fetch employee hierarchy");
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
