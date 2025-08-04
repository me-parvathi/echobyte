from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from core.database import get_db
from . import schemas, service

router = APIRouter()

# Timesheet API Endpoints

@router.get("/", response_model=schemas.TimesheetListResponse)
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

@router.get("/employee/{employee_id}/week/{week_start_date}", response_model=schemas.TimesheetResponse)
def get_employee_weekly_timesheet(
    employee_id: int, 
    week_start_date: date, 
    db: Session = Depends(get_db)
):
    """Get timesheet for a specific employee and week"""
    timesheet = service.TimesheetService.get_employee_weekly_timesheet(db, employee_id, week_start_date)
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found for this week")
    return timesheet

@router.get("/employee/{employee_id}/daily/{work_date}", response_model=schemas.TimesheetDetailResponse)
def get_daily_entry(
    employee_id: int, 
    work_date: date, 
    db: Session = Depends(get_db)
):
    """Get daily timesheet entry for a specific employee and date"""
    detail = service.TimesheetService.get_daily_entry(db, employee_id, work_date)
    if not detail:
        raise HTTPException(status_code=404, detail="Daily entry not found")
    return detail

@router.post("/weekly", response_model=schemas.TimesheetResponse, status_code=201)
def create_weekly_timesheet(weekly_data: schemas.WeeklyTimesheetCreate, db: Session = Depends(get_db)):
    """
    Create a complete weekly timesheet with all daily details in one operation.
    Use this for bulk weekly data entry.
    """
    return service.TimesheetService.create_weekly_timesheet(db, weekly_data)

@router.post("/daily", response_model=schemas.TimesheetDetailResponse, status_code=201)
def create_daily_entry(daily_data: schemas.DailyEntryCreate, db: Session = Depends(get_db)):
    """
    Create or update a daily timesheet entry (smart method).
    Automatically creates timesheet if needed and handles updates.
    Use this for individual daily time entries.
    """
    # Ensure EmployeeID is passed from the request and used in the service
    return service.TimesheetService.create_or_update_daily_entry(db, daily_data)

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

@router.get("/{timesheet_id}/details", response_model=schemas.TimesheetDetailListResponse)
def get_timesheet_details(
    timesheet_id: int, 
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all details for a specific timesheet"""
    return service.TimesheetService.get_timesheet_details(db, timesheet_id, skip, limit)

@router.get("/details/{detail_id}", response_model=schemas.TimesheetDetailResponse)
def get_timesheet_detail(detail_id: int, db: Session = Depends(get_db)):
    """Get a specific timesheet detail by ID"""
    detail = service.TimesheetService.get_timesheet_detail(db, detail_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Timesheet detail not found")
    return detail

@router.put("/details/{detail_id}", response_model=schemas.TimesheetDetailResponse)
def update_timesheet_detail(
    detail_id: int, 
    detail_update: schemas.TimesheetDetailUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing timesheet detail"""
    # Ensure EmployeeID can be updated if provided
    return service.TimesheetService.update_timesheet_detail(db, detail_id, detail_update)

@router.delete("/details/{detail_id}", status_code=204)
def delete_timesheet_detail(detail_id: int, db: Session = Depends(get_db)):
    """Delete a timesheet detail"""
    service.TimesheetService.delete_timesheet_detail(db, detail_id)
    return None

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

@router.get("/employee/{employee_id}/batch", response_model=schemas.TimesheetBatchResponse)
def get_employee_timesheet_batch(
    employee_id: int,
    week_start_date: Optional[date] = None,
    include_history: bool = True,
    history_limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get batched timesheet data for an employee including:
    - Current week timesheet with details
    - Recent timesheet history
    - Employee profile (basic info)
    """
    return service.TimesheetService.get_employee_timesheet_batch(
        db, employee_id, week_start_date, include_history, history_limit
    )