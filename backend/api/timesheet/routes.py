from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from . import schemas, service

router = APIRouter()

# Timesheet routes
@router.get("/", response_model=List[schemas.TimesheetResponse])
def get_timesheets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employee_id: Optional[int] = None,
    status_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of timesheets with optional filtering"""
    return service.TimesheetService.get_timesheets(db, skip, limit, employee_id, status_code)

@router.get("/{timesheet_id}", response_model=schemas.TimesheetResponse)
def get_timesheet(timesheet_id: int, db: Session = Depends(get_db)):
    """Get a specific timesheet by ID"""
    timesheet = service.TimesheetService.get_timesheet(db, timesheet_id)
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    return timesheet

@router.post("/", response_model=schemas.TimesheetResponse, status_code=201)
def create_timesheet(timesheet: schemas.TimesheetCreate, db: Session = Depends(get_db)):
    """Create a new timesheet"""
    return service.TimesheetService.create_timesheet(db, timesheet)

@router.put("/{timesheet_id}", response_model=schemas.TimesheetResponse)
def update_timesheet(
    timesheet_id: int, 
    timesheet_update: schemas.TimesheetUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing timesheet"""
    return service.TimesheetService.update_timesheet(db, timesheet_id, timesheet_update)

@router.delete("/{timesheet_id}", status_code=204)
def delete_timesheet(timesheet_id: int, db: Session = Depends(get_db)):
    """Delete a timesheet"""
    service.TimesheetService.delete_timesheet(db, timesheet_id)
    return None

# Timesheet Detail routes
@router.get("/{timesheet_id}/details", response_model=List[schemas.TimesheetDetailResponse])
def get_timesheet_details(timesheet_id: int, db: Session = Depends(get_db)):
    """Get all details for a specific timesheet"""
    return service.TimesheetService.get_timesheet_details(db, timesheet_id)

@router.get("/details/{detail_id}", response_model=schemas.TimesheetDetailResponse)
def get_timesheet_detail(detail_id: int, db: Session = Depends(get_db)):
    """Get a specific timesheet detail by ID"""
    detail = service.TimesheetService.get_timesheet_detail(db, detail_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Timesheet detail not found")
    return detail

@router.post("/{timesheet_id}/details", response_model=schemas.TimesheetDetailResponse, status_code=201)
def create_timesheet_detail(
    timesheet_id: int, 
    detail: schemas.TimesheetDetailCreate, 
    db: Session = Depends(get_db)
):
    """Create a new timesheet detail"""
    detail.TimesheetID = timesheet_id
    return service.TimesheetService.create_timesheet_detail(db, detail)

@router.put("/details/{detail_id}", response_model=schemas.TimesheetDetailResponse)
def update_timesheet_detail(
    detail_id: int, 
    detail_update: schemas.TimesheetDetailUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing timesheet detail"""
    return service.TimesheetService.update_timesheet_detail(db, detail_id, detail_update)

@router.delete("/details/{detail_id}", status_code=204)
def delete_timesheet_detail(detail_id: int, db: Session = Depends(get_db)):
    """Delete a timesheet detail"""
    service.TimesheetService.delete_timesheet_detail(db, detail_id)
    return None

# Approval routes
@router.post("/{timesheet_id}/submit")
def submit_timesheet(timesheet_id: int, db: Session = Depends(get_db)):
    """Submit a timesheet for approval"""
    return service.TimesheetService.submit_timesheet(db, timesheet_id)

@router.post("/{timesheet_id}/approve")
def approve_timesheet(
    timesheet_id: int,
    approval: schemas.TimesheetApprovalRequest,
    db: Session = Depends(get_db)
):
    """Approve or reject a timesheet"""
    return service.TimesheetService.approve_timesheet(db, timesheet_id, approval) 