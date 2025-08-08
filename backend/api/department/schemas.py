from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base schemas
class LocationBase(BaseModel):
    LocationName: str
    Address1: str
    Address2: Optional[str] = None
    City: str
    State: Optional[str] = None
    Country: str
    PostalCode: Optional[str] = None
    Phone: Optional[str] = None
    TimeZone: str
    IsActive: bool = True

class DepartmentBase(BaseModel):
    DepartmentName: str
    DepartmentCode: str
    ParentDepartmentID: Optional[int] = None
    LocationID: int
    IsActive: bool = True

# Create schemas
class LocationCreate(LocationBase):
    pass

class DepartmentCreate(DepartmentBase):
    pass

# Update schemas
class LocationUpdate(BaseModel):
    LocationName: Optional[str] = None
    Address1: Optional[str] = None
    Address2: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    Country: Optional[str] = None
    PostalCode: Optional[str] = None
    Phone: Optional[str] = None
    TimeZone: Optional[str] = None
    IsActive: Optional[bool] = None

class DepartmentUpdate(BaseModel):
    DepartmentName: Optional[str] = None
    DepartmentCode: Optional[str] = None
    ParentDepartmentID: Optional[int] = None
    LocationID: Optional[int] = None
    IsActive: Optional[bool] = None

# Response schemas
class LocationResponse(LocationBase):
    LocationID: int
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True

class DepartmentResponse(DepartmentBase):
    DepartmentID: int
    CreatedAt: datetime
    UpdatedAt: datetime
    location: Optional[LocationResponse] = None
    
    class Config:
        from_attributes = True

# Hierarchical schemas for department relationships
class DepartmentHierarchyResponse(DepartmentBase):
    DepartmentID: int
    CreatedAt: datetime
    UpdatedAt: datetime
    location: Optional[LocationResponse] = None
    parent_department: Optional['DepartmentHierarchyResponse'] = None
    child_departments: List['DepartmentHierarchyResponse'] = []
    
    class Config:
        from_attributes = True

# List response schemas
class DepartmentListResponse(BaseModel):
    departments: List[DepartmentResponse]
    total: int
    page: int
    size: int

class LocationListResponse(BaseModel):
    locations: List[LocationResponse]
    total: int
    page: int
    size: int 