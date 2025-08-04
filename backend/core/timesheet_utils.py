"""
Timesheet utility functions for week calculations and smart timesheet management
"""

from datetime import date, timedelta, datetime
from typing import Tuple, Optional
from sqlalchemy.orm import Session
from api.timesheet import models
from api.leave import models as leave_models

def get_week_dates(work_date: date) -> Tuple[date, date]:
    """
    Calculate week start (Monday) and end (Sunday) for a given date.
    """
    days_since_monday = work_date.weekday()
    week_start = work_date - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end

def get_week_start_date(work_date: date) -> date:
    """
    Get the Monday date for the week containing the given date.
    """
    days_since_monday = work_date.weekday()
    return work_date - timedelta(days=days_since_monday)

def is_valid_work_date(work_date: date) -> bool:
    """
    Check if the date is a valid work date (Monday to Friday and not in the future).
    """
    today = date.today()
    if work_date > today:
        return False
    return work_date.weekday() < 5  # Monday = 0, Friday = 4

def check_leave_conflicts_for_timesheet_upload(
    db: Session, 
    employee_id: int, 
    work_date: date
) -> bool:
    """
    Check if there are any leave conflicts when uploading timesheet data.
    Raises HTTPException if there are conflicts.
    """
    from fastapi import HTTPException
    week_start, week_end = get_week_dates(work_date)
    conflicting_leaves = db.query(leave_models.LeaveApplication).filter(
        leave_models.LeaveApplication.EmployeeID == employee_id,
        leave_models.LeaveApplication.StatusCode.in_([
            "Submitted", "Manager-Approved", "HR-Approved"
        ]),
        leave_models.LeaveApplication.StartDate <= week_end,
        leave_models.LeaveApplication.EndDate >= week_start
    ).all()
    if conflicting_leaves:
        leave_details = [
            f"Leave {leave.LeaveApplicationID}: {leave.StartDate} to {leave.EndDate} (Status: {leave.StatusCode})"
            for leave in conflicting_leaves
        ]
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
    Raises HTTPException if there are conflicts.
    """
    from fastapi import HTTPException
    conflicting_timesheets = db.query(models.Timesheet).filter(
        models.Timesheet.EmployeeID == employee_id,
        models.Timesheet.StatusCode.in_(["Submitted", "Approved"]),
        models.Timesheet.WeekStartDate <= end_date,
        models.Timesheet.WeekEndDate >= start_date
    ).all()
    if conflicting_timesheets:
        timesheet_details = [
            f"Timesheet {ts.TimesheetID}: Week of {ts.WeekStartDate} (Status: {ts.StatusCode})"
            for ts in conflicting_timesheets
        ]
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
    Raises HTTPException if there are conflicts.
    """
    from fastapi import HTTPException
    timesheet = db.query(models.Timesheet).filter(
        models.Timesheet.TimesheetID == timesheet_id
    ).first()
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    conflicting_leaves = db.query(leave_models.LeaveApplication).filter(
        leave_models.LeaveApplication.EmployeeID == timesheet.EmployeeID,
        leave_models.LeaveApplication.StatusCode.in_([
            "Submitted", "Manager-Approved", "HR-Approved"
        ]),
        leave_models.LeaveApplication.StartDate <= timesheet.WeekEndDate,
        leave_models.LeaveApplication.EndDate >= timesheet.WeekStartDate
    ).all()
    if conflicting_leaves:
        leave_details = [
            f"Leave {leave.LeaveApplicationID}: {leave.StartDate} to {leave.EndDate} (Status: {leave.StatusCode})"
            for leave in conflicting_leaves
        ]
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
    """
    week_start, week_end = get_week_dates(work_date)
    timesheet = db.query(models.Timesheet).filter(
        models.Timesheet.EmployeeID == employee_id,
        models.Timesheet.WeekStartDate == week_start
    ).first()
    if not timesheet:
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
    """
    details = db.query(models.TimesheetDetail).filter(
        models.TimesheetDetail.TimesheetID == timesheet_id
    ).all()
    total_hours = sum(detail.HoursWorked for detail in details)
    return round(total_hours, 2)

