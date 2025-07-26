from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Employee Feedback schemas
class EmployeeFeedbackBase(BaseModel):
    EmployeeID: int
    FeedbackTypeID: int
    Subject: str
    Content: str
    Rating: Optional[int] = None
    IsActive: bool = True

class EmployeeFeedbackCreate(EmployeeFeedbackBase):
    pass

class EmployeeFeedbackUpdate(BaseModel):
    EmployeeID: Optional[int] = None
    FeedbackTypeID: Optional[int] = None
    Subject: Optional[str] = None
    Content: Optional[str] = None
    Rating: Optional[int] = None
    IsActive: Optional[bool] = None

class EmployeeFeedbackResponse(EmployeeFeedbackBase):
    FeedbackID: int
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True

# Feedback Type schemas
class FeedbackTypeBase(BaseModel):
    TypeName: str
    TypeCode: str
    Description: Optional[str] = None
    IsActive: bool = True

class FeedbackTypeCreate(FeedbackTypeBase):
    pass

class FeedbackTypeUpdate(BaseModel):
    TypeName: Optional[str] = None
    TypeCode: Optional[str] = None
    Description: Optional[str] = None
    IsActive: Optional[bool] = None

class FeedbackTypeResponse(FeedbackTypeBase):
    FeedbackTypeID: int
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True

# Feedback Read Request schema
class FeedbackReadRequest(BaseModel):
    EmployeeID: Optional[int] = None
    FeedbackTypeID: Optional[int] = None
    StartDate: Optional[datetime] = None
    EndDate: Optional[datetime] = None 