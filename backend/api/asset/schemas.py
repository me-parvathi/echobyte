from pydantic import BaseModel
from typing import Optional, List, Dict, Generic, TypeVar
from datetime import date, datetime

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper"""
    items: List[T]
    total_count: int
    page: int
    size: int
    has_next: bool
    has_previous: bool

# Asset schemas
class AssetBase(BaseModel):
    AssetTag: str
    AssetTypeID: int
    SerialNumber: Optional[str] = None
    Model: Optional[str] = None
    Vendor: Optional[str] = None
    PurchaseDate: Optional[date] = None
    WarrantyEndDate: Optional[date] = None
    AssetStatusCode: str
    IsActive: bool = True

class AssetCreate(AssetBase):
    pass

class AssetUpdate(BaseModel):
    AssetTag: Optional[str] = None
    AssetTypeID: Optional[int] = None
    SerialNumber: Optional[str] = None
    Model: Optional[str] = None
    Vendor: Optional[str] = None
    PurchaseDate: Optional[date] = None
    WarrantyEndDate: Optional[date] = None
    AssetStatusCode: Optional[str] = None
    IsActive: Optional[bool] = None

class AssetResponse(AssetBase):
    AssetID: int
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True

# Asset Type schemas
class AssetTypeBase(BaseModel):
    AssetTypeName: str
    IsActive: bool = True

class AssetTypeCreate(AssetTypeBase):
    pass

class AssetTypeUpdate(BaseModel):
    AssetTypeName: Optional[str] = None
    IsActive: Optional[bool] = None

class AssetTypeResponse(AssetTypeBase):
    AssetTypeID: int
    CreatedAt: datetime
    
    class Config:
        from_attributes = True

# Asset Assignment schemas
class AssetAssignmentBase(BaseModel):
    AssetID: int
    EmployeeID: int
    DueReturnDate: Optional[date] = None
    ConditionAtAssign: Optional[str] = None
    Notes: Optional[str] = None
    # AssignedByID will be set by the backend from current user
    # AssignedAt will be set by the database default

class AssetAssignmentCreate(AssetAssignmentBase):
    pass

class AssetAssignmentUpdate(BaseModel):
    AssetID: Optional[int] = None
    EmployeeID: Optional[int] = None
    DueReturnDate: Optional[date] = None
    ConditionAtAssign: Optional[str] = None
    Notes: Optional[str] = None

class AssetReturnRequest(BaseModel):
    ConditionAtReturn: Optional[str] = None
    Notes: Optional[str] = None

class AssetAssignmentResponse(AssetAssignmentBase):
    AssignmentID: int
    AssignedAt: datetime
    AssignedByID: int
    ReturnedAt: Optional[datetime] = None
    ConditionAtReturn: Optional[str] = None
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True

# Asset Status schemas
class AssetStatusBase(BaseModel):
    AssetStatusName: str
    IsAssignable: bool
    IsActive: bool = True

class AssetStatusCreate(AssetStatusBase):
    pass

class AssetStatusUpdate(BaseModel):
    AssetStatusName: Optional[str] = None
    IsAssignable: Optional[bool] = None
    IsActive: Optional[bool] = None

class AssetStatusResponse(AssetStatusBase):
    AssetStatusCode: str
    CreatedAt: datetime
    
    class Config:
        from_attributes = True

# Asset Statistics schema
class AssetStatisticsResponse(BaseModel):
    total_assets: int
    active_assets: int
    assigned_assets: int
    available_assets: int
    in_maintenance: int
    decommissioning: int
    retired: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    
    class Config:
        from_attributes = True 