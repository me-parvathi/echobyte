export interface WorkflowRequest {
  id: string
  type: "leave" | "timesheet" | "support" | "feedback"
  submittedBy: {
    email: string
    name: string
    department: string
    role: string
  }
  submittedAt: string
  status: "pending" | "approved" | "rejected" | "in-progress" | "resolved"
  assignedTo?: string
  data: any
  priority?: "low" | "medium" | "high" | "critical"
  comments?: Array<{
    author: string
    message: string
    timestamp: string
  }>
}

class WorkflowManager {
  private static instance: WorkflowManager
  private requests: WorkflowRequest[] = []

  private constructor() {
    // Load existing requests from localStorage
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("workflow_requests")
      if (stored) {
        this.requests = JSON.parse(stored)
      }
    }
  }

  static getInstance(): WorkflowManager {
    if (!WorkflowManager.instance) {
      WorkflowManager.instance = new WorkflowManager()
    }
    return WorkflowManager.instance
  }

  private saveToStorage() {
    if (typeof window !== "undefined") {
      localStorage.setItem("workflow_requests", JSON.stringify(this.requests))
    }
  }

  submitRequest(request: Omit<WorkflowRequest, "id" | "submittedAt" | "status">): string {
    const newRequest: WorkflowRequest = {
      ...request,
      id: `REQ-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      submittedAt: new Date().toISOString(),
      status: "pending",
    }

    // Auto-assign based on request type
    switch (request.type) {
      case "leave":
        // Leave requests go to manager first, then HR if needed
        newRequest.assignedTo = this.getManagerForDepartment(request.submittedBy.department)
        break
      case "timesheet":
        // Timesheet approvals go to manager
        newRequest.assignedTo = this.getManagerForDepartment(request.submittedBy.department)
        break
      case "support":
        // Support tickets go to appropriate department based on category
        const supportData = request.data as { department: string }
        newRequest.assignedTo = this.getDepartmentLead(supportData.department)
        break
      case "feedback":
        // Feedback goes to HR
        newRequest.assignedTo = "hr.admin@company.com"
        break
    }

    this.requests.push(newRequest)
    this.saveToStorage()
    return newRequest.id
  }

  getRequestsForUser(userEmail: string, userRole: string): WorkflowRequest[] {
    return this.requests.filter((request) => {
      // Users can see their own requests
      if (request.submittedBy.email === userEmail) {
        return true
      }

      // Managers can see requests assigned to them
      if (request.assignedTo === userEmail) {
        return true
      }

      // HR can see all leave requests and feedback
      if (userRole === "hr" && (request.type === "leave" || request.type === "feedback")) {
        return true
      }

      // IT can see all support tickets
      if (userRole === "it" && request.type === "support") {
        return true
      }

      return false
    })
  }

  updateRequestStatus(requestId: string, status: WorkflowRequest["status"], comment?: string, updatedBy?: string) {
    const request = this.requests.find((r) => r.id === requestId)
    if (request) {
      request.status = status

      if (comment && updatedBy) {
        if (!request.comments) request.comments = []
        request.comments.push({
          author: updatedBy,
          message: comment,
          timestamp: new Date().toISOString(),
        })
      }

      this.saveToStorage()
    }
  }

  private getManagerForDepartment(department: string): string {
    // In a real system, this would query the database
    const managerMap: Record<string, string> = {
      Engineering: "jane.manager@company.com",
      Marketing: "jane.manager@company.com",
      "Human Resources": "hr.admin@company.com",
      "IT Support": "it.support@company.com",
    }
    return managerMap[department] || "jane.manager@company.com"
  }

  private getDepartmentLead(department: string): string {
    const leadMap: Record<string, string> = {
      it: "it.support@company.com",
      hr: "hr.admin@company.com",
      admin: "hr.admin@company.com",
      facilities: "hr.admin@company.com",
      finance: "hr.admin@company.com",
      security: "it.support@company.com",
    }
    return leadMap[department] || "hr.admin@company.com"
  }
}

export default WorkflowManager
