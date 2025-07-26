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

# Create schemas
class LocationCreate(LocationBase):
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

# Response schemas
class LocationResponse(LocationBase):
    LocationID: int
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True

# Alias for backward compatibility
Location = LocationResponse

# List response schemas
class LocationListResponse(BaseModel):
    locations: List[LocationResponse]
    total: int
    page: int
    size: int 