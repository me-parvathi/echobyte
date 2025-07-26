from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas
from fastapi import HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import os
import hashlib
from core.auth import create_access_token, verify_token

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthService:
    """Authentication service for user login/logout and token management"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its SHA-256 hash (matching generate_data.py)"""
        # Hash the plain password using the same method as generate_data.py
        input_hash = hashlib.sha256(plain_password.encode()).hexdigest()
        # Compare the hashes
        return input_hash == hashed_password
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password using SHA-256 (matching generate_data.py)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create a JWT access token"""
        return create_access_token(data, expires_delta)
    
    @staticmethod
    def login(db: Session, login_request: schemas.LoginRequest):
        """User login with JWT token generation"""
        # Find user by username
        user = db.query(models.User).filter(
            models.User.Username == login_request.username,
            models.User.IsActive == True
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Verify password
        if not AuthService.verify_password(login_request.password, user.Password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Generate access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": user.Username, "user_id": user.UserID}, 
            expires_delta=access_token_expires
        )
        
        # Generate refresh token (in production, store this securely)
        refresh_token = AuthService.create_access_token(
            data={"sub": user.Username, "type": "refresh"},
            expires_delta=timedelta(days=7)
        )
        
        return schemas.LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    @staticmethod
    def logout(db: Session):
        """User logout (in a real implementation, you might blacklist the token)"""
        return {"message": "Successfully logged out"}
    
    @staticmethod
    def get_current_user(user: models.User):
        """Get current user information from authenticated user"""
        return schemas.UserResponse(
            UserID=user.UserID,
            Username=user.Username,
            Email=user.Email,
            IsActive=user.IsActive,
            CreatedAt=user.CreatedAt,
            UpdatedAt=user.UpdatedAt
        )
    
    @staticmethod
    def refresh_token(db: Session, refresh_request: schemas.RefreshTokenRequest):
        """Refresh access token"""
        try:
            # Verify refresh token
            payload = verify_token(refresh_request.refresh_token)
            
            # Check if it's a refresh token
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            username = payload.get("sub")
            if not username:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            # Get user
            user = db.query(models.User).filter(
                models.User.Username == username,
                models.User.IsActive == True
            ).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            # Generate new access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = AuthService.create_access_token(
                data={"sub": user.Username, "user_id": user.UserID},
                expires_delta=access_token_expires
            )
            
            return schemas.TokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

class UserService:
    """User management service"""
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> List[schemas.UserResponse]:
        """Get list of users"""
        query = db.query(models.User)
        
        if is_active is not None:
            query = query.filter(models.User.IsActive == is_active)
        
        users = query.order_by(models.User.UserID).offset(skip).limit(limit).all()
        return [schemas.UserResponse.from_orm(user) for user in users]
    
    @staticmethod
    def get_user(db: Session, user_id: str) -> Optional[schemas.UserResponse]:
        """Get user by ID"""
        user = db.query(models.User).filter(models.User.UserID == user_id).first()
        if user:
            return schemas.UserResponse.from_orm(user)
        return None
    
    @staticmethod
    def create_user(db: Session, user: schemas.UserCreate) -> schemas.UserResponse:
        """Create a new user"""
        # Check if username already exists
        existing_user = db.query(models.User).filter(
            models.User.Username == user.Username
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if email already exists
        existing_email = db.query(models.User).filter(
            models.User.Email == user.Email
        ).first()
        
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Hash password
        hashed_password = AuthService.get_password_hash(user.Password)
        
        # Create user
        db_user = models.User(
            Username=user.Username,
            Email=user.Email,
            Password=hashed_password,
            IsActive=user.IsActive
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return schemas.UserResponse.from_orm(db_user)
    
    @staticmethod
    def update_user(db: Session, user_id: str, user_update: schemas.UserUpdate) -> schemas.UserResponse:
        """Update user"""
        # Mock implementation
        return schemas.UserResponse(
            UserID=int(user_id),
            Username=user_update.Username or "user",
            Email=user_update.Email or "user@example.com",
            IsActive=user_update.IsActive if user_update.IsActive is not None else True,
            CreatedAt=datetime.utcnow(),
            UpdatedAt=datetime.utcnow()
        )
    
    @staticmethod
    def delete_user(db: Session, user_id: str):
        """Delete user"""
        return {"message": f"User {user_id} deleted"}
    
    @staticmethod
    def change_password(db: Session, user_id: str, password_change: schemas.PasswordChangeRequest):
        """Change user password"""
        return {"message": "Password changed successfully"}

class RoleService:
    """Role management service"""
    
    @staticmethod
    def get_roles(db: Session, is_active: Optional[bool] = None) -> List[schemas.RoleResponse]:
        """Get list of roles from database"""
        query = db.query(models.Role)
        
        if is_active is not None:
            query = query.filter(models.Role.IsActive == is_active)
        
        roles = query.all()
        return [schemas.RoleResponse.from_orm(role) for role in roles]
    
    @staticmethod
    def get_role(db: Session, role_id: int) -> Optional[schemas.RoleResponse]:
        """Get role by ID"""
        role = db.query(models.Role).filter(models.Role.RoleID == role_id).first()
        if role:
            return schemas.RoleResponse.from_orm(role)
        return None
    
    @staticmethod
    def create_role(db: Session, role: schemas.RoleCreate) -> schemas.RoleResponse:
        """Create a new role"""
        # Check if role name already exists
        existing_role = db.query(models.Role).filter(
            models.Role.RoleName == role.RoleName
        ).first()
        
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name already exists"
            )
        
        # Create new role
        db_role = models.Role(
            RoleName=role.RoleName,
            Description=role.Description,
            IsActive=role.IsActive if role.IsActive is not None else True
        )
        
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        
        return schemas.RoleResponse.from_orm(db_role)
    
    @staticmethod
    def update_role(db: Session, role_id: int, role_update: schemas.RoleUpdate) -> schemas.RoleResponse:
        """Update role"""
        # Get existing role
        role = db.query(models.Role).filter(models.Role.RoleID == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Check if new role name conflicts with existing role
        if role_update.RoleName and role_update.RoleName != role.RoleName:
            existing_role = db.query(models.Role).filter(
                models.Role.RoleName == role_update.RoleName
            ).first()
            
            if existing_role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Role name already exists"
                )
        
        # Update role fields
        if role_update.RoleName is not None:
            role.RoleName = role_update.RoleName
        if role_update.Description is not None:
            role.Description = role_update.Description
        if role_update.IsActive is not None:
            role.IsActive = role_update.IsActive
        
        db.commit()
        db.refresh(role)
        
        return schemas.RoleResponse.from_orm(role)
    
    @staticmethod
    def delete_role(db: Session, role_id: int):
        """Delete role"""
        # Get existing role
        role = db.query(models.Role).filter(models.Role.RoleID == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Check if role is assigned to any employees
        from api.auth.models import EmployeeRole
        employee_roles = db.query(EmployeeRole).filter(
            EmployeeRole.RoleID == role_id,
            EmployeeRole.IsActive == True
        ).first()
        
        if employee_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete role that is assigned to employees"
            )
        
        # Soft delete the role
        role.IsActive = False
        db.commit()
        
        return {"message": f"Role {role_id} deleted"}

class EmployeeRoleService:
    """Employee role assignment service"""
    
    @staticmethod
    def get_employee_roles(db: Session, employee_id: Optional[int] = None, role_id: Optional[int] = None, is_active: Optional[bool] = None) -> List[schemas.EmployeeRoleResponse]:
        """Get employee role assignments"""
        query = db.query(models.EmployeeRole)
        
        if employee_id is not None:
            query = query.filter(models.EmployeeRole.EmployeeID == employee_id)
        if role_id is not None:
            query = query.filter(models.EmployeeRole.RoleID == role_id)
        if is_active is not None:
            query = query.filter(models.EmployeeRole.IsActive == is_active)
        
        assignments = query.all()
        return [
            schemas.EmployeeRoleResponse(
                AssignmentID=assignment.EmployeeRoleID,
                EmployeeID=assignment.EmployeeID,
                RoleID=assignment.RoleID,
                AssignedAt=assignment.AssignedAt,
                AssignedByID=assignment.AssignedByID,
                IsActive=assignment.IsActive
            ) for assignment in assignments
        ]

    @staticmethod
    def get_employee_roles_with_details(db: Session, employee_id: Optional[int] = None, is_active: Optional[bool] = None) -> List[schemas.EmployeeRoleWithDetailsResponse]:
        """Get employee role assignments with role details"""
        query = db.query(models.EmployeeRole, models.Role).join(
            models.Role, models.EmployeeRole.RoleID == models.Role.RoleID
        )
        
        if employee_id is not None:
            query = query.filter(models.EmployeeRole.EmployeeID == employee_id)
        if is_active is not None:
            query = query.filter(models.EmployeeRole.IsActive == is_active)
        
        results = query.all()
        
        role_assignments = []
        for assignment, role in results:
            role_assignments.append(schemas.EmployeeRoleWithDetailsResponse(
                AssignmentID=assignment.EmployeeRoleID,
                EmployeeID=assignment.EmployeeID,
                RoleID=assignment.RoleID,
                RoleName=role.RoleName,
                RoleDescription=role.Description,
                AssignedDate=assignment.AssignedAt,
                IsActive=assignment.IsActive,
                CreatedAt=assignment.AssignedAt,  # Using AssignedAt as CreatedAt
                UpdatedAt=assignment.AssignedAt   # Using AssignedAt as UpdatedAt
            ))
        
        return role_assignments
    
    @staticmethod
    def get_employee_role(db: Session, assignment_id: int) -> Optional[schemas.EmployeeRoleResponse]:
        """Get employee role assignment by ID"""
        assignment = db.query(models.EmployeeRole).filter(
            models.EmployeeRole.EmployeeRoleID == assignment_id
        ).first()
        
        if assignment:
            return schemas.EmployeeRoleResponse(
                AssignmentID=assignment.EmployeeRoleID,
                EmployeeID=assignment.EmployeeID,
                RoleID=assignment.RoleID,
                AssignedAt=assignment.AssignedAt,
                AssignedByID=assignment.AssignedByID,
                IsActive=assignment.IsActive
            )
        return None
    
    @staticmethod
    def create_employee_role(db: Session, assignment: schemas.EmployeeRoleCreate) -> schemas.EmployeeRoleResponse:
        """Create employee role assignment"""
        # Check if employee exists
        from api.employee.models import Employee
        employee = db.query(Employee).filter(
            Employee.EmployeeID == assignment.EmployeeID,
            Employee.IsActive == True
        ).first()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Check if role exists
        role = db.query(models.Role).filter(
            models.Role.RoleID == assignment.RoleID,
            models.Role.IsActive == True
        ).first()
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Check if assignment already exists
        existing_assignment = db.query(models.EmployeeRole).filter(
            models.EmployeeRole.EmployeeID == assignment.EmployeeID,
            models.EmployeeRole.RoleID == assignment.RoleID,
            models.EmployeeRole.IsActive == True
        ).first()
        
        if existing_assignment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee already has this role assigned"
            )
        
        # Create new assignment
        db_assignment = models.EmployeeRole(
            EmployeeID=assignment.EmployeeID,
            RoleID=assignment.RoleID,
            AssignedByID=assignment.AssignedByID  # Use from schema if provided
        )
        
        db.add(db_assignment)
        db.commit()
        db.refresh(db_assignment)
        
        # Convert database model to response schema with proper field mapping
        return schemas.EmployeeRoleResponse(
            AssignmentID=db_assignment.EmployeeRoleID,
            EmployeeID=db_assignment.EmployeeID,
            RoleID=db_assignment.RoleID,
            AssignedAt=db_assignment.AssignedAt,
            AssignedByID=db_assignment.AssignedByID,
            IsActive=db_assignment.IsActive
        )
    
    @staticmethod
    def update_employee_role(db: Session, assignment_id: int, assignment_update: schemas.EmployeeRoleUpdate) -> schemas.EmployeeRoleResponse:
        """Update employee role assignment"""
        # Get existing assignment
        assignment = db.query(models.EmployeeRole).filter(
            models.EmployeeRole.EmployeeRoleID == assignment_id
        ).first()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee role assignment not found"
            )
        
        # Update fields if provided
        if assignment_update.EmployeeID is not None:
            # Check if new employee exists
            from api.employee.models import Employee
            employee = db.query(Employee).filter(
                Employee.EmployeeID == assignment_update.EmployeeID,
                Employee.IsActive == True
            ).first()
            
            if not employee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Employee not found"
                )
            assignment.EmployeeID = assignment_update.EmployeeID
        
        if assignment_update.RoleID is not None:
            # Check if new role exists
            role = db.query(models.Role).filter(
                models.Role.RoleID == assignment_update.RoleID,
                models.Role.IsActive == True
            ).first()
            
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Role not found"
                )
            assignment.RoleID = assignment_update.RoleID
        
        if assignment_update.IsActive is not None:
            assignment.IsActive = assignment_update.IsActive
        
        db.commit()
        db.refresh(assignment)
        
        return schemas.EmployeeRoleResponse(
            AssignmentID=assignment.EmployeeRoleID,
            EmployeeID=assignment.EmployeeID,
            RoleID=assignment.RoleID,
            AssignedAt=assignment.AssignedAt,
            AssignedByID=assignment.AssignedByID,
            IsActive=assignment.IsActive
        )
    
    @staticmethod
    def delete_employee_role(db: Session, assignment_id: int):
        """Delete employee role assignment"""
        # Get existing assignment
        assignment = db.query(models.EmployeeRole).filter(
            models.EmployeeRole.EmployeeRoleID == assignment_id
        ).first()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee role assignment not found"
            )
        
        # Soft delete the assignment
        assignment.IsActive = False
        db.commit()
        
        return {"message": f"Employee role assignment {assignment_id} deleted"} 