"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Calendar, Clock, CheckCircle, XCircle, AlertCircle, Plus, FileText } from "lucide-react"
import WorkflowManager from "@/lib/workflow-manager"

export default function LeaveApplication() {
  const [leaveType, setLeaveType] = useState("")
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [reason, setReason] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)

  const leaveBalance = [
    { type: "Vacation", available: 18, used: 7, total: 25, color: "bg-blue-100 text-blue-800" },
    { type: "Sick", available: 12, used: 3, total: 15, color: "bg-green-100 text-green-800" },
    { type: "Personal", available: 5, used: 0, total: 5, color: "bg-purple-100 text-purple-800" },
    { type: "Comp Off", available: 2, used: 1, total: 3, color: "bg-orange-100 text-orange-800" },
  ]

  const leaveHistory = [
    {
      id: 1,
      type: "Vacation",
      dates: "Dec 25-27, 2024",
      days: 3,
      status: "pending",
      reason: "Christmas holidays",
      appliedDate: "2024-12-15",
    },
    {
      id: 2,
      type: "Sick Leave",
      dates: "Dec 15, 2024",
      days: 1,
      status: "approved",
      reason: "Medical appointment",
      appliedDate: "2024-12-14",
    },
    {
      id: 3,
      type: "Personal",
      dates: "Nov 28, 2024",
      days: 1,
      status: "approved",
      reason: "Family event",
      appliedDate: "2024-11-25",
    },
    {
      id: 4,
      type: "Comp Off",
      dates: "Nov 20, 2024",
      days: 1,
      status: "approved",
      reason: "Overtime compensation",
      appliedDate: "2024-11-18",
    },
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "approved":
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case "pending":
        return <AlertCircle className="w-4 h-4 text-yellow-600" />
      case "rejected":
        return <XCircle className="w-4 h-4 text-red-600" />
      default:
        return <Clock className="w-4 h-4 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "approved":
        return "bg-green-100 text-green-800"
      case "pending":
        return "bg-yellow-100 text-yellow-800"
      case "rejected":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // Get user info from localStorage
    const userEmail = localStorage.getItem("userEmail") || ""
    const userName = localStorage.getItem("userName") || ""
    const userDepartment = localStorage.getItem("userDepartment") || ""
    const userType = localStorage.getItem("userType") || ""

    // Submit to workflow system
    const workflowManager = WorkflowManager.getInstance()
    const requestId = workflowManager.submitRequest({
      type: "leave",
      submittedBy: {
        email: userEmail,
        name: userName,
        department: userDepartment,
        role: userType,
      },
      data: {
        leaveType,
        startDate,
        endDate,
        reason,
        days: calculateDays(),
      },
      priority: "medium",
    })

    console.log("Leave request submitted with ID:", requestId)

    // Reset form
    setLeaveType("")
    setStartDate("")
    setEndDate("")
    setReason("")
    setIsSubmitting(false)

    // Show success message (you can add a toast notification here)
    alert(`Leave request submitted successfully! Request ID: ${requestId}`)
  }

  const calculateDays = () => {
    if (startDate && endDate) {
      const start = new Date(startDate)
      const end = new Date(endDate)
      const diffTime = Math.abs(end.getTime() - start.getTime())
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
      return diffDays
    }
    return 0
  }

  return (
    <div className="space-y-8">
      {/* Leave Balance Overview */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Leave Management</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {leaveBalance.map((leave, index) => (
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
              <Plus className="w-5 h-5" />
              Apply for Leave
            </CardTitle>
            <CardDescription>Submit a new leave request for manager approval</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="leaveType">Leave Type</Label>
                <Select value={leaveType} onValueChange={setLeaveType} required>
                  <SelectTrigger className="h-11">
                    <SelectValue placeholder="Select leave type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="vacation">Vacation Leave</SelectItem>
                    <SelectItem value="sick">Sick Leave</SelectItem>
                    <SelectItem value="personal">Personal Leave</SelectItem>
                    <SelectItem value="comp-off">Comp Off</SelectItem>
                    <SelectItem value="maternity">Maternity Leave</SelectItem>
                    <SelectItem value="paternity">Paternity Leave</SelectItem>
                    <SelectItem value="emergency">Emergency Leave</SelectItem>
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
                  />
                </div>
              </div>

              {startDate && endDate && (
                <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-sm font-medium text-blue-900">
                    Duration: {calculateDays()} day{calculateDays() !== 1 ? "s" : ""}
                  </p>
                </div>
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

              <Button
                type="submit"
                className="w-full h-11 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Clock className="w-4 h-4 mr-2 animate-spin" />
                    Submitting Request...
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4 mr-2" />
                    Submit Leave Request
                  </>
                )}
              </Button>
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
            <div className="space-y-4">
              {leaveHistory.map((leave) => (
                <div
                  key={leave.id}
                  className="p-4 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors duration-200"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(leave.status)}
                      <div>
                        <p className="font-medium text-gray-900">{leave.type}</p>
                        <p className="text-sm text-gray-600">{leave.dates}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge className={getStatusColor(leave.status)}>{leave.status}</Badge>
                      <p className="text-xs text-gray-500 mt-1">
                        {leave.days} day{leave.days !== 1 ? "s" : ""}
                      </p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{leave.reason}</p>
                  <p className="text-xs text-gray-500">Applied on {leave.appliedDate}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
