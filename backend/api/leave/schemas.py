from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

# Leave Application schemas
class LeaveApplicationBase(BaseModel):
    EmployeeID: int
    LeaveTypeID: int
    StartDate: date
    EndDate: date
    NumberOfDays: Decimal
    Reason: Optional[str] = None
    StatusCode: str
    SubmittedAt: Optional[datetime] = None
    ManagerID: Optional[int] = None
    ManagerApprovalStatus: Optional[str] = None
    ManagerApprovalAt: Optional[datetime] = None
    HRApproverID: Optional[int] = None
    HRApprovalStatus: Optional[str] = None
    HRApprovalAt: Optional[datetime] = None

class LeaveApplicationCreate(BaseModel):
    EmployeeID: int
    LeaveTypeID: int
    StartDate: date
    EndDate: date
    NumberOfDays: Optional[Decimal] = None  # Can be calculated from dates if not provided
    Reason: Optional[str] = None
    StatusCode: str = "Submitted"  # Default status for new applications
    calculation_type: Optional[str] = "business"  # "business" or "calendar"
    exclude_holidays: Optional[bool] = True  # Whether to exclude holidays for business days

class LeaveApplicationUpdate(BaseModel):
    EmployeeID: Optional[int] = None
    LeaveTypeID: Optional[int] = None
    StartDate: Optional[date] = None
    EndDate: Optional[date] = None
    NumberOfDays: Optional[Decimal] = None
    Reason: Optional[str] = None
    StatusCode: Optional[str] = None
    ManagerID: Optional[int] = None
    ManagerApprovalStatus: Optional[str] = None
    HRApproverID: Optional[int] = None
    HRApprovalStatus: Optional[str] = None

class LeaveApplicationResponse(BaseModel):
    LeaveApplicationID: int
    EmployeeID: int
    LeaveTypeID: int
    StartDate: date
    EndDate: date
    NumberOfDays: Decimal
    Reason: Optional[str] = None
    StatusCode: str
    SubmittedAt: Optional[datetime] = None
    ManagerID: Optional[int] = None
    ManagerApprovalStatus: Optional[str] = None
    ManagerApprovalAt: Optional[datetime] = None
    HRApproverID: Optional[int] = None
    HRApprovalStatus: Optional[str] = None
    HRApprovalAt: Optional[datetime] = None
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True

# Leave Type schemas
class LeaveTypeBase(BaseModel):
    LeaveTypeName: str
    LeaveCode: str
    DefaultDaysPerYear: Optional[Decimal] = None
    IsActive: bool = True

class LeaveTypeCreate(LeaveTypeBase):
    pass

class LeaveTypeUpdate(BaseModel):
    LeaveTypeName: Optional[str] = None
    LeaveCode: Optional[str] = None
    DefaultDaysPerYear: Optional[Decimal] = None
    IsActive: Optional[bool] = None

class LeaveTypeResponse(LeaveTypeBase):
    LeaveTypeID: int
    CreatedAt: datetime
    
    class Config:
        from_attributes = True

# Leave Balance schemas
class LeaveBalanceBase(BaseModel):
    EmployeeID: int
    LeaveTypeID: int
    Year: int
    EntitledDays: Decimal
    UsedDays: Decimal = Decimal('0')

class LeaveBalanceCreate(LeaveBalanceBase):
    pass

class LeaveBalanceUpdate(BaseModel):
    EmployeeID: Optional[int] = None
    LeaveTypeID: Optional[int] = None
    Year: Optional[int] = None
    EntitledDays: Optional[Decimal] = None
    UsedDays: Optional[Decimal] = None

class LeaveBalanceResponse(LeaveBalanceBase):
    BalanceID: int
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True

# Approval schemas
class LeaveApprovalRequest(BaseModel):
    approval_status: str
    comments: Optional[str] = None
    is_manager_approval: bool = True

class ManagerApprovalRequest(BaseModel):
    approval_status: str  # "Approved" or "Rejected"
    comments: Optional[str] = None
    manager_id: int = Field(gt=0, description="Must be a valid employee ID greater than 0")

class HRApprovalRequest(BaseModel):
    approval_status: str  # "Approved" or "Rejected"
    comments: Optional[str] = None
    hr_approver_id: int = Field(gt=0, description="Must be a valid employee ID greater than 0") 