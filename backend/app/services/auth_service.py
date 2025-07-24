from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.core.security import verify_password, create_access_token, verify_token
from app.core.config import settings
from app.schemas.auth import LoginRequest, TokenData

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password"""
        # Get user by email
        user = self.db.query(User).filter(User.Email == email).first()
        
        if not user:
            return None
        
        # Check if user is active
        if not user.IsActive:
            return None
        
        # Verify password
        if not verify_password(password, user.HashedPassword):
            return None
        
        return user

    def login(self, login_data: LoginRequest) -> Dict[str, Any]:
        """Handle user login and return access token"""
        # Authenticate user
        user = self.authenticate_user(login_data.email, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update last login time
        user.LastLoginAt = datetime.utcnow()
        self.db.commit()
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user.UserID,
                "email": user.Email,
                "username": user.Username,
                "is_superuser": user.IsSuperuser
            },
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
            "user_id": user.UserID,
            "username": user.Username,
            "email": user.Email,
            "is_superuser": user.IsSuperuser
        }

    def get_current_user(self, token: str) -> User:
        """Get current user from token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        # Verify token
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Get user from database
        user = self.db.query(User).filter(User.UserID == user_id).first()
        if user is None:
            raise credentials_exception
        
        # Check if user is still active
        if not user.IsActive:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated"
            )
        
        return user

    def get_current_active_user(self, token: str) -> User:
        """Get current active user from token"""
        user = self.get_current_user(token)
        if not user.IsActive:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return user

    def get_current_superuser(self, token: str) -> User:
        """Get current superuser from token"""
        user = self.get_current_user(token)
        if not user.IsSuperuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return user

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        # For now, we'll use the same token for both access and refresh
        # In a production system, you'd want separate refresh tokens
        payload = verify_token(refresh_token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user to ensure they still exist and are active
        user = self.db.query(User).filter(User.UserID == user_id).first()
        if not user or not user.IsActive:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user.UserID,
                "email": user.Email,
                "username": user.Username,
                "is_superuser": user.IsSuperuser
            },
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        } 