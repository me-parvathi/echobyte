"""
Timesheet utility functions for week calculations and smart timesheet management
"""

from datetime import date, timedelta
from typing import Tuple, Optional
from sqlalchemy.orm import Session
from api.timesheet import models
from api.leave import models as leave_models


def get_week_dates(work_date: date) -> Tuple[date, date]:
    """
    Calculate week start (Monday) and end (Sunday) for a given date.
    
    Args:
        work_date: Any date within the week
        
    Returns:
        Tuple of (week_start_date, week_end_date)
    """
    # Find Monday of the week (weekday() returns 0=Monday, 6=Sunday)
    days_since_monday = work_date.weekday()
    week_start = work_date - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)  # Sunday
    return week_start, week_end


def get_week_start_date(work_date: date) -> date:
    """
    Get the Monday date for the week containing the given date.
    
    Args:
        work_date: Any date within the week
        
    Returns:
        Monday date of the week
    """
    days_since_monday = work_date.weekday()
    return work_date - timedelta(days=days_since_monday)


def is_valid_work_date(work_date: date) -> bool:
    """
    Check if the date is a valid work date (Monday to Friday and not in the future).
    
    Args:
        work_date: Date to validate
        
    Returns:
        True if it's a weekday (Monday-Friday) and not in the future, False otherwise
    """
    from datetime import date as current_date
    today = current_date.today()
    
    # Check if it's a future date
    if work_date > today:
        return False
    
    # Check if it's a weekday (Monday-Friday)
    return work_date.weekday() < 5  # Monday = 0, Friday = 4


def check_leave_conflicts_for_timesheet_upload(
    db: Session, 
    employee_id: int, 
    work_date: date
) -> bool:
    """
    Check if there are any leave conflicts when uploading timesheet data.
    
    Args:
        db: Database session
        employee_id: Employee ID
        work_date: Work date to check
        
    Returns:
        True if there are leave conflicts, False otherwise
        
    Raises:
        HTTPException: If there are leave conflicts
    """
    from fastapi import HTTPException
    
    # Get the week dates for the work date
    week_start, week_end = get_week_dates(work_date)
    
    # Check for any leave applications that overlap with the timesheet week
    # and are in submitted or approved states
    conflicting_leaves = db.query(leave_models.LeaveApplication).filter(
        leave_models.LeaveApplication.EmployeeID == employee_id,
        leave_models.LeaveApplication.StatusCode.in_([
            "Submitted", 
            "Manager-Approved", 
            "HR-Approved"
        ]),
        # Check for date overlap
        leave_models.LeaveApplication.StartDate <= week_end,
        leave_models.LeaveApplication.EndDate >= week_start
    ).all()
    
    if conflicting_leaves:
        leave_details = []
        for leave in conflicting_leaves:
            leave_details.append(
                f"Leave {leave.LeaveApplicationID}: {leave.StartDate} to {leave.EndDate} "
                f"(Status: {leave.StatusCode})"
            )
        
        raise HTTPException(
            status_code=400,
            detail=f"Cannot upload timesheet data. Employee has conflicting leave applications: {'; '.join(leave_details)}"
        )
    
    return False


def check_timesheet_conflicts_for_leave_application(
    db: Session, 
    employee_id: int, 
    start_date: date, 
    end_date: date
) -> bool:
    """
    Check if there are any timesheet conflicts when applying for leave.
    
    Args:
        db: Database session
        employee_id: Employee ID
        start_date: Leave start date
        end_date: Leave end date
        
    Returns:
        True if there are timesheet conflicts, False otherwise
        
    Raises:
        HTTPException: If there are timesheet conflicts
    """
    from fastapi import HTTPException
    
    # Check for timesheets in submitted or approved states that overlap with the leave period
    conflicting_timesheets = db.query(models.Timesheet).filter(
        models.Timesheet.EmployeeID == employee_id,
        models.Timesheet.StatusCode.in_(["Submitted", "Approved"]),
        # Check for date overlap
        models.Timesheet.WeekStartDate <= end_date,
        models.Timesheet.WeekEndDate >= start_date
    ).all()
    
    if conflicting_timesheets:
        timesheet_details = []
        for timesheet in conflicting_timesheets:
            timesheet_details.append(
                f"Timesheet {timesheet.TimesheetID}: Week of {timesheet.WeekStartDate} "
                f"(Status: {timesheet.StatusCode})"
            )
        
        raise HTTPException(
            status_code=400,
            detail=f"Cannot apply for leave. Employee has conflicting timesheets in submitted/approved state: {'; '.join(timesheet_details)}"
        )
    
    return False


def check_leave_conflicts_for_timesheet_submission(
    db: Session, 
    timesheet_id: int
) -> bool:
    """
    Check if there are any leave conflicts when submitting a timesheet.
    
    Args:
        db: Database session
        timesheet_id: Timesheet ID
        
    Returns:
        True if there are leave conflicts, False otherwise
        
    Raises:
        HTTPException: If there are leave conflicts
    """
    from fastapi import HTTPException
    
    # Get the timesheet
    timesheet = db.query(models.Timesheet).filter(
        models.Timesheet.TimesheetID == timesheet_id
    ).first()
    
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    # Check for any leave applications that overlap with the timesheet week
    # and are in submitted or approved states
    conflicting_leaves = db.query(leave_models.LeaveApplication).filter(
        leave_models.LeaveApplication.EmployeeID == timesheet.EmployeeID,
        leave_models.LeaveApplication.StatusCode.in_([
            "Submitted", 
            "Manager-Approved", 
            "HR-Approved"
        ]),
        # Check for date overlap
        leave_models.LeaveApplication.StartDate <= timesheet.WeekEndDate,
        leave_models.LeaveApplication.EndDate >= timesheet.WeekStartDate
    ).all()
    
    if conflicting_leaves:
        leave_details = []
        for leave in conflicting_leaves:
            leave_details.append(
                f"Leave {leave.LeaveApplicationID}: {leave.StartDate} to {leave.EndDate} "
                f"(Status: {leave.StatusCode})"
            )
        
        raise HTTPException(
            status_code=400,
            detail=f"Cannot submit timesheet. Employee has conflicting leave applications: {'; '.join(leave_details)}"
        )
    
    return False


