"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Calendar, Clock, CheckCircle, XCircle, DollarSign, FileText, Eye } from "lucide-react"
import { LeaveApplication } from "@/lib/types"
import { useLeaveManagement } from "@/hooks/use-leave"
import { LeaveApprovalDialog } from "@/components/ui/leave-approval-dialog"
import { useToast } from "@/hooks/use-toast"
import TimesheetApprovals from "@/components/features/timesheet-approvals"
import { api } from "@/lib/api"

interface UserInfo {
  email: string
  name: string
  department: string
  type: string
  employeeId?: number
}

interface ManagerApprovalsProps {
  userInfo: UserInfo
}

export default function ManagerApprovals({ userInfo }: ManagerApprovalsProps) {
  const [selectedLeaveApplication, setSelectedLeaveApplication] = useState<LeaveApplication | null>(null)
  const [isApprovalDialogOpen, setIsApprovalDialogOpen] = useState(false)
  const { toast } = useToast()

  // Fetch leave applications that need manager approval
  const {
    leaveApplications,
    loading,
    error,
    refreshData
  } = useLeaveManagement({
    immediate: true,
    onSuccess: () => {
      // Success callback
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: "Failed to load leave applications",
        variant: "destructive"
      })
    }
  })

  // Filter leave applications for manager approval
  const pendingLeaveApplications = leaveApplications.filter(
    (app) => app.StatusCode === "Submitted" || app.StatusCode === "Manager-Approved"
  )

  const handleViewLeaveApplication = (application: LeaveApplication) => {
    setSelectedLeaveApplication(application)
    setIsApprovalDialogOpen(true)
  }

  const handleApprovalComplete = (updatedApplication: LeaveApplication) => {
    // Refresh the data to show updated status
    refreshData()
    toast({
      title: "Success",
      description: "Leave application updated successfully",
    })
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Submitted":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400"
      case "Manager-Approved":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400"
      case "HR-Approved":
        return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400"
      case "Rejected":
        return "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400"
    }
  }

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
  }

  const isManager = userInfo.type === "manager" || userInfo.type === "hr"
  const isHR = userInfo.type === "hr"

  const [timesheetCount, setTimesheetCount] = useState(0)

  // Fetch timesheet count immediately when component loads
  useEffect(() => {
    const fetchTimesheetCount = async () => {
      try {
        const params = new URLSearchParams();
        params.append('skip', '0');
        params.append('limit', '1'); // We only need the count, not the data
        params.append('status_code', 'Submitted');
        
        const data = await api.get<{ total_count: number }>(`/api/timesheets/manager/subordinates?${params.toString()}`);
        setTimesheetCount(data.total_count || 0);
      } catch (error) {
        console.error('Failed to fetch timesheet count:', error);
      }
    };

    fetchTimesheetCount();
  }, []);

  const expenseRequests = [
    {
      id: 1,
      employeeName: "David Brown",
      employeeId: "EMP007",
      type: "Travel",
      amount: 1250.0,
      description: "Client meeting in New York",
      date: "2024-01-05",
      status: "pending",
      submittedDate: "2024-01-06",
      receipts: 3,
    },
    {
      id: 2,
      employeeName: "Anna Wilson",
      employeeId: "EMP008",
      type: "Equipment",
      amount: 899.99,
      description: "New laptop for development work",
      date: "2024-01-03",
      status: "pending",
      submittedDate: "2024-01-04",
      receipts: 1,
    },
  ]

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case "high":
        return "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400"
      case "normal":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400"
      case "low":
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400"
    }
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Manager Approvals</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Review and approve team requests</p>
        </div>
        <div className="flex items-center gap-4">
          <Card className="p-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">
                {pendingLeaveApplications.length +
                  timesheetCount +
                  expenseRequests.filter((r) => r.status === "pending").length}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Pending Approvals</p>
            </div>
          </Card>
        </div>
      </div>

      {/* Approval Tabs */}
      <Tabs defaultValue="leave" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3 bg-white dark:bg-gray-800 shadow-lg">
          <TabsTrigger value="leave" className="flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            Leave Requests ({pendingLeaveApplications.length})
          </TabsTrigger>
          <TabsTrigger value="timesheet" className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Timesheets ({timesheetCount})
          </TabsTrigger>
          <TabsTrigger value="expense" className="flex items-center gap-2">
            <DollarSign className="w-4 h-4" />
            Expenses ({expenseRequests.filter((r) => r.status === "pending").length})
          </TabsTrigger>
        </TabsList>

        {/* Leave Requests Tab */}
        <TabsContent value="leave">
          <div className="grid gap-4">
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
                <p className="mt-2 text-gray-600">Loading leave applications...</p>
              </div>
            ) : error ? (
              <div className="text-center py-8">
                <p className="text-red-600">Failed to load leave applications</p>
                <Button onClick={refreshData} className="mt-2">Retry</Button>
              </div>
            ) : pendingLeaveApplications.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-600">No leave applications pending approval</p>
              </div>
            ) : (
              pendingLeaveApplications.map((application) => (
                <Card key={application.LeaveApplicationID} className="shadow-lg hover:shadow-xl transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <Avatar className="w-12 h-12">
                          <AvatarFallback className="bg-gradient-to-r from-orange-500 to-amber-500 text-white">
                            {getInitials(`${application.employee?.FirstName || ''} ${application.employee?.LastName || ''}`)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <h3 className="font-semibold text-lg">
                            {application.employee?.FirstName} {application.employee?.LastName}
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            ID: {application.EmployeeID}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getStatusColor(application.StatusCode)}>
                          {application.StatusCode}
                        </Badge>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Leave Type</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {application.leave_type?.LeaveTypeName}
                        </p>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Duration</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {new Date(application.StartDate).toLocaleDateString()} to {new Date(application.EndDate).toLocaleDateString()} ({application.NumberOfDays} days)
                        </p>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Submitted</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {application.SubmittedAt ? new Date(application.SubmittedAt).toLocaleDateString() : 'N/A'}
                        </p>
                      </div>
                    </div>

                    {application.Reason && (
                      <div className="mt-4">
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Reason</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
                          {application.Reason}
                        </p>
                      </div>
                    )}

                    <div className="flex justify-end gap-2 mt-6">
                      <Button
                        variant="outline"
                        onClick={() => handleViewLeaveApplication(application)}
                        className="flex items-center gap-2"
                      >
                        <Eye className="w-4 h-4" />
                        View Details
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        {/* Timesheet Requests Tab */}
        <TabsContent value="timesheet">
          <TimesheetApprovals onCountUpdate={setTimesheetCount} />
        </TabsContent>

        {/* Expense Requests Tab */}
        <TabsContent value="expense">
          <div className="grid gap-4">
            {expenseRequests.map((request) => (
              <Card key={request.id} className="shadow-lg hover:shadow-xl transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <Avatar className="w-12 h-12">
                        <AvatarFallback className="bg-gradient-to-r from-green-500 to-emerald-500 text-white">
                          {getInitials(request.employeeName)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <h3 className="font-semibold text-lg">{request.employeeName}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">ID: {request.employeeId}</p>
                      </div>
                    </div>
                    <Badge className={getStatusColor(request.status)}>{request.status}</Badge>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Type</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{request.type}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Amount</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400 font-semibold">
                        ${request.amount.toFixed(2)}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Date</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{request.date}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Receipts</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{request.receipts} attached</p>
                    </div>
                  </div>

                  <div className="mt-4">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
                      {request.description}
                    </p>
                  </div>

                  {request.status === "pending" && (
                    <div className="flex justify-end gap-2 mt-6">
                      <Button
                        variant="outline"
                        className="text-blue-600 border-blue-200 hover:bg-blue-50 bg-transparent"
                      >
                        <FileText className="w-4 h-4 mr-2" />
                        View Receipts
                      </Button>
                      <Button variant="outline" className="text-red-600 border-red-200 hover:bg-red-50 bg-transparent">
                        <XCircle className="w-4 h-4 mr-2" />
                        Reject
                      </Button>
                      <Button className="bg-green-600 hover:bg-green-700 text-white">
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Approve
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Leave Approval Dialog */}
      {selectedLeaveApplication && (
        <LeaveApprovalDialog
          leaveApplication={selectedLeaveApplication}
          isOpen={isApprovalDialogOpen}
          onClose={() => {
            setIsApprovalDialogOpen(false)
            setSelectedLeaveApplication(null)
          }}
          onApprovalComplete={handleApprovalComplete}
          userInfo={{
            employeeId: userInfo.employeeId || 0,
            name: userInfo.name,
            type: userInfo.type
          }}
          isManager={isManager}
          isHR={isHR}
        />
      )}
    </div>
  )
}
