from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
import re

# User schemas
class UserBase(BaseModel):
    Username: str
    Email: str
    IsActive: bool = True

class UserCreate(UserBase):
    Password: str

class UserUpdate(BaseModel):
    Username: Optional[str] = None
    Email: Optional[str] = None
    Password: Optional[str] = None
    IsActive: Optional[bool] = None

class UserResponse(UserBase):
    UserID: str
    PasswordChangedAt: datetime
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True

# Authentication schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Password change schema
class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validate password strength requirements"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        return v

# Role schemas
class RoleBase(BaseModel):
    RoleName: str
    Description: Optional[str] = None
    IsActive: bool = True

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    RoleName: Optional[str] = None
    Description: Optional[str] = None
    IsActive: Optional[bool] = None

class RoleResponse(RoleBase):
    RoleID: int
    CreatedAt: datetime
    
    class Config:
        from_attributes = True

# Employee Role schemas
class EmployeeRoleBase(BaseModel):
    EmployeeID: int
    RoleID: int
    AssignedAt: datetime
    IsActive: bool = True

class EmployeeRoleCreate(BaseModel):
    EmployeeID: int
    RoleID: int
    AssignedByID: Optional[int] = None

class EmployeeRoleUpdate(BaseModel):
    EmployeeID: Optional[int] = None
    RoleID: Optional[int] = None
    IsActive: Optional[bool] = None

class EmployeeRoleResponse(BaseModel):
    AssignmentID: int
    EmployeeID: int
    RoleID: int
    AssignedAt: datetime
    AssignedByID: Optional[int] = None
    IsActive: bool
    
    class Config:
        from_attributes = True

# Enhanced Employee Role Response with Role Details
class EmployeeRoleWithDetailsResponse(BaseModel):
    AssignmentID: int
    EmployeeID: int
    RoleID: int
    RoleName: str
    RoleDescription: Optional[str] = None
    AssignedDate: datetime
    IsActive: bool
    CreatedAt: datetime
    UpdatedAt: datetime
    
    class Config:
        from_attributes = True 