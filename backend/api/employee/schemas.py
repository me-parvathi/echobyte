from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import date, datetime

# Base schemas
class GenderBase(BaseModel):
    GenderCode: str
    GenderName: str
    IsActive: bool = True

class EmploymentTypeBase(BaseModel):
    EmploymentTypeCode: str
    EmploymentTypeName: str
    IsActive: bool = True

class WorkModeBase(BaseModel):
    WorkModeCode: str
    WorkModeName: str
    IsActive: bool = True

class DesignationBase(BaseModel):
    DesignationName: str
    IsActive: bool = True

class EmergencyContactBase(BaseModel):
    ContactName: str
    Relationship: str
    Phone1: str
    Phone2: Optional[str] = None
    Email: Optional[str] = None
    Address: Optional[str] = None
    IsPrimary: bool = False
    IsActive: bool = True

class EmployeeBase(BaseModel):
    EmployeeCode: str
    UserID: str
    CompanyEmail: EmailStr
    FirstName: str
    MiddleName: Optional[str] = None
    LastName: str
    DateOfBirth: Optional[date] = None
    GenderCode: str
    MaritalStatus: Optional[str] = None
    PersonalEmail: Optional[EmailStr] = None
    PersonalPhone: Optional[str] = None
    WorkPhone: Optional[str] = None
    
    # Address
    Address1: Optional[str] = None
    Address2: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    Country: Optional[str] = None
    PostalCode: Optional[str] = None
    
    # Work details
    TeamID: int
    LocationID: int
    ManagerID: Optional[int] = None
    DesignationID: int
    EmploymentTypeCode: str
    WorkModeCode: str
    HireDate: date
    TerminationDate: Optional[date] = None
    IsActive: bool = True

    @validator('TerminationDate')
    def validate_termination_date(cls, v, values):
        if v and 'HireDate' in values and v <= values['HireDate']:
            raise ValueError('Termination date must be after hire date')
        return v

# Create schemas
class GenderCreate(GenderBase):
    pass

class EmploymentTypeCreate(EmploymentTypeBase):
    pass

class WorkModeCreate(WorkModeBase):
    pass

class DesignationCreate(DesignationBase):
    pass

class EmergencyContactCreate(EmergencyContactBase):
    pass

class EmployeeCreate(EmployeeBase):
    pass

# Update schemas
class GenderUpdate(BaseModel):
    GenderName: Optional[str] = None
    IsActive: Optional[bool] = None

class EmploymentTypeUpdate(BaseModel):
    EmploymentTypeName: Optional[str] = None
    IsActive: Optional[bool] = None

class WorkModeUpdate(BaseModel):
    WorkModeName: Optional[str] = None
    IsActive: Optional[bool] = None

class DesignationUpdate(BaseModel):
    DesignationName: Optional[str] = None
    IsActive: Optional[bool] = None

class EmergencyContactUpdate(BaseModel):
    ContactName: Optional[str] = None
    Relationship: Optional[str] = None
    Phone1: Optional[str] = None
    Phone2: Optional[str] = None
    Email: Optional[str] = None
    Address: Optional[str] = None
    IsPrimary: Optional[bool] = None
    IsActive: Optional[bool] = None

class EmployeeUpdate(BaseModel):
    EmployeeCode: Optional[str] = None
    UserID: Optional[str] = None
    CompanyEmail: Optional[EmailStr] = None
    FirstName: Optional[str] = None
    MiddleName: Optional[str] = None
    LastName: Optional[str] = None
    DateOfBirth: Optional[date] = None
    GenderCode: Optional[str] = None
    MaritalStatus: Optional[str] = None
    PersonalEmail: Optional[EmailStr] = None
    PersonalPhone: Optional[str] = None
    WorkPhone: Optional[str] = None
    Address1: Optional[str] = None
    Address2: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    Country: Optional[str] = None
    PostalCode: Optional[str] = None
    TeamID: Optional[int] = None
    LocationID: Optional[int] = None
    ManagerID: Optional[int] = None
    DesignationID: Optional[int] = None
    EmploymentTypeCode: Optional[str] = None
    WorkModeCode: Optional[str] = None
    HireDate: Optional[date] = None
    TerminationDate: Optional[date] = None
    IsActive: Optional[bool] = None

# Response schemas
class GenderResponse(GenderBase):
    CreatedAt: datetime
    
    class Config:
        from_attributes = True

class EmploymentTypeResponse(EmploymentTypeBase):
    CreatedAt: datetime
    
    class Config:
        from_attributes = True

class WorkModeResponse(WorkModeBase):
    CreatedAt: datetime
    
    class Config:
        from_attributes = True

class DesignationResponse(DesignationBase):
    DesignationID: int
    CreatedAt: datetime
    
    class Config:
        from_attributes = True

class EmergencyContactResponse(EmergencyContactBase):
    ContactID: int
    EmployeeID: int
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True

class EmployeeResponse(EmployeeBase):
    EmployeeID: int
    CreatedAt: datetime
    UpdatedAt: datetime
    gender: Optional[GenderResponse] = None
    employment_type: Optional[EmploymentTypeResponse] = None
    work_mode: Optional[WorkModeResponse] = None
    designation: Optional[DesignationResponse] = None
    emergency_contacts: List[EmergencyContactResponse] = []
    
    class Config:
        from_attributes = True

# List response schemas
class EmployeeListResponse(BaseModel):
    employees: List[EmployeeResponse]
    total: int
    page: int
    size: int

# Manager-specific schemas
class ManagerTeamOverviewResponse(BaseModel):
    manager: EmployeeResponse
    subordinates: List[EmployeeResponse]
    total_subordinates: int
    active_subordinates: int
    team_info: dict  # Will contain team and department information
    
    class Config:
        from_attributes = True

class ManagerBatchResponse(BaseModel):
    manager: EmployeeResponse
    subordinates: List[EmployeeResponse]
    total_subordinates: int
    active_subordinates: int
    team_info: dict
    last_updated: str
    
    class Config:
        from_attributes = True 