def get_or_create_timesheet_for_date(
    db: Session, 
    employee_id: int, 
    work_date: date
) -> models.Timesheet:
    """
    Get existing timesheet for week or create new one in draft status.
    
    Args:
        db: Database session
        employee_id: Employee ID
        work_date: Any date within the week
        
    Returns:
        Timesheet object (existing or newly created)
    """
    week_start, week_end = get_week_dates(work_date)
    
    # Check if timesheet exists for this week
    timesheet = db.query(models.Timesheet).filter(
        models.Timesheet.EmployeeID == employee_id,
        models.Timesheet.WeekStartDate == week_start
    ).first()
    
    if not timesheet:
        # Create new draft timesheet
        timesheet = models.Timesheet(
            EmployeeID=employee_id,
            WeekStartDate=week_start,
            WeekEndDate=week_end,
            StatusCode="Draft",
            TotalHours=0.0
        )
        db.add(timesheet)
        db.commit()
        db.refresh(timesheet)
    
    return timesheet


def calculate_weekly_total_hours(db: Session, timesheet_id: int) -> float:
    """
    Calculate total hours for a timesheet based on its details.
    
    Args:
        db: Database session
        timesheet_id: Timesheet ID
        
    Returns:
        Total hours as float
    """
    details = db.query(models.TimesheetDetail).filter(
        models.TimesheetDetail.TimesheetID == timesheet_id
    ).all()
    
    total_hours = sum(detail.HoursWorked for detail in details)
    return round(total_hours, 2)


def update_timesheet_total_hours(db: Session, timesheet_id: int) -> None:
    """
    Update the total hours for a timesheet based on its details.
    
    Args:
        db: Database session
        timesheet_id: Timesheet ID
    """
    timesheet = db.query(models.Timesheet).filter(
        models.Timesheet.TimesheetID == timesheet_id
    ).first()
    
    if timesheet:
        total_hours = calculate_weekly_total_hours(db, timesheet_id)
        timesheet.TotalHours = total_hours
        db.commit()


def get_timesheet_for_employee_week(
    db: Session, 
    employee_id: int, 
    week_start_date: date
) -> Optional[models.Timesheet]:
    """
    Get timesheet for a specific employee and week.
    
    Args:
        db: Database session
        employee_id: Employee ID
        week_start_date: Monday date of the week
        
    Returns:
        Timesheet object if found, None otherwise
    """
    return db.query(models.Timesheet).filter(
        models.Timesheet.EmployeeID == employee_id,
        models.Timesheet.WeekStartDate == week_start_date
    ).first()


def get_timesheet_details_for_date(
    db: Session, 
    employee_id: int, 
    work_date: date
) -> Optional[models.TimesheetDetail]:
    """
    Get timesheet detail for a specific employee and date.
    
    Args:
        db: Database session
        employee_id: Employee ID
        work_date: Work date
        
    Returns:
        TimesheetDetail object if found, None otherwise
    """
    week_start, _ = get_week_dates(work_date)
    
    # Get timesheet for this week
    timesheet = get_timesheet_for_employee_week(db, employee_id, week_start)
    if not timesheet:
        return None
    
    # Get detail for this specific date
    return db.query(models.TimesheetDetail).filter(
        models.TimesheetDetail.TimesheetID == timesheet.TimesheetID,
        models.TimesheetDetail.WorkDate == work_date
    ).first()


def validate_timesheet_submission(db: Session, timesheet_id: int) -> bool:
    """
    Validate if a timesheet can be submitted (has details for all weekdays).
    
    Args:
        db: Database session
        timesheet_id: Timesheet ID
        
    Returns:
        True if timesheet can be submitted, False otherwise
    """
    timesheet = db.query(models.Timesheet).filter(
        models.Timesheet.TimesheetID == timesheet_id
    ).first()
    
    if not timesheet:
        return False
    
    # Get all weekdays in the timesheet period
    weekdays = []
    current_date = timesheet.WeekStartDate
    while current_date <= timesheet.WeekEndDate:
        if is_valid_work_date(current_date):
            weekdays.append(current_date)
        current_date += timedelta(days=1)
    
    # Get existing details
    details = db.query(models.TimesheetDetail).filter(
        models.TimesheetDetail.TimesheetID == timesheet_id
    ).all()
    
    detail_dates = {detail.WorkDate for detail in details}
    
    # Check if all weekdays have details
    return all(weekday in detail_dates for weekday in weekdays)


def get_employee_timesheets_for_period(
    db: Session, 
    employee_id: int, 
    start_date: date, 
    end_date: date
) -> list[models.Timesheet]:
    """
    Get all timesheets for an employee within a date range.
    
    Args:
        db: Database session
        employee_id: Employee ID
        start_date: Start date of period
        end_date: End date of period
        
    Returns:
        List of timesheet objects
    """
    return db.query(models.Timesheet).filter(
        models.Timesheet.EmployeeID == employee_id,
        models.Timesheet.WeekStartDate >= start_date,
        models.Timesheet.WeekEndDate <= end_date
    ).order_by(models.Timesheet.WeekStartDate).all() 