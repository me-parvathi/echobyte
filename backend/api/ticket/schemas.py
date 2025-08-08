from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

# Generic response wrapper for lists
class ListResponse(BaseModel):
    items: List
    total_count: int
    page: int
    size: int
    has_next: bool
    has_previous: bool

# Base schemas
class TicketStatusBase(BaseModel):
    TicketStatusCode: str
    TicketStatusName: str
    IsActive: bool = True

class TicketPriorityBase(BaseModel):
    PriorityCode: str
    PriorityName: str
    SLAHours: int
    IsActive: bool = True

class TicketCategoryBase(BaseModel):
    CategoryName: str
    ParentCategoryID: Optional[int] = None
    IsActive: bool = True

class TicketActivityBase(BaseModel):
    ActivityType: str
    OldValue: Optional[str] = None
    NewValue: Optional[str] = None
    ActivityDetails: Optional[str] = None

class TicketAttachmentBase(BaseModel):
    FileName: str
    FilePath: str
    FileSize: int
    MimeType: Optional[str] = None

class TicketBase(BaseModel):
    Subject: str
    Description: str
    CategoryID: int
    PriorityCode: str
    StatusCode: str = "Open"
    AssignedToID: Optional[int] = None
    EscalatedToID: Optional[int] = None
    AssetID: Optional[int] = None

    @validator('Subject')
    def validate_subject(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Subject must be at least 5 characters long')
        return v.strip()

    @validator('Description')
    def validate_description(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Description must be at least 10 characters long')
        return v.strip()

# Create schemas
class TicketStatusCreate(TicketStatusBase):
    pass

class TicketPriorityCreate(TicketPriorityBase):
    pass

class TicketCategoryCreate(TicketCategoryBase):
    pass

class TicketCreate(TicketBase):
    pass

class TicketActivityCreate(TicketActivityBase):
    pass

class TicketAttachmentCreate(TicketAttachmentBase):
    pass

# Update schemas
class TicketStatusUpdate(BaseModel):
    TicketStatusName: Optional[str] = None
    IsActive: Optional[bool] = None

class TicketPriorityUpdate(BaseModel):
    PriorityName: Optional[str] = None
    SLAHours: Optional[int] = None
    IsActive: Optional[bool] = None

class TicketCategoryUpdate(BaseModel):
    CategoryName: Optional[str] = None
    ParentCategoryID: Optional[int] = None
    IsActive: Optional[bool] = None

class TicketUpdate(BaseModel):
    Subject: Optional[str] = None
    Description: Optional[str] = None
    CategoryID: Optional[int] = None
    PriorityCode: Optional[str] = None
    StatusCode: Optional[str] = None
    AssignedToID: Optional[int] = None
    EscalatedToID: Optional[int] = None
    AssetID: Optional[int] = None

    @validator('Subject')
    def validate_subject(cls, v):
        if v is not None and len(v.strip()) < 5:
            raise ValueError('Subject must be at least 5 characters long')
        return v.strip() if v else v

    @validator('Description')
    def validate_description(cls, v):
        if v is not None and len(v.strip()) < 10:
            raise ValueError('Description must be at least 10 characters long')
        return v.strip() if v else v

class TicketActivityUpdate(BaseModel):
    ActivityDetails: Optional[str] = None

# Response schemas
class TicketStatusResponse(TicketStatusBase):
    CreatedAt: datetime
    
    class Config:
        from_attributes = True

class TicketPriorityResponse(TicketPriorityBase):
    CreatedAt: datetime
    
    class Config:
        from_attributes = True

class TicketCategoryResponse(TicketCategoryBase):
    CategoryID: int
    CreatedAt: datetime
    # Remove self-referencing relationships to prevent recursion
    # parent: Optional['TicketCategoryResponse'] = None
    # children: List['TicketCategoryResponse'] = []
    
    class Config:
        from_attributes = True

class TicketActivityResponse(TicketActivityBase):
    ActivityID: int
    TicketID: int
    PerformedByID: int
    PerformedAt: datetime
    performed_by: Optional['EmployeeResponse'] = None
    
    class Config:
        from_attributes = True

class TicketAttachmentResponse(TicketAttachmentBase):
    AttachmentID: int
    TicketID: int
    UploadedByID: int
    UploadedAt: datetime
    uploaded_by: Optional['EmployeeResponse'] = None
    
    class Config:
        from_attributes = True

class TicketResponse(TicketBase):
    TicketID: int
    TicketNumber: str
    OpenedByID: int
    OpenedAt: datetime
    AssignedAt: Optional[datetime] = None
    EscalatedAt: Optional[datetime] = None
    ResolvedAt: Optional[datetime] = None
    ClosedAt: Optional[datetime] = None
    DueDate: Optional[datetime] = None
    CreatedAt: datetime
    UpdatedAt: datetime
    
    # Relationships
    category: Optional[TicketCategoryResponse] = None
    priority: Optional[TicketPriorityResponse] = None
    status: Optional[TicketStatusResponse] = None
    opened_by: Optional['EmployeeResponse'] = None
    assigned_to: Optional['EmployeeResponse'] = None
    escalated_to: Optional['EmployeeResponse'] = None
    asset: Optional['AssetResponse'] = None
    activities: List[TicketActivityResponse] = []
    attachments: List[TicketAttachmentResponse] = []
    
    class Config:
        from_attributes = True

# List response schemas
class TicketListResponse(ListResponse):
    items: List[TicketResponse]

class TicketCategoryListResponse(BaseModel):
    categories: List[TicketCategoryResponse]
    total: int

# Asset selection schemas
class AssetSelectionOption(BaseModel):
    AssetID: int
    AssetTag: str
    AssetTypeName: str
    LocationName: str
    IsAssignedToUser: bool
    AssignmentType: str  # "Personal", "Community", "Public"

class AssetSelectionResponse(BaseModel):
    personal_assets: List[AssetSelectionOption] = []
    community_assets: List[AssetSelectionOption] = []
    total_assets: int

class TicketCreationContext(BaseModel):
    user_id: int
    user_location_id: Optional[int] = None
    category_id: Optional[int] = None
    available_assets: AssetSelectionResponse

# Forward references for circular imports
from api.employee.schemas import EmployeeResponse
from api.asset.schemas import AssetResponse

# Update forward references
TicketActivityResponse.model_rebuild()
TicketAttachmentResponse.model_rebuild()
TicketResponse.model_rebuild()
TicketCategoryResponse.model_rebuild() 