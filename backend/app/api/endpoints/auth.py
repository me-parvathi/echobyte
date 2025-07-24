from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import (
    LoginRequest, 
    LoginResponse, 
    TokenRefreshRequest, 
    TokenRefreshResponse,
    LogoutRequest,
    LogoutResponse
)
from app.schemas.user import User as UserSchema

router = APIRouter()
security = HTTPBearer()

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access token
    """
    auth_service = AuthService(db)
    return auth_service.login(login_data)

@router.post("/logout", response_model=LogoutResponse)
async def logout(
    logout_data: LogoutRequest,
    db: Session = Depends(get_db)
):
    """
    Logout user (invalidate token)
    Note: In a stateless JWT system, tokens are invalidated client-side
    For server-side invalidation, you'd need a token blacklist/redis cache
    """
    # For now, we'll just return a success message
    # In production, you might want to add the token to a blacklist
    return {"message": "Successfully logged out"}

@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    auth_service = AuthService(db)
    return auth_service.refresh_token(refresh_data.refresh_token)

@router.get("/me", response_model=UserSchema)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information
    """
    auth_service = AuthService(db)
    user = auth_service.get_current_active_user(credentials.credentials)
    
    # Convert to schema format
    return UserSchema(
        id=user.UserID,
        email=user.Email,
        username=user.Username,
        is_active=user.IsActive,
        is_superuser=user.IsSuperuser,
        created_at=user.CreatedAt,
        updated_at=user.UpdatedAt
    )

@router.get("/verify")
async def verify_token_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Verify if the current token is valid
    """
    auth_service = AuthService(db)
    user = auth_service.get_current_active_user(credentials.credentials)
    
    return {
        "valid": True,
        "user_id": user.UserID,
        "email": user.Email,
        "username": user.Username,
        "is_superuser": user.IsSuperuser
    } 