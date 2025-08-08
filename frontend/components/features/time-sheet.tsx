"use client"

import { useState, useEffect, useMemo, useCallback } from "react"
import { format, addDays, isToday, isSameDay, startOfWeek } from "date-fns"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle 
} from "@/components/ui/dialog"
import { 
  Clock, 
  Calendar, 
  TrendingUp, 
  CheckCircle, 
  AlertCircle, 
  Play, 
  Pause, 
  RotateCcw,
  Loader2,
  FileText,
  CalendarDays,
  Save,
  Send
} from "lucide-react"
import { useTimesheetBatch, useTimesheetHistoryPagination } from "@/hooks/use-timesheet"
import { TimesheetApiService } from "@/lib/timesheet-api"
import TimesheetEntryTable from "./timesheet-entry-table"
import WeekSelector from "./week-selector"
import { Timesheet, TimesheetDetail } from "@/lib/types"
import { isWithinSubmissionRange } from "@/lib/timesheet-utils"
import { useToast } from "@/hooks/use-toast"

export default function TimeSheet() {
  const { toast } = useToast()
  const [currentTime, setCurrentTime] = useState(new Date())
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [isTimerRunning, setIsTimerRunning] = useState(false)
  const [timerStart, setTimerStart] = useState<Date | null>(null)
  const [todayHours, setTodayHours] = useState(0)
  const [showSubmissionModal, setShowSubmissionModal] = useState(false)
  const [submitLoading, setSubmitLoading] = useState(false)
  
  // Timesheet details modal state
  const [showDetailsModal, setShowDetailsModal] = useState(false)
  const [selectedTimesheet, setSelectedTimesheet] = useState<Timesheet | null>(null)
  const [timesheetDetails, setTimesheetDetails] = useState<TimesheetDetail[]>([])
  const [detailsLoading, setDetailsLoading] = useState(false)

  // Week selection state
  const [selectedWeekStart, setSelectedWeekStart] = useState(() => startOfWeek(new Date(), { weekStartsOn: 1 }))

  // Get timesheet data for selected week
  const { data: timesheetData, loading: timesheetLoading } = useTimesheetBatch(
    format(selectedWeekStart, "yyyy-MM-dd")
  )

  // Get timesheet history with pagination
  const { 
    data: historyData, 
    loading: historyLoading, 
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
      const date = addDays(selectedWeekStart, i)
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
  }, [selectedWeekStart, selectedDate])

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
    setTodayHours(0)
    setIsTimerRunning(false)
    setTimerStart(null)
  }, [])

  const handleWeekChange = useCallback((weekStart: Date) => {
    setSelectedWeekStart(weekStart)
    // Reset time entries when changing weeks
    setTimeEntries({
      monday: { hours: "0", project: "", description: "", overtime: false },
      tuesday: { hours: "0", project: "", description: "", overtime: false },
      wednesday: { hours: "0", project: "", description: "", overtime: false },
      thursday: { hours: "0", project: "", description: "", overtime: false },
      friday: { hours: "0", project: "", description: "", overtime: false },
      saturday: { hours: "0", project: "", description: "", overtime: false },
      sunday: { hours: "0", project: "", description: "", overtime: false },
    })
  }, [])

  const handleSubmit = useCallback(() => {
    setShowSubmissionModal(true)
  }, [])

  const confirmSubmit = useCallback(async () => {
    if (!timesheetData?.current_week?.TimesheetID) {
      toast({
        title: "No timesheet found",
        description: "Please save your timesheet first before submitting.",
        variant: "destructive",
      })
      return
    }
    
    if (!isWithinSubmissionRange(selectedWeekStart)) {
      toast({
        title: "Cannot submit",
        description: "This week is outside the submission range. You can only submit timesheets for the current month.",
        variant: "destructive",
      })
      return
    }
    
    setSubmitLoading(true)
    try {
      await TimesheetApiService.submitMyTimesheet(timesheetData.current_week.TimesheetID)
      setShowSubmissionModal(false)
      toast({
        title: "Timesheet submitted",
        description: "Your timesheet has been submitted for approval.",
      })
      // Optionally refresh data
    } catch (error) {
      console.error("Failed to submit timesheet:", error)
      toast({
        title: "Submission failed",
        description: error instanceof Error ? error.message : "Failed to submit timesheet",
        variant: "destructive",
      })
    } finally {
      setSubmitLoading(false)
    }
  }, [timesheetData?.current_week?.TimesheetID, selectedWeekStart, toast])

  // Handle timesheet details view
  const handleViewDetails = useCallback(async (timesheet: any) => {
    setSelectedTimesheet(timesheet)
    setShowDetailsModal(true)
    setDetailsLoading(true)
    
    try {
      console.log("Opening timesheet details for:", timesheet)
      
      // Use the existing history data if available
      const foundTimesheet = historyData?.items?.find(t => t.TimesheetID === timesheet.timesheetId)
      if (foundTimesheet && foundTimesheet.details) {
        console.log("Found timesheet with details in history:", foundTimesheet)
        setSelectedTimesheet(foundTimesheet)
        setTimesheetDetails(foundTimesheet.details)
      } else {
        // If not found in current history, try to fetch it
        console.log("Timesheet not found in history, trying to fetch from API...")
        try {
          const fullTimesheet = await TimesheetApiService.getTimesheetDetails(timesheet.timesheetId)
          console.log("API response:", fullTimesheet)
          if (fullTimesheet) {
            setSelectedTimesheet(fullTimesheet)
            setTimesheetDetails(fullTimesheet.details || [])
          }
        } catch (apiError) {
          console.error("API call failed:", apiError)
          // Show a simple message in the modal
          setTimesheetDetails([])
        }
      }
    } catch (error) {
      console.error("Failed to load timesheet details:", error)
      // Show a simple message in the modal
      setTimesheetDetails([])
    } finally {
      setDetailsLoading(false)
    }
  }, [historyData?.items])

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <Card className="border-0 shadow-lg bg-gradient-to-r from-orange-50 to-amber-50 border-orange-200">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-gradient-to-r from-orange-600 to-amber-600 rounded-xl shadow-lg">
                <Calendar className="w-6 h-6 text-white" />
              </div>
              <div>
                <CardTitle className="text-2xl font-bold text-gray-900">Timesheet</CardTitle>
                <div className="flex items-center gap-4">
                  <WeekSelector
                    selectedWeekStart={selectedWeekStart}
                    onWeekChange={handleWeekChange}
                    className="text-gray-600"
                  />
                  {timesheetData?.current_week && (
                    <Badge className="bg-gradient-to-r from-orange-600 to-amber-600 text-white text-xs shadow-lg">
                      {timesheetData.current_week.StatusCode}
                    </Badge>
                  )}
                </div>
              </div>
            </div>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={handleSubmit}
                disabled={submitLoading || !isWithinSubmissionRange(selectedWeekStart)}
                className="bg-transparent border-orange-200 hover:bg-orange-50"
              >
                <Save className="w-4 h-4 mr-2" />
                {submitLoading ? "Submitting..." : "Submit for Approval"}
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

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

      {/* Daily Entries */}
      <TimesheetEntryTable
        weekDays={weekDays}
        timeEntries={timeEntries}
        setTimeEntries={setTimeEntries}
        projects={projects}
        selectedWeekStart={selectedWeekStart}
        isWithinSubmissionRange={isWithinSubmissionRange(selectedWeekStart)}
      />

      {/* Previous Timesheets */}
      <Card className="border-0 shadow-lg bg-white">
        <CardHeader>
          <CardTitle className="text-xl font-bold text-gray-900">Previous Timesheets</CardTitle>
          <CardDescription>Your submitted timesheet history - Page {currentPage} of {totalPages}</CardDescription>
        </CardHeader>
        <CardContent>
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
                        onClick={() => handleViewDetails(timesheet)}
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
                  <div className="flex justify-center gap-2">
                    <Button
                      onClick={previousPage}
                      disabled={!historyData?.has_previous || historyLoading}
                      variant="outline"
                      size="sm"
                    >
                      Previous
                    </Button>
                    <span className="px-4 py-2 text-sm text-gray-600">
                      Page {currentPage} of {totalPages}
                    </span>
                    <Button
                      onClick={nextPage}
                      disabled={!historyData?.has_next || historyLoading}
                      variant="outline"
                      size="sm"
                    >
                      Next
                    </Button>
                  </div>
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
                <p>• Week: {format(selectedWeekStart, "MMM d")} - {format(addDays(selectedWeekStart, 6), "MMM d, yyyy")}</p>
                <p>• Total Hours: {totalHours}</p>
                <p>• Regular Hours: {regularHours}</p>
                <p>• Overtime Hours: {overtimeHours}</p>
                {!isWithinSubmissionRange(selectedWeekStart) && (
                  <p className="text-orange-600 font-medium">⚠️ This week is outside the submission range</p>
                )}
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
                  disabled={submitLoading || !isWithinSubmissionRange(selectedWeekStart)}
                  className="flex-1 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700"
                >
                  {submitLoading ? "Submitting..." : "Submit"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Timesheet Details Modal */}
      <Dialog open={showDetailsModal} onOpenChange={setShowDetailsModal}>
        <DialogContent className="max-w-4xl h-[90vh] flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="w-6 h-6 text-gray-600" />
              Timesheet Details for Week Ending {selectedTimesheet?.WeekEndDate ? format(new Date(selectedTimesheet.WeekEndDate), "MMM d, yyyy") : ""}
            </DialogTitle>
            <DialogDescription asChild>
            <div>
              {detailsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-8 h-8 animate-spin text-orange-600" />
                  <span className="ml-2 text-lg text-gray-600">Loading timesheet details...</span>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">Timesheet Overview</h4>
                    <div className="grid grid-cols-2 gap-2 text-sm text-gray-700">
                      <span>Timesheet ID:</span>
                      <span>{selectedTimesheet?.TimesheetID}</span>
                      <span>Week Ending:</span>
                      <span>{selectedTimesheet?.WeekEndDate ? format(new Date(selectedTimesheet.WeekEndDate), "MMM d, yyyy") : ""}</span>
                      <span>Status:</span>
                      <span>{selectedTimesheet?.StatusCode}</span>
                      <span>Total Hours:</span>
                      <span>{selectedTimesheet?.TotalHours}</span>
                    </div>
                  </div>
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">Details</h4>
                    <div className="overflow-y-auto max-h-[calc(90vh-250px)] pr-2">
                      {timesheetDetails.length === 0 ? (
                        <div className="text-center py-8">
                          <FileText className="w-12 h-12 mx-auto text-gray-300 mb-4" />
                          <p className="text-sm text-gray-500">No detailed entries found for this timesheet.</p>
                          <p className="text-xs text-gray-400 mt-2">This timesheet may not have daily entries recorded.</p>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          {timesheetDetails.map((detail, index) => (
                            <div key={index} className="grid grid-cols-1 md:grid-cols-6 gap-2 text-sm text-gray-800">
                              <span className="font-medium">Day {index + 1}:</span>
                              <span>{format(new Date(detail.WorkDate), "MMM d, yyyy")}</span>
                              <span>Hours: {detail.HoursWorked}</span>
                              <span>Project: {detail.ProjectCode || "N/A"}</span>
                              <span>Description: {detail.TaskDescription || "N/A"}</span>
                              <span>Overtime: {detail.IsOvertime ? "Yes" : "No"}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </div>
  )
}
