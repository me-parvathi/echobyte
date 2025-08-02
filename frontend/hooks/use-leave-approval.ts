import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import type { 
  LeaveApplication, 
  ManagerApprovalRequest, 
  HRApprovalRequest,
  LeaveConflict,
  Comment,
  CommentCreate,
  CommentListResponse
} from '@/lib/types';

interface UseLeaveApprovalOptions {
  managerId?: number;
  hrApproverId?: number;
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
}

export function useLeaveApproval(options: UseLeaveApprovalOptions = {}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [conflict, setConflict] = useState<LeaveConflict | null>(null);

  const { managerId, hrApproverId, onSuccess, onError } = options;

  // Manager approval
  const approveAsManager = useCallback(async (
    applicationId: number, 
    approval: ManagerApprovalRequest
  ): Promise<LeaveApplication> => {
    setLoading(true);
    setError(null);

    try {
      const result = await api.post<LeaveApplication>(
        `/api/leave/applications/${applicationId}/manager-approve`,
        approval
      );
      
      onSuccess?.(result);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to approve leave application');
      setError(error);
      onError?.(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [onSuccess, onError]);

  // HR approval
  const approveAsHR = useCallback(async (
    applicationId: number, 
    approval: HRApprovalRequest
  ): Promise<LeaveApplication> => {
    setLoading(true);
    setError(null);

    try {
      const result = await api.post<LeaveApplication>(
        `/api/leave/applications/${applicationId}/hr-approve`,
        approval
      );
      
      onSuccess?.(result);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to approve leave application');
      setError(error);
      onError?.(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [onSuccess, onError]);

  // Check for leave conflicts
  const checkLeaveConflicts = useCallback(async (
    startDate: string,
    endDate: string,
    managerId: number
  ): Promise<LeaveConflict> => {
    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
        manager_id: managerId.toString()
      });
      
      const result = await api.get<LeaveConflict>(`/api/leave/check-conflicts?${params.toString()}`);
      setConflict(result);
      return result;
    } catch (err) {
      // If the endpoint doesn't exist yet, return no conflict
      const noConflict: LeaveConflict = { has_conflict: false };
      setConflict(noConflict);
      return noConflict;
    }
  }, []);

  // Get comments for a leave application
  const getComments = useCallback(async (
    applicationId: number
  ): Promise<CommentListResponse> => {
    try {
      const result = await api.get<CommentListResponse>(`/api/comments/LeaveApplication/${applicationId}`);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch comments');
      throw error;
    }
  }, []);

  // Add a comment to a leave application
  const addComment = useCallback(async (
    applicationId: number,
    commentData: CommentCreate
  ): Promise<Comment> => {
    try {
      const result = await api.post<Comment>(`/api/comments/LeaveApplication/${applicationId}`, commentData);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to add comment');
      throw error;
    }
  }, []);

  // Update a comment
  const updateComment = useCallback(async (
    commentId: number,
    commentData: { comment_text: string }
  ): Promise<Comment> => {
    try {
      const result = await api.put<Comment>(`/api/comments/${commentId}`, commentData);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to update comment');
      throw error;
    }
  }, []);

  // Delete a comment
  const deleteComment = useCallback(async (commentId: number): Promise<void> => {
    try {
      await api.delete(`/api/comments/${commentId}`);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to delete comment');
      throw error;
    }
  }, []);

  return {
    loading,
    error,
    conflict,
    approveAsManager,
    approveAsHR,
    checkLeaveConflicts,
    getComments,
    addComment,
    updateComment,
    deleteComment,
  };
} 