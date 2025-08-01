from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.auth import get_current_user, get_current_active_user, require_admin, require_hr
from . import schemas, service, models

router = APIRouter()

# Authentication routes
@router.post("/login", response_model=schemas.LoginResponse)
def login(login_request: schemas.LoginRequest, db: Session = Depends(get_db)):
    """User login"""
    return service.AuthService.login(db, login_request)

@router.post("/logout")
def logout(current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """User logout"""
    return service.AuthService.logout(db)

@router.get("/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user: models.User = Depends(get_current_active_user)):
    """Get current user information"""
    return service.AuthService.get_current_user(current_user)

@router.post("/refresh", response_model=schemas.TokenResponse)
def refresh_token(refresh_request: schemas.RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token"""
    return service.AuthService.refresh_token(db, refresh_request)

# User routes
@router.get("/users", response_model=List[schemas.UserResponse])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Get list of users with optional filtering (Admin only)"""
    print(f"🚀 DEBUG: get_users endpoint called by user: {current_user.Username}")
    print(f"🚀 DEBUG: User IsActive: {current_user.IsActive}")
    return service.UserService.get_users(db, skip, limit, is_active)

@router.get("/test-admin")
def test_admin_endpoint(current_user: models.User = Depends(require_admin)):
    """Test admin endpoint"""
    print(f"🧪 DEBUG: test_admin_endpoint called by user: {current_user.Username}")
    return {"message": "Admin access granted", "user": current_user.Username}

@router.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    user = service.UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", response_model=schemas.UserResponse, status_code=201)
def create_user(
    user: schemas.UserCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Create a new user (Admin only)"""
    return service.UserService.create_user(db, user)

@router.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: str, 
    user_update: schemas.UserUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing user"""
    return service.UserService.update_user(db, user_id, user_update)

@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    """Delete a user"""
    service.UserService.delete_user(db, user_id)
    return None

@router.post("/users/{user_id}/change-password")
def change_password(
    user_id: str,
    password_change: schemas.PasswordChangeRequest,
    db: Session = Depends(get_db)
):
    """Change user password"""
    return service.UserService.change_password(db, user_id, password_change)

# Role routes
@router.get("/roles", response_model=List[schemas.RoleResponse])
def get_roles(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get list of roles (authenticated users only)"""
    return service.RoleService.get_roles(db, is_active)

@router.get("/roles/{role_id}", response_model=schemas.RoleResponse)
def get_role(role_id: int, db: Session = Depends(get_db)):
    """Get a specific role by ID"""
    role = service.RoleService.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.post("/roles", response_model=schemas.RoleResponse, status_code=201)
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    """Create a new role"""
    return service.RoleService.create_role(db, role)

@router.put("/roles/{role_id}", response_model=schemas.RoleResponse)
def update_role(
    role_id: int, 
    role_update: schemas.RoleUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing role"""
    return service.RoleService.update_role(db, role_id, role_update)

@router.delete("/roles/{role_id}", status_code=204)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    """Delete a role"""
    service.RoleService.delete_role(db, role_id)
    return None

# Employee Role assignment routes
@router.get("/employee-roles", response_model=List[schemas.EmployeeRoleResponse])
def get_employee_roles(
    employee_id: Optional[int] = None,
    role_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get employee role assignments with optional filtering (authenticated users only)"""
    return service.EmployeeRoleService.get_employee_roles(db, employee_id, role_id, is_active)

@router.get("/employee-roles/current", response_model=List[schemas.EmployeeRoleWithDetailsResponse])
def get_current_user_roles(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get current user's role assignments with details"""
    print(f"🔍 DEBUG: get_current_user_roles called by user: {current_user.Username}")
    
    # Get employee record for the current user
    from api.employee.models import Employee
    employee = db.query(Employee).filter(
        Employee.UserID == current_user.UserID,
        Employee.IsActive == True
    ).first()
    
    if not employee:
        print(f"❌ DEBUG: No employee record found for user {current_user.Username}")
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    print(f"✅ DEBUG: Found employee: {employee.EmployeeCode} ({employee.FirstName} {employee.LastName})")
    
    # Get roles for the employee
    roles = service.EmployeeRoleService.get_employee_roles_with_details(db, employee.EmployeeID)
    print(f"📋 DEBUG: Found {len(roles)} roles for employee {employee.EmployeeCode}:")
    for role in roles:
        print(f"   - {role.RoleName} (ID: {role.RoleID})")
    
    return roles

@router.get("/employee-roles-with-details", response_model=List[schemas.EmployeeRoleWithDetailsResponse])
def get_employee_roles_with_details(
    employee_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get employee role assignments with role details (authenticated users only)"""
    return service.EmployeeRoleService.get_employee_roles_with_details(db, employee_id, is_active)

@router.get("/employee-roles/{assignment_id}", response_model=schemas.EmployeeRoleResponse)
def get_employee_role(assignment_id: int, db: Session = Depends(get_db)):
    """Get a specific employee role assignment by ID"""
    assignment = service.EmployeeRoleService.get_employee_role(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Employee role assignment not found")
    return assignment

@router.post("/employee-roles", response_model=schemas.EmployeeRoleResponse, status_code=201)
def create_employee_role(assignment: schemas.EmployeeRoleCreate, db: Session = Depends(get_db)):
    """Create a new employee role assignment"""
    return service.EmployeeRoleService.create_employee_role(db, assignment)

@router.put("/employee-roles/{assignment_id}", response_model=schemas.EmployeeRoleResponse)
def update_employee_role(
    assignment_id: int, 
    assignment_update: schemas.EmployeeRoleUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing employee role assignment"""
    return service.EmployeeRoleService.update_employee_role(db, assignment_id, assignment_update)

@router.delete("/employee-roles/{assignment_id}", status_code=204)
def delete_employee_role(assignment_id: int, db: Session = Depends(get_db)):
    """Delete an employee role assignment"""
    service.EmployeeRoleService.delete_employee_role(db, assignment_id)
    return None 