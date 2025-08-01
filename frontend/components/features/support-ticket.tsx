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
import { TicketIcon, Send, Clock, CheckCircle, AlertTriangle, Phone, Mail, MessageSquare } from "lucide-react"
import WorkflowManager from "@/lib/workflow-manager"

export default function SupportTicket() {
  const [department, setDepartment] = useState("")
  const [priority, setPriority] = useState("")
  const [subject, setSubject] = useState("")
  const [description, setDescription] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)

  const departments = [
    {
      value: "it",
      label: "IT Support",
      description: "Technical issues, software, hardware",
      contact: "Ext: 2001 | it-support@company.com",
    },
    {
      value: "hr",
      label: "Human Resources",
      description: "Benefits, policies, employee relations",
      contact: "Ext: 2002 | hr@company.com",
    },
    {
      value: "admin",
      label: "Administration",
      description: "Office supplies, general requests",
      contact: "Ext: 2003 | admin@company.com",
    },
    {
      value: "facilities",
      label: "Facilities",
      description: "Building maintenance, workspace issues",
      contact: "Ext: 2004 | facilities@company.com",
    },
    {
      value: "finance",
      label: "Finance",
      description: "Payroll, expenses, financial queries",
      contact: "Ext: 2005 | finance@company.com",
    },
    {
      value: "security",
      label: "Security",
      description: "Access cards, security concerns",
      contact: "Ext: 2006 | security@company.com",
    },
  ]

  const existingTickets = [
    {
      id: "TK-001",
      subject: "Laptop performance issues",
      department: "IT",
      priority: 1,
      status: "in-progress",
      created: "2024-12-15",
      updated: "2024-12-16",
      assignee: "Mike Wilson",
    },
    {
      id: "TK-002",
      subject: "Benefits enrollment question",
      department: "HR",
      priority: 2,
      status: "resolved",
      created: "2024-12-10",
      updated: "2024-12-12",
      assignee: "Sarah Johnson",
    },
    {
      id: "TK-003",
      subject: "Office supplies request",
      department: "Admin",
      priority: 3,
      status: "open",
      created: "2024-12-08",
      updated: "2024-12-08",
      assignee: "Admin Team",
    },
  ]

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
      type: "support",
      submittedBy: {
        email: userEmail,
        name: userName,
        department: userDepartment,
        role: userType,
      },
      data: {
        department,
        priority: Number.parseInt(priority),
        subject,
        description,
      },
      priority: priority === "1" ? "critical" : priority === "2" ? "high" : "medium",
    })

    console.log("Support ticket submitted with ID:", requestId)

    // Reset form
    setDepartment("")
    setPriority("")
    setSubject("")
    setDescription("")
    setIsSubmitting(false)

    // Show success message
    alert(`Support ticket submitted successfully! Ticket ID: ${requestId}`)
  }

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 1:
        return "bg-red-100 text-red-800"
      case 2:
        return "bg-orange-100 text-orange-800"
      case 3:
        return "bg-yellow-100 text-yellow-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "resolved":
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case "in-progress":
        return <Clock className="w-4 h-4 text-blue-600" />
      case "open":
        return <AlertTriangle className="w-4 h-4 text-orange-600" />
      default:
        return <TicketIcon className="w-4 h-4 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "resolved":
        return "bg-green-100 text-green-800"
      case "in-progress":
        return "bg-blue-100 text-blue-800"
      case "open":
        return "bg-orange-100 text-orange-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Support Center</h2>
        <p className="text-gray-600">Get help from our support team</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Create Ticket Form */}
        <Card className="border-0 shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TicketIcon className="w-5 h-5" />
              Create Support Ticket
            </CardTitle>
            <CardDescription>Submit a request to the appropriate department for assistance</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="department">Department</Label>
                <Select value={department} onValueChange={setDepartment} required>
                  <SelectTrigger className="h-11">
                    <SelectValue placeholder="Select department" />
                  </SelectTrigger>
                  <SelectContent>
                    {departments.map((dept) => (
                      <SelectItem key={dept.value} value={dept.value}>
                        <div>
                          <div className="font-medium">{dept.label}</div>
                          <div className="text-sm text-gray-500">{dept.description}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="priority">Priority Level</Label>
                <Select value={priority} onValueChange={setPriority} required>
                  <SelectTrigger className="h-11">
                    <SelectValue placeholder="Select priority" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                        <div>
                          <div className="font-medium">Critical</div>
                          <div className="text-sm text-gray-500">System down, urgent issue</div>
                        </div>
                      </div>
                    </SelectItem>
                    <SelectItem value="2">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                        <div>
                          <div className="font-medium">High</div>
                          <div className="text-sm text-gray-500">Important, affects productivity</div>
                        </div>
                      </div>
                    </SelectItem>
                    <SelectItem value="3">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                        <div>
                          <div className="font-medium">Medium</div>
                          <div className="text-sm text-gray-500">General request or question</div>
                        </div>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="subject">Subject</Label>
                <Input
                  id="subject"
                  placeholder="Brief description of your issue"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  className="h-11"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Please provide detailed information about your request or issue..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={5}
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
                    Submitting Ticket...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4 mr-2" />
                    Submit Ticket
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Department Contacts */}
        <Card className="border-0 shadow-sm">
          <CardHeader>
            <CardTitle>Department Contacts</CardTitle>
            <CardDescription>Direct contact information for urgent matters</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {departments.map((dept) => (
              <div
                key={dept.value}
                className="p-4 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors duration-200"
              >
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{dept.label}</h4>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="h-8 w-8 p-0 bg-transparent">
                      <Phone className="w-4 h-4" />
                    </Button>
                    <Button size="sm" variant="outline" className="h-8 w-8 p-0 bg-transparent">
                      <Mail className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                <p className="text-sm text-gray-600 mb-2">{dept.description}</p>
                <p className="text-sm font-medium text-blue-600">{dept.contact}</p>
              </div>
            ))}

            <div className="p-4 bg-red-50 rounded-xl border border-red-200">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-5 h-5 text-red-600" />
                <h4 className="font-medium text-red-900">Emergency</h4>
              </div>
              <p className="text-sm text-red-700">For urgent security or safety issues, call: ext. 911</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Existing Tickets */}
      <Card className="border-0 shadow-sm">
        <CardHeader>
          <CardTitle>Your Support Tickets</CardTitle>
          <CardDescription>Track the status of your submitted tickets</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {existingTickets.map((ticket) => (
              <div
                key={ticket.id}
                className="p-4 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors duration-200"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-4">
                    {getStatusIcon(ticket.status)}
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-sm font-medium text-gray-900">{ticket.id}</span>
                        <Badge variant="outline">{ticket.department}</Badge>
                        <Badge className={getPriorityColor(ticket.priority)}>Priority {ticket.priority}</Badge>
                      </div>
                      <p className="font-medium text-gray-900 mb-1">{ticket.subject}</p>
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span>Created: {ticket.created}</span>
                        <span>Updated: {ticket.updated}</span>
                        <span>Assignee: {ticket.assignee}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={getStatusColor(ticket.status)}>{ticket.status.replace("-", " ")}</Badge>
                    <Button size="sm" variant="outline" className="bg-transparent">
                      <MessageSquare className="w-4 h-4 mr-1" />
                      View
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
