from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.auth import get_current_active_user, require_manager
from . import schemas, service

router = APIRouter()

# Current employee route - must come first to avoid conflicts
@router.get("/profile/current", response_model=schemas.EmployeeResponse)
def get_current_employee(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current employee profile by authenticated user"""
    employee = service.EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    return employee

@router.get("/profile/current/comprehensive")
def get_current_employee_comprehensive(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive current employee profile with all relationships for profile page"""
    profile_data = service.EmployeeService.get_comprehensive_employee_profile(db, current_user.UserID)
    if not profile_data:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    return profile_data

# Feedback targets route - must come before parameterized routes
@router.get("/feedback-targets", response_model=List[schemas.EmployeeFeedbackTargetResponse])
def get_feedback_targets(db: Session = Depends(get_db)):
    """Get list of employees who can receive feedback (managers and HR)"""
    return service.LookupService.get_feedback_targets(db)

# Current user's manager route
@router.get("/profile/current/manager", response_model=Optional[schemas.EmployeeFeedbackTargetResponse])
def get_current_user_manager(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's manager information"""
    return service.EmployeeService.get_current_user_manager(db, current_user.UserID)

# Manager-specific routes (require manager role)
@router.get("/manager/subordinates", response_model=List[schemas.EmployeeResponse])
def get_manager_subordinates(
    current_user = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Get all subordinates for the current manager"""
    employee = service.EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    subordinates = service.EmployeeService.get_subordinates(db, employee.EmployeeID)
    return subordinates

@router.get("/manager/batch", response_model=schemas.ManagerBatchResponse)
def get_manager_batch_data(
    current_user = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Get manager data and subordinates in a single request for better performance"""
    employee = service.EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    return service.EmployeeService.get_manager_batch_data(db, employee.EmployeeID)

@router.get("/manager/subordinates/{employee_id}", response_model=schemas.EmployeeResponse)
def get_manager_subordinate(
    employee_id: int,
    current_user = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Get a specific subordinate for the current manager"""
    manager_employee = service.EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not manager_employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    # Verify the employee is actually a subordinate of the current manager
    subordinate = service.EmployeeService.get_employee(db, employee_id)
    if not subordinate:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if subordinate.ManagerID != manager_employee.EmployeeID:
        raise HTTPException(status_code=403, detail="Access denied. Employee is not your subordinate")
    
    return subordinate

@router.get("/manager/team-overview", response_model=schemas.ManagerTeamOverviewResponse)
def get_manager_team_overview(
    current_user = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Get team overview for the current manager"""
    manager_employee = service.EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not manager_employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    return service.EmployeeService.get_manager_team_overview(db, manager_employee.EmployeeID)

# Employee routes
@router.get("/", response_model=schemas.EmployeeListResponse)
def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    team_id: Optional[int] = None,
    department_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of employees with optional filtering"""
    employees, total = service.EmployeeService.get_employees_with_count(
        db, skip=skip, limit=limit, 
        is_active=is_active, team_id=team_id, department_id=department_id, search=search
    )
    return schemas.EmployeeListResponse(
        employees=employees, total=total, page=skip//limit + 1, size=limit
    )

@router.post("/", response_model=schemas.EmployeeResponse, status_code=201)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    """Create a new employee"""
    return service.EmployeeService.create_employee(db, employee)

# Lookup routes (must come before parameterized routes)
@router.get("/lookup/genders", response_model=List[schemas.GenderResponse])
def get_genders(db: Session = Depends(get_db)):
    """Get all active genders"""
    return service.LookupService.get_genders(db)

@router.get("/lookup/employment-types", response_model=List[schemas.EmploymentTypeResponse])
def get_employment_types(db: Session = Depends(get_db)):
    """Get all active employment types"""
    return service.LookupService.get_employment_types(db)

@router.get("/lookup/work-modes", response_model=List[schemas.WorkModeResponse])
def get_work_modes(db: Session = Depends(get_db)):
    """Get all active work modes"""
    return service.LookupService.get_work_modes(db)

@router.get("/lookup/designations", response_model=List[schemas.DesignationResponse])
def get_designations(db: Session = Depends(get_db)):
    """Get all active designations"""
    return service.LookupService.get_designations(db)

# Parameterized routes (must come after specific routes)
@router.get("/{employee_id}", response_model=schemas.EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """Get a specific employee by ID"""
    employee = service.EmployeeService.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.put("/{employee_id}", response_model=schemas.EmployeeResponse)
def update_employee(
    employee_id: int, 
    employee_update: schemas.EmployeeUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing employee"""
    return service.EmployeeService.update_employee(db, employee_id, employee_update)

@router.delete("/{employee_id}", status_code=204)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """Soft delete an employee (set IsActive to False)"""
    service.EmployeeService.delete_employee(db, employee_id)
    return None

@router.get("/{employee_id}/hierarchy", response_model=List[schemas.EmployeeResponse])
def get_employee_hierarchy(employee_id: int, db: Session = Depends(get_db)):
    """Get employee hierarchy (manager chain)"""
    hierarchy = service.EmployeeService.get_employee_hierarchy(db, employee_id)
    return hierarchy

@router.get("/{employee_id}/subordinates", response_model=List[schemas.EmployeeResponse])
def get_subordinates(employee_id: int, db: Session = Depends(get_db)):
    """Get all direct subordinates of an employee"""
    subordinates = service.EmployeeService.get_subordinates(db, employee_id)
    return subordinates

# Emergency contact routes
@router.get("/{employee_id}/emergency-contacts", response_model=List[schemas.EmergencyContactResponse])
def get_emergency_contacts(employee_id: int, db: Session = Depends(get_db)):
    """Get emergency contacts for an employee"""
    contacts = service.EmergencyContactService.get_emergency_contacts(db, employee_id)
    return contacts

@router.post("/{employee_id}/emergency-contacts", response_model=schemas.EmergencyContactResponse, status_code=201)
def create_emergency_contact(
    employee_id: int, 
    contact: schemas.EmergencyContactCreate, 
    db: Session = Depends(get_db)
):
    """Create an emergency contact for an employee"""
    return service.EmergencyContactService.create_emergency_contact(db, employee_id, contact)

@router.put("/emergency-contacts/{contact_id}", response_model=schemas.EmergencyContactResponse)
def update_emergency_contact(
    contact_id: int, 
    contact_update: schemas.EmergencyContactUpdate, 
    db: Session = Depends(get_db)
):
    """Update an emergency contact"""
    return service.EmergencyContactService.update_emergency_contact(db, contact_id, contact_update)

@router.delete("/emergency-contacts/{contact_id}", status_code=204)
def delete_emergency_contact(contact_id: int, db: Session = Depends(get_db)):
    """Delete an emergency contact"""
    service.EmergencyContactService.delete_emergency_contact(db, contact_id)
    return None 