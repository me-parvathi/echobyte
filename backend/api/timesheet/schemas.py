from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

# Timesheet schemas
class TimesheetBase(BaseModel):
    EmployeeID: int
    WeekStartDate: date
    WeekEndDate: date
    TotalHours: float
    StatusID: int
    IsActive: bool = True

class TimesheetCreate(TimesheetBase):
    pass

class TimesheetUpdate(BaseModel):
    EmployeeID: Optional[int] = None
    WeekStartDate: Optional[date] = None
    WeekEndDate: Optional[date] = None
    TotalHours: Optional[float] = None
    StatusID: Optional[int] = None
    IsActive: Optional[bool] = None

class TimesheetResponse(TimesheetBase):
    TimesheetID: int
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True

# Timesheet Detail schemas
class TimesheetDetailBase(BaseModel):
    TimesheetID: int
    ProjectID: Optional[int] = None
    TaskDescription: str
    Date: date
    Hours: float
    IsActive: bool = True

class TimesheetDetailCreate(TimesheetDetailBase):
    pass

class TimesheetDetailUpdate(BaseModel):
    TimesheetID: Optional[int] = None
    ProjectID: Optional[int] = None
    TaskDescription: Optional[str] = None
    Date: Optional[date] = None
    Hours: Optional[float] = None
    IsActive: Optional[bool] = None

class TimesheetDetailResponse(TimesheetDetailBase):
    TimesheetDetailID: int
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True

# Approval schemas
class TimesheetApprovalRequest(BaseModel):
    Approved: bool
    Comments: Optional[str] = None
    ApprovedBy: int 