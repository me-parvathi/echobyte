"use client"

import { useState, useCallback } from 'react'
import { TimesheetApiService } from '@/lib/timesheet-api'
import { WeeklyTimesheetFormData, Timesheet } from '@/lib/types'

interface UseCreateWeeklyTimesheetResult {
  createWeeklyTimesheet: (data: WeeklyTimesheetFormData) => Promise<void>
  timesheet: Timesheet | null
  loading: boolean
  error: Error | null
  success: boolean
}

/**
 * Custom hook to create (or update) the current user's weekly timesheet.
 * The backend endpoint automatically associates the newly-created timesheet
 * with the currently authenticated employee, so we only need to send the
 * week range and an array of DailyEntryFormData.
 */
export const useCreateWeeklyTimesheet = (): UseCreateWeeklyTimesheetResult => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const [timesheet, setTimesheet] = useState<Timesheet | null>(null)
  const [success, setSuccess] = useState(false)

  const createWeeklyTimesheet = useCallback(async (data: WeeklyTimesheetFormData) => {
    setLoading(true)
    setError(null)
    setSuccess(false)
    try {
      const result = await TimesheetApiService.createMyWeeklyTimesheet(data)
      setTimesheet(result)
      setSuccess(true)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to create weekly timesheet'))
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    createWeeklyTimesheet,
    timesheet,
    loading,
    error,
    success,
  }
}
