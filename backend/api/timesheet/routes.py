from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from core.database import get_db
from core.auth import get_current_active_user, require_manager, require_admin
from . import schemas, service

router = APIRouter()

# Timesheet API Endpoints
# 
# Employee-specific endpoints (require authentication):
# - GET /my/timesheets: Get current employee's timesheets
# - GET /my/timesheet/{timesheet_id}: Get specific timesheet (own only)
# - GET /my/week/{week_start_date}: Get current employee's weekly timesheet
# - GET /my/daily/{work_date}: Get current employee's daily entry
# - POST /my/daily: Create/update current employee's daily entry
# - POST /my/weekly: Create current employee's weekly timesheet
# - PUT /my/timesheet/{timesheet_id}: Update own timesheet
# - DELETE /my/timesheet/{timesheet_id}: Delete own timesheet
# - POST /my/timesheet/{timesheet_id}/submit: Submit own timesheet
#
# Manager/Admin endpoints (require manager/admin role):
# - GET /: List all timesheets (filtered by employee_id)
# - GET /{timesheet_id}: Get any timesheet
# - POST /weekly: Create weekly timesheet for any employee
# - POST /daily: Create daily entry for any employee
# - PUT /{timesheet_id}: Update any timesheet
# - DELETE /{timesheet_id}: Delete any timesheet
# - POST /{timesheet_id}/approve: Approve/reject timesheet

