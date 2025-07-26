from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from . import schemas, service
from datetime import date
from decimal import Decimal

router = APIRouter()

# Utility endpoint for calculating days
@router.get("/calculate-days")
def calculate_leave_days(
    start_date: date = Query(..., description="Start date of leave period"),
    end_date: date = Query(..., description="End date of leave period"),
    calculation_type: str = Query("business", description="Type of calculation: 'business' or 'calendar'"),
    exclude_holidays: bool = Query(True, description="Whether to exclude holidays (for business days)")
):
    """Calculate the number of days between two dates"""
    try:
        if calculation_type.lower() == "business":
            days = service.calculate_business_days(start_date, end_date, exclude_holidays)
        elif calculation_type.lower() == "calendar":
            days = service.calculate_calendar_days(start_date, end_date)
        else:
            raise HTTPException(status_code=400, detail="calculation_type must be 'business' or 'calendar'")
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "calculation_type": calculation_type,
            "exclude_holidays": exclude_holidays,
            "number_of_days": float(days)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Leave Application routes
@router.get("/applications", response_model=List[schemas.LeaveApplicationResponse])
def get_leave_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employee_id: Optional[int] = None,
    status_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of leave applications with optional filtering"""
    return service.LeaveService.get_leave_applications(db, skip, limit, employee_id, status_code)

@router.get("/applications/{application_id}", response_model=schemas.LeaveApplicationResponse)
def get_leave_application(application_id: int, db: Session = Depends(get_db)):
    """Get a specific leave application by ID"""
    application = service.LeaveService.get_leave_application(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Leave application not found")
    return application

@router.post("/applications", response_model=schemas.LeaveApplicationResponse, status_code=201)
def create_leave_application(application: schemas.LeaveApplicationCreate, db: Session = Depends(get_db)):
    """Create a new leave application"""
    return service.LeaveService.create_leave_application(db, application)

@router.put("/applications/{application_id}", response_model=schemas.LeaveApplicationResponse)
def update_leave_application(
    application_id: int, 
    application_update: schemas.LeaveApplicationUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing leave application"""
    return service.LeaveService.update_leave_application(db, application_id, application_update)

@router.delete("/applications/{application_id}", status_code=204)
def delete_leave_application(application_id: int, db: Session = Depends(get_db)):
    """Delete a leave application"""
    service.LeaveService.delete_leave_application(db, application_id)
    return None

# Leave Type routes
@router.get("/types", response_model=List[schemas.LeaveTypeResponse])
def get_leave_types(db: Session = Depends(get_db)):
    """Get list of leave types"""
    return service.LeaveService.get_leave_types(db)

@router.get("/types/{type_id}", response_model=schemas.LeaveTypeResponse)
def get_leave_type(type_id: int, db: Session = Depends(get_db)):
    """Get a specific leave type by ID"""
    leave_type = service.LeaveService.get_leave_type(db, type_id)
    if not leave_type:
        raise HTTPException(status_code=404, detail="Leave type not found")
    return leave_type

@router.post("/types", response_model=schemas.LeaveTypeResponse, status_code=201)
def create_leave_type(leave_type: schemas.LeaveTypeCreate, db: Session = Depends(get_db)):
    """Create a new leave type"""
    return service.LeaveService.create_leave_type(db, leave_type)

@router.put("/types/{type_id}", response_model=schemas.LeaveTypeResponse)
def update_leave_type(
    type_id: int, 
    leave_type_update: schemas.LeaveTypeUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing leave type"""
    return service.LeaveService.update_leave_type(db, type_id, leave_type_update)

@router.delete("/types/{type_id}", status_code=204)
def delete_leave_type(type_id: int, db: Session = Depends(get_db)):
    """Delete a leave type"""
    service.LeaveService.delete_leave_type(db, type_id)
    return None

# Leave Balance routes
@router.get("/balances", response_model=List[schemas.LeaveBalanceResponse])
def get_leave_balances(
    employee_id: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get leave balances with optional filtering"""
    return service.LeaveService.get_leave_balances(db, employee_id, year)

@router.get("/balances/{balance_id}", response_model=schemas.LeaveBalanceResponse)
def get_leave_balance(balance_id: int, db: Session = Depends(get_db)):
    """Get a specific leave balance by ID"""
    balance = service.LeaveService.get_leave_balance(db, balance_id)
    if not balance:
        raise HTTPException(status_code=404, detail="Leave balance not found")
    return balance

@router.post("/balances", response_model=schemas.LeaveBalanceResponse, status_code=201)
def create_leave_balance(balance: schemas.LeaveBalanceCreate, db: Session = Depends(get_db)):
    """Create a new leave balance"""
    return service.LeaveService.create_leave_balance(db, balance)

@router.put("/balances/{balance_id}", response_model=schemas.LeaveBalanceResponse)
def update_leave_balance(
    balance_id: int, 
    balance_update: schemas.LeaveBalanceUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing leave balance"""
    return service.LeaveService.update_leave_balance(db, balance_id, balance_update)

@router.delete("/balances/{balance_id}", status_code=204)
def delete_leave_balance(balance_id: int, db: Session = Depends(get_db)):
    """Delete a leave balance"""
    service.LeaveService.delete_leave_balance(db, balance_id)
    return None

# Approval routes
@router.post("/applications/{application_id}/approve")
def approve_leave_application(
    application_id: int,
    approval: schemas.LeaveApprovalRequest,
    db: Session = Depends(get_db)
):
    """Approve or reject a leave application"""
    return service.LeaveService.approve_leave_application(db, application_id, approval)

@router.post("/applications/{application_id}/manager-approve")
def manager_approve_leave_application(
    application_id: int,
    approval: schemas.ManagerApprovalRequest,
    db: Session = Depends(get_db)
):
    """Manager approval for leave application"""
    return service.LeaveService.manager_approve_leave_application(db, application_id, approval)

@router.post("/applications/{application_id}/hr-approve")
def hr_approve_leave_application(
    application_id: int,
    approval: schemas.HRApprovalRequest,
    db: Session = Depends(get_db)
):
    """HR approval for leave application (only after manager approval)"""
    return service.LeaveService.hr_approve_leave_application(db, application_id, approval) 