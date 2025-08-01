// Database Schema for Employee Dashboard System
// This will be used when connecting to your actual database

export interface DatabaseTables {
  // Users table
  users: {
    id: string
    email: string
    name: string
    department: string
    role: "employee" | "manager" | "hr" | "it"
    manager_id?: string
    created_at: Date
    updated_at: Date
  }

  // Workflow requests table
  workflow_requests: {
    id: string
    type: "leave" | "timesheet" | "support" | "feedback"
    submitted_by: string // user_id
    assigned_to?: string // user_id
    status: "pending" | "approved" | "rejected" | "in-progress" | "resolved"
    priority: "low" | "medium" | "high" | "critical"
    data: any // JSON field for request-specific data
    submitted_at: Date
    updated_at: Date
  }

  // Comments table for workflow requests
  workflow_comments: {
    id: string
    request_id: string
    author_id: string
    message: string
    created_at: Date
  }

  // Assets table
  assets: {
    id: string
    name: string
    category: string
    serial_number: string
    assigned_to?: string // user_id
    department: string
    status: "active" | "maintenance" | "retired"
    condition: "excellent" | "good" | "fair" | "poor"
    purchase_date: Date
    warranty_expiry?: Date
    location: string
    specifications?: string
    last_maintenance?: Date
    created_at: Date
    updated_at: Date
  }

  // Leave balances table
  leave_balances: {
    id: string
    user_id: string
    leave_type: string
    total_days: number
    used_days: number
    available_days: number
    year: number
    created_at: Date
    updated_at: Date
  }

  // Timesheets table
  timesheets: {
    id: string
    user_id: string
    week_ending: Date
    total_hours: number
    regular_hours: number
    overtime_hours: number
    status: "draft" | "submitted" | "approved" | "rejected"
    submitted_at?: Date
    approved_at?: Date
    approved_by?: string
    created_at: Date
    updated_at: Date
  }

  // Timesheet entries table
  timesheet_entries: {
    id: string
    timesheet_id: string
    date: Date
    hours: number
    project: string
    description: string
    created_at: Date
    updated_at: Date
  }

  // Learning progress table
  learning_progress: {
    id: string
    user_id: string
    course_id: string
    progress: number // 0-100
    completed: boolean
    completed_at?: Date
    created_at: Date
    updated_at: Date
  }

  // Badges table
  user_badges: {
    id: string
    user_id: string
    badge_name: string
    badge_description: string
    earned_date: Date
    created_at: Date
  }
}

// Database operations that will be implemented
export interface DatabaseOperations {
  // Workflow operations
  createWorkflowRequest: (
    request: Omit<DatabaseTables["workflow_requests"], "id" | "submitted_at" | "updated_at">,
  ) => Promise<string>
  getWorkflowRequestsForUser: (userId: string, userRole: string) => Promise<DatabaseTables["workflow_requests"][]>
  updateWorkflowRequestStatus: (
    requestId: string,
    status: string,
    comment?: string,
    updatedBy?: string,
  ) => Promise<void>

  // Asset operations
  createAsset: (asset: Omit<DatabaseTables["assets"], "id" | "created_at" | "updated_at">) => Promise<string>
  getAssets: (filters?: { status?: string; category?: string; search?: string }) => Promise<DatabaseTables["assets"][]>
  updateAsset: (assetId: string, updates: Partial<DatabaseTables["assets"]>) => Promise<void>
  deleteAsset: (assetId: string) => Promise<void>

  // Leave operations
  getLeaveBalance: (userId: string, year: number) => Promise<DatabaseTables["leave_balances"][]>
  updateLeaveBalance: (userId: string, leaveType: string, daysUsed: number) => Promise<void>

  // Timesheet operations
  createTimesheet: (
    timesheet: Omit<DatabaseTables["timesheets"], "id" | "created_at" | "updated_at">,
  ) => Promise<string>
  getTimesheets: (
    userId: string,
    filters?: { status?: string; weekEnding?: Date },
  ) => Promise<DatabaseTables["timesheets"][]>
  updateTimesheetStatus: (timesheetId: string, status: string, approvedBy?: string) => Promise<void>

  // User operations
  getUser: (userId: string) => Promise<DatabaseTables["users"] | null>
  getUsersByDepartment: (department: string) => Promise<DatabaseTables["users"][]>
  getManagerForUser: (userId: string) => Promise<DatabaseTables["users"] | null>
}

// Example API endpoints that will be created
export const API_ENDPOINTS = {
  // Workflow endpoints
  POST_WORKFLOW_REQUEST: "/workflow/requests",
  GET_WORKFLOW_REQUESTS: "/workflow/requests",
  PUT_WORKFLOW_REQUEST: "/workflow/requests/[id]",

  // Asset endpoints
  POST_ASSET: "/assets",
  GET_ASSETS: "/assets",
  PUT_ASSET: "/assets/[id]",
  DELETE_ASSET: "/assets/[id]",

  // Leave endpoints
  POST_LEAVE_REQUEST: "/leave/requests",
  GET_LEAVE_BALANCE: "/leave/balance",
  PUT_LEAVE_BALANCE: "/leave/balance",

  // Timesheet endpoints
  POST_TIMESHEET: "/timesheets",
  GET_TIMESHEETS: "/timesheets",
  PUT_TIMESHEET: "/timesheets/[id]",

  // User endpoints
  GET_USER: "/users/[id]",
  GET_USERS: "/users",
}

// Example of how data will flow when database is connected:
export const DATABASE_FLOW_EXAMPLE = {
  // When user submits leave request:
  submitLeaveRequest: async (leaveData: any, createWorkflowRequest: any) => {
    // 1. Create workflow request in database
    const requestId = await createWorkflowRequest({
      type: "leave",
      submitted_by: leaveData.userId,
      assigned_to: leaveData.managerId, // Auto-assigned to manager
      status: "pending",
      priority: "medium",
      data: leaveData,
    })

    // 2. Send notification to manager
    // 3. Update leave balance (pending)
    // 4. Return request ID to user
    return requestId
  },

  // When manager approves/rejects:
  processLeaveRequest: async (
    requestId: string,
    status: "approved" | "rejected",
    comment: string,
    updateWorkflowRequestStatus: any,
  ) => {
    // 1. Update workflow request status
    await updateWorkflowRequestStatus(requestId, status, comment)

    // 2. If approved, update leave balance
    if (status === "approved") {
      // Update user's leave balance
    }

    // 3. Send notification to employee
    // 4. Log the action
  },
}