def update_timesheet_total_hours(db: Session, timesheet_id: int) -> None:
    """
    Update the total hours for a timesheet based on its details.
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
    """
    week_start, _ = get_week_dates(work_date)
    timesheet = get_timesheet_for_employee_week(db, employee_id, week_start)
    if not timesheet:
        return None
    return db.query(models.TimesheetDetail).filter(
        models.TimesheetDetail.TimesheetID == timesheet.TimesheetID,
        models.TimesheetDetail.WorkDate == work_date
    ).first()

def validate_timesheet_submission(db: Session, timesheet_id: int) -> bool:
    """
    Validate if a timesheet can be submitted (has details for all weekdays).
    """
    timesheet = db.query(models.Timesheet).filter(
        models.Timesheet.TimesheetID == timesheet_id
    ).first()
    if not timesheet:
        return False
    weekdays = []
    current_date = timesheet.WeekStartDate
    while current_date <= timesheet.WeekEndDate:
        if is_valid_work_date(current_date):
            weekdays.append(current_date)
        current_date += timedelta(days=1)
    details = db.query(models.TimesheetDetail).filter(
        models.TimesheetDetail.TimesheetID == timesheet_id
    ).all()
    detail_dates = {detail.WorkDate for detail in details}
    return all(weekday in detail_dates for weekday in weekdays)

def get_employee_timesheets_for_period(
    db: Session, 
    employee_id: int, 
    start_date: date, 
    end_date: date
) -> list[models.Timesheet]:
    """
    Get all timesheets for an employee within a date range.
    """
    return db.query(models.Timesheet).filter(
        models.Timesheet.EmployeeID == employee_id,
        models.Timesheet.WeekStartDate >= start_date,
        models.Timesheet.WeekEndDate <= end_date
    ).order_by(models.Timesheet.WeekStartDate).all()

# --- PTO Calculation Utility ---

def process_biweekly_overtime_pto(db: Session, employee_id: int, period_start: date, period_end: date):
    """
    Process overtime for an employee for a bi-weekly period.
    If HoursWorked > 8, add extra hours to EmployeeOvertimePTO.
    Grant 1 PTO day for every 16 overtime hours.
    """
    details = db.query(models.TimesheetDetail).filter(
        models.TimesheetDetail.EmployeeID == employee_id,
        models.TimesheetDetail.WorkDate >= period_start,
        models.TimesheetDetail.WorkDate <= period_end
    ).all()

    overtime_hours = 0.0
    for detail in details:
        if detail.HoursWorked > 8:
            overtime_hours += detail.HoursWorked - 8

    pto_record = db.query(models.EmployeeOvertimePTO).filter(
        models.EmployeeOvertimePTO.EmployeeID == employee_id
    ).first()
    if not pto_record:
        pto_record = models.EmployeeOvertimePTO(
            EmployeeID=employee_id,
            OvertimeHours=0.0,
            PTOGranted=0,
            LastCalculated=datetime.now()
        )
        db.add(pto_record)
        db.commit()
        db.refresh(pto_record)

    pto_record.OvertimeHours += overtime_hours

    additional_pto = int(pto_record.OvertimeHours // 16)
    if additional_pto > 0:
        pto_record.PTOGranted += additional_pto
        pto_record.OvertimeHours -= 16 * additional_pto

    pto_record.LastCalculated = datetime.now()
    db.commit()
    db.refresh(pto_record)
    return pto_record

def process_last_biweekly_for_employee(db: Session, employee_id: int):
    """
    Process the most recent bi-weekly period for an employee.
    """
    today = date.today()
    last_monday = today - timedelta(days=today.weekday())
    period_end = last_monday + timedelta(days=13)
    period_start = last_monday
    return process_biweekly_overtime_pto(db, employee_id, period_start, period_end)