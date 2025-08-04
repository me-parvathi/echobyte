from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
from . import models, schemas
from fastapi import HTTPException
from core.pagination import paginate_query
from core.timesheet_utils import (
    get_week_dates,
    get_week_start_date,
    get_or_create_timesheet_for_date,
    update_timesheet_total_hours,
    get_timesheet_details_for_date,
    validate_timesheet_submission,
    is_valid_work_date,
    get_employee_timesheets_for_period,
    check_leave_conflicts_for_timesheet_upload,
    check_leave_conflicts_for_timesheet_submission,
    calculate_pto_from_overtime,
    process_last_biweekly_for_employee  # <-- Make sure this is imported!
)

def get_or_404(query, not_found_msg="Not found"):
    obj = query.first()
    if not obj:
        raise HTTPException(status_code=404, detail=not_found_msg)
    return obj

class TimesheetService:
    @staticmethod
    def get_timesheets(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        employee_id: Optional[int] = None,
        status_code: Optional[str] = None
    ) -> dict:
        query = db.query(models.Timesheet)
        if employee_id:
            query = query.filter(models.Timesheet.EmployeeID == employee_id)
        if status_code:
            query = query.filter(models.Timesheet.StatusCode == status_code)
        return paginate_query(query, skip, limit, models.Timesheet.CreatedAt)
    
    @staticmethod
    def get_timesheet(db: Session, timesheet_id: int) -> Optional[models.Timesheet]:
        return get_or_404(
            db.query(models.Timesheet).filter(models.Timesheet.TimesheetID == timesheet_id),
            "Timesheet not found"
        )
    
    @staticmethod
    def create_weekly_timesheet(db: Session, weekly_data: schemas.WeeklyTimesheetCreate) -> models.Timesheet:
        week_start, week_end = get_week_dates(weekly_data.WeekStartDate)
        if week_start != weekly_data.WeekStartDate or week_end != weekly_data.WeekEndDate:
            raise HTTPException(
                status_code=400, 
                detail="WeekStartDate and WeekEndDate must represent a complete week (Monday to Sunday)"
            )
        for detail_data in weekly_data.details:
            check_leave_conflicts_for_timesheet_upload(db, weekly_data.EmployeeID, detail_data.WorkDate)
        existing_timesheet = db.query(models.Timesheet).filter(
            models.Timesheet.EmployeeID == weekly_data.EmployeeID,
            models.Timesheet.WeekStartDate == weekly_data.WeekStartDate
        ).first()
        if existing_timesheet:
            raise HTTPException(
                status_code=400,
                detail=f"Timesheet already exists for week starting {weekly_data.WeekStartDate}"
            )
        timesheet = models.Timesheet(
            EmployeeID=weekly_data.EmployeeID,
            WeekStartDate=weekly_data.WeekStartDate,
            WeekEndDate=weekly_data.WeekEndDate,
            StatusCode="Draft",
            TotalHours=0.0,
            Comments=weekly_data.Comments
        )
        db.add(timesheet)
        db.commit()
        db.refresh(timesheet)
        total_hours = 0.0
        for detail_data in weekly_data.details:
            if not (weekly_data.WeekStartDate <= detail_data.WorkDate <= weekly_data.WeekEndDate):
                raise HTTPException(
                    status_code=400,
                    detail=f"Work date {detail_data.WorkDate} is not within the specified week"
                )
            if detail_data.HoursWorked < 0 or detail_data.HoursWorked > 24:
                raise HTTPException(
                    status_code=400,
                    detail=f"Hours worked must be between 0 and 24, got {detail_data.HoursWorked}"
                )
            detail = models.TimesheetDetail(
                TimesheetID=timesheet.TimesheetID,
                EmployeeID=weekly_data.EmployeeID,
                WorkDate=detail_data.WorkDate,
                ProjectCode=detail_data.ProjectCode,
                TaskDescription=detail_data.TaskDescription,
                HoursWorked=detail_data.HoursWorked,
                IsOvertime=detail_data.IsOvertime
            )
            db.add(detail)
            total_hours += detail_data.HoursWorked
        timesheet.TotalHours = round(total_hours, 2)
        db.commit()
        db.refresh(timesheet)
        return timesheet
    
    @staticmethod
    def update_timesheet(db: Session, timesheet_id: int, timesheet_update: schemas.TimesheetUpdate) -> Optional[models.Timesheet]:
        db_timesheet = TimesheetService.get_timesheet(db, timesheet_id)
        update_data = timesheet_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_timesheet, field, value)
        db.commit()
        db.refresh(db_timesheet)
        return db_timesheet
    
    @staticmethod
    def delete_timesheet(db: Session, timesheet_id: int) -> bool:
        db_timesheet = TimesheetService.get_timesheet(db, timesheet_id)
        db.delete(db_timesheet)
        db.commit()
        return True
    
    @staticmethod
    def get_timesheet_details(
        db: Session, 
        timesheet_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> dict:
        query = db.query(models.TimesheetDetail).filter(
            models.TimesheetDetail.TimesheetID == timesheet_id
        )
        return paginate_query(query, skip, limit, models.TimesheetDetail.WorkDate)
    
    @staticmethod
    def get_timesheet_detail(db: Session, detail_id: int) -> Optional[models.TimesheetDetail]:
        return get_or_404(
            db.query(models.TimesheetDetail).filter(models.TimesheetDetail.DetailID == detail_id),
            "Timesheet detail not found"
        )
    
    @staticmethod
    def create_or_update_daily_entry(db: Session, daily_data: schemas.DailyEntryCreate) -> models.TimesheetDetail:
        if not is_valid_work_date(daily_data.WorkDate):
            from datetime import date as current_date
            today = current_date.today()
            if daily_data.WorkDate > today:
                raise HTTPException(
                    status_code=400,
                    detail=f"Work date {daily_data.WorkDate} is in the future. Only past and current dates are allowed."
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Work date {daily_data.WorkDate} is not a valid work day (Monday-Friday)"
                )
        if daily_data.HoursWorked < 0 or daily_data.HoursWorked > 24:
            raise HTTPException(
                status_code=400,
                detail=f"Hours worked must be between 0 and 24, got {daily_data.HoursWorked}"
            )
        check_leave_conflicts_for_timesheet_upload(db, daily_data.EmployeeID, daily_data.WorkDate)
        timesheet = get_or_create_timesheet_for_date(db, daily_data.EmployeeID, daily_data.WorkDate)
        existing_detail = db.query(models.TimesheetDetail).filter(
            models.TimesheetDetail.TimesheetID == timesheet.TimesheetID,
            models.TimesheetDetail.WorkDate == daily_data.WorkDate
        ).first()
        if existing_detail:
            existing_detail.ProjectCode = daily_data.ProjectCode
            existing_detail.TaskDescription = daily_data.TaskDescription
            existing_detail.HoursWorked = daily_data.HoursWorked
            existing_detail.IsOvertime = daily_data.IsOvertime
            existing_detail.EmployeeID = daily_data.EmployeeID
            db.commit()
            db.refresh(existing_detail)
            update_timesheet_total_hours(db, timesheet.TimesheetID)
            return existing_detail
        else:
            detail = models.TimesheetDetail(
                TimesheetID=timesheet.TimesheetID,
                EmployeeID=daily_data.EmployeeID,
                WorkDate=daily_data.WorkDate,
                ProjectCode=daily_data.ProjectCode,
                TaskDescription=daily_data.TaskDescription,
                HoursWorked=daily_data.HoursWorked,
                IsOvertime=daily_data.IsOvertime
            )
            db.add(detail)
            db.commit()
            db.refresh(detail)
            update_timesheet_total_hours(db, timesheet.TimesheetID)
            return detail
    
    @staticmethod
    def get_daily_entry(db: Session, employee_id: int, work_date: date) -> Optional[models.TimesheetDetail]:
        return get_timesheet_details_for_date(db, employee_id, work_date)
    
    @staticmethod
    def get_employee_weekly_timesheet(db: Session, employee_id: int, week_start_date: date) -> Optional[models.Timesheet]:
        return db.query(models.Timesheet).filter(
            models.Timesheet.EmployeeID == employee_id,
            models.Timesheet.WeekStartDate == week_start_date
        ).first()
    
    @staticmethod
    def update_timesheet_detail(db: Session, detail_id: int, detail_update: schemas.TimesheetDetailUpdate) -> Optional[models.TimesheetDetail]:
        db_detail = TimesheetService.get_timesheet_detail(db, detail_id)
        update_data = detail_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_detail, field, value)
        db.commit()
        db.refresh(db_detail)
        return db_detail
    
    @staticmethod
    def delete_timesheet_detail(db: Session, detail_id: int) -> bool:
        db_detail = TimesheetService.get_timesheet_detail(db, detail_id)
        db.delete(db_detail)
        db.commit()
        return True
    
    @staticmethod
    def submit_timesheet(db: Session, timesheet_id: int) -> models.Timesheet:
        db_timesheet = TimesheetService.get_timesheet(db, timesheet_id)
        check_leave_conflicts_for_timesheet_submission(db, timesheet_id)
        if not validate_timesheet_submission(db, timesheet_id):
            raise HTTPException(
                status_code=400,
                detail="Timesheet cannot be submitted. Please ensure all weekdays have entries."
            )
        if db_timesheet.StatusCode in ["Submitted", "Approved", "Rejected"]:
            raise HTTPException(
                status_code=400,
                detail=f"Timesheet is already {db_timesheet.StatusCode.lower()}"
            )
        db_timesheet.StatusCode = "Submitted"
        db_timesheet.SubmittedAt = datetime.now()
        db.commit()
        db.refresh(db_timesheet)

        # Bi-weekly PTO calculation and update EmployeeOvertimePTO table
        process_last_biweekly_for_employee(db, db_timesheet.EmployeeID)

        return db_timesheet
    
    @staticmethod
    def approve_timesheet(db: Session, timesheet_id: int, approval: schemas.TimesheetApprovalRequest) -> models.Timesheet:
        db_timesheet = TimesheetService.get_timesheet(db, timesheet_id)
        db_timesheet.StatusCode = approval.status
        db_timesheet.ApprovedByID = approval.approved_by_id
        db_timesheet.ApprovedAt = datetime.now()
        if approval.comments:
            db_timesheet.Comments = approval.comments
        db.commit()
        db.refresh(db_timesheet)
        return db_timesheet

    @staticmethod
    def get_employee_timesheet_batch(
        db: Session, 
        employee_id: int, 
        week_start_date: Optional[date] = None,
        include_history: bool = True,
        history_limit: int = 10
    ) -> dict:
        from datetime import date as current_date
        from api.employee import models as employee_models
        if not week_start_date:
            today = current_date.today()
            week_start_date = get_week_start_date(today)
        week_end_date = week_start_date + timedelta(days=6)
        employee = db.query(employee_models.Employee).filter(
            employee_models.Employee.EmployeeID == employee_id
        ).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        employee_profile = {
            "EmployeeID": employee.EmployeeID,
            "FirstName": employee.FirstName,
            "LastName": employee.LastName,
            "Email": employee.CompanyEmail,
            "UserID": employee.UserID
        }
        current_week = db.query(models.Timesheet).filter(
            models.Timesheet.EmployeeID == employee_id,
            models.Timesheet.WeekStartDate == week_start_date
        ).first()
        if not current_week:
            current_week = models.Timesheet(
                EmployeeID=employee_id,
                WeekStartDate=week_start_date,
                WeekEndDate=week_end_date,
                StatusCode="Draft",
                TotalHours=0.0
            )
            db.add(current_week)
            db.commit()
            db.refresh(current_week)
        details = db.query(models.TimesheetDetail).filter(
            models.TimesheetDetail.TimesheetID == current_week.TimesheetID
        ).order_by(models.TimesheetDetail.WorkDate).all()
        current_week.details = details
        timesheet_history = []
        if include_history:
            history_query = db.query(models.Timesheet).filter(
                models.Timesheet.EmployeeID == employee_id,
                models.Timesheet.TimesheetID != current_week.TimesheetID
            ).order_by(models.Timesheet.WeekStartDate.desc()).limit(history_limit)
            timesheet_history = history_query.all()
        return {
            "current_week": current_week,
            "timesheet_history": timesheet_history,
            "employee_profile": employee_profile,
            "total_count": len(timesheet_history) + 1,
            "week_start_date": week_start_date,
            "week_end_date": week_end_date
        }