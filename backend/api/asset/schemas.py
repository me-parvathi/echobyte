from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

# Asset schemas
class AssetBase(BaseModel):
    AssetName: str
    AssetTypeID: int
    SerialNumber: Optional[str] = None
    Model: Optional[str] = None
    Manufacturer: Optional[str] = None
    PurchaseDate: Optional[date] = None
    PurchaseCost: Optional[float] = None
    StatusID: int
    IsActive: bool = True

class AssetCreate(AssetBase):
    pass

class AssetUpdate(BaseModel):
    AssetName: Optional[str] = None
    AssetTypeID: Optional[int] = None
    SerialNumber: Optional[str] = None
    Model: Optional[str] = None
    Manufacturer: Optional[str] = None
    PurchaseDate: Optional[date] = None
    PurchaseCost: Optional[float] = None
    StatusID: Optional[int] = None
    IsActive: Optional[bool] = None

class AssetResponse(AssetBase):
    AssetID: int
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True

# Asset Type schemas
class AssetTypeBase(BaseModel):
    TypeName: str
    Description: Optional[str] = None
    IsActive: bool = True

class AssetTypeCreate(AssetTypeBase):
    pass

class AssetTypeUpdate(BaseModel):
    TypeName: Optional[str] = None
    Description: Optional[str] = None
    IsActive: Optional[bool] = None

class AssetTypeResponse(AssetTypeBase):
    AssetTypeID: int
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True

# Asset Assignment schemas
class AssetAssignmentBase(BaseModel):
    AssetID: int
    EmployeeID: int
    AssignedDate: date
    ReturnDate: Optional[date] = None
    AssignedBy: int
    IsActive: bool = True

class AssetAssignmentCreate(AssetAssignmentBase):
    pass

class AssetAssignmentUpdate(BaseModel):
    AssetID: Optional[int] = None
    EmployeeID: Optional[int] = None
    AssignedDate: Optional[date] = None
    ReturnDate: Optional[date] = None
    AssignedBy: Optional[int] = None
    IsActive: Optional[bool] = None

class AssetAssignmentResponse(AssetAssignmentBase):
    AssignmentID: int
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True

# Asset Status schemas
class AssetStatusBase(BaseModel):
    StatusName: str
    Description: Optional[str] = None
    IsActive: bool = True

class AssetStatusCreate(AssetStatusBase):
    pass

class AssetStatusUpdate(BaseModel):
    StatusName: Optional[str] = None
    Description: Optional[str] = None
    IsActive: Optional[bool] = None

class AssetStatusResponse(AssetStatusBase):
    StatusID: int
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True 