"use client"

import { useState, useEffect, useMemo, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Clock, Save, Send, Award, TrendingUp, CheckCircle, CalendarIcon, Play, Pause, RotateCcw, AlertCircle } from "lucide-react"
import { format, startOfWeek, addDays, isSameDay, isToday } from "date-fns"
import { useTimesheetBatch, useBulkSaveEntries, useSubmitTimesheet, useTimesheetHistoryPagination } from "@/hooks/use-timesheet"
import { TimesheetStatusBadge } from "./timesheet-status-badge"
import { Pagination } from "@/components/ui/pagination"
import { convertToDailyEntryFormData, convertFromTimesheetDetail, isCurrentWeek, isPastWeek, getWeekStartDate, getWeekEndDate, formatDate } from "@/lib/timesheet-utils"
import { DailyEntryFormData } from "@/lib/types"

export default function TimeSheet() {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())
  const [currentWeekStart, setCurrentWeekStart] = useState(startOfWeek(new Date(), { weekStartsOn: 1 }))
  const [isTimerRunning, setIsTimerRunning] = useState(false)
  const [timerStart, setTimerStart] = useState<Date | null>(null)
  const [todayHours, setTodayHours] = useState(0)
  const [showCalendar, setShowCalendar] = useState(false)
  const [showSubmissionModal, setShowSubmissionModal] = useState(false)
  const [validationErrors, setValidationErrors] = useState<string[]>([])

  // API hooks
  const { data: timesheetData, loading: timesheetLoading, error: timesheetError, refetch: refetchTimesheet } = useTimesheetBatch(
    formatDate(currentWeekStart),
    false, // Don't include history in batch call
    0
  )
  const { bulkSave, loading: bulkSaveLoading, error: bulkSaveError, success: bulkSaveSuccess } = useBulkSaveEntries()
  const { submitTimesheet, loading: submitLoading, error: submitError, success: submitSuccess } = useSubmitTimesheet()
  
  // Paginated history hook
  const { 
    data: historyData, 
    loading: historyLoading, 
    error: historyError, 
    currentPage, 
    totalPages, 
    goToPage, 
    nextPage, 
    previousPage 
  } = useTimesheetHistoryPagination(5) // 5 items per page
  
  // State for pagination mode
  const [paginationMode, setPaginationMode] = useState<'pagination' | 'load-more'>('pagination')

  // Combined timer effect to reduce overhead
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
      
      // Update timer hours if running
      if (isTimerRunning && timerStart) {
        const elapsed = (new Date().getTime() - timerStart.getTime()) / (1000 * 60 * 60)
        setTodayHours(elapsed)
      }
    }, 1000)

    return () => clearInterval(timer)
  }, [isTimerRunning, timerStart])

  // Initialize time entries from API data or defaults
  const [timeEntries, setTimeEntries] = useState({
    monday: { hours: "0", project: "", description: "", overtime: false },
    tuesday: { hours: "0", project: "", description: "", overtime: false },
    wednesday: { hours: "0", project: "", description: "", overtime: false },
    thursday: { hours: "0", project: "", description: "", overtime: false },
    friday: { hours: "0", project: "", description: "", overtime: false },
    saturday: { hours: "0", project: "", description: "", overtime: false },
    sunday: { hours: "0", project: "", description: "", overtime: false },
  })

  // Update time entries when API data loads
  useEffect(() => {
    if (timesheetData?.current_week?.details) {
      const newEntries = { ...timeEntries }
      
      timesheetData.current_week.details.forEach(detail => {
        const date = new Date(detail.WorkDate)
        const dayOfWeek = date.getDay()
        const dayNames = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        const dayKey = dayNames[dayOfWeek]
        
        if (dayKey && newEntries[dayKey as keyof typeof newEntries]) {
          newEntries[dayKey as keyof typeof newEntries] = {
            hours: detail.HoursWorked.toString(),
            project: detail.ProjectCode || "",
            description: detail.TaskDescription || "",
            overtime: detail.IsOvertime
          }
        }
      })
      
      setTimeEntries(newEntries)
    }
  }, [timesheetData])

  const projects = [
    "Project Alpha",
    "Project Beta", 
    "Project Gamma",
    "Internal Tools",
    "Training",
    "Meetings",
    "Administrative",
  ]

  // Memoize expensive calculations
  const weekDays = useMemo(() => {
    return Array.from({ length: 7 }, (_, i) => {
      const date = addDays(currentWeekStart, i)
      const dayNames = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
      return {
        key: dayNames[date.getDay()],
        label: format(date, "EEEE"),
        date: format(date, "d"),
        fullDate: format(date, "yyyy-MM-dd"),
        dateObj: date,
        isToday: isToday(date),
        isSelected: isSameDay(date, selectedDate),
      }
    })
  }, [currentWeekStart, selectedDate])

  // Convert previous timesheets from paginated API data
  const previousTimesheets = useMemo(() => {
    if (!historyData?.items) return []
    
    return historyData.items.map(timesheet => ({
      week: format(new Date(timesheet.WeekEndDate), "MMM d, yyyy"),
      hours: timesheet.TotalHours,
      overtime: Math.max(timesheet.TotalHours - 40, 0),
      status: timesheet.StatusCode.toLowerCase(),
      compOff: Math.floor(Math.max(timesheet.TotalHours - 40, 0) / 16),
      timesheetId: timesheet.TimesheetID
    }))
  }, [historyData?.items])

  // Memoize totals calculation
  const { totalHours, regularHours, overtimeHours, compOffEarned, compOffProgress } = useMemo(() => {
    const total = Object.values(timeEntries).reduce((sum, entry) => sum + Number.parseFloat(entry.hours || "0"), 0)
    const regular = Math.min(total, 40)
    const overtime = Math.max(total - 40, 0)
    const compOff = Math.floor(overtime / 16)
    const progress = ((overtime % 16) / 16) * 100
    
    return { totalHours: total, regularHours: regular, overtimeHours: overtime, compOffEarned: compOff, compOffProgress: progress }
  }, [timeEntries])

  // Memoize handlers
  const handleTimerToggle = useCallback(() => {
    if (isTimerRunning) {
      setIsTimerRunning(false)
      setTimerStart(null)
    } else {
      setIsTimerRunning(true)
      setTimerStart(new Date())
    }
  }, [isTimerRunning])

  const handleTimerReset = useCallback(() => {
    setIsTimerRunning(false)
    setTimerStart(null)
    setTodayHours(0)
  }, [])

  const handleSave = useCallback(async () => {
    // Validate before saving
    const errors: string[] = []
    const entriesToSave: DailyEntryFormData[] = []
    
    weekDays.forEach(day => {
      const entry = timeEntries[day.key as keyof typeof timeEntries]
      if (parseFloat(entry.hours) > 0) {
        const formData = convertToDailyEntryFormData(
          day.key,
          entry.hours,
          entry.project,
          entry.description,
          entry.overtime,
          day.dateObj
        )
        
        // Basic validation
        if (parseFloat(entry.hours) > 24) {
          errors.push(`${day.label}: Hours cannot exceed 24`)
        }
        if (parseFloat(entry.hours) > 0 && !entry.description.trim()) {
          errors.push(`${day.label}: Description required when hours are entered`)
        }
        
        entriesToSave.push(formData)
      }
    })
    
    if (errors.length > 0) {
      setValidationErrors(errors)
      return
    }
    
    setValidationErrors([])
    
    // Save entries
    if (entriesToSave.length > 0) {
      await bulkSave(entriesToSave)
      if (bulkSaveSuccess) {
        refetchTimesheet()
      }
    }
  }, [timeEntries, weekDays, bulkSave, bulkSaveSuccess, refetchTimesheet])

  const handleSubmit = useCallback(async () => {
    if (!timesheetData?.current_week?.TimesheetID) {
      setValidationErrors(['No timesheet found to submit'])
      return
    }
    
    // Validate before submitting
    const errors: string[] = []
    const weekdays = weekDays.filter(day => {
      const dayOfWeek = day.dateObj.getDay()
      return dayOfWeek >= 1 && dayOfWeek <= 5 // Monday-Friday
    })
    
    weekdays.forEach(day => {
      const entry = timeEntries[day.key as keyof typeof timeEntries]
      if (parseFloat(entry.hours) === 0) {
        errors.push(`${day.label}: Hours cannot be 0 for weekdays`)
      }
    })
    
    if (errors.length > 0) {
      setValidationErrors(errors)
      return
    }
    
    setValidationErrors([])
    setShowSubmissionModal(true)
  }, [timeEntries, weekDays, timesheetData])

  const confirmSubmit = useCallback(async () => {
    if (!timesheetData?.current_week?.TimesheetID) return
    
    await submitTimesheet(timesheetData.current_week.TimesheetID)
    if (submitSuccess) {
      setShowSubmissionModal(false)
      refetchTimesheet()
    }
  }, [timesheetData, submitTimesheet, submitSuccess, refetchTimesheet])

  const navigateWeek = useCallback((direction: "prev" | "next") => {
    const newWeekStart = direction === "prev" 
      ? addDays(currentWeekStart, -7)
      : addDays(currentWeekStart, 7)
    
    // Only allow navigation to current week or past 8 weeks
    const today = new Date()
    const currentWeek = getWeekStartDate(today)
    const pastLimit = addDays(currentWeek, -56) // 8 weeks back
    
    if (direction === "next" && newWeekStart > currentWeek) {
      return // Don't allow future weeks
    }
    
    if (direction === "prev" && newWeekStart < pastLimit) {
      return // Don't allow more than 8 weeks back
    }
    
    setCurrentWeekStart(newWeekStart)
  }, [currentWeekStart])

  const updateTimeEntry = useCallback((day: string, field: string, value: string | boolean) => {
    setTimeEntries((prev) => ({
      ...prev,
      [day]: {
        ...prev[day as keyof typeof prev],
        [field]: value,
        overtime: field === "hours" ? Number.parseFloat(value as string) > 8 : prev[day as keyof typeof prev].overtime,
      },
    }))
  }, [])

  // Check if current week is editable
  const isCurrentWeekEditable = isCurrentWeek(currentWeekStart)
  const isPastWeekViewable = isPastWeek(currentWeekStart)

  return (
    <div className="space-y-8">
      {/* Header with Current Time */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
            Weekly Timesheet
          </h2>
          <div className="flex items-center gap-4 mt-2">
            <p className="text-gray-600">Week ending {format(addDays(currentWeekStart, 6), "MMMM d, yyyy")}</p>
            {timesheetData?.current_week && (
              <TimesheetStatusBadge status={timesheetData.current_week.StatusCode} />
            )}
            <div className="flex items-center gap-3 px-4 py-2 bg-gradient-to-r from-orange-50 to-amber-50 rounded-xl border border-orange-200/50 shadow-sm">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-gradient-to-r from-orange-500 to-amber-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-orange-700">Live</span>
              </div>
              <div className="h-4 w-px bg-orange-300"></div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-orange-600" />
                <span className="text-lg font-bold text-orange-800 font-mono tracking-wider">
                  {format(currentTime, "HH:mm:ss")}
                </span>
              </div>
              <div className="h-4 w-px bg-orange-300"></div>
              <span className="text-sm text-orange-600 font-medium">{format(currentTime, "EEE, MMM d")}</span>
            </div>
          </div>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={handleSave}
            disabled={!isCurrentWeekEditable || bulkSaveLoading}
            className="bg-transparent border-orange-200 hover:bg-orange-50"
          >
            <Save className="w-4 h-4 mr-2" />
            {bulkSaveLoading ? "Saving..." : "Save Draft"}
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!isCurrentWeekEditable || submitLoading}
            className="bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700 text-white shadow-lg"
          >
            <Send className="w-4 h-4 mr-2" />
            {submitLoading ? "Submitting..." : "Submit for Approval"}
          </Button>
        </div>
      </div>

      {/* Error Display */}
      {(validationErrors.length > 0 || bulkSaveError || submitError || historyError) && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-red-700">
              <AlertCircle className="w-4 h-4" />
              <span className="font-medium">Please fix the following errors:</span>
            </div>
            <ul className="mt-2 ml-6 text-sm text-red-600 list-disc">
              {validationErrors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
              {bulkSaveError && <li>{bulkSaveError.message}</li>}
              {submitError && <li>{submitError.message}</li>}
              {historyError && <li>{historyError.message}</li>}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Success Messages */}
      {(bulkSaveSuccess || submitSuccess) && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-green-700">
              <CheckCircle className="w-4 h-4" />
              <span className="font-medium">
                {bulkSaveSuccess && "Timesheet saved successfully!"}
                {submitSuccess && "Timesheet submitted successfully!"}
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Loading State */}
      {timesheetLoading && (
        <Card className="border-orange-200 bg-orange-50">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-orange-700">
              <Clock className="w-4 h-4 animate-spin" />
              <span>Loading timesheet data...</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Live Timer Card */}
      <Card className="border-0 shadow-lg bg-gradient-to-r from-orange-50 to-amber-50 border-orange-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-4 bg-gradient-to-r from-orange-600 to-amber-600 rounded-xl shadow-lg">
                <Clock className="w-8 h-8 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Today's Timer</h3>
                <p className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
                  {Math.floor(todayHours)}h {Math.floor((todayHours % 1) * 60)}m
                </p>
                <p className="text-sm text-gray-600">{isTimerRunning ? "Timer running..." : "Timer stopped"}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={handleTimerToggle}
                className={`${
                  isTimerRunning
                    ? "bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                    : "bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
                } text-white shadow-lg`}
              >
                {isTimerRunning ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
                {isTimerRunning ? "Pause" : "Start"}
              </Button>
              <Button
                onClick={handleTimerReset}
                variant="outline"
                className="border-orange-200 hover:bg-orange-50 bg-transparent"
              >
                <RotateCcw className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Calendar Navigation */}
      <Card className="border-0 shadow-lg">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
                Week Navigation
              </CardTitle>
              <CardDescription>
                {isCurrentWeekEditable ? "Current week - Editable" : 
                 isPastWeekViewable ? "Past week - View only" : "Week navigation"}
              </CardDescription>
            </div>
            <Popover open={showCalendar} onOpenChange={setShowCalendar}>
              <PopoverTrigger asChild>
                <Button variant="outline" className="border-orange-200 hover:bg-orange-50 bg-transparent">
                  <CalendarIcon className="w-4 h-4 mr-2" />
                  Select Date
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="end">
                <Calendar
                  mode="single"
                  selected={selectedDate}
                  onSelect={(date) => {
                    if (date) {
                      setSelectedDate(date)
                      setCurrentWeekStart(startOfWeek(date, { weekStartsOn: 1 }))
                      setShowCalendar(false)
                    }
                  }}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <Button
              onClick={() => navigateWeek("prev")}
              variant="outline"
              className="border-orange-200 hover:bg-orange-50"
            >
              ← Previous Week
            </Button>
            <div className="flex gap-2">
              {weekDays.map((day) => (
                <div
                  key={day.key}
                  className={`px-3 py-2 rounded-lg text-center cursor-pointer transition-all duration-200 ${
                    day.isToday
                      ? "bg-gradient-to-r from-orange-600 to-amber-600 text-white shadow-lg"
                      : day.isSelected
                        ? "bg-orange-100 text-orange-700 border border-orange-300"
                        : "bg-gray-50 text-gray-600 hover:bg-orange-50"
                  }`}
                  onClick={() => setSelectedDate(day.dateObj)}
                >
                  <div className="text-xs font-medium">{day.label.slice(0, 3)}</div>
                  <div className="text-sm font-bold">{day.date}</div>
                </div>
              ))}
            </div>
            <Button
              onClick={() => navigateWeek("next")}
              variant="outline"
              className="border-orange-200 hover:bg-orange-50"
              disabled={isCurrentWeekEditable}
            >
              Next Week →
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Time Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-blue-600 to-blue-700 rounded-xl shadow-lg">
                <Clock className="w-6 h-6 text-white" />
              </div>
              <TrendingUp className="w-4 h-4 text-blue-400" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-blue-700">Total Hours</p>
              <p className="text-2xl font-bold text-blue-900">{totalHours}</p>
              <p className="text-xs text-blue-600">This week</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-green-50 to-emerald-100 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-green-600 to-emerald-600 rounded-xl shadow-lg">
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <TrendingUp className="w-4 h-4 text-green-400" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-green-700">Regular Hours</p>
              <p className="text-2xl font-bold text-green-900">{regularHours}</p>
              <p className="text-xs text-green-600">Standard work time</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-orange-50 to-amber-100 border-orange-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-orange-600 to-amber-600 rounded-xl shadow-lg">
                <Clock className="w-6 h-6 text-white" />
              </div>
              <TrendingUp className="w-4 h-4 text-orange-400" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-orange-700">Overtime</p>
              <p className="text-2xl font-bold text-orange-900">{overtimeHours}</p>
              <p className="text-xs text-orange-600">Extra hours worked</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-purple-600 to-purple-700 rounded-xl shadow-lg">
                <Award className="w-6 h-6 text-white" />
              </div>
              <Badge className="bg-gradient-to-r from-purple-600 to-purple-700 text-white text-xs shadow-lg">
                {compOffEarned} earned
              </Badge>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium text-purple-700">Comp Off Progress</p>
              <div className="w-full bg-purple-200 rounded-full h-3 shadow-inner">
                <div
                  className="bg-gradient-to-r from-purple-600 to-purple-700 h-3 rounded-full transition-all duration-500 shadow-lg"
                  style={{ width: `${compOffProgress}%` }}
                />
              </div>
              <p className="text-xs text-purple-600">{overtimeHours % 16}/16 hours to next comp off</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Daily Time Entries */}
      <Card className="border-0 shadow-lg">
        <CardHeader>
          <CardTitle className="text-xl bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
            Daily Time Entries
          </CardTitle>
          <CardDescription>
            {isCurrentWeekEditable 
              ? "Enter your hours worked for each day of the week" 
              : "View only - This week cannot be edited"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {weekDays.map((day) => (
              <div
                key={day.key}
                className={`grid grid-cols-1 md:grid-cols-6 gap-4 p-4 rounded-xl transition-all duration-200 ${
                  day.isToday
                    ? "bg-gradient-to-r from-orange-50 to-amber-50 border-2 border-orange-300 shadow-lg"
                    : "border border-gray-200 hover:bg-gray-50 hover:shadow-md"
                }`}
              >
                <div className="flex items-center">
                  <div>
                    <p className={`font-medium ${day.isToday ? "text-orange-900" : "text-gray-900"}`}>{day.label}</p>
                    <p className={`text-sm ${day.isToday ? "text-orange-700" : "text-gray-600"}`}>
                      {format(day.dateObj, "MMM d")}
                    </p>
                    {day.isToday && (
                      <Badge className="bg-gradient-to-r from-orange-600 to-amber-600 text-white text-xs mt-1 shadow-lg">
                        Today
                      </Badge>
                    )}
                    {timeEntries[day.key as keyof typeof timeEntries].overtime && (
                      <Badge className="bg-gradient-to-r from-red-500 to-red-600 text-white text-xs mt-1 shadow-lg">
                        Overtime
                      </Badge>
                    )}
                  </div>
                </div>

                <div>
                  <Label htmlFor={`${day.key}-hours`} className="text-sm font-medium">
                    Hours
                  </Label>
                  <Input
                    id={`${day.key}-hours`}
                    type="number"
                    step="0.5"
                    min="0"
                    max="24"
                    value={timeEntries[day.key as keyof typeof timeEntries].hours}
                    onChange={(e) => updateTimeEntry(day.key, "hours", e.target.value)}
                    disabled={!isCurrentWeekEditable}
                    className={`mt-1 h-10 ${
                      day.isToday ? "border-orange-300 focus:border-orange-500 focus:ring-orange-500" : ""
                    }`}
                  />
                </div>

                <div>
                  <Label htmlFor={`${day.key}-project`} className="text-sm font-medium">
                    Project
                  </Label>
                  <Select
                    value={timeEntries[day.key as keyof typeof timeEntries].project}
                    onValueChange={(value) => updateTimeEntry(day.key, "project", value)}
                    disabled={!isCurrentWeekEditable}
                  >
                    <SelectTrigger
                      className={`mt-1 h-10 ${
                        day.isToday ? "border-orange-300 focus:border-orange-500 focus:ring-orange-500" : ""
                      }`}
                    >
                      <SelectValue placeholder="Select project" />
                    </SelectTrigger>
                    <SelectContent>
                      {projects.map((project) => (
                        <SelectItem key={project} value={project}>
                          {project}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="md:col-span-3">
                  <Label htmlFor={`${day.key}-description`} className="text-sm font-medium">
                    Work Description
                  </Label>
                  <Input
                    id={`${day.key}-description`}
                    value={timeEntries[day.key as keyof typeof timeEntries].description}
                    onChange={(e) => updateTimeEntry(day.key, "description", e.target.value)}
                    placeholder="Describe your work for this day..."
                    disabled={!isCurrentWeekEditable}
                    className={`mt-1 h-10 ${
                      day.isToday ? "border-orange-300 focus:border-orange-500 focus:ring-orange-500" : ""
                    }`}
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Previous Timesheets */}
      <Card className="border-0 shadow-lg">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
                Previous Timesheets
              </CardTitle>
              <CardDescription>
                Your submitted timesheet history - {paginationMode === 'pagination' ? `Page ${currentPage} of ${totalPages}` : `${historyData?.total_count || 0} total timesheets`}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant={paginationMode === 'pagination' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setPaginationMode('pagination')}
                className="text-xs"
              >
                Pagination
              </Button>
              <Button
                variant={paginationMode === 'load-more' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setPaginationMode('load-more')}
                className="text-xs"
              >
                Load More
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Loading state for history */}
          {historyLoading && (
            <div className="flex items-center justify-center py-8">
              <div className="flex items-center gap-2 text-orange-600">
                <Clock className="w-4 h-4 animate-spin" />
                <span>Loading timesheet history...</span>
              </div>
            </div>
          )}
          
          {/* Empty state */}
          {!historyLoading && previousTimesheets.length === 0 && (
            <div className="flex items-center justify-center py-8">
              <div className="text-center text-gray-500">
                <CheckCircle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium">No timesheet history found</p>
                <p className="text-sm">Your submitted timesheets will appear here</p>
              </div>
            </div>
          )}
          
          {/* Timesheet list */}
          {!historyLoading && previousTimesheets.length > 0 && (
            <>
              <div className="space-y-3">
                {previousTimesheets.map((timesheet, index) => (
                  <div
                    key={timesheet.timesheetId}
                    className="flex items-center justify-between p-4 border border-gray-200 rounded-xl hover:bg-gradient-to-r hover:from-orange-50 hover:to-amber-50 hover:border-orange-200 transition-all duration-200 hover:shadow-md"
                  >
                    <div className="flex items-center gap-4">
                      <div className="p-2 bg-gradient-to-r from-green-600 to-emerald-600 rounded-lg shadow-lg">
                        <CheckCircle className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">Week ending {timesheet.week}</p>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span>{timesheet.hours} total hours</span>
                          {timesheet.overtime > 0 && (
                            <span className="text-orange-600 font-medium">{timesheet.overtime} overtime</span>
                          )}
                          {timesheet.compOff > 0 && (
                            <span className="text-purple-600 font-medium">{timesheet.compOff} comp off earned</span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge className="bg-gradient-to-r from-green-600 to-emerald-600 text-white shadow-lg">
                        {timesheet.status}
                      </Badge>
                      <Button
                        variant="outline"
                        size="sm"
                        className="bg-transparent border-orange-200 hover:bg-orange-50 hover:border-orange-300"
                      >
                        View Details
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Pagination Controls */}
              <div className="mt-6 pt-4 border-t border-gray-200">
                {paginationMode === 'pagination' ? (
                  <Pagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={goToPage}
                    isLoading={historyLoading}
                    className="justify-center"
                  />
                ) : (
                  <div className="flex justify-center">
                    <Button
                      onClick={nextPage}
                      disabled={!historyData?.has_next || historyLoading}
                      variant="outline"
                      className="bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700 text-white border-orange-600"
                    >
                      {historyLoading ? (
                        <>
                          <Clock className="w-4 h-4 mr-2 animate-spin" />
                          Loading...
                        </>
                      ) : (
                        <>
                          <TrendingUp className="w-4 h-4 mr-2" />
                          Load More
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Submission Modal */}
      {showSubmissionModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-96">
            <CardHeader>
              <CardTitle>Confirm Submission</CardTitle>
              <CardDescription>
                Are you sure you want to submit this timesheet for approval? This action cannot be undone.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-sm text-gray-600">
                <p>• Total Hours: {totalHours}</p>
                <p>• Regular Hours: {regularHours}</p>
                <p>• Overtime Hours: {overtimeHours}</p>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => setShowSubmissionModal(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={confirmSubmit}
                  disabled={submitLoading}
                  className="flex-1 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700"
                >
                  {submitLoading ? "Submitting..." : "Submit"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
