"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Calendar, Clock, CheckCircle, XCircle, AlertCircle, Plus, FileText, Trash2, Edit, MessageSquare } from "lucide-react"
import { useLeaveManagement } from "@/hooks/use-leave"
import { getCurrentEmployeeId, getCurrentUserInfo } from "@/lib/utils"
import type { LeaveApplication, LeaveType, LeaveBalanceSummary, LeaveFilterParams } from "@/lib/types"
import { useToast } from "@/hooks/use-toast"
import { api } from "@/lib/api"
import { Pagination } from "@/components/ui/pagination"
import { LeaveFilters } from "@/components/ui/leave-filters"
import { LeaveCommentsDialog } from "@/components/ui/leave-comments-dialog"

export default function LeaveApplication() {
  const { toast } = useToast()
  
  const [leaveType, setLeaveType] = useState("")
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [reason, setReason] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [editingApplication, setEditingApplication] = useState<LeaveApplication | null>(null)
  const [timesheetConflict, setTimesheetConflict] = useState<string | null>(null)
  const [calculatedDays, setCalculatedDays] = useState<number>(0)
  const [isFiltersExpanded, setIsFiltersExpanded] = useState(false)
  const [selectedLeaveApplication, setSelectedLeaveApplication] = useState<LeaveApplication | null>(null)
  const [isCommentsDialogOpen, setIsCommentsDialogOpen] = useState(false)

  const currentEmployeeId = getCurrentEmployeeId()
  const currentUser = getCurrentUserInfo()

  // Helper function to check if selected leave type is sick leave
  const isSickLeave = () => {
    const selectedType = leaveTypes.find(lt => lt.LeaveTypeID.toString() === leaveType)
    return selectedType?.LeaveTypeName.toLowerCase().includes('sick') || false
  }

  // Helper functions to check if applications can be edited or canceled
  const canEditApplication = (application: LeaveApplication) => {
    const status = application.StatusCode.toLowerCase()
    return status === "draft" || status === "submitted"
  }

  const canCancelApplication = (application: LeaveApplication) => {
    const status = application.StatusCode.toLowerCase()
    return status === "draft" || status === "submitted"
  }

  // Helper function to check if form can be saved as draft
  const canSaveAsDraft = () => {
    return leaveType && startDate && endDate && reason.trim() && !isSubmitting
  }

  // Shared validation function
  const validateFormData = (): { isValid: boolean; error?: string } => {
    if (!currentEmployeeId) {
      return { isValid: false, error: "Employee ID not found. Please log in again." }
    }

    if (!leaveType) {
      return { isValid: false, error: "Please select a leave type" }
    }

    if (!startDate) {
      return { isValid: false, error: "Please select a start date" }
    }

    if (!endDate) {
      return { isValid: false, error: "Please select an end date" }
    }

    if (!reason.trim()) {
      return { isValid: false, error: "Please provide a reason for your leave request" }
    }

    // Business logic: Sick leaves cannot be submitted for future dates
    const selectedLeaveType = leaveTypes.find(lt => lt.LeaveTypeID.toString() === leaveType)
    if (selectedLeaveType) {
      const isSickLeaveType = isSickLeave()
      const today = new Date()
      today.setHours(0, 0, 0, 0) // Reset time to start of day
      
      const startDateObj = new Date(startDate)
      const endDateObj = new Date(endDate)
      
      if (isSickLeaveType && (startDateObj > today || endDateObj > today)) {
        return { isValid: false, error: "Sick leave cannot be submitted for future dates. Please select past or current dates only." }
      }
    }

    if (timesheetConflict) {
      return { isValid: false, error: timesheetConflict }
    }

    return { isValid: true }
  }

  const {
    leaveApplications,
    leaveTypes,
    leaveBalance,
    loading,
    error,
    pagination,
    paginationInfo,
    filters,
    createLeaveApplication,
    updateLeaveApplication,
    deleteLeaveApplication,
    cancelLeaveApplication,
    calculateLeaveDays,
    checkTimesheetConflicts,
    refreshData,
    updateFilters,
    clearFilters,
    nextPage,
    previousPage,
    goToPage
  } = useLeaveManagement({
    employeeId: currentEmployeeId || undefined,
    onSuccess: () => {
      toast({
        title: "Success",
        description: "Leave application updated successfully",
      })
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    }
  })

  // Calculate days when dates change
  useEffect(() => {
    if (startDate && endDate) {
      calculateLeaveDays(startDate, endDate).then(result => {
        setCalculatedDays(result.number_of_days)
      }).catch(() => {
        // Fallback calculation
        const start = new Date(startDate)
        const end = new Date(endDate)
        const diffTime = Math.abs(end.getTime() - start.getTime())
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
        setCalculatedDays(diffDays)
      })
    }
  }, [startDate, endDate])

  // Check for timesheet conflicts when dates change
  useEffect(() => {
    if (startDate && endDate) {
      checkTimesheetConflicts(startDate, endDate).then(result => {
        if (result.has_conflict) {
          setTimesheetConflict(result.message || "Timesheet conflicts detected for the selected dates")
        } else {
          setTimesheetConflict(null)
        }
      }).catch(() => {
        setTimesheetConflict(null)
      })
    }
  }, [startDate, endDate])

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case "approved":
      case "hr-approved":
      case "manager-approved":
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case "submitted":
      case "pending":
        return <AlertCircle className="w-4 h-4 text-yellow-600" />
      case "rejected":
        return <XCircle className="w-4 h-4 text-red-600" />
      case "draft":
        return <Clock className="w-4 h-4 text-gray-600" />
      case "cancelled":
        return <XCircle className="w-4 h-4 text-orange-600" />
      default:
        return <Clock className="w-4 h-4 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "approved":
      case "hr-approved":
      case "manager-approved":
        return "bg-green-100 text-green-800"
      case "submitted":
      case "pending":
        return "bg-yellow-100 text-yellow-800"
      case "rejected":
        return "bg-red-100 text-red-800"
      case "draft":
        return "bg-gray-100 text-gray-800"
      case "cancelled":
        return "bg-orange-100 text-orange-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const validationResult = validateFormData()
    if (!validationResult.isValid) {
      toast({
        title: "Error",
        description: validationResult.error || "Failed to submit leave application",
        variant: "destructive",
      })
      return
    }

    setIsSubmitting(true)

    try {
      const selectedLeaveType = leaveTypes.find(lt => lt.LeaveTypeID.toString() === leaveType)
      
      if (!selectedLeaveType) {
        throw new Error("Please select a valid leave type")
      }

      const applicationData = {
        EmployeeID: currentEmployeeId!,
        LeaveTypeID: selectedLeaveType.LeaveTypeID,
        StartDate: startDate,
        EndDate: endDate,
        NumberOfDays: calculatedDays,
        Reason: reason,
        StatusCode: "Submitted",
        calculation_type: "business",
        exclude_holidays: true
      }

      if (editingApplication) {
        await updateLeaveApplication(editingApplication.LeaveApplicationID, applicationData)
        setEditingApplication(null)
      } else {
        await createLeaveApplication(applicationData)
      }

      // Reset form
      setLeaveType("")
      setStartDate("")
      setEndDate("")
      setReason("")
      setCalculatedDays(0)
      setTimesheetConflict(null)

      toast({
        title: "Success",
        description: editingApplication 
          ? "Leave application updated successfully" 
          : "Leave application submitted successfully",
      })
    } catch (error) {
      console.error("Leave application error:", error)
      const defaultMsg = "Failed to submit leave application";
      let msg = defaultMsg;
      if (error instanceof Error) {
        msg = error.message.includes("already has a leave application")
          ? "Submission not allowed. You already have a leave request for these dates. Please edit or cancel the existing application."
          : error.message;
      }
      
      toast({
        title: "Error",
        description: msg,
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSaveAsDraft = async () => {
    const validationResult = validateFormData()
    if (!validationResult.isValid) {
      toast({
        title: "Error",
        description: validationResult.error || "Failed to save leave application as draft",
        variant: "destructive",
      })
      return
    }

    setIsSubmitting(true)

    try {
      const selectedLeaveType = leaveTypes.find(lt => lt.LeaveTypeID.toString() === leaveType)
      
      if (!selectedLeaveType) {
        throw new Error("Please select a valid leave type")
      }

      const applicationData = {
        EmployeeID: currentEmployeeId!,
        LeaveTypeID: selectedLeaveType.LeaveTypeID,
        StartDate: startDate,
        EndDate: endDate,
        NumberOfDays: calculatedDays,
        Reason: reason,
        StatusCode: "Draft",
        calculation_type: "business",
        exclude_holidays: true
      }

      if (editingApplication) {
        await updateLeaveApplication(editingApplication.LeaveApplicationID, applicationData)
        setEditingApplication(null)
      } else {
        await createLeaveApplication(applicationData)
      }

      // Reset form
      setLeaveType("")
      setStartDate("")
      setEndDate("")
      setReason("")
      setCalculatedDays(0)
      setTimesheetConflict(null)

      toast({
        title: "Success",
        description: editingApplication 
          ? "Leave application updated as draft successfully" 
          : "Leave application saved as draft successfully",
      })
    } catch (error) {
      console.error("Save as Draft error:", error)
      const defaultMsg = "Failed to save leave application as draft";
      let msg = defaultMsg;
      if (error instanceof Error) {
        msg = error.message.includes("already has a leave application")
          ? "Save as draft not allowed. You already have a leave request for these dates. Edit or cancel the existing application."
          : error.message;
      }
      toast({
        title: "Error",
        description: msg,
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleEdit = (application: LeaveApplication) => {
    setEditingApplication(application)
    setLeaveType(application.LeaveTypeID.toString())
    setStartDate(application.StartDate)
    setEndDate(application.EndDate)
    setReason(application.Reason || "")
    setCalculatedDays(application.NumberOfDays)
  }

  const handleDelete = async (applicationId: number) => {
    if (!confirm("Are you sure you want to delete this leave application?")) {
      return
    }

    try {
      await deleteLeaveApplication(applicationId)
      toast({
        title: "Success",
        description: "Leave application deleted successfully",
      })
    } catch (error) {
      console.error("Delete error:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to delete leave application",
        variant: "destructive",
      })
    }
  }

  const handleCancel = async (applicationId: number) => {
    if (!confirm("Are you sure you want to cancel this leave application?")) {
      return
    }

    try {
      await cancelLeaveApplication(applicationId)
      toast({
        title: "Success",
        description: "Leave application cancelled successfully",
      })
    } catch (error) {
      console.error("Cancel error:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to cancel leave application",
        variant: "destructive",
      })
    }
  }

  const handleSubmitDraft = async (application: LeaveApplication) => {
    if (!confirm("Are you sure you want to submit this draft leave application?")) {
      return
    }

    try {
      const applicationData = {
        EmployeeID: application.EmployeeID,
        LeaveTypeID: application.LeaveTypeID,
        StartDate: application.StartDate,
        EndDate: application.EndDate,
        NumberOfDays: application.NumberOfDays,
        Reason: application.Reason,
        StatusCode: "Submitted",
        calculation_type: "business",
        exclude_holidays: true
      }

      await updateLeaveApplication(application.LeaveApplicationID, applicationData)
      toast({
        title: "Success",
        description: "Draft leave application submitted successfully",
      })
    } catch (error) {
      console.error("Submit draft error:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to submit draft leave application",
        variant: "destructive",
      })
    }
  }

  const handleCancelEdit = () => {
    setEditingApplication(null)
    setLeaveType("")
    setStartDate("")
    setEndDate("")
    setReason("")
    setCalculatedDays(0)
    setTimesheetConflict(null)
  }

  const handleViewComments = (application: LeaveApplication) => {
    setSelectedLeaveApplication(application)
    setIsCommentsDialogOpen(true)
  }

  const handleCloseCommentsDialog = () => {
    setIsCommentsDialogOpen(false)
    setSelectedLeaveApplication(null)
  }

  // Format leave balance data for display
  const leaveBalanceDisplay = leaveBalance ? [
    ...leaveBalance.balances.map(balance => ({
      type: balance.leave_type?.LeaveTypeName || "Unknown",
      available: balance.EntitledDays - balance.UsedDays,
      used: balance.UsedDays,
      total: balance.EntitledDays,
      color: "bg-blue-100 text-blue-800"
    }))
  ] : []



  if (loading && !leaveApplications.length) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          {error.message}
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-8">
      {/* Leave Balance Overview */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Leave Management</h2>
        {leaveBalance ? (
          <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="font-semibold text-blue-900 mb-2">Leave Balance Summary</h3>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-blue-700">Total Entitled:</span>
                <span className="ml-2 font-semibold">{leaveBalance.total_entitled_days} days</span>
              </div>
              <div>
                <span className="text-blue-700">Total Used:</span>
                <span className="ml-2 font-semibold">{leaveBalance.total_used_days} days</span>
              </div>
              <div>
                <span className="text-blue-700">Remaining:</span>
                <span className="ml-2 font-semibold">{leaveBalance.total_remaining_days} days</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="mb-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <h3 className="font-semibold text-yellow-900 mb-2">Leave Balance Summary</h3>
            <p className="text-yellow-700 text-sm mb-3">
              {loading ? "Loading leave balance..." : "No leave balance found. Please contact HR to set up your leave entitlements."}
            </p>
            {!loading && (
              <Button 
                variant="outline" 
                size="sm"
                onClick={async () => {
                  try {
                    await api.post('/api/leave/my/setup-default-balance');
                    toast.toast({
                      title: "Leave entitlements created",
                      description: "Default PTO and sick leave entitlements have been set up for 2025.",
                    });
                    // Refresh the balance
                    refreshBalance();
                  } catch (err) {
                    console.error('Failed to setup leave balance:', err);
                    toast.toast({
                      title: "Error",
                      description: "Failed to set up leave entitlements. Please contact HR.",
                      variant: "destructive"
                    });
                  }
                }}
                className="text-yellow-700 border-yellow-300 hover:bg-yellow-100"
              >
                Set Up Default Entitlements (Testing)
              </Button>
            )}
          </div>
        )}
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {leaveBalanceDisplay.map((leave, index) => (
            <Card key={index} className="border-0 shadow-sm hover:shadow-md transition-shadow duration-200">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <Badge className={leave.color}>{leave.type}</Badge>
                  <Calendar className="w-5 h-5 text-gray-400" />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Available</span>
                    <span className="font-semibold">{leave.available} days</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(leave.available / leave.total) * 100}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>Used: {leave.used}</span>
                    <span>Total: {leave.total}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Leave Application Form */}
        <Card className="border-0 shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {editingApplication ? <Edit className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
              {editingApplication 
                ? editingApplication.StatusCode.toLowerCase() === "draft" 
                  ? "Edit Draft Leave Application" 
                  : "Edit Leave Application"
                : "Apply for Leave"
              }
            </CardTitle>
            <CardDescription>
              {editingApplication 
                ? editingApplication.StatusCode.toLowerCase() === "draft"
                  ? "Update your draft leave request"
                  : "Update your leave request" 
                : "Submit a new leave request for manager approval"
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              
              <div className="space-y-2">
                <Label htmlFor="leaveType">Leave Type</Label>
                <Select value={leaveType} onValueChange={setLeaveType}>
                  <SelectTrigger className="h-11">
                    <SelectValue placeholder="Select leave type" />
                  </SelectTrigger>
                  <SelectContent>
                    {leaveTypes.map((type) => (
                      <SelectItem key={type.LeaveTypeID} value={type.LeaveTypeID.toString()}>
                        {type.LeaveTypeName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="startDate">Start Date</Label>
                  <Input
                    id="startDate"
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="h-11"
                    required
                    max={isSickLeave() ? new Date().toISOString().split('T')[0] : undefined}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="endDate">End Date</Label>
                  <Input
                    id="endDate"
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="h-11"
                    min={startDate}
                    required
                    max={isSickLeave() ? new Date().toISOString().split('T')[0] : undefined}
                  />
                </div>
              </div>

              {startDate && endDate && (
                <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-sm font-medium text-blue-900">
                    Duration: {calculatedDays} day{calculatedDays !== 1 ? "s" : ""}
                  </p>
                </div>
              )}

              {/* Sick leave date restriction notice */}
              {leaveType && isSickLeave() && (
                <div className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                  <p className="text-sm font-medium text-yellow-800">
                    ⚠️ Sick Leave Restriction: Only past or current dates are allowed
                  </p>
                </div>
              )}

              {timesheetConflict && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    {timesheetConflict}
                  </AlertDescription>
                </Alert>
              )}

              <div className="space-y-2">
                <Label htmlFor="reason">Reason for Leave</Label>
                <Textarea
                  id="reason"
                  placeholder="Please provide a detailed reason for your leave request..."
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  rows={4}
                  className="resize-none"
                  required
                />
              </div>

              <div className="flex gap-3">
                <Button
                  type="submit"
                  className="flex-1 h-11 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                  disabled={isSubmitting || !!timesheetConflict}
                >
                  {isSubmitting ? (
                    <>
                      <Clock className="w-4 h-4 mr-2 animate-spin" />
                      {editingApplication ? "Updating..." : "Submitting Request..."}
                    </>
                  ) : (
                    <>
                      <FileText className="w-4 h-4 mr-2" />
                      {editingApplication ? "Update Leave Request" : "Submit Leave Request"}
                    </>
                  )}
                </Button>
                
                {/* Save as Draft button */}
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => handleSaveAsDraft()}
                  disabled={!canSaveAsDraft()}
                  className="h-11"
                >
                  <Clock className="w-4 h-4 mr-2" />
                  {editingApplication ? "Update as Draft" : "Save as Draft"}
                </Button>
                
                {editingApplication && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleCancelEdit}
                    className="h-11"
                  >
                    Cancel
                  </Button>
                )}
              </div>
            </form>
            
          </CardContent>
        </Card>

        {/* Leave History */}
        <Card className="border-0 shadow-sm">
          <CardHeader>
            <CardTitle>Leave History</CardTitle>
            <CardDescription>Your recent leave requests and their status</CardDescription>
          </CardHeader>
          <CardContent>
            {/* Filters */}
            <LeaveFilters
              filters={filters}
              onFiltersChange={updateFilters}
              onClearFilters={clearFilters}
              leaveTypes={leaveTypes}
              loading={loading}
              isExpanded={isFiltersExpanded}
              onToggleExpanded={() => setIsFiltersExpanded(!isFiltersExpanded)}
            />

            <div className="space-y-4">
              {leaveApplications.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>No leave applications found</p>
                </div>
              ) : (
                <>
                  {leaveApplications.map((application) => {
                    const leaveType = leaveTypes.find(lt => lt.LeaveTypeID === application.LeaveTypeID)
                    return (
                      <div
                        key={application.LeaveApplicationID}
                        className="p-4 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors duration-200"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-3">
                            {getStatusIcon(application.StatusCode)}
                            <div>
                              <p className="font-medium text-gray-900">
                                {leaveType?.LeaveTypeName || "Unknown Type"}
                              </p>
                              <p className="text-sm text-gray-600">
                                {new Date(`${application.StartDate}T00:00:00`).toLocaleDateString()} - {new Date(`${application.EndDate}T00:00:00`).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <Badge className={getStatusColor(application.StatusCode)}>
                              {application.StatusCode}
                            </Badge>
                            <p className="text-xs text-gray-500 mt-1">
                              {application.NumberOfDays} day{application.NumberOfDays !== 1 ? "s" : ""}
                            </p>
                          </div>
                        </div>
                        
                        {application.Reason && (
                          <p className="text-sm text-gray-600 mb-2">{application.Reason}</p>
                        )}
                        
                        <p className="text-xs text-gray-500 mb-3">
                          Applied on {new Date(`${application.CreatedAt}` ).toLocaleDateString()}
                          {application.StatusCode.toLowerCase() === "draft" && " • Draft - You can edit, delete, or submit this application"}
                          {application.StatusCode.toLowerCase() === "submitted" && " • You can edit or cancel this application"}
                          {application.StatusCode.toLowerCase() === "manager-approved" && " • Approved by manager, pending HR approval"}
                          {application.StatusCode.toLowerCase() === "hr-approved" && " • Approved by HR"}
                          {application.StatusCode.toLowerCase() === "rejected" && " • Application was rejected"}
                          {application.StatusCode.toLowerCase() === "cancelled" && " • Application was cancelled"}
                        </p>

                        {/* Action buttons */}
                        <div className="flex gap-2 mt-3">
                          {/* View Comments button - always visible */}
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleViewComments(application)}
                            className="h-8"
                          >
                            <MessageSquare className="w-3 h-3 mr-1" />
                            View Comments
                          </Button>
                          
                          {/* Edit/Delete/Cancel buttons for applications that can be edited or canceled */}
                          {(canEditApplication(application) || canCancelApplication(application)) && (
                            <>
                              {canEditApplication(application) && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleEdit(application)}
                                  className="h-8"
                                >
                                  <Edit className="w-3 h-3 mr-1" />
                                  Edit
                                </Button>
                              )}
                              {application.StatusCode.toLowerCase() === "draft" && (
                                <>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => handleDelete(application.LeaveApplicationID)}
                                    className="h-8 text-red-600 hover:text-red-700"
                                  >
                                    <Trash2 className="w-3 h-3 mr-1" />
                                    Delete
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="default"
                                    onClick={() => handleSubmitDraft(application)}
                                    className="h-8 bg-blue-600 hover:bg-blue-700"
                                  >
                                    <FileText className="w-3 h-3 mr-1" />
                                    Submit
                                  </Button>
                                </>
                              )}
                              {canCancelApplication(application) && application.StatusCode.toLowerCase() !== "draft" && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleCancel(application.LeaveApplicationID)}
                                  className="h-8 text-orange-600 hover:text-orange-700"
                                >
                                  <XCircle className="w-3 h-3 mr-1" />
                                  Cancel
                                </Button>
                              )}
                            </>
                          )}
                        </div>
                      </div>
                    )
                  })}
                  
                  {/* Pagination */}
                  <Pagination
                    currentPage={pagination.page || 1}
                    totalPages={paginationInfo.pages}
                    hasNext={paginationInfo.has_next}
                    hasPrevious={paginationInfo.has_previous}
                    onPageChange={goToPage}
                    totalCount={paginationInfo.total}
                    pageSize={pagination.limit || 5}
                  />
                </>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Comments Dialog */}
      {selectedLeaveApplication && (
        <LeaveCommentsDialog
          leaveApplication={selectedLeaveApplication}
          isOpen={isCommentsDialogOpen}
          onClose={handleCloseCommentsDialog}
        />
      )}
    </div>
  )
}
