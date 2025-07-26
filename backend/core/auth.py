"""
Authentication and authorization utilities.
This module provides JWT token validation, user authentication, and security dependencies.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import os
from typing import Optional

from core.database import get_db
from api.auth import models, schemas

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security scheme
oauth2_scheme = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
) -> models.User:
    """Get current authenticated user from JWT token"""
    try:
        # Decode JWT token
        payload = verify_token(credentials.credentials)
        username = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
            
        # Get user from database
        user = db.query(models.User).filter(
            models.User.Username == username,
            models.User.IsActive == True
        ).first()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or inactive"
            )
            
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error"
        )

def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """Get current active user (additional validation)"""
    if not current_user.IsActive:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_role(required_role: str):
    """Dependency to require specific role"""
    def role_checker(
        current_user: models.User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> models.User:
        print(f"🔍 DEBUG: Checking role '{required_role}' for user '{current_user.Username}'")
        
        try:
            # Get employee record for the user
            from api.employee.models import Employee
            employee = db.query(Employee).filter(
                Employee.UserID == current_user.UserID,
                Employee.IsActive == True
            ).first()
            
            if not employee:
                print(f"❌ DEBUG: No employee record found for user")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Employee record not found"
                )
            
            print(f"✅ DEBUG: Found employee: {employee.EmployeeCode}")
            
            # Check if employee has the required role
            from api.auth.models import EmployeeRole, Role
            role = db.query(Role).filter(Role.RoleName == required_role).first()
            
            if not role:
                print(f"❌ DEBUG: Role '{required_role}' not found in system")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Role '{required_role}' not found in system"
                )
            
            print(f"✅ DEBUG: Found role: {role.RoleName} (ID: {role.RoleID})")
            
            # Check if employee has this role assigned
            employee_role = db.query(EmployeeRole).filter(
                EmployeeRole.EmployeeID == employee.EmployeeID,
                EmployeeRole.RoleID == role.RoleID,
                EmployeeRole.IsActive == True
            ).first()
            
            if not employee_role:
                print(f"❌ DEBUG: Employee does not have '{required_role}' role")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required role: {required_role}"
                )
            
            print(f"✅ DEBUG: Employee has '{required_role}' role - access granted")
            return current_user
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            print(f"❌ DEBUG: Unexpected error in require_role: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Authentication error: {str(e)}"
            )
    
    return role_checker

# Role-based dependencies
require_admin = require_role("Admin")
require_manager = require_role("Manager")
require_hr = require_role("HR")

def has_admin_access(user: models.User, db: Session) -> bool:
    """Check if user has admin access (admin role only)"""
    # Get employee record for the user
    from api.employee.models import Employee
    employee = db.query(Employee).filter(
        Employee.UserID == user.UserID,
        Employee.IsActive == True
    ).first()
    
    if not employee:
        return False
    
    # Check if employee has admin role
    from api.auth.models import EmployeeRole, Role
    admin_role = db.query(Role).filter(Role.RoleName == "Admin").first()
    
    if not admin_role:
        return False
    
    # Check if employee has admin role assigned
    employee_role = db.query(EmployeeRole).filter(
        EmployeeRole.EmployeeID == employee.EmployeeID,
        EmployeeRole.RoleID == admin_role.RoleID,
        EmployeeRole.IsActive == True
    ).first()
    
    return employee_role is not None 