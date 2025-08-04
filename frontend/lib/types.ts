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

  export interface TimesheetApprovalRequest {
    status: 'Approved' | 'Rejected';
    approved_by_id: number;
    comments?: string;
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

  // New comprehensive leave interfaces matching backend schemas
  export interface LeaveApplication {
    LeaveApplicationID: number;
    EmployeeID: number;
    LeaveTypeID: number;
    StartDate: string;
    EndDate: string;
    NumberOfDays: number;
    Reason?: string;
    StatusCode: string;
    SubmittedAt?: string;
    ManagerID?: number;
    ManagerApprovalStatus?: string;
    ManagerApprovalAt?: string;
    HRApproverID?: number;
    HRApprovalStatus?: string;
    HRApprovalAt?: string;
    CreatedAt: string;
    UpdatedAt: string;
    leave_type?: LeaveType;
    employee?: EmployeeInfo;
  }

  export interface LeaveApplicationCreate {
    EmployeeID: number;
    LeaveTypeID: number;
    StartDate: string;
    EndDate: string;
    NumberOfDays?: number;
    Reason?: string;
    StatusCode?: string;
    calculation_type?: string;
    exclude_holidays?: boolean;
  }

  export interface LeaveApplicationUpdate {
    EmployeeID?: number;
    LeaveTypeID?: number;
    StartDate?: string;
    EndDate?: string;
    NumberOfDays?: number;
    Reason?: string;
    StatusCode?: string;
    ManagerID?: number;
    ManagerApprovalStatus?: string;
    HRApproverID?: number;
    HRApprovalStatus?: string;
  }

  export interface LeaveType {
    LeaveTypeID: number;
    LeaveTypeName: string;
    LeaveCode: string;
    DefaultDaysPerYear?: number;
    IsActive: boolean;
    CreatedAt: string;
  }

  export interface LeaveBalance {
    BalanceID: number;
    EmployeeID: number;
    LeaveTypeID: number;
    Year: number;
    EntitledDays: number;
    UsedDays: number;
    CreatedAt: string;
    UpdatedAt: string;
    leave_type?: LeaveType;
  }

  export interface LeaveBalanceSummary {
    employee_id: number;
    year: number;
    total_entitled_days: number;
    total_used_days: number;
    total_remaining_days: number;
    balances: LeaveBalance[];
  }

  export interface LeaveDaysCalculation {
    start_date: string;
    end_date: string;
    calculation_type: string;
    exclude_holidays: boolean;
    number_of_days: number;
  }

  export interface TimesheetConflict {
    has_conflict: boolean;
    conflicting_dates?: string[];
    message?: string;
  }

  // Pagination interfaces
  export interface PaginationParams {
    skip?: number;
    limit?: number;
    page?: number;
  }

  export interface PaginatedLeaveResponse {
    items: LeaveApplication[];
    total_count: number;
    page: number;
    size: number;
    has_next: boolean;
    has_previous: boolean;
  }

  export interface LeaveFilterParams {
    employee_id?: number;
    status_code?: string;
    start_date?: string;
    end_date?: string;
    leave_type_id?: number;
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

  // Asset Management Interfaces
  export interface AssetStatus {
    AssetStatusCode: string;
    AssetStatusName: string;
    IsAssignable: boolean;
    IsActive: boolean;
    CreatedAt: string;
  }

  export interface AssetType {
    AssetTypeID: number;
    AssetTypeName: string;
    IsActive: boolean;
    CreatedAt: string;
  }

  export interface Asset {
    AssetID: number;
    AssetTag: string;
    SerialNumber?: string;
    MACAddress?: string;
    AssetTypeID: number;
    AssetStatusCode: string;
    Model?: string;
    Vendor?: string;
    PurchaseDate?: string;
    WarrantyEndDate?: string;
    IsUnderContract: boolean;
    ContractStartDate?: string;
    ContractExpiryDate?: string;
    LocationID?: number;
    Notes?: string;
    IsActive: boolean;
    CreatedAt: string;
    UpdatedAt: string;
    // Relationships
    asset_type?: AssetType;
    asset_status?: AssetStatus;
    location?: Location;
    assignments?: AssetAssignment[];
    current_assignment?: AssetAssignment;
  }

  export interface AssetAssignment {
    AssignmentID: number;
    AssetID: number;
    EmployeeID: number;
    AssignedAt: string;
    DueReturnDate?: string;
    ReturnedAt?: string;
    ConditionAtAssign?: string;
    ConditionAtReturn?: string;
    AssignedByID: number;
    ReceivedByID?: number;
    Notes?: string;
    CreatedAt: string;
    UpdatedAt: string;
    // Relationships
    asset?: Asset;
    employee?: EmployeeInfo;
    assigned_by?: EmployeeInfo;
    received_by?: EmployeeInfo;
  }

  export interface Location {
    LocationID: number;
    LocationName: string;
    Address1: string;
    Address2?: string;
    City: string;
    State?: string;
    Country: string;
    PostalCode?: string;
    Phone?: string;
    TimeZone: string;
    IsActive: boolean;
    CreatedAt: string;
    UpdatedAt: string;
  }

  // Asset creation and update interfaces


  export interface AssetAssignmentCreate {
    AssetID: number;
    EmployeeID: number;
    DueReturnDate?: string;
    ConditionAtAssign?: string;
    Notes?: string;
  }

  export interface AssetAssignmentUpdate {
    DueReturnDate?: string;
    ReturnedAt?: string;
    ConditionAtReturn?: string;
    Notes?: string;
  }

  // Asset filter and pagination interfaces
  export interface AssetFilterParams {
    asset_type_id?: number;
    status_code?: string;
    location_id?: number;
    assigned_to_employee?: number;
    warranty_expiring_soon?: boolean;
    contract_expiring_soon?: boolean;
    search?: string;
  }

  export interface AssetSortParams {
    sort_by?: 'created_at' | 'updated_at' | 'asset_tag' | 'purchase_date' | 'warranty_end_date' | 'contract_expiry_date';
    sort_order?: 'asc' | 'desc';
  }

  export interface AssetListParams extends AssetFilterParams, AssetSortParams, PaginationParams {}

  export interface PaginatedAssetResponse {
    items: Asset[];
    total_count: number;
    page: number;
    size: number;
    has_next: boolean;
    has_previous: boolean;
  }

  // Asset statistics interfaces
  export interface AssetStatistics {
    total_assets: number;
    active_assets: number;
    in_maintenance: number;
    assigned_assets: number;
    available_assets: number;
    retiring_soon: number;
    warranty_expiring_soon: number;
    contract_expiring_soon: number;
    by_status: Record<string, number>;
    by_type: Record<string, number>;
    by_location: Record<string, number>;
  }

  // Asset status transition interfaces
  export interface AssetStatusTransition {
    from_status: string;
    to_status: string;
    allowed: boolean;
    requires_approval?: boolean;
    notes_required?: boolean;
  }

  // Asset status transition rules
  export const ASSET_STATUS_TRANSITIONS: Record<string, string[]> = {
    'In-Stock': ['Available', 'Maintenance', 'Decommissioning'],
    'Available': ['Assigned', 'Maintenance', 'Decommissioning'],
    'Assigned': ['Available', 'Maintenance', 'Decommissioning'],
    'Maintenance': ['Available', 'Assigned', 'Decommissioning'],
    'Decommissioning': ['Retired'],
    'Retired': [] // Terminal state
  }

  // Required fields based on database schema
  export interface AssetRequiredFields {
    AssetTag: string;
    AssetTypeID: number;
    AssetStatusCode: string;
    IsActive: boolean;
  }

  // Optional fields that can be null
  export interface AssetOptionalFields {
    SerialNumber?: string;
    MACAddress?: string;
    Model?: string;
    Vendor?: string;
    PurchaseDate?: string;
    WarrantyEndDate?: string;
    IsUnderContract?: boolean;
    ContractStartDate?: string;
    ContractExpiryDate?: string;
    LocationID?: number;
    Notes?: string;
  }

  // Asset creation with proper validation
  export interface AssetCreate {
    AssetTag: string;
    AssetTypeID: number;
    AssetStatusCode: string;
    IsActive: boolean;
    SerialNumber?: string;
    MACAddress?: string;
    Model?: string;
    Vendor?: string;
    PurchaseDate?: string;
    WarrantyEndDate?: string;
    IsUnderContract?: boolean;
    ContractStartDate?: string;
    ContractExpiryDate?: string;
    LocationID?: number;
    Notes?: string;
  }

  // Asset update with all fields optional
  export interface AssetUpdate {
    AssetTag?: string;
    AssetTypeID?: number;
    AssetStatusCode?: string;
    IsActive?: boolean;
    SerialNumber?: string;
    MACAddress?: string;
    Model?: string;
    Vendor?: string;
    PurchaseDate?: string;
    WarrantyEndDate?: string;
    IsUnderContract?: boolean;
    ContractStartDate?: string;
    ContractExpiryDate?: string;
    LocationID?: number;
    Notes?: string;
  }

  // Asset assignment with validation
  export interface AssetAssignmentCreate {
    AssetID: number;
    EmployeeID: number;
    DueReturnDate?: string;
    ConditionAtAssign?: string;
    Notes?: string;
  }

  // Asset return with validation
  export interface AssetReturnData {
    ReturnedAt: string;
    ConditionAtReturn?: string;
    Notes?: string;
  }

  // Asset status change with validation
  export interface AssetStatusChange {
    AssetID: number;
    NewStatusCode: string;
    Notes?: string;
    RequiresApproval?: boolean;
  }

  // Asset bulk operations
  export interface AssetBulkOperation {
    asset_ids: number[];
    operation: 'delete' | 'status_change' | 'assign' | 'export';
    data?: any;
  }

  // Advanced filtering for server-side
  export interface AssetAdvancedFilters {
    // Basic filters
    asset_type_id?: number;
    status_code?: string;
    location_id?: number;
    assigned_to_employee?: number;
    
    // Date-based filters
    purchase_date_from?: string;
    purchase_date_to?: string;
    warranty_expiring_from?: string;
    warranty_expiring_to?: string;
    contract_expiring_from?: string;
    contract_expiring_to?: string;
    
    // Text search
    search?: string;
    search_fields?: ('asset_tag' | 'serial_number' | 'model' | 'vendor' | 'notes')[];
    
    // Boolean filters
    is_under_contract?: boolean;
    is_active?: boolean;
    has_warranty?: boolean;
    has_contract?: boolean;
    
    // Assignment filters
    is_assigned?: boolean;
    assignment_date_from?: string;
    assignment_date_to?: string;
  }

  // Enhanced sorting options
  export interface AssetSortOptions {
    field: 'created_at' | 'updated_at' | 'asset_tag' | 'purchase_date' | 'warranty_end_date' | 'contract_expiry_date' | 'assigned_at' | 'model' | 'vendor' | 'location';
    order: 'asc' | 'desc';
  }

  // Server-side response with enhanced metadata
  export interface PaginatedAssetResponse {
    items: Asset[];
    total_count: number;
    page: number;
    size: number;
    has_next: boolean;
    has_previous: boolean;
    filters_applied: AssetListParams;
    sort_applied: AssetSortOptions;
    statistics: AssetStatistics;
  }

  // Asset statistics with more details
  export interface AssetStatistics {
    total_assets: number;
    active_assets: number;
    in_maintenance: number;
    assigned_assets: number;
    available_assets: number;
    retiring_soon: number;
    warranty_expiring_soon: number;
    contract_expiring_soon: number;
    decommissioning: number;
    retired: number;
    by_status: Record<string, number>;
    by_type: Record<string, number>;
    by_location: Record<string, number>;
    by_assignment: {
      assigned: number;
      unassigned: number;
      overdue_returns: number;
    };
    by_warranty: {
      active: number;
      expiring_soon: number;
      expired: number;
    };
    by_contract: {
      under_contract: number;
      expiring_soon: number;
      expired: number;
    };
  }

  // Feedback interfaces
  export interface FeedbackType {
    FeedbackTypeCode: string;
    FeedbackTypeName: string;
    IsActive: boolean;
    CreatedAt: string;
  }

  export interface EmployeeFeedback {
    FeedbackID: number;
    FeedbackAt: string;
    FeedbackTypeCode: string;
    Category?: string;
    Subject?: string;
    FeedbackText: string;
    TargetManagerID?: number;
    TargetDepartmentID?: number;
    FeedbackHash?: string;
    IsRead: boolean;
    ReadByID?: number;
    ReadAt?: string;
    // Relationships
    feedback_type?: FeedbackType;
    target_manager?: EmployeeInfo;
    target_department?: Department;
    read_by?: EmployeeInfo;
  }

  export interface EmployeeFeedbackCreate {
    FeedbackTypeCode: string;
    Category?: string;
    Subject?: string;
    FeedbackText: string;
    TargetManagerID?: number;
    TargetDepartmentID?: number;
  }

  export interface EmployeeFeedbackUpdate {
    FeedbackTypeCode?: string;
    Category?: string;
    Subject?: string;
    FeedbackText?: string;
    TargetManagerID?: number;
    TargetDepartmentID?: number;
  }

  export interface FeedbackFilterParams {
    feedback_type_code?: string;
    target_manager_id?: number;
    target_department_id?: number;
    is_read?: boolean;
    skip?: number;
    limit?: number;
  }

  export interface Department {
    DepartmentID: number;
    DepartmentName: string;
    DepartmentCode: string;
    ParentDepartmentID?: number;
    LocationID: number;
    IsActive: boolean;
    CreatedAt: string;
    UpdatedAt: string;
  }

  // Women-specific feedback categories
  export const WOMEN_FEEDBACK_CATEGORIES = [
    'Safe Workplace',
    'Equal Employment',
    'Maternity Benefits',
    'Work-Life Balance',
    'Career Development',
    'Harassment Prevention',
    'Gender Equality',
    'Health & Wellness',
    'Other'
  ] as const;

  export type WomenFeedbackCategory = typeof WOMEN_FEEDBACK_CATEGORIES[number];

  // General feedback categories
  export const GENERAL_FEEDBACK_CATEGORIES = [
    'Work Environment',
    'Team Collaboration',
    'Management',
    'Compensation',
    'Benefits',
    'Training',
    'Technology',
    'Processes',
    'Other'
  ] as const;

  export type GeneralFeedbackCategory = typeof GENERAL_FEEDBACK_CATEGORIES[number];

  // Feedback target selection
  export interface FeedbackTarget {
    EmployeeID: number;
    EmployeeName: string;
    DesignationName: string;
    DepartmentName: string;
    isManager: boolean;
    isHR: boolean;
  }

// Employee-related interfaces
export interface Employee {
  EmployeeID: number;
  EmployeeCode: string;
  UserID: string;
  CompanyEmail: string;
  FirstName: string;
  MiddleName?: string;
  LastName: string;
  DateOfBirth?: string;
  GenderCode: string;
  MaritalStatus?: string;
  PersonalEmail?: string;
  PersonalPhone?: string;
  WorkPhone?: string;
  
  // Address
  Address1?: string;
  Address2?: string;
  City?: string;
  State?: string;
  Country?: string;
  PostalCode?: string;
  
  // Work details
  TeamID: number;
  LocationID: number;
  ManagerID?: number;
  DesignationID: number;
  EmploymentTypeCode: string;
  WorkModeCode: string;
  HireDate: string;
  TerminationDate?: string;
  IsActive: boolean;
  CreatedAt: string;
  UpdatedAt: string;
  
  // Related data
  gender?: Gender;
  employment_type?: EmploymentType;
  work_mode?: WorkMode;
  designation?: Designation;
  team?: Team;
  location?: Location;
  manager?: Employee;
  subordinates?: Employee[];
  emergency_contacts?: EmergencyContact[];
}

export interface Gender {
  GenderCode: string;
  GenderName: string;
  IsActive: boolean;
  CreatedAt: string;
}

export interface EmploymentType {
  EmploymentTypeCode: string;
  EmploymentTypeName: string;
  IsActive: boolean;
  CreatedAt: string;
}

export interface WorkMode {
  WorkModeCode: string;
  WorkModeName: string;
  IsActive: boolean;
  CreatedAt: string;
}

export interface Designation {
  DesignationID: number;
  DesignationName: string;
  IsActive: boolean;
  CreatedAt: string;
}

export interface EmergencyContact {
  ContactID: number;
  EmployeeID: number;
  ContactName: string;
  Relationship: string;
  Phone1: string;
  Phone2?: string;
  Email?: string;
  Address?: string;
  IsPrimary: boolean;
  IsActive: boolean;
  CreatedAt: string;
  UpdatedAt: string;
}

// Team-related interfaces
export interface Team {
  TeamID: number;
  TeamName: string;
  TeamCode: string;
  DepartmentID: number;
  TeamLeadEmployeeID?: number;
  IsActive: boolean;
  CreatedAt: string;
  UpdatedAt: string;
  // Relationships
  department?: Department;
  team_lead?: Employee;
}

// Department-related interfaces
export interface Department {
  DepartmentID: number;
  DepartmentName: string;
  DepartmentCode: string;
  ParentDepartmentID?: number;
  LocationID: number;
  IsActive: boolean;
  CreatedAt: string;
  UpdatedAt: string;
  location?: Location;
  parent_department?: Department;
  child_departments?: Department[];
  teams?: Team[];
}

// Location-related interfaces
export interface Location {
  LocationID: number;
  LocationName: string;
  Address1: string;
  Address2?: string;
  City: string;
  State?: string;
  Country: string;
  PostalCode?: string;
  Phone?: string;
  TimeZone: string;
  IsActive: boolean;
  CreatedAt: string;
  UpdatedAt: string;
  departments?: Department[];
}

// API Response interfaces
export interface EmployeeListResponse {
  employees: Employee[];
  total: number;
  page: number;
  size: number;
}

export interface TeamListResponse {
  teams: Team[];
  total: number;
  page: number;
  size: number;
}

export interface ManagerTeamOverviewResponse {
  manager: Employee;
  subordinates: Employee[];
  total_subordinates: number;
  active_subordinates: number;
  team_info: Record<string, any>;
}

export interface EmployeeFeedbackTargetResponse {
  EmployeeID: number;
  EmployeeName: string;
  DesignationName: string;
  DepartmentName: string;
  isManager: boolean;
  isHR: boolean;
}

// Frontend-specific interfaces for enhanced data
export interface EmployeeWithDetails extends Employee {
  // Computed fields for frontend display
  fullName: string;
  displayName: string;
  initials: string;
  locationName?: string;
  departmentName?: string;
  teamName?: string;
  managerName?: string;
  role: 'employee' | 'manager' | 'hr' | 'it' | 'ceo' | 'cto';
  status: 'active' | 'inactive' | 'away' | 'offline';
  skills?: string[];
}

export interface TeamWithMembers extends Team {
  members?: EmployeeWithDetails[];
  department?: Department;
  teamLead?: EmployeeWithDetails;
}

export interface DepartmentWithTeams extends Department {
  teams?: TeamWithMembers[];
  employees?: EmployeeWithDetails[];
}

// Ticket Management Interfaces
export interface TicketStatus {
  TicketStatusCode: string;
  TicketStatusName: string;
  IsActive: boolean;
  CreatedAt: string;
}

export interface TicketPriority {
  PriorityCode: string;
  PriorityName: string;
  SLAHours: number;
  IsActive: boolean;
  CreatedAt: string;
}

export interface TicketCategory {
  CategoryID: number;
  CategoryName: string;
  ParentCategoryID?: number;
  IsActive: boolean;
  CreatedAt: string;
  parent?: TicketCategory;
  children?: TicketCategory[];
}

export interface TicketActivity {
  ActivityID: number;
  TicketID: number;
  ActivityType: string;
  PerformedByID: number;
  OldValue?: string;
  NewValue?: string;
  ActivityDetails?: string;
  PerformedAt: string;
  performed_by?: EmployeeInfo;
}

export interface TicketAttachment {
  AttachmentID: number;
  TicketID: number;
  FileName: string;
  FilePath: string;
  FileSize: number;
  MimeType?: string;
  UploadedByID: number;
  UploadedAt: string;
  uploaded_by?: EmployeeInfo;
}

export interface Ticket {
  TicketID: number;
  TicketNumber: string;
  Subject: string;
  Description: string;
  CategoryID: number;
  PriorityCode: string;
  StatusCode: string;
  OpenedByID: number;
  AssignedToID?: number;
  EscalatedToID?: number;
  AssetID?: number;
  OpenedAt: string;
  AssignedAt?: string;
  EscalatedAt?: string;
  ResolvedAt?: string;
  ClosedAt?: string;
  DueDate?: string;
  CreatedAt: string;
  UpdatedAt: string;
  // Relationships
  category?: TicketCategory;
  priority?: TicketPriority;
  status?: TicketStatus;
  opened_by?: EmployeeInfo;
  assigned_to?: EmployeeInfo;
  escalated_to?: EmployeeInfo;
  asset?: Asset;
  activities?: TicketActivity[];
  attachments?: TicketAttachment[];
}

export interface TicketCreate {
  Subject: string;
  Description: string;
  CategoryID: number;
  PriorityCode: string;
  StatusCode?: string;
  AssignedToID?: number;
  EscalatedToID?: number;
  AssetID?: number;
}

export interface TicketUpdate {
  Subject?: string;
  Description?: string;
  CategoryID?: number;
  PriorityCode?: string;
  StatusCode?: string;
  AssignedToID?: number;
  EscalatedToID?: number;
  AssetID?: number;
}

export interface TicketActivityCreate {
  ActivityType: string;
  OldValue?: string;
  NewValue?: string;
  ActivityDetails?: string;
}

export interface TicketActivityUpdate {
  ActivityDetails?: string;
}

export interface TicketAttachmentCreate {
  FileName: string;
  FilePath: string;
  FileSize: number;
  MimeType?: string;
}

export interface AssetSelectionOption {
  AssetID: number;
  AssetTag: string;
  AssetTypeName: string;
  LocationName: string;
  IsAssignedToUser: boolean;
  AssignmentType: string;
}

export interface AssetSelectionResponse {
  personal_assets: AssetSelectionOption[];
  community_assets: AssetSelectionOption[];
  total_assets: number;
}

export interface TicketListResponse {
  items: Ticket[];
  total_count: number;
  page: number;
  size: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface TicketFilterParams {
  status_code?: string;
  priority_code?: string;
  category_id?: number;
  assigned_to_id?: number;
  opened_by_id?: number;
  asset_id?: number;
  is_active?: boolean;
  skip?: number;
  limit?: number;
}

export interface TicketStatistics {
  total_tickets: number;
  open_tickets: number;
  in_progress_tickets: number;
  resolved_tickets: number;
  closed_tickets: number;
  escalated_tickets: number;
  cancelled_tickets: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  by_category: Record<string, number>;
  by_assignment: Record<string, number>;
}

export interface TicketComment {
  ActivityID: number;
  TicketID: number;
  ActivityType: 'Comment';
  PerformedByID: number;
  ActivityDetails: string;
  PerformedAt: string;
  performed_by?: EmployeeInfo;
}

export interface PendingStatus {
  is_pending_vendor: boolean;
  is_pending_user: boolean;
  last_comment_time?: string;
  last_comment_by?: EmployeeInfo;
  hours_since_last_comment?: number;
}

export interface LeaveApprovalRequest {
  approval_status: string;
  comments?: string;
  is_manager_approval: boolean;
}

export interface ManagerApprovalRequest {
  approval_status: string;
  comments?: string;
  manager_id: number;
}

export interface HRApprovalRequest {
  approval_status: string;
  comments?: string;
  hr_approver_id: number;
}

export interface LeaveConflict {
  has_conflict: boolean;
  conflicting_employees?: Array<{
    employee_id: number;
    employee_name: string;
    leave_dates: string[];
    leave_type: string;
  }>;
  message?: string;
}

export interface Comment {
  comment_id: number;
  entity_type: string;
  entity_id: number;
  commenter_id: number;
  commenter_name: string;
  commenter_role?: string;
  comment_text: string;
  created_at: string;
  updated_at?: string;
  is_edited: boolean;
  is_active: boolean;
}

export interface CommentCreate {
  comment_text: string;
  commenter_role?: string;
}

export interface CommentListResponse {
  comments: Comment[];
  total_count: number;
}

export interface ComprehensiveEmployeeProfile {
  EmployeeID: number
  EmployeeCode: string
  UserID: string
  CompanyEmail: string
  FirstName: string
  MiddleName?: string
  LastName: string
  FullName: string
  DateOfBirth?: string
  GenderCode: string
  GenderName?: string
  MaritalStatus?: string
  PersonalEmail?: string
  PersonalPhone?: string
  WorkPhone?: string
  Address1?: string
  Address2?: string
  City?: string
  State?: string
  Country?: string
  PostalCode?: string
  HireDate: string
  TerminationDate?: string
  EmploymentDuration: number
  IsActive: boolean
  CreatedAt: string
  UpdatedAt: string
  Designation?: {
    DesignationID: number
    DesignationName: string
  }
  EmploymentType?: {
    EmploymentTypeCode: string
    EmploymentTypeName: string
  }
  WorkMode?: {
    WorkModeCode: string
    WorkModeName: string
  }
  Team?: {
    TeamID: number
    TeamName: string
    TeamCode: string
  }
  Department?: {
    DepartmentID: number
    DepartmentName: string
    DepartmentCode: string
  }
  Location?: {
    LocationID: number
    LocationName: string
    City: string
    State: string
    Country: string
  }
  Manager?: {
    EmployeeID: number
    EmployeeCode: string
    Name: string
    Designation: string
  }
  EmergencyContacts: EmergencyContact[]
}

export interface EmergencyContact {
  ContactID: number
  EmployeeID: number
  ContactName: string
  Relationship: string
  Phone1: string
  Phone2?: string
  Email?: string
  Address?: string
  IsPrimary: boolean
  IsActive: boolean
  CreatedAt: string
  UpdatedAt: string
}