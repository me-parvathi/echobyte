from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base schemas
class TeamBase(BaseModel):
    TeamName: str
    TeamCode: str
    DepartmentID: int
    TeamLeadEmployeeID: Optional[int] = None
    IsActive: bool = True

# Create schemas
class TeamCreate(TeamBase):
    pass

# Update schemas
class TeamUpdate(BaseModel):
    TeamName: Optional[str] = None
    TeamCode: Optional[str] = None
    DepartmentID: Optional[int] = None
    TeamLeadEmployeeID: Optional[int] = None
    IsActive: Optional[bool] = None

# Response schemas
class TeamResponse(TeamBase):
    TeamID: int
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True

# List response schemas
class TeamListResponse(BaseModel):
    teams: List[TeamResponse]
    total: int
    page: int
    size: int 