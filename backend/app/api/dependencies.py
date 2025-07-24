from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.auth_service import AuthService
from app.models.user import User
from typing import Optional

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user
    """
    auth_service = AuthService(db)
    return auth_service.get_current_active_user(credentials.credentials)

def get_current_superuser(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated superuser
    """
    auth_service = AuthService(db)
    return auth_service.get_current_superuser(credentials.credentials)

def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get current user if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        auth_service = AuthService(db)
        return auth_service.get_current_active_user(credentials.credentials)
    except HTTPException:
        return None 