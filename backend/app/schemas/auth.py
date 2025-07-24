from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    username: str
    email: str
    is_superuser: bool

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None

class LogoutResponse(BaseModel):
    message: str = "Successfully logged out"

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None
    is_superuser: Optional[bool] = None 