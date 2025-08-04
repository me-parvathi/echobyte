from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime, date


class ProfilePictureBase(BaseModel):
    FileName: str
    FilePath: str
    FileSize: int
    MimeType: Optional[str] = None


class ProfilePictureResponse(ProfilePictureBase):
    PictureID: int
    EmployeeID: int
    UploadedByID: int
    UploadedAt: datetime
    employee: Optional['EmployeeResponse'] = None
    uploaded_by: Optional['EmployeeResponse'] = None
    
    class Config:
        from_attributes = True


class ProfilePictureUploadResponse(BaseModel):
    success: bool
    blob_name: str
    blob_url: str
    file_size: int
    content_type: str
    metadata: dict
    picture_id: Optional[int] = None  # Database record ID if created
    
    class Config:
        from_attributes = True


class ProfilePictureListResponse(BaseModel):
    pictures: List[ProfilePictureResponse]
    total: int
    employee_id: int


class ProfilePictureDeleteResponse(BaseModel):
    success: bool
    message: str
    blob_name: str
    picture_id: Optional[int] = None


# Forward references for circular imports
from api.employee.schemas import EmployeeResponse

# Update forward references
ProfilePictureResponse.model_rebuild() 