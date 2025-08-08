import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle, XCircle, Clock, Calendar } from "lucide-react"
import { Timesheet, TimesheetDetail } from "@/lib/types"
import { useTimesheetApproval } from "@/hooks/use-timesheet-approval"
import { useToast } from "@/hooks/use-toast"
import { format } from "date-fns"

interface TimesheetApprovalDialogProps {
  timesheet: Timesheet
  isOpen: boolean
  onClose: () => void
  onApprovalComplete: (updatedTimesheet: Timesheet) => void
  userInfo: {
    employeeId: number
    name: string
    type: string
  }
  isManager?: boolean
  isHR?: boolean
}

export function TimesheetApprovalDialog({
  timesheet,
  isOpen,
  onClose,
  onApprovalComplete,
  userInfo,
  isManager = false,
  isHR = false
}: TimesheetApprovalDialogProps) {
  const [approvalComment, setApprovalComment] = useState("")

  const { toast } = useToast()
  const {
    loading,
    error,
    approveTimesheet
  } = useTimesheetApproval()

  const handleApproval = async (action: "approve" | "reject") => {
    if (!userInfo.employeeId) {
      toast({
        title: "Error",
        description: "User information not available",
        variant: "destructive"
      })
      return
    }

    try {
      const result = await approveTimesheet(timesheet.TimesheetID, {
        status: action === "approve" ? "Approved" : "Rejected",
        approved_by_id: userInfo.employeeId,
        comments: approvalComment
      })

      toast({
        title: "Success",
        description: `Timesheet ${action}d successfully`,
      })

      onApprovalComplete(result)
      onClose()
    } catch (error) {
      console.error('Approval failed:', error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to process approval",
        variant: "destructive"
      })
    }
  }



  const getStatusColor = (status: string) => {
    switch (status) {
      case "Draft":
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400"
      case "Submitted":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400"
      case "Approved":
        return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400"
      case "Rejected":
        return "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400"
    }
  }

  const canApprove = () => {
    return timesheet.StatusCode === "Submitted" && (isManager || isHR)
  }

  const canReject = () => {
    return timesheet.StatusCode === "Submitted" && (isManager || isHR)
  }

  const calculateTotalHours = (details: TimesheetDetail[]) => {
    return details.reduce((total, detail) => total + detail.HoursWorked, 0)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Timesheet Approval</h2>
            <Button variant="ghost" onClick={onClose} size="sm">
              ✕
            </Button>
          </div>

          {/* Timesheet Details */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Timesheet #{timesheet.TimesheetID}</span>
                <Badge className={getStatusColor(timesheet.StatusCode)}>
                  {timesheet.StatusCode}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium">Employee</Label>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {timesheet.employee?.FirstName} {timesheet.employee?.LastName}
                  </p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Week Period</Label>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {format(new Date(timesheet.WeekStartDate), "MMM d, yyyy")} - {format(new Date(timesheet.WeekEndDate), "MMM d, yyyy")}
                  </p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Total Hours</Label>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {timesheet.TotalHours} hours
                  </p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Submitted At</Label>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {timesheet.SubmittedAt ? format(new Date(timesheet.SubmittedAt), "MMM d, yyyy 'at' h:mm a") : "Not submitted"}
                  </p>
                </div>
              </div>
              
              {timesheet.Comments && (
                <div>
                  <Label className="text-sm font-medium">Comments</Label>
                  <p className="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
                    {timesheet.Comments}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Timesheet Details */}
          {timesheet.details && timesheet.details.length > 0 && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Daily Entries
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {timesheet.details.map((detail, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className="p-2 bg-blue-100 rounded-lg">
                          <Clock className="w-4 h-4 text-blue-600" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">
                            {format(new Date(detail.WorkDate), "EEEE, MMM d, yyyy")}
                          </p>
                          <p className="text-sm text-gray-600">
                            {detail.HoursWorked} hours • {detail.ProjectCode || "No project"}
                          </p>
                          {detail.TaskDescription && (
                            <p className="text-xs text-gray-500 mt-1">
                              {detail.TaskDescription}
                            </p>
                          )}
                        </div>
                      </div>
                      {detail.IsOvertime && (
                        <Badge className="bg-orange-100 text-orange-800">
                          Overtime
                        </Badge>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Approval Section */}
          {(canApprove() || canReject()) && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5" />
                  {isManager ? "Manager Approval" : "HR Approval"}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="approval-comment">Approval Comments (Optional)</Label>
                  <Textarea
                    id="approval-comment"
                    placeholder="Add comments for the employee..."
                    value={approvalComment}
                    onChange={(e) => setApprovalComment(e.target.value)}
                    className="mt-1"
                    rows={3}
                  />
                </div>
                
                <div className="flex gap-2">
                  <Button
                    onClick={() => handleApproval("approve")}
                    disabled={loading}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    {loading ? "Processing..." : "Approve"}
                  </Button>
                  <Button
                    onClick={() => handleApproval("reject")}
                    disabled={loading}
                    variant="destructive"
                  >
                    <XCircle className="w-4 h-4 mr-2" />
                    {loading ? "Processing..." : "Reject"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}


        </div>
      </div>
    </div>
  )
} 