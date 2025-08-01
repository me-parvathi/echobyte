"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import WorkflowManager, { type WorkflowRequest } from "@/lib/workflow-manager"
import {
  CheckCircle,
  XCircle,
  Clock,
  Calendar,
  TicketIcon,
  MessageSquare,
  User,
  Sparkles,
  AlertTriangle,
} from "lucide-react"

interface PendingApprovalsProps {
  userEmail: string
  userRole: string
}

export default function PendingApprovals({ userEmail, userRole }: PendingApprovalsProps) {
  const [requests, setRequests] = useState<WorkflowRequest[]>([])
  const [selectedRequest, setSelectedRequest] = useState<WorkflowRequest | null>(null)
  const [comment, setComment] = useState("")
  const [isProcessing, setIsProcessing] = useState(false)

  useEffect(() => {
    const workflowManager = WorkflowManager.getInstance()
    const userRequests = workflowManager.getRequestsForUser(userEmail, userRole)
    setRequests(userRequests.filter((r) => r.assignedTo === userEmail && r.status === "pending"))
  }, [userEmail, userRole])

  const handleApproval = async (requestId: string, status: "approved" | "rejected") => {
    setIsProcessing(true)

    // Simulate processing time
    await new Promise((resolve) => setTimeout(resolve, 1000))

    const workflowManager = WorkflowManager.getInstance()
    workflowManager.updateRequestStatus(requestId, status, comment, userEmail)

    // Refresh requests
    const userRequests = workflowManager.getRequestsForUser(userEmail, userRole)
    setRequests(userRequests.filter((r) => r.assignedTo === userEmail && r.status === "pending"))

    setSelectedRequest(null)
    setComment("")
    setIsProcessing(false)
  }

  const getRequestIcon = (type: string) => {
    switch (type) {
      case "leave":
        return <Calendar className="w-5 h-5 text-emerald-600" />
      case "support":
        return <TicketIcon className="w-5 h-5 text-blue-600" />
      case "feedback":
        return <MessageSquare className="w-5 h-5 text-purple-600" />
      default:
        return <Clock className="w-5 h-5 text-gray-600" />
    }
  }

  const getRequestIconBg = (type: string) => {
    switch (type) {
      case "leave":
        return "bg-gradient-to-r from-emerald-400 to-teal-500"
      case "support":
        return "bg-gradient-to-r from-blue-400 to-cyan-500"
      case "feedback":
        return "bg-gradient-to-r from-purple-400 to-pink-500"
      default:
        return "bg-gradient-to-r from-gray-400 to-slate-500"
    }
  }

  const getRequestBg = (type: string) => {
    switch (type) {
      case "leave":
        return "from-emerald-50/80 to-teal-50/80 border-emerald-200/50"
      case "support":
        return "from-blue-50/80 to-cyan-50/80 border-blue-200/50"
      case "feedback":
        return "from-purple-50/80 to-pink-50/80 border-purple-200/50"
      default:
        return "from-gray-50/80 to-slate-50/80 border-gray-200/50"
    }
  }

  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case "critical":
        return "bg-gradient-to-r from-red-500 to-rose-500 text-white shadow-lg"
      case "high":
        return "bg-gradient-to-r from-orange-500 to-amber-500 text-white shadow-lg"
      case "medium":
        return "bg-gradient-to-r from-yellow-500 to-orange-500 text-white shadow-lg"
      case "low":
        return "bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg"
      default:
        return "bg-gradient-to-r from-gray-500 to-slate-500 text-white shadow-lg"
    }
  }

  const formatRequestData = (request: WorkflowRequest) => {
    switch (request.type) {
      case "leave":
        return `${request.data.leaveType} - ${request.data.startDate} to ${request.data.endDate} (${request.data.days} days)`
      case "support":
        return `${request.data.subject} - ${request.data.department} department`
      case "feedback":
        return `Feedback submission`
      default:
        return "Request details"
    }
  }

  if (requests.length === 0) {
    return (
      <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
        <CardContent className="p-12 text-center">
          <div className="relative">
            <div className="w-20 h-20 bg-gradient-to-r from-emerald-400 to-teal-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
              <CheckCircle className="w-10 h-10 text-white" />
            </div>
            <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-r from-amber-400 to-orange-500 rounded-full flex items-center justify-center shadow-lg">
              <Sparkles className="w-4 h-4 text-white animate-pulse" />
            </div>
          </div>
          <h3 className="text-xl font-semibold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent mb-2">
            All caught up!
          </h3>
          <p className="text-gray-600">No pending approvals at the moment. Great work staying on top of things!</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent mb-2">
          Pending Approvals
        </h2>
        <p className="text-gray-600">Review and approve requests from your team</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm hover:scale-105">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-orange-400 to-amber-500 rounded-xl shadow-lg">
                <AlertTriangle className="w-6 h-6 text-white" />
              </div>
              <Badge className="bg-gradient-to-r from-orange-500 to-amber-600 text-white border-0 shadow-sm">
                {requests.length}
              </Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Total Pending</p>
              <p className="text-2xl font-bold text-gray-900">{requests.length}</p>
              <p className="text-xs text-gray-500">Awaiting your review</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm hover:scale-105">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-emerald-400 to-teal-500 rounded-xl shadow-lg">
                <Calendar className="w-6 h-6 text-white" />
              </div>
              <Badge className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white border-0 shadow-sm">
                {requests.filter((r) => r.type === "leave").length}
              </Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Leave Requests</p>
              <p className="text-2xl font-bold text-gray-900">{requests.filter((r) => r.type === "leave").length}</p>
              <p className="text-xs text-gray-500">Time off requests</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm hover:scale-105">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-blue-400 to-cyan-500 rounded-xl shadow-lg">
                <TicketIcon className="w-6 h-6 text-white" />
              </div>
              <Badge className="bg-gradient-to-r from-blue-500 to-cyan-600 text-white border-0 shadow-sm">
                {requests.filter((r) => r.type === "support").length}
              </Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Support Tickets</p>
              <p className="text-2xl font-bold text-gray-900">{requests.filter((r) => r.type === "support").length}</p>
              <p className="text-xs text-gray-500">Help requests</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Requests List */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Pending Requests</h3>
          {requests.map((request) => (
            <Card
              key={request.id}
              className={`border-0 shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer group bg-gradient-to-r ${getRequestBg(request.type)} backdrop-blur-sm hover:scale-105 ${
                selectedRequest?.id === request.id ? "ring-2 ring-orange-400 shadow-2xl" : ""
              }`}
              onClick={() => setSelectedRequest(request)}
            >
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div
                      className={`p-3 ${getRequestIconBg(request.type)} rounded-xl shadow-lg group-hover:scale-110 transition-transform duration-300`}
                    >
                      {getRequestIcon(request.type)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="font-mono text-sm font-medium text-gray-900 bg-white/60 px-2 py-1 rounded-lg backdrop-blur-sm">
                          {request.id}
                        </span>
                        {request.priority && (
                          <Badge className={`${getPriorityColor(request.priority)} text-xs border-0`}>
                            {request.priority}
                          </Badge>
                        )}
                      </div>
                      <p className="font-semibold text-gray-900 mb-1">{formatRequestData(request)}</p>
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <div className="flex items-center gap-1">
                          <User className="w-4 h-4" />
                          <span className="font-medium">{request.submittedBy.name}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          <span>{new Date(request.submittedAt).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white border-0 shadow-lg animate-pulse">
                    Pending
                  </Badge>
                </div>

                {request.type === "leave" && (
                  <div className="mt-4 p-3 bg-white/40 rounded-lg backdrop-blur-sm">
                    <p className="text-sm text-gray-700">
                      <strong>Reason:</strong> {request.data.reason}
                    </p>
                  </div>
                )}

                {request.type === "support" && (
                  <div className="mt-4 p-3 bg-white/40 rounded-lg backdrop-blur-sm">
                    <p className="text-sm text-gray-700">
                      <strong>Description:</strong> {request.data.description.substring(0, 100)}...
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Request Details & Actions */}
        {selectedRequest && (
          <Card className="border-0 shadow-xl bg-white/90 backdrop-blur-sm sticky top-6">
            <CardHeader className="bg-gradient-to-r from-orange-50 to-amber-50 border-b border-orange-200/50">
              <CardTitle className="flex items-center gap-3">
                <div className={`p-2 ${getRequestIconBg(selectedRequest.type)} rounded-lg shadow-md`}>
                  {getRequestIcon(selectedRequest.type)}
                </div>
                <div>
                  <span className="bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
                    Request Details
                  </span>
                  <p className="text-sm font-normal text-gray-600 mt-1">Review and take action on this request</p>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6 p-6">
              <div className="bg-gradient-to-r from-gray-50 to-slate-50 p-4 rounded-xl border border-gray-200/50">
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-orange-500" />
                  Request Information
                </h4>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">ID:</span>
                    <span className="font-mono font-medium bg-white px-2 py-1 rounded">{selectedRequest.id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Type:</span>
                    <Badge variant="outline" className="capitalize">
                      {selectedRequest.type}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Submitted by:</span>
                    <span className="font-medium">{selectedRequest.submittedBy.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Department:</span>
                    <Badge variant="outline">{selectedRequest.submittedBy.department}</Badge>
                  </div>
                  <div className="flex justify-between col-span-2">
                    <span className="text-gray-600">Submitted:</span>
                    <span className="font-medium">{new Date(selectedRequest.submittedAt).toLocaleString()}</span>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-blue-50 to-cyan-50 p-4 rounded-xl border border-blue-200/50">
                <h4 className="font-semibold text-gray-900 mb-3">Request Details</h4>
                <div className="space-y-3 text-sm">
                  {selectedRequest.type === "leave" && (
                    <>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <span className="text-gray-600 block">Leave Type:</span>
                          <span className="font-medium">{selectedRequest.data.leaveType}</span>
                        </div>
                        <div>
                          <span className="text-gray-600 block">Duration:</span>
                          <span className="font-medium">{selectedRequest.data.days} days</span>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <span className="text-gray-600 block">Start Date:</span>
                          <span className="font-medium">{selectedRequest.data.startDate}</span>
                        </div>
                        <div>
                          <span className="text-gray-600 block">End Date:</span>
                          <span className="font-medium">{selectedRequest.data.endDate}</span>
                        </div>
                      </div>
                      <div>
                        <span className="text-gray-600 block mb-1">Reason:</span>
                        <p className="bg-white/60 p-2 rounded-lg">{selectedRequest.data.reason}</p>
                      </div>
                    </>
                  )}

                  {selectedRequest.type === "support" && (
                    <>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <span className="text-gray-600 block">Department:</span>
                          <Badge variant="outline">{selectedRequest.data.department}</Badge>
                        </div>
                        <div>
                          <span className="text-gray-600 block">Priority:</span>
                          <Badge className={getPriorityColor(selectedRequest.priority)}>
                            {selectedRequest.priority}
                          </Badge>
                        </div>
                      </div>
                      <div>
                        <span className="text-gray-600 block mb-1">Subject:</span>
                        <p className="font-medium bg-white/60 p-2 rounded-lg">{selectedRequest.data.subject}</p>
                      </div>
                      <div>
                        <span className="text-gray-600 block mb-1">Description:</span>
                        <p className="bg-white/60 p-2 rounded-lg text-sm">{selectedRequest.data.description}</p>
                      </div>
                    </>
                  )}
                </div>
              </div>

              <div>
                <Label htmlFor="comment" className="text-sm font-semibold text-gray-700">
                  Comments (Optional)
                </Label>
                <Textarea
                  id="comment"
                  placeholder="Add a comment for the requester..."
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  rows={3}
                  className="resize-none mt-2 bg-white/80 border-gray-200/50 focus:border-orange-300 focus:ring-orange-200"
                />
              </div>

              <div className="flex gap-3">
                <Button
                  onClick={() => handleApproval(selectedRequest.id, "approved")}
                  disabled={isProcessing}
                  className="flex-1 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white shadow-lg hover:shadow-xl transition-all duration-300"
                >
                  {isProcessing ? (
                    <Clock className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <CheckCircle className="w-4 h-4 mr-2" />
                  )}
                  Approve
                </Button>
                <Button
                  onClick={() => handleApproval(selectedRequest.id, "rejected")}
                  disabled={isProcessing}
                  className="flex-1 bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 text-white shadow-lg hover:shadow-xl transition-all duration-300"
                >
                  {isProcessing ? (
                    <Clock className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <XCircle className="w-4 h-4 mr-2" />
                  )}
                  Reject
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
