"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { 
  Clock, 
  Calendar, 
  CheckCircle, 
  XCircle, 
  Eye,
  Loader2,
  AlertCircle
} from "lucide-react"
import { format } from "date-fns"
import { useTimesheetApprovals } from "@/hooks/use-timesheet-approvals"
import useUserInfo from "@/hooks/use-user-info"
import { TimesheetApprovalDialog } from "@/components/ui/timesheet-approval-dialog"
import { Timesheet } from "@/lib/types"
import { useToast } from "@/hooks/use-toast"

interface TimesheetApprovalsProps {
  onCountUpdate?: (count: number) => void;
}

export default function TimesheetApprovals({ onCountUpdate }: TimesheetApprovalsProps) {
  const [selectedTimesheet, setSelectedTimesheet] = useState<Timesheet | null>(null)
  const [showApprovalDialog, setShowApprovalDialog] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 10

  const { userInfo, isManager, isHR, loading: userLoading } = useUserInfo()
  const { toast } = useToast()

  const { data, loading, error, refetch } = useTimesheetApprovals({
    skip: (currentPage - 1) * pageSize,
    limit: pageSize,
    statusCode: "Submitted"
  })

  // Update parent component with count when data changes
  useEffect(() => {
    if (data && onCountUpdate) {
      onCountUpdate(data.total_count || 0)
    }
  }, [data, onCountUpdate])

  const handleViewTimesheet = (timesheet: Timesheet) => {
    setSelectedTimesheet(timesheet)
    setShowApprovalDialog(true)
  }

  const handleApprovalComplete = (updatedTimesheet: Timesheet) => {
    // Refresh the list after approval
    refetch()
    toast({
      title: "Success",
      description: `Timesheet ${updatedTimesheet.StatusCode.toLowerCase()} successfully`,
    })
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Draft":
        return "bg-gray-100 text-gray-800"
      case "Submitted":
        return "bg-yellow-100 text-yellow-800"
      case "Approved":
        return "bg-green-100 text-green-800"
      case "Rejected":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const canApprove = () => {
    return isManager || isHR
  }

  // Show loading state while user info is loading
  if (userLoading) {
    return (
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="p-6">
          <div className="flex items-center gap-3 text-blue-700">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Loading user permissions...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Check permissions after user info has loaded
  if (!canApprove()) {
    return (
      <Card className="border-orange-200 bg-orange-50">
        <CardContent className="p-6">
          <div className="flex items-center gap-3 text-orange-700">
            <AlertCircle className="w-5 h-5" />
            <span>You don't have permission to approve timesheets.</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="border-0 shadow-lg bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl shadow-lg">
                <Clock className="w-6 h-6 text-white" />
              </div>
              <div>
                <CardTitle className="text-2xl font-bold text-gray-900">Timesheet Approvals</CardTitle>
                <CardDescription>
                  Review and approve timesheets from your team members
                </CardDescription>
              </div>
            </div>
            <Badge className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
              {data?.total_count || 0} Pending
            </Badge>
          </div>
        </CardHeader>
      </Card>

      {/* Loading State */}
      {loading && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 text-blue-700">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Loading timesheet approvals...</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error State */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 text-red-700">
              <AlertCircle className="w-5 h-5" />
              <span>Error loading timesheet approvals: {error.message}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Timesheet List */}
      {!loading && !error && data && (
        <div className="space-y-4">
          {data.items && data.items.length > 0 ? (
            data.items.map((timesheet) => (
              <Card key={timesheet.TimesheetID} className="border-0 shadow-md hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-gradient-to-r from-blue-100 to-indigo-100 rounded-xl">
                        <Calendar className="w-6 h-6 text-blue-600" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-semibold text-gray-900">
                            {timesheet.employee?.FirstName} {timesheet.employee?.LastName}
                          </h3>
                          <Badge className={getStatusColor(timesheet.StatusCode)}>
                            {timesheet.StatusCode}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                          <div>
                            <span className="font-medium">Week:</span>{" "}
                            {format(new Date(timesheet.WeekStartDate), "MMM d")} - {format(new Date(timesheet.WeekEndDate), "MMM d, yyyy")}
                          </div>
                          <div>
                            <span className="font-medium">Total Hours:</span> {timesheet.TotalHours}
                          </div>
                          <div>
                            <span className="font-medium">Submitted:</span>{" "}
                            {timesheet.SubmittedAt ? format(new Date(timesheet.SubmittedAt), "MMM d, h:mm a") : "Not submitted"}
                          </div>
                        </div>
                        {timesheet.Comments && (
                          <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                            <p className="text-sm text-gray-700">{timesheet.Comments}</p>
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        onClick={() => handleViewTimesheet(timesheet)}
                        variant="outline"
                        size="sm"
                        className="border-blue-200 hover:bg-blue-50"
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        Review
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <Card className="border-gray-200 bg-gray-50">
              <CardContent className="p-8 text-center">
                <div className="flex flex-col items-center gap-3">
                  <CheckCircle className="w-12 h-12 text-green-500" />
                  <h3 className="text-lg font-semibold text-gray-900">No Pending Approvals</h3>
                  <p className="text-gray-600">All timesheets have been reviewed and processed.</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Pagination */}
          {data.items && data.items.length > 0 && (
            <div className="flex justify-center gap-2 mt-6">
              <Button
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                variant="outline"
                size="sm"
              >
                Previous
              </Button>
              <span className="px-4 py-2 text-sm text-gray-600">
                Page {currentPage} of {Math.ceil((data.total_count || 0) / pageSize)}
              </span>
              <Button
                onClick={() => setCurrentPage(prev => prev + 1)}
                disabled={currentPage >= Math.ceil((data.total_count || 0) / pageSize)}
                variant="outline"
                size="sm"
              >
                Next
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Approval Dialog */}
      {selectedTimesheet && (
        <TimesheetApprovalDialog
          timesheet={selectedTimesheet}
          isOpen={showApprovalDialog}
          onClose={() => {
            setShowApprovalDialog(false)
            setSelectedTimesheet(null)
          }}
          onApprovalComplete={handleApprovalComplete}
          userInfo={{
            employeeId: parseInt(userInfo?.employeeId || "0"),
            name: userInfo?.name || "",
            type: userInfo?.type || ""
          }}
          isManager={isManager}
          isHR={isHR}
        />
      )}
    </div>
  )
} 