# Employee-specific routes (require authentication, restricted to own data)
@router.get("/my/timesheets", response_model=schemas.TimesheetListResponse)
def get_my_timesheets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_code: Optional[str] = None,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current employee's timesheets"""
    # Get employee ID for current user
    from api.employee.models import Employee
    employee = db.query(Employee).filter(
        Employee.UserID == current_user.UserID,
        Employee.IsActive == True
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    return service.TimesheetService.get_timesheets(db, skip, limit, employee.EmployeeID, status_code)

@router.get("/my/timesheet/{timesheet_id}", response_model=schemas.TimesheetWithDetailsResponse)
def get_my_timesheet(
    timesheet_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific timesheet (own only)"""
    # Get employee ID for current user
    from api.employee.models import Employee
    employee = db.query(Employee).filter(
        Employee.UserID == current_user.UserID,
        Employee.IsActive == True
    ).first()
    
    print(f"DEBUG: get_my_timesheet - User: {current_user.Username}, Employee: {employee.EmployeeID if employee else 'None'}")
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    # Get timesheet with details and verify ownership
    timesheet = service.TimesheetService.get_timesheet(db, timesheet_id, include_details=True)
    print(f"DEBUG: get_my_timesheet - Found timesheet: {timesheet.TimesheetID if timesheet else 'None'}")
    print(f"DEBUG: get_my_timesheet - Timesheet employee: {timesheet.EmployeeID if timesheet else 'None'}")
    print(f"DEBUG: get_my_timesheet - Timesheet details count: {len(timesheet.details) if timesheet and timesheet.details else 0}")
    
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    if timesheet.EmployeeID != employee.EmployeeID:
        raise HTTPException(status_code=403, detail="Access denied. You can only view your own timesheets.")
    
    return timesheet

@router.get("/my/week/{week_start_date}", response_model=schemas.TimesheetResponse)
def get_my_weekly_timesheet(
    week_start_date: date,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current employee's weekly timesheet"""
    # Get employee ID for current user
    from api.employee.models import Employee
    employee = db.query(Employee).filter(
        Employee.UserID == current_user.UserID,
        Employee.IsActive == True
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    timesheet = service.TimesheetService.get_employee_weekly_timesheet(db, employee.EmployeeID, week_start_date)
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found for this week")
    return timesheet

@router.get("/my/daily/{work_date}", response_model=schemas.TimesheetDetailResponse)
def get_my_daily_entry(
    work_date: date,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current employee's daily timesheet entry"""
    # Get employee ID for current user
    from api.employee.models import Employee
    employee = db.query(Employee).filter(
        Employee.UserID == current_user.UserID,
        Employee.IsActive == True
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    detail = service.TimesheetService.get_daily_entry(db, employee.EmployeeID, work_date)
    if not detail:
        raise HTTPException(status_code=404, detail="Daily entry not found")
    return detail

@router.post("/my/daily", response_model=schemas.TimesheetDetailResponse, status_code=201)
def create_my_daily_entry(
    daily_data: schemas.DailyEntryCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create or update current employee's daily timesheet entry"""
    # Get employee ID for current user
    from api.employee.models import Employee
    employee = db.query(Employee).filter(
        Employee.UserID == current_user.UserID,
        Employee.IsActive == True
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    # Ensure the daily entry is for the current employee
    if daily_data.EmployeeID != employee.EmployeeID:
        raise HTTPException(status_code=403, detail="Access denied. You can only create entries for yourself.")
    
    return service.TimesheetService.create_or_update_daily_entry(db, daily_data)

@router.post("/my/weekly", response_model=schemas.TimesheetResponse, status_code=201)
def create_my_weekly_timesheet(
    weekly_data: schemas.WeeklyTimesheetCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create current employee's weekly timesheet"""
    # Get employee ID for current user
    from api.employee.models import Employee
    employee = db.query(Employee).filter(
        Employee.UserID == current_user.UserID,
        Employee.IsActive == True
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    # Ensure the weekly timesheet is for the current employee
    if weekly_data.EmployeeID != employee.EmployeeID:
        raise HTTPException(status_code=403, detail="Access denied. You can only create timesheets for yourself.")
    
    return service.TimesheetService.create_weekly_timesheet(db, weekly_data)

@router.put("/my/timesheet/{timesheet_id}", response_model=schemas.TimesheetResponse)
def update_my_timesheet(
    timesheet_id: int,
    timesheet_update: schemas.TimesheetUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current employee's timesheet"""
    # Get employee ID for current user
    from api.employee.models import Employee
    employee = db.query(Employee).filter(
        Employee.UserID == current_user.UserID,
        Employee.IsActive == True
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    # Get timesheet and verify ownership
    timesheet = service.TimesheetService.get_timesheet(db, timesheet_id)
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    if timesheet.EmployeeID != employee.EmployeeID:
        raise HTTPException(status_code=403, detail="Access denied. You can only update your own timesheets.")
    
    return service.TimesheetService.update_timesheet(db, timesheet_id, timesheet_update)

@router.delete("/my/timesheet/{timesheet_id}", status_code=204)
def delete_my_timesheet(
    timesheet_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete current employee's timesheet"""
    # Get employee ID for current user
    from api.employee.models import Employee
    employee = db.query(Employee).filter(
        Employee.UserID == current_user.UserID,
        Employee.IsActive == True
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    # Get timesheet and verify ownership
    timesheet = service.TimesheetService.get_timesheet(db, timesheet_id)
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    if timesheet.EmployeeID != employee.EmployeeID:
        raise HTTPException(status_code=403, detail="Access denied. You can only delete your own timesheets.")
    
    service.TimesheetService.delete_timesheet(db, timesheet_id)
    return None

@router.post("/my/timesheet/{timesheet_id}/submit")
def submit_my_timesheet(
    timesheet_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit current employee's timesheet for approval"""
    # Get employee ID for current user
    from api.employee.models import Employee
    employee = db.query(Employee).filter(
        Employee.UserID == current_user.UserID,
        Employee.IsActive == True
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    # Get timesheet and verify ownership
    timesheet = service.TimesheetService.get_timesheet(db, timesheet_id)
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    if timesheet.EmployeeID != employee.EmployeeID:
        raise HTTPException(status_code=403, detail="Access denied. You can only submit your own timesheets.")
    
    return service.TimesheetService.submit_timesheet(db, timesheet_id)

@router.get("/my/batch", response_model=schemas.TimesheetBatchResponse)
def get_my_timesheet_batch(
    week_start_date: Optional[date] = None,
    include_history: bool = True,
    history_limit: int = Query(10, ge=1, le=50),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current employee's batched timesheet data"""
    # Get employee ID for current user
    from api.employee.models import Employee
    employee = db.query(Employee).filter(
        Employee.UserID == current_user.UserID,
        Employee.IsActive == True
    ).first()
    
    print(f"DEBUG: Current user: {current_user.Username} (UserID: {current_user.UserID})")
    print(f"DEBUG: Found employee: {employee.EmployeeID if employee else 'None'}")
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    print(f"DEBUG: Calling get_employee_timesheet_batch for employee {employee.EmployeeID}")
    
    return service.TimesheetService.get_employee_timesheet_batch(
        db, employee.EmployeeID, week_start_date, include_history, history_limit
    )

# Manager/Admin routes (require manager or admin role)
@router.get("/", response_model=schemas.TimesheetListResponse)
def get_timesheets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employee_id: Optional[int] = None,
    status_code: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)  # Require manager or admin role
):
    """Get list of timesheets with optional filtering (Manager/Admin only)"""
    return service.TimesheetService.get_timesheets(db, skip, limit, employee_id, status_code)

# New endpoint for managers to get timesheets from their subordinates
@router.get("/manager/subordinates", response_model=schemas.TimesheetWithEmployeeListResponse)
def get_manager_subordinates_timesheets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_code: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)  # Require manager or admin role
):
    """Get timesheets from subordinates that need approval (Manager only)"""
    # Get current manager's employee record
    from api.employee.models import Employee
    manager_employee = db.query(Employee).filter(
        Employee.UserID == current_user.UserID,
        Employee.IsActive == True
    ).first()
    
    if not manager_employee:
        raise HTTPException(status_code=404, detail="Manager employee record not found")
    
    return service.TimesheetService.get_manager_subordinates_timesheets(
        db, manager_employee.EmployeeID, skip, limit, status_code
    )

@router.get("/{timesheet_id}", response_model=schemas.TimesheetResponse)
def get_timesheet(
    timesheet_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)  # Require manager or admin role
):
    """Get a specific timesheet by ID (Manager/Admin only)"""
    timesheet = service.TimesheetService.get_timesheet(db, timesheet_id)
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    return timesheet

@router.get("/employee/{employee_id}/week/{week_start_date}", response_model=schemas.TimesheetResponse)
def get_employee_weekly_timesheet(
    employee_id: int, 
    week_start_date: date, 
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)  # Require manager or admin role
):
    """Get timesheet for a specific employee and week (Manager/Admin only)"""
    timesheet = service.TimesheetService.get_employee_weekly_timesheet(db, employee_id, week_start_date)
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found for this week")
    return timesheet

@router.get("/employee/{employee_id}/daily/{work_date}", response_model=schemas.TimesheetDetailResponse)
def get_daily_entry(
    employee_id: int, 
    work_date: date, 
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)  # Require manager or admin role
):
    """Get daily timesheet entry for a specific employee and date (Manager/Admin only)"""
    detail = service.TimesheetService.get_daily_entry(db, employee_id, work_date)
    if not detail:
        raise HTTPException(status_code=404, detail="Daily entry not found")
    return detail

@router.post("/weekly", response_model=schemas.TimesheetResponse, status_code=201)
def create_weekly_timesheet(
    weekly_data: schemas.WeeklyTimesheetCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)  # Require manager or admin role
):
    """Create a complete weekly timesheet with all daily details (Manager/Admin only)"""
    return service.TimesheetService.create_weekly_timesheet(db, weekly_data)

@router.post("/daily", response_model=schemas.TimesheetDetailResponse, status_code=201)
def create_daily_entry(
    daily_data: schemas.DailyEntryCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)  # Require manager or admin role
):
    """Create or update a daily timesheet entry (Manager/Admin only)"""
    return service.TimesheetService.create_or_update_daily_entry(db, daily_data)

@router.put("/{timesheet_id}", response_model=schemas.TimesheetResponse)
def update_timesheet(
    timesheet_id: int, 
    timesheet_update: schemas.TimesheetUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)  # Require manager or admin role
):
    """Update an existing timesheet (Manager/Admin only)"""
    return service.TimesheetService.update_timesheet(db, timesheet_id, timesheet_update)

@router.delete("/{timesheet_id}", status_code=204)
def delete_timesheet(
    timesheet_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)  # Require manager or admin role
):
    """Delete a timesheet (Manager/Admin only)"""
    service.TimesheetService.delete_timesheet(db, timesheet_id)
    return None

# Timesheet Detail routes (Manager/Admin only)
@router.get("/{timesheet_id}/details", response_model=schemas.TimesheetDetailListResponse)
def get_timesheet_details(
    timesheet_id: int, 
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)  # Require manager or admin role
):
    """Get all details for a specific timesheet (Manager/Admin only)"""
    return service.TimesheetService.get_timesheet_details(db, timesheet_id, skip, limit)

@router.get("/details/{detail_id}", response_model=schemas.TimesheetDetailResponse)
def get_timesheet_detail(
    detail_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)  # Require manager or admin role
):
    """Get a specific timesheet detail by ID (Manager/Admin only)"""
    detail = service.TimesheetService.get_timesheet_detail(db, detail_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Timesheet detail not found")
    return detail

@router.put("/details/{detail_id}", response_model=schemas.TimesheetDetailResponse)
def update_timesheet_detail(
    detail_id: int, 
    detail_update: schemas.TimesheetDetailUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)  # Require manager or admin role
):
    """Update an existing timesheet detail (Manager/Admin only)"""
    return service.TimesheetService.update_timesheet_detail(db, detail_id, detail_update)

@router.delete("/details/{detail_id}", status_code=204)
def delete_timesheet_detail(
    detail_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)  # Require manager or admin role
):
    """Delete a timesheet detail (Manager/Admin only)"""
    service.TimesheetService.delete_timesheet_detail(db, detail_id)
    return None

# Approval routes (Manager/Admin only)
@router.post("/{timesheet_id}/approve")
def approve_timesheet(
    timesheet_id: int,
    approval: schemas.TimesheetApprovalRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)  # Require manager or admin role
):
    """Approve or reject a timesheet (Manager/Admin only)"""
    return service.TimesheetService.approve_timesheet(db, timesheet_id, approval)

# Batched data endpoint (Manager/Admin only)
@router.get("/employee/{employee_id}/batch", response_model=schemas.TimesheetBatchResponse)
def get_employee_timesheet_batch(
    employee_id: int,
    week_start_date: Optional[date] = None,
    include_history: bool = True,
    history_limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)  # Require manager or admin role
):
    """Get batched timesheet data for any employee (Manager/Admin only)"""
    return service.TimesheetService.get_employee_timesheet_batch(
        db, employee_id, week_start_date, include_history, history_limit
    ) 