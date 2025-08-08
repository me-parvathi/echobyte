from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Employee Feedback schemas
class EmployeeFeedbackBase(BaseModel):
    FeedbackTypeCode: str
    Category: Optional[str] = None
    Subject: Optional[str] = None
    FeedbackText: str
    TargetManagerID: Optional[int] = None
    TargetDepartmentID: Optional[int] = None

class EmployeeFeedbackCreate(EmployeeFeedbackBase):
    pass

class EmployeeFeedbackUpdate(BaseModel):
    FeedbackTypeCode: Optional[str] = None
    Category: Optional[str] = None
    Subject: Optional[str] = None
    FeedbackText: Optional[str] = None
    TargetManagerID: Optional[int] = None
    TargetDepartmentID: Optional[int] = None

class EmployeeFeedbackResponse(EmployeeFeedbackBase):
    FeedbackID: int
    FeedbackAt: datetime
    FeedbackHash: Optional[str] = None
    IsRead: bool
    ReadByID: Optional[int] = None
    ReadAt: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Feedback Type schemas
class FeedbackTypeBase(BaseModel):
    FeedbackTypeName: str
    IsActive: bool = True

class FeedbackTypeCreate(FeedbackTypeBase):
    FeedbackTypeCode: str

class FeedbackTypeUpdate(BaseModel):
    FeedbackTypeName: Optional[str] = None
    FeedbackTypeCode: Optional[str] = None
    IsActive: Optional[bool] = None

class FeedbackTypeResponse(FeedbackTypeBase):
    FeedbackTypeCode: str
    CreatedAt: datetime
    
    class Config:
        from_attributes = True

# Feedback Read Request schema
class FeedbackReadRequest(BaseModel):
    EmployeeID: Optional[int] = None
    FeedbackTypeID: Optional[int] = None
    StartDate: Optional[datetime] = None
    EndDate: Optional[datetime] = None 