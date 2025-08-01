"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Calendar, Clock, CheckCircle, XCircle, DollarSign, FileText } from "lucide-react"

interface UserInfo {
  email: string
  name: string
  department: string
  type: string
}

interface ManagerApprovalsProps {
  userInfo: UserInfo
}

export default function ManagerApprovals({ userInfo }: ManagerApprovalsProps) {
  const [selectedRequest, setSelectedRequest] = useState<any>(null)
  const [approvalComment, setApprovalComment] = useState("")

  // Mock data for demonstration
  const leaveRequests = [
    {
      id: 1,
      employeeName: "Sarah Johnson",
      employeeId: "EMP002",
      type: "Vacation",
      startDate: "2024-01-15",
      endDate: "2024-01-19",
      days: 5,
      reason: "Family vacation to Hawaii",
      status: "pending",
      submittedDate: "2024-01-01",
      urgency: "normal",
    },
    {
      id: 2,
      employeeName: "Mike Chen",
      employeeId: "EMP003",
      type: "Sick Leave",
      startDate: "2024-01-10",
      endDate: "2024-01-12",
      days: 3,
      reason: "Medical appointment and recovery",
      status: "pending",
      submittedDate: "2024-01-08",
      urgency: "high",
    },
    {
      id: 3,
      employeeName: "Emily Davis",
      employeeId: "EMP004",
      type: "Personal",
      startDate: "2024-01-20",
      endDate: "2024-01-20",
      days: 1,
      reason: "Moving to new apartment",
      status: "approved",
      submittedDate: "2023-12-28",
      urgency: "normal",
    },
  ]

  const timesheetRequests = [
    {
      id: 1,
      employeeName: "John Smith",
      employeeId: "EMP005",
      week: "Week of Jan 1-7, 2024",
      totalHours: 42,
      overtimeHours: 2,
      status: "pending",
      submittedDate: "2024-01-08",
      projects: [
        { name: "Project Alpha", hours: 25 },
        { name: "Project Beta", hours: 17 },
      ],
    },
    {
      id: 2,
      employeeName: "Lisa Wang",
      employeeId: "EMP006",
      week: "Week of Jan 8-14, 2024",
      totalHours: 40,
      overtimeHours: 0,
      status: "pending",
      submittedDate: "2024-01-15",
      projects: [
        { name: "Project Gamma", hours: 20 },
        { name: "Project Delta", hours: 20 },
      ],
    },
  ]

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

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400"
      case "approved":
        return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400"
      case "rejected":
        return "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400"
    }
  }

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

  const handleApproval = (requestId: number, action: "approve" | "reject", type: string) => {
    console.log(`${action} request ${requestId} of type ${type}`)
    console.log("Comment:", approvalComment)
    setApprovalComment("")
    setSelectedRequest(null)
  }

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
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
                {leaveRequests.filter((r) => r.status === "pending").length +
                  timesheetRequests.filter((r) => r.status === "pending").length +
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
            Leave Requests ({leaveRequests.filter((r) => r.status === "pending").length})
          </TabsTrigger>
          <TabsTrigger value="timesheet" className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Timesheets ({timesheetRequests.filter((r) => r.status === "pending").length})
          </TabsTrigger>
          <TabsTrigger value="expense" className="flex items-center gap-2">
            <DollarSign className="w-4 h-4" />
            Expenses ({expenseRequests.filter((r) => r.status === "pending").length})
          </TabsTrigger>
        </TabsList>

        {/* Leave Requests Tab */}
        <TabsContent value="leave">
          <div className="grid gap-4">
            {leaveRequests.map((request) => (
              <Card key={request.id} className="shadow-lg hover:shadow-xl transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <Avatar className="w-12 h-12">
                        <AvatarFallback className="bg-gradient-to-r from-orange-500 to-amber-500 text-white">
                          {getInitials(request.employeeName)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <h3 className="font-semibold text-lg">{request.employeeName}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">ID: {request.employeeId}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getUrgencyColor(request.urgency)}>{request.urgency}</Badge>
                      <Badge className={getStatusColor(request.status)}>{request.status}</Badge>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Leave Type</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{request.type}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Duration</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {request.startDate} to {request.endDate} ({request.days} days)
                      </p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Submitted</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{request.submittedDate}</p>
                    </div>
                  </div>

                  <div className="mt-4">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Reason</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
                      {request.reason}
                    </p>
                  </div>

                  {request.status === "pending" && (
                    <div className="flex justify-end gap-2 mt-6">
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button
                            variant="outline"
                            className="text-red-600 border-red-200 hover:bg-red-50 bg-transparent"
                            onClick={() => setSelectedRequest(request)}
                          >
                            <XCircle className="w-4 h-4 mr-2" />
                            Reject
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Reject Leave Request</DialogTitle>
                            <DialogDescription>
                              Are you sure you want to reject {request.employeeName}'s leave request?
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4">
                            <Label htmlFor="comment">Reason for rejection (optional)</Label>
                            <Textarea
                              id="comment"
                              placeholder="Provide feedback for the employee..."
                              value={approvalComment}
                              onChange={(e) => setApprovalComment(e.target.value)}
                            />
                          </div>
                          <DialogFooter>
                            <Button variant="outline" onClick={() => setSelectedRequest(null)}>
                              Cancel
                            </Button>
                            <Button variant="destructive" onClick={() => handleApproval(request.id, "reject", "leave")}>
                              Reject Request
                            </Button>
                          </DialogFooter>
                        </DialogContent>
                      </Dialog>

                      <Dialog>
                        <DialogTrigger asChild>
                          <Button
                            className="bg-green-600 hover:bg-green-700 text-white"
                            onClick={() => setSelectedRequest(request)}
                          >
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Approve
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Approve Leave Request</DialogTitle>
                            <DialogDescription>
                              Approve {request.employeeName}'s leave request for {request.days} days?
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4">
                            <Label htmlFor="comment">Comments (optional)</Label>
                            <Textarea
                              id="comment"
                              placeholder="Add any comments for the employee..."
                              value={approvalComment}
                              onChange={(e) => setApprovalComment(e.target.value)}
                            />
                          </div>
                          <DialogFooter>
                            <Button variant="outline" onClick={() => setSelectedRequest(null)}>
                              Cancel
                            </Button>
                            <Button
                              className="bg-green-600 hover:bg-green-700"
                              onClick={() => handleApproval(request.id, "approve", "leave")}
                            >
                              Approve Request
                            </Button>
                          </DialogFooter>
                        </DialogContent>
                      </Dialog>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Timesheet Requests Tab */}
        <TabsContent value="timesheet">
          <div className="grid gap-4">
            {timesheetRequests.map((request) => (
              <Card key={request.id} className="shadow-lg hover:shadow-xl transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <Avatar className="w-12 h-12">
                        <AvatarFallback className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white">
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

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Week</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{request.week}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Total Hours</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {request.totalHours}h
                        {request.overtimeHours > 0 && (
                          <span className="text-orange-600"> (+{request.overtimeHours}h OT)</span>
                        )}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Submitted</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{request.submittedDate}</p>
                    </div>
                  </div>

                  <div className="mt-4">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Project Breakdown</p>
                    <div className="space-y-2">
                      {request.projects.map((project, index) => (
                        <div
                          key={index}
                          className="flex justify-between items-center bg-gray-50 dark:bg-gray-800 p-2 rounded"
                        >
                          <span className="text-sm">{project.name}</span>
                          <span className="text-sm font-medium">{project.hours}h</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {request.status === "pending" && (
                    <div className="flex justify-end gap-2 mt-6">
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
    </div>
  )
}
