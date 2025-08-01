// Common API response interfaces
export interface ApiResponse<T = any> {
    data?: T;
    error?: string;
    message?: string;
  }
  
  export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    size: number;
    pages: number;
  }
  
  // Timesheet interfaces - Updated to match backend schemas
  export interface TimesheetDetail {
    DetailID: number;
    TimesheetID: number;
    WorkDate: string;
    ProjectCode?: string | null;
    TaskDescription?: string;
    HoursWorked: number;
    IsOvertime: boolean;
    CreatedAt: string;
  }

  export interface Timesheet {
    TimesheetID: number;
    EmployeeID: number;
    WeekStartDate: string;
    WeekEndDate: string;
    TotalHours: number;
    StatusCode: 'Draft' | 'Submitted' | 'Approved' | 'Rejected';
    SubmittedAt?: string;
    ApprovedByID?: number;
    ApprovedAt?: string;
    Comments?: string;
    CreatedAt: string;
    UpdatedAt: string;
    details?: TimesheetDetail[];
    employee?: EmployeeInfo;
  }

  export interface EmployeeInfo {
    EmployeeID: number;
    FirstName: string;
    MiddleName?: string;
    LastName: string;
    CompanyEmail: string;
    DesignationName?: string;
  }

  export interface TimesheetBatchResponse {
    employee: EmployeeInfo;
    current_week: Timesheet;
    history: Timesheet[];
    week_start_date: string;
    week_end_date: string;
  }

  // Form interfaces
  export interface DailyEntryFormData {
    WorkDate: string;
    ProjectCode?: string | null;
    TaskDescription?: string;
    HoursWorked: number;
    IsOvertime: boolean;
  }

  export interface WeeklyTimesheetFormData {
    WeekStartDate: string;
    WeekEndDate: string;
    Comments?: string;
    details: DailyEntryFormData[];
  }

  // API response interfaces
  export interface BulkSaveResponse {
    success: boolean;
    saved_entries: TimesheetDetail[];
    errors: string[];
  }

  export interface TimesheetSubmissionResponse {
    success: boolean;
    timesheet: Timesheet;
    message: string;
  }

  // Legacy interfaces for backward compatibility
  export interface TimesheetEntry {
    id: number;
    employeeId: number;
    workDate: string;
    hours: number;
    project: string;
    description: string;
    overtime: boolean;
  }
  
  // Employee interfaces
  export interface Employee {
    id: number;
    name: string;
    email: string;
    position: string;
    department: string;
    joinDate: string;
    managerId?: number;
    status: 'active' | 'inactive';
  }
  
  // Leave interfaces
  export interface LeaveRequest {
    id: number;
    employeeId: number;
    leaveType: string;
    startDate: string;
    endDate: string;
    reason: string;
    status: 'pending' | 'approved' | 'rejected';
  }

  // Auth interfaces
  export interface LoginRequest {
    username: string;
    password: string;
  }

  export interface LoginResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
  }

  export interface UserResponse {
    UserID: string;
    Username: string;
    Email: string;
    IsActive: boolean;
    CreatedAt: string;
    UpdatedAt: string;
  }