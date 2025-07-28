from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

# Generic response wrapper for lists
class ListResponse(BaseModel):
    items: List
    total_count: int
    page: int
    size: int
    has_next: bool
    has_previous: bool

# Timesheet schemas
class TimesheetBase(BaseModel):
    EmployeeID: int
    WeekStartDate: date
    WeekEndDate: date
    TotalHours: float = 0.0
    StatusCode: str = "Draft"
    Comments: Optional[str] = None



class TimesheetUpdate(BaseModel):
    EmployeeID: Optional[int] = None
    WeekStartDate: Optional[date] = None
    WeekEndDate: Optional[date] = None
    TotalHours: Optional[float] = None
    StatusCode: Optional[str] = None
    Comments: Optional[str] = None

class TimesheetResponse(TimesheetBase):
    TimesheetID: int
    SubmittedAt: Optional[datetime] = None
    ApprovedByID: Optional[int] = None
    ApprovedAt: Optional[datetime] = None
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True

# Timesheet response with details included
class TimesheetWithDetailsResponse(TimesheetBase):
    TimesheetID: int
    SubmittedAt: Optional[datetime] = None
    ApprovedByID: Optional[int] = None
    ApprovedAt: Optional[datetime] = None
    CreatedAt: datetime
    UpdatedAt: datetime
    details: List["TimesheetDetailResponse"] = []
    
    class Config:
        from_attributes = True

# List response schemas
class TimesheetListResponse(ListResponse):
    items: List[TimesheetResponse]

# Timesheet Detail schemas
class TimesheetDetailBase(BaseModel):
    TimesheetID: int
    WorkDate: date
    ProjectCode: Optional[str] = None
    TaskDescription: Optional[str] = None
    HoursWorked: float
    IsOvertime: bool = False



# Smart detail creation - doesn't require TimesheetID
class TimesheetDetailSmartCreate(BaseModel):
    EmployeeID: int
    WorkDate: date
    ProjectCode: Optional[str] = None
    TaskDescription: Optional[str] = None
    HoursWorked: float
    IsOvertime: bool = False

class TimesheetDetailUpdate(BaseModel):
    TimesheetID: Optional[int] = None
    WorkDate: Optional[date] = None
    ProjectCode: Optional[str] = None
    TaskDescription: Optional[str] = None
    HoursWorked: Optional[float] = None
    IsOvertime: Optional[bool] = None

class TimesheetDetailResponse(TimesheetDetailBase):
    DetailID: int
    CreatedAt: datetime
    
    class Config:
        from_attributes = True

class TimesheetDetailListResponse(ListResponse):
    items: List[TimesheetDetailResponse]

# Approval schemas
class TimesheetApprovalRequest(BaseModel):
    status: str  # "Approved" or "Rejected"
    approved_by_id: int
    comments: Optional[str] = None

# Weekly timesheet creation
class WeeklyTimesheetCreate(BaseModel):
    EmployeeID: int
    WeekStartDate: date
    WeekEndDate: date
    Comments: Optional[str] = None
    details: List[TimesheetDetailSmartCreate] = []

# Daily entry creation
class DailyEntryCreate(BaseModel):
    EmployeeID: int
    WorkDate: date
    ProjectCode: Optional[str] = None
    TaskDescription: Optional[str] = None
    HoursWorked: float
    IsOvertime: bool = False

# NEW: Batched response schema for optimized API calls
class TimesheetBatchResponse(BaseModel):
    current_week: Optional[TimesheetWithDetailsResponse] = None
    timesheet_history: List[TimesheetResponse] = []
    employee_profile: Optional[dict] = None  # Basic employee info
    total_count: int = 0
    week_start_date: Optional[date] = None
    week_end_date: Optional[date] = None 