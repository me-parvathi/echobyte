import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '@/lib/api';
import { 
  Ticket, 
  TicketCreate, 
  TicketUpdate, 
  TicketListResponse, 
  TicketFilterParams,
  TicketActivity,
  TicketActivityCreate,
  TicketAttachment,
  TicketStatus,
  TicketPriority,
  TicketCategory,
  AssetSelectionResponse,
  TicketStatistics,
  PendingStatus
} from '@/lib/types';

interface UseTicketsOptions {
  immediate?: boolean;
  filters?: TicketFilterParams;
  pageSize?: number;
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
}

export function useTickets(options: UseTicketsOptions = {}) {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrevious, setHasPrevious] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(options.pageSize || 20);

  // Request deduplication
  const requestRef = useRef<AbortController | null>(null);
  const isRequestingRef = useRef(false);
  const initialFetchDoneRef = useRef(false);
  const optionsRef = useRef(options);

  // Update options ref when options change
  useEffect(() => {
    optionsRef.current = options;
  }, [options]);

  const fetchTickets = useCallback(async (params?: TicketFilterParams, page: number = 1) => {
    // Cancel any ongoing request
    if (requestRef.current) {
      requestRef.current.abort();
    }

    // Prevent duplicate requests
    if (isRequestingRef.current) {
      return;
    }

    setLoading(true);
    setError(null);
    isRequestingRef.current = true;

    // Create new abort controller
    requestRef.current = new AbortController();

    try {
      const queryParams = new URLSearchParams();
      const finalParams = { ...optionsRef.current.filters, ...params };
      
      // Add pagination parameters
      const skip = (page - 1) * pageSize;
      queryParams.append('skip', skip.toString());
      queryParams.append('limit', pageSize.toString());
      
      Object.entries(finalParams).forEach(([key, value]) => {
        if (value !== undefined && value !== null && key !== 'skip' && key !== 'limit') {
          queryParams.append(key, value.toString());
        }
      });

      const endpoint = `/api/tickets/?${queryParams.toString()}`;
      const result: TicketListResponse = await api.get(endpoint, {
        signal: requestRef.current.signal
      });
      
      setTickets(result.items);
      setTotalCount(result.total_count);
      setHasNext(result.has_next);
      setHasPrevious(result.has_previous);
      setCurrentPage(page);
      optionsRef.current.onSuccess?.(result);
    } catch (err) {
      // Don't set error if request was aborted
      if (err instanceof Error && err.name === 'AbortError') {
        return;
      }
      const error = err instanceof Error ? err : new Error('Failed to fetch tickets');
      setError(error);
      optionsRef.current.onError?.(error);
    } finally {
      setLoading(false);
      isRequestingRef.current = false;
      requestRef.current = null;
    }
  }, [pageSize]); // Only depend on pageSize

  const createTicket = useCallback(async (ticketData: TicketCreate, openedById: number) => {
    setLoading(true);
    setError(null);

    try {
      const queryParams = new URLSearchParams({ opened_by_id: openedById.toString() });
      const endpoint = `/api/tickets/?${queryParams.toString()}`;
      const result: Ticket = await api.post(endpoint, ticketData);
      
      // Add the new ticket to the list
      setTickets(prev => [result, ...prev]);
      setTotalCount(prev => prev + 1);
      optionsRef.current.onSuccess?.(result);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to create ticket');
      setError(error);
      optionsRef.current.onError?.(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateTicket = useCallback(async (ticketId: number, updateData: TicketUpdate) => {
    setLoading(true);
    setError(null);

    try {
      const endpoint = `/api/tickets/${ticketId}`;
      const result: Ticket = await api.put(endpoint, updateData);
      
      // Update the ticket in the list
      setTickets(prev => prev.map(ticket => 
        ticket.TicketID === ticketId ? result : ticket
      ));
      optionsRef.current.onSuccess?.(result);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to update ticket');
      setError(error);
      optionsRef.current.onError?.(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteTicket = useCallback(async (ticketId: number) => {
    setLoading(true);
    setError(null);

    try {
      const endpoint = `/api/tickets/${ticketId}`;
      await api.delete(endpoint);
      
      // Remove the ticket from the list
      setTickets(prev => prev.filter(ticket => ticket.TicketID !== ticketId));
      setTotalCount(prev => prev - 1);
      optionsRef.current.onSuccess?.(null);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to delete ticket');
      setError(error);
      optionsRef.current.onError?.(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const addComment = useCallback(async (ticketId: number, comment: string, performedById: number) => {
    setLoading(true);
    setError(null);

    try {
      const activityData: TicketActivityCreate = {
        ActivityType: 'Comment',
        ActivityDetails: comment
      };

      const queryParams = new URLSearchParams({ performed_by_id: performedById.toString() });
      const endpoint = `/api/tickets/${ticketId}/activities?${queryParams.toString()}`;
      const result: TicketActivity = await api.post(endpoint, activityData);
      
      // Update the ticket's activities
      setTickets(prev => prev.map(ticket => 
        ticket.TicketID === ticketId 
          ? { ...ticket, activities: [...(ticket.activities || []), result] }
          : ticket
      ));
      optionsRef.current.onSuccess?.(result);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to add comment');
      setError(error);
      optionsRef.current.onError?.(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const getTicketActivities = useCallback(async (ticketId: number) => {
    setLoading(true);
    setError(null);

    try {
      const endpoint = `/api/tickets/${ticketId}/activities`;
      const result: TicketActivity[] = await api.get(endpoint);
      optionsRef.current.onSuccess?.(result);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch ticket activities');
      setError(error);
      optionsRef.current.onError?.(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  // Pagination functions
  const goToPage = useCallback((page: number) => {
    fetchTickets(undefined, page);
  }, [fetchTickets]);

  const nextPage = useCallback(() => {
    if (hasNext) {
      goToPage(currentPage + 1);
    }
  }, [hasNext, currentPage, goToPage]);

  const previousPage = useCallback(() => {
    if (hasPrevious) {
      goToPage(currentPage - 1);
    }
  }, [hasPrevious, currentPage, goToPage]);

  const refetch = useCallback(() => {
    fetchTickets(undefined, currentPage);
  }, [fetchTickets, currentPage]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (requestRef.current) {
        requestRef.current.abort();
      }
    };
  }, []);

  // Initial fetch - only run once
  useEffect(() => {
    if (options.immediate && !initialFetchDoneRef.current) {
      initialFetchDoneRef.current = true;
      // Use setTimeout to ensure this runs after the component is fully mounted
      setTimeout(() => {
        fetchTickets(undefined, 1);
      }, 0);
    }
  }, [options.immediate]); // Add options.immediate as dependency

  return {
    tickets,
    loading,
    error,
    totalCount,
    hasNext,
    hasPrevious,
    currentPage,
    pageSize,
    fetchTickets,
    createTicket,
    updateTicket,
    deleteTicket,
    addComment,
    getTicketActivities,
    goToPage,
    nextPage,
    previousPage,
    refetch
  };
}

export function useTicket(ticketId: number | null) {
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchTicket = useCallback(async () => {
    if (!ticketId) return;

    setLoading(true);
    setError(null);

    try {
      const endpoint = `/api/tickets/${ticketId}`;
      const result: Ticket = await api.get(endpoint);
      setTicket(result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch ticket');
      setError(error);
    } finally {
      setLoading(false);
    }
  }, [ticketId]);

  const updateTicket = useCallback(async (updateData: TicketUpdate) => {
    if (!ticketId) return;

    setLoading(true);
    setError(null);

    try {
      const endpoint = `/api/tickets/${ticketId}`;
      const result: Ticket = await api.put(endpoint, updateData);
      setTicket(result);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to update ticket');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [ticketId]);

  const addComment = useCallback(async (comment: string, performedById: number) => {
    if (!ticketId) return;

    setLoading(true);
    setError(null);

    try {
      const activityData: TicketActivityCreate = {
        ActivityType: 'Comment',
        ActivityDetails: comment
      };

      const queryParams = new URLSearchParams({ performed_by_id: performedById.toString() });
      const endpoint = `/api/tickets/${ticketId}/activities?${queryParams.toString()}`;
      const result: TicketActivity = await api.post(endpoint, activityData);
      
      setTicket(prev => prev ? { ...prev, activities: [...(prev.activities || []), result] } : null);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to add comment');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [ticketId]);

  useEffect(() => {
    if (ticketId) {
      fetchTicket();
    }
  }, [ticketId, fetchTicket]);

  return {
    ticket,
    loading,
    error,
    fetchTicket,
    updateTicket,
    addComment
  };
}

export function useTicketLookups() {
  const [statuses, setStatuses] = useState<TicketStatus[]>([]);
  const [priorities, setPriorities] = useState<TicketPriority[]>([]);
  const [categories, setCategories] = useState<TicketCategory[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchLookups = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [statusesResult, prioritiesResult, categoriesResult] = await Promise.all([
        api.get<TicketStatus[]>('/api/tickets/lookup/statuses'),
        api.get<TicketPriority[]>('/api/tickets/lookup/priorities'),
        api.get<TicketCategory[]>('/api/tickets/lookup/categories')
      ]);

      setStatuses(statusesResult);
      setPriorities(prioritiesResult);
      setCategories(categoriesResult);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch ticket lookups');
      setError(error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLookups();
  }, [fetchLookups]);

  return {
    statuses,
    priorities,
    categories,
    loading,
    error,
    refetch: fetchLookups
  };
}

export function useAssetSelection(userId: number, categoryId?: number) {
  const [assets, setAssets] = useState<AssetSelectionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchAssets = useCallback(async () => {
    if (!userId) return;

    setLoading(true);
    setError(null);

    try {
      const queryParams = new URLSearchParams({ user_id: userId.toString() });
      if (categoryId) {
        queryParams.append('category_id', categoryId.toString());
      }

      const endpoint = `/api/tickets/assets/selection?${queryParams.toString()}`;
      const result: AssetSelectionResponse = await api.get(endpoint);
      setAssets(result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch asset selection');
      setError(error);
    } finally {
      setLoading(false);
    }
  }, [userId, categoryId]);

  useEffect(() => {
    fetchAssets();
  }, [fetchAssets]);

  return {
    assets,
    loading,
    error,
    refetch: fetchAssets
  };
}

export function useTicketStatistics() {
  const [statistics, setStatistics] = useState<TicketStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchStatistics = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const endpoint = '/api/tickets/statistics/dashboard';
      const result: TicketStatistics = await api.get(endpoint);
      setStatistics(result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch ticket statistics');
      setError(error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatistics();
  }, [fetchStatistics]);

  return {
    statistics,
    loading,
    error,
    refetch: fetchStatistics
  };
}

export function usePendingStatus(ticket: Ticket | null) {
  const [pendingStatus, setPendingStatus] = useState<PendingStatus>({
    is_pending_vendor: false,
    is_pending_user: false
  });

  useEffect(() => {
    if (!ticket || !ticket.activities) return;

    const comments = ticket.activities.filter(activity => activity.ActivityType === 'Comment');
    if (comments.length === 0) return;

    const lastComment = comments[comments.length - 1];
    const lastCommentTime = new Date(lastComment.PerformedAt);
    const now = new Date();
    const hoursSinceLastComment = (now.getTime() - lastCommentTime.getTime()) / (1000 * 60 * 60);

    // If last comment was more than 36 hours ago, set pending status
    if (hoursSinceLastComment > 36) {
      setPendingStatus({
        is_pending_vendor: true,
        is_pending_user: true,
        last_comment_time: lastComment.PerformedAt,
        last_comment_by: lastComment.performed_by,
        hours_since_last_comment: Math.floor(hoursSinceLastComment)
      });
    } else {
      setPendingStatus({
        is_pending_vendor: false,
        is_pending_user: false,
        last_comment_time: lastComment.PerformedAt,
        last_comment_by: lastComment.performed_by,
        hours_since_last_comment: Math.floor(hoursSinceLastComment)
      });
    }
  }, [ticket]);

  return pendingStatus;
} 