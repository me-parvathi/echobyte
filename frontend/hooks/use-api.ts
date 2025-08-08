import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

interface UseApiOptions {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
}

export function useApi<T>(
  endpoint: string | null,
  options: UseApiOptions = {}
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const { immediate = true, onSuccess, onError } = options;

  const fetchData = async () => {
    if (!endpoint) return;

    setLoading(true);
    setError(null);

    try {
      const result = await api.get<T>(endpoint);
      setData(result);
      onSuccess?.(result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      onError?.(error);
    } finally {
      setLoading(false);
    }
  };

  const mutate = async (newData: T) => {
    setData(newData);
  };

  const refetch = () => {
    fetchData();
  };

  useEffect(() => {
    if (immediate && endpoint) {
      fetchData();
    }
  }, [endpoint, immediate]);

  return {
    data,
    loading,
    error,
    refetch,
    mutate,
  };
}