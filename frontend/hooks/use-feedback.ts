"use client"

import { useState, useEffect } from "react"
import { api } from "@/lib/api"
import { EmployeeFeedbackCreate, FeedbackTarget, FeedbackFilterParams } from "@/lib/types"

interface UseFeedbackReturn {
  feedback: any[]
  feedbackTypes: any[]
  targets: FeedbackTarget[]
  currentUserManager: FeedbackTarget | null
  departments: any[]
  submitting: boolean
  loading: boolean
  error: string | null
  submitFeedback: (data: EmployeeFeedbackCreate) => Promise<boolean>
  getFeedback: (params?: FeedbackFilterParams) => Promise<void>
  getFeedbackTypes: () => Promise<void>
  getTargets: () => Promise<void>
  getCurrentUserManager: () => Promise<void>
  getDepartments: () => Promise<void>
  markAsRead: (feedbackId: number) => Promise<boolean>
  clearError: () => void
  setErrorState: (error: string) => void
}

export function useFeedback(): UseFeedbackReturn {
  const [feedback, setFeedback] = useState<any[]>([])
  const [feedbackTypes, setFeedbackTypes] = useState<any[]>([])
  const [targets, setTargets] = useState<FeedbackTarget[]>([])
  const [currentUserManager, setCurrentUserManager] = useState<FeedbackTarget | null>(null)
  const [departments, setDepartments] = useState<any[]>([])
  const [submitting, setSubmitting] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const clearError = () => setError(null)

  const setErrorState = (error: string) => setError(error)

  const getFeedbackTypes = async () => {
    try {
      setLoading(true)
      const response = await api.get<any[]>("/feedback/types")
      setFeedbackTypes(response)
    } catch (err: any) {
      setError(err.message || "Failed to load feedback types")
    } finally {
      setLoading(false)
    }
  }

  const getTargets = async () => {
    try {
      setLoading(true)
      const response = await api.get<FeedbackTarget[]>("/employees/feedback-targets")
      setTargets(response)
    } catch (err: any) {
      setError(err.message || "Failed to load feedback targets")
    } finally {
      setLoading(false)
    }
  }

  const getCurrentUserManager = async () => {
    try {
      setLoading(true)
      const response = await api.get<FeedbackTarget>("/employees/profile/current/manager")
      setCurrentUserManager(response)
    } catch (err: any) {
      // Manager might not exist, so don't set error
      console.log("No manager found for current user")
    } finally {
      setLoading(false)
    }
  }

  const getDepartments = async () => {
    try {
      setLoading(true)
      const response = await api.get<any>("/departments")
      console.log("Departments response:", response)
      // The API returns { departments: [...], total: number, page: number, size: number }
      const departmentsArray = response.departments || []
      setDepartments(Array.isArray(departmentsArray) ? departmentsArray : [])
    } catch (err: any) {
      console.error("Failed to load departments:", err)
      setError(err.message || "Failed to load departments")
      setDepartments([]) // Ensure it's always an array
    } finally {
      setLoading(false)
    }
  }

  const submitFeedback = async (data: EmployeeFeedbackCreate): Promise<boolean> => {
    try {
      setSubmitting(true)
      setError(null)
      
      await api.post("/feedback/", data)
      return true
    } catch (err: any) {
      setError(err.message || "Failed to submit feedback")
      return false
    } finally {
      setSubmitting(false)
    }
  }

  const getFeedback = async (params?: FeedbackFilterParams) => {
    try {
      setLoading(true)
      
      // Build query parameters
      const queryParams = new URLSearchParams()
      
      // Add filter parameters when they exist
      if (params) {
        if (params.feedback_type_code) queryParams.append('feedback_type_code', params.feedback_type_code)
        if (params.target_manager_id) queryParams.append('target_manager_id', params.target_manager_id.toString())
        if (params.target_department_id) queryParams.append('target_department_id', params.target_department_id.toString())
        if (params.is_read !== undefined) queryParams.append('is_read', params.is_read.toString())
        if (params.skip !== undefined) queryParams.append('skip', params.skip.toString())
        if (params.limit !== undefined) queryParams.append('limit', params.limit.toString())
      }
      
      // Construct the endpoint with query parameters
      const endpoint = `/feedback/${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
      const response = await api.get<any[]>(endpoint)
      setFeedback(response)
    } catch (err: any) {
      setError(err.message || "Failed to load feedback")
    } finally {
      setLoading(false)
    }
  }

  const markAsRead = async (feedbackId: number): Promise<boolean> => {
    try {
      await api.post(`/feedback/${feedbackId}/mark-read`, { read_by: 0 }) // Will be set by backend
      return true
    } catch (err: any) {
      setError(err.message || "Failed to mark feedback as read")
      return false
    }
  }

  return {
    feedback,
    feedbackTypes,
    targets,
    currentUserManager,
    departments,
    submitting,
    loading,
    error,
    submitFeedback,
    getFeedback,
    getFeedbackTypes,
    getTargets,
    getCurrentUserManager,
    getDepartments,
    markAsRead,
    clearError,
    setErrorState
  }
} 