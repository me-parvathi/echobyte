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
    check_leave_conflicts_for_timesheet_approval
)

# Placeholder service for timesheets
class TimesheetService:
    @staticmethod
    def get_timesheets(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        employee_id: Optional[int] = None,
        status_code: Optional[str] = None
    ) -> dict:
        """Get list of timesheets with optional filtering and count"""
        query = db.query(models.Timesheet)
        
        if employee_id:
            query = query.filter(models.Timesheet.EmployeeID == employee_id)
        
        if status_code:
            query = query.filter(models.Timesheet.StatusCode == status_code)
        
        return paginate_query(query, skip, limit, models.Timesheet.CreatedAt)
    
    @staticmethod
    def get_timesheet(db: Session, timesheet_id: int, include_details: bool = False) -> Optional[models.Timesheet]:
        """Get a specific timesheet by ID"""
        timesheet = db.query(models.Timesheet).filter(models.Timesheet.TimesheetID == timesheet_id).first()
        
        if timesheet and include_details:
            # Load details for the timesheet
            details = db.query(models.TimesheetDetail).filter(
                models.TimesheetDetail.TimesheetID == timesheet_id
            ).order_by(models.TimesheetDetail.WorkDate).all()
            timesheet.details = details
        
        return timesheet
    

    
    @staticmethod
    def create_weekly_timesheet(db: Session, weekly_data: schemas.WeeklyTimesheetCreate) -> models.Timesheet:
        """
        Create a weekly timesheet with all details in one operation.
        This is for when user enters weekly data at once.
        """
        # Validate week dates
        week_start, week_end = get_week_dates(weekly_data.WeekStartDate)
        if week_start != weekly_data.WeekStartDate or week_end != weekly_data.WeekEndDate:
            raise HTTPException(
                status_code=400, 
                detail="WeekStartDate and WeekEndDate must represent a complete week (Monday to Sunday)"
            )
        
        # Check for leave conflicts before creating timesheet
        for detail_data in weekly_data.details:
            check_leave_conflicts_for_timesheet_upload(db, weekly_data.EmployeeID, detail_data.WorkDate)
        
        # Check if timesheet already exists for this week
        existing_timesheet = db.query(models.Timesheet).filter(
            models.Timesheet.EmployeeID == weekly_data.EmployeeID,
            models.Timesheet.WeekStartDate == weekly_data.WeekStartDate
        ).first()
        
        if existing_timesheet:
            raise HTTPException(
                status_code=400,
                detail=f"Timesheet already exists for week starting {weekly_data.WeekStartDate}"
            )
        
        # Create timesheet
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
        
        # Create details for each day
        total_hours = 0.0
        for detail_data in weekly_data.details:
            # Validate work date is within the week
            if not (weekly_data.WeekStartDate <= detail_data.WorkDate <= weekly_data.WeekEndDate):
                raise HTTPException(
                    status_code=400,
                    detail=f"Work date {detail_data.WorkDate} is not within the specified week"
                )
            
            # Validate hours
            if detail_data.HoursWorked < 0 or detail_data.HoursWorked > 24:
                raise HTTPException(
                    status_code=400,
                    detail=f"Hours worked must be between 0 and 24, got {detail_data.HoursWorked}"
                )
            
            detail = models.TimesheetDetail(
                TimesheetID=timesheet.TimesheetID,
                WorkDate=detail_data.WorkDate,
                TaskDescription=detail_data.TaskDescription,
                HoursWorked=detail_data.HoursWorked,
                IsOvertime=detail_data.IsOvertime
            )
            db.add(detail)
            total_hours += detail_data.HoursWorked
        
        # Update total hours
        timesheet.TotalHours = round(total_hours, 2)
        db.commit()
        db.refresh(timesheet)
        
        return timesheet
    
    @staticmethod
    def update_timesheet(db: Session, timesheet_id: int, timesheet_update: schemas.TimesheetUpdate) -> Optional[models.Timesheet]:
        """Update an existing timesheet"""
        db_timesheet = TimesheetService.get_timesheet(db, timesheet_id)
        if not db_timesheet:
            raise HTTPException(status_code=404, detail="Timesheet not found")
        
        update_data = timesheet_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_timesheet, field, value)
        
        db.commit()
        db.refresh(db_timesheet)
        return db_timesheet
    
    @staticmethod
    def delete_timesheet(db: Session, timesheet_id: int) -> bool:
        """Delete a timesheet"""
        db_timesheet = TimesheetService.get_timesheet(db, timesheet_id)
        if not db_timesheet:
            raise HTTPException(status_code=404, detail="Timesheet not found")
        
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
        """Get all details for a specific timesheet with count"""
        query = db.query(models.TimesheetDetail).filter(
            models.TimesheetDetail.TimesheetID == timesheet_id
        )
        
        return paginate_query(query, skip, limit, models.TimesheetDetail.WorkDate)
    
    @staticmethod
    def get_timesheet_detail(db: Session, detail_id: int) -> Optional[models.TimesheetDetail]:
        """Get a specific timesheet detail by ID"""
        return db.query(models.TimesheetDetail).filter(
            models.TimesheetDetail.DetailID == detail_id
        ).first()
    

    
    @staticmethod
    def create_or_update_daily_entry(db: Session, daily_data: schemas.DailyEntryCreate) -> models.TimesheetDetail:
        """
        Create or update a daily timesheet entry.
        This is the smart method that automatically handles timesheet creation.
        """
        # Validate work date
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
        
        # Validate hours
        if daily_data.HoursWorked < 0 or daily_data.HoursWorked > 24:
            raise HTTPException(
                status_code=400,
                detail=f"Hours worked must be between 0 and 24, got {daily_data.HoursWorked}"
            )
        
        # Check for leave conflicts before creating/updating timesheet entry
        check_leave_conflicts_for_timesheet_upload(db, daily_data.EmployeeID, daily_data.WorkDate)
        
        # Get or create timesheet for this week
        timesheet = get_or_create_timesheet_for_date(db, daily_data.EmployeeID, daily_data.WorkDate)
        
        # Handle potential race conditions by wrapping in try-catch
        try:
            # Check if detail already exists for this date
            existing_detail = db.query(models.TimesheetDetail).filter(
                models.TimesheetDetail.TimesheetID == timesheet.TimesheetID,
                models.TimesheetDetail.WorkDate == daily_data.WorkDate
            ).first()
            
            if existing_detail:
                # Update existing detail
                existing_detail.TaskDescription = daily_data.TaskDescription
                existing_detail.HoursWorked = daily_data.HoursWorked
                existing_detail.IsOvertime = daily_data.IsOvertime
                db.commit()
                db.refresh(existing_detail)
                
                # Update timesheet total hours
                update_timesheet_total_hours(db, timesheet.TimesheetID)
                
                return existing_detail
            else:
                # Create new detail
                detail = models.TimesheetDetail(
                    TimesheetID=timesheet.TimesheetID,
                    WorkDate=daily_data.WorkDate,
                    TaskDescription=daily_data.TaskDescription,
                    HoursWorked=daily_data.HoursWorked,
                    IsOvertime=daily_data.IsOvertime
                )
                db.add(detail)
                db.commit()
                db.refresh(detail)
                
                # Update timesheet total hours
                update_timesheet_total_hours(db, timesheet.TimesheetID)
                
                return detail
                
        except Exception as e:
            db.rollback()
            # If it's a unique constraint violation on TimesheetDetails, it means the detail already exists
            if "UNIQUE KEY constraint" in str(e) and "TimesheetDetails" in str(e):
                # Try to get the existing detail and update it
                existing_detail = db.query(models.TimesheetDetail).filter(
                    models.TimesheetDetail.TimesheetID == timesheet.TimesheetID,
                    models.TimesheetDetail.WorkDate == daily_data.WorkDate
                ).first()
                
                if existing_detail:
                    # Update existing detail
                    existing_detail.TaskDescription = daily_data.TaskDescription
                    existing_detail.HoursWorked = daily_data.HoursWorked
                    existing_detail.IsOvertime = daily_data.IsOvertime
                    db.commit()
                    db.refresh(existing_detail)
                    
                    # Update timesheet total hours
                    update_timesheet_total_hours(db, timesheet.TimesheetID)
                    
                    return existing_detail
            
            # Re-raise the exception if it's not a unique constraint violation we can handle
            raise e
    
    @staticmethod
    def get_daily_entry(db: Session, employee_id: int, work_date: date) -> Optional[models.TimesheetDetail]:
        """
        Get a daily timesheet entry for a specific employee and date.
        """
        return get_timesheet_details_for_date(db, employee_id, work_date)
    
    @staticmethod
    def get_employee_weekly_timesheet(db: Session, employee_id: int, week_start_date: date) -> Optional[models.Timesheet]:
        """
        Get timesheet for a specific employee and week.
        """
        return db.query(models.Timesheet).filter(
            models.Timesheet.EmployeeID == employee_id,
            models.Timesheet.WeekStartDate == week_start_date
        ).first()
    
    @staticmethod
    def update_timesheet_detail(db: Session, detail_id: int, detail_update: schemas.TimesheetDetailUpdate) -> Optional[models.TimesheetDetail]:
        """Update an existing timesheet detail"""
        db_detail = TimesheetService.get_timesheet_detail(db, detail_id)
        if not db_detail:
            raise HTTPException(status_code=404, detail="Timesheet detail not found")
        
        update_data = detail_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_detail, field, value)
        
        db.commit()
        db.refresh(db_detail)
        
        # Update timesheet total hours after modifying detail
        update_timesheet_total_hours(db, db_detail.TimesheetID)
        
        return db_detail
    
    @staticmethod
    def delete_timesheet_detail(db: Session, detail_id: int) -> bool:
        """Delete a timesheet detail"""
        db_detail = TimesheetService.get_timesheet_detail(db, detail_id)
        if not db_detail:
            raise HTTPException(status_code=404, detail="Timesheet detail not found")
        
        timesheet_id = db_detail.TimesheetID
        db.delete(db_detail)
        db.commit()
        
        # Update timesheet total hours after deleting detail
        update_timesheet_total_hours(db, timesheet_id)
        
        return True
    
    @staticmethod
    def submit_timesheet(db: Session, timesheet_id: int) -> models.Timesheet:
        """Submit a timesheet for approval"""
        db_timesheet = TimesheetService.get_timesheet(db, timesheet_id)
        if not db_timesheet:
            raise HTTPException(status_code=404, detail="Timesheet not found")
        
        # Check for leave conflicts before submitting timesheet
        check_leave_conflicts_for_timesheet_submission(db, timesheet_id)
        
        # Validate that timesheet can be submitted
        if not validate_timesheet_submission(db, timesheet_id):
            raise HTTPException(
                status_code=400,
                detail="Timesheet cannot be submitted. Please ensure all weekdays have entries."
            )
        
        # Check if timesheet is already submitted or approved
        if db_timesheet.StatusCode in ["Submitted", "Approved", "Rejected"]:
            raise HTTPException(
                status_code=400,
                detail=f"Timesheet is already {db_timesheet.StatusCode.lower()}"
            )
        
        db_timesheet.StatusCode = "Submitted"
        db_timesheet.SubmittedAt = datetime.now()
        db.commit()
        db.refresh(db_timesheet)
        return db_timesheet
    
    @staticmethod
    def approve_timesheet(db: Session, timesheet_id: int, approval: schemas.TimesheetApprovalRequest) -> models.Timesheet:
        """Approve or reject a timesheet"""
        db_timesheet = TimesheetService.get_timesheet(db, timesheet_id)
        if not db_timesheet:
            raise HTTPException(status_code=404, detail="Timesheet not found")
        
        # Check for leave conflicts before approval
        check_leave_conflicts_for_timesheet_approval(db, timesheet_id)
        
        # Validate that timesheet is in submitted state
        if db_timesheet.StatusCode != "Submitted":
            raise HTTPException(
                status_code=400,
                detail=f"Timesheet cannot be approved. Current status: {db_timesheet.StatusCode}"
            )
        
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
        """
        Get batched timesheet data for an employee including current week and history.
        This method optimizes multiple database queries into a single response.
        """
        from datetime import date as current_date
        from api.employee import models as employee_models
        
        # Calculate week dates if not provided
        if not week_start_date:
            today = current_date.today()
            week_start_date = get_week_start_date(today)
        
        week_end_date = week_start_date + timedelta(days=6)
        
        # Get employee profile (basic info only)
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
        
        # Get current week timesheet
        current_week = db.query(models.Timesheet).filter(
            models.Timesheet.EmployeeID == employee_id,
            models.Timesheet.WeekStartDate == week_start_date
        ).first()
        
        print(f"DEBUG: Looking for timesheet for employee {employee_id}, week {week_start_date}")
        print(f"DEBUG: Found current week timesheet: {current_week.TimesheetID if current_week else 'None'}")
        
        # If no current week timesheet, create one
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
            print(f"DEBUG: Created new timesheet: {current_week.TimesheetID}")
        
        # Get timesheet details for current week
        details = db.query(models.TimesheetDetail).filter(
            models.TimesheetDetail.TimesheetID == current_week.TimesheetID
        ).order_by(models.TimesheetDetail.WorkDate).all()
        
        print(f"DEBUG: Found {len(details)} timesheet details for timesheet {current_week.TimesheetID}")
        for detail in details:
            print(f"DEBUG: Detail - Date: {detail.WorkDate}, Hours: {detail.HoursWorked}, Task: {detail.TaskDescription}")
        
        # Attach details to current week
        current_week.details = details
        
        # Get timesheet history if requested
        timesheet_history = []
        if include_history:
            history_query = db.query(models.Timesheet).filter(
                models.Timesheet.EmployeeID == employee_id,
                models.Timesheet.WeekStartDate < week_start_date
            ).order_by(models.Timesheet.WeekStartDate.desc()).limit(history_limit)
            
            timesheet_history = history_query.all()
            
            # Load details for each historical timesheet
            for hist_timesheet in timesheet_history:
                hist_details = db.query(models.TimesheetDetail).filter(
                    models.TimesheetDetail.TimesheetID == hist_timesheet.TimesheetID
                ).order_by(models.TimesheetDetail.WorkDate).all()
                hist_timesheet.details = hist_details
        
        return {
            "employee": employee_profile,
            "current_week": current_week,
            "history": timesheet_history,
            "week_start_date": week_start_date,
            "week_end_date": week_end_date
        }

    @staticmethod
    def get_manager_subordinates_timesheets(
        db: Session,
        manager_id: int,
        skip: int = 0,
        limit: int = 100,
        status_code: Optional[str] = None
    ) -> dict:
        """Get timesheets from subordinates that need approval"""
        from api.employee import models as employee_models
        
        # Get all subordinates of the manager
        subordinates = db.query(employee_models.Employee).filter(
            employee_models.Employee.ManagerID == manager_id,
            employee_models.Employee.IsActive == True
        ).all()
        
        if not subordinates:
            return {
                "items": [],
                "total_count": 0,
                "page": 1,
                "size": limit,
                "has_next": False,
                "has_previous": False
            }
        
        # Get subordinate employee IDs
        subordinate_ids = [sub.EmployeeID for sub in subordinates]
        
        # Build query for timesheets from subordinates
        query = db.query(models.Timesheet).filter(
            models.Timesheet.EmployeeID.in_(subordinate_ids)
        )
        
        # Filter by status if provided
        if status_code:
            query = query.filter(models.Timesheet.StatusCode == status_code)
        else:
            # Default to showing submitted timesheets that need approval
            query = query.filter(models.Timesheet.StatusCode == "Submitted")
        
        # Get total count before ordering
        total_count = query.count()
        
        # Order by submission date (most recent first)
        query = query.order_by(models.Timesheet.SubmittedAt.desc())
        
        # Apply pagination
        items = query.offset(skip).limit(limit).all()
        
        # Calculate pagination info
        page = (skip // limit) + 1 if limit > 0 else 1
        has_next = (skip + limit) < total_count
        has_previous = skip > 0
        
        result = {
            "items": items,
            "total_count": total_count,
            "page": page,
            "size": limit,
            "has_next": has_next,
            "has_previous": has_previous
        }
        
        print(f"DEBUG: paginate_query result: {result}")
        print(f"DEBUG: result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
        # Load employee details for each timesheet
        timesheets_with_employees = []
        for timesheet in result["items"]:
            employee = db.query(employee_models.Employee).filter(
                employee_models.Employee.EmployeeID == timesheet.EmployeeID
            ).first()
            
            # Convert timesheet to dict and add employee info
            timesheet_dict = {
                "TimesheetID": timesheet.TimesheetID,
                "EmployeeID": timesheet.EmployeeID,
                "WeekStartDate": timesheet.WeekStartDate,
                "WeekEndDate": timesheet.WeekEndDate,
                "TotalHours": float(timesheet.TotalHours) if timesheet.TotalHours else 0.0,
                "StatusCode": timesheet.StatusCode,
                "SubmittedAt": timesheet.SubmittedAt,
                "ApprovedByID": timesheet.ApprovedByID,
                "ApprovedAt": timesheet.ApprovedAt,
                "Comments": timesheet.Comments,
                "CreatedAt": timesheet.CreatedAt,
                "UpdatedAt": timesheet.UpdatedAt,
                "employee": None
            }
            
            if employee:
                # Get designation name safely
                designation_name = None
                if hasattr(employee, 'designation') and employee.designation:
                    designation_name = employee.designation.DesignationName
                
                timesheet_dict["employee"] = {
                    "EmployeeID": employee.EmployeeID,
                    "FirstName": employee.FirstName,
                    "MiddleName": employee.MiddleName,
                    "LastName": employee.LastName,
                    "CompanyEmail": employee.CompanyEmail,
                    "DesignationName": designation_name
                }
            
            timesheets_with_employees.append(timesheet_dict)
        
        result["items"] = timesheets_with_employees
        
        print(f"DEBUG: Final result: {result}")
        return result 

    @staticmethod
    def check_leave_timesheet_conflicts(
        db: Session,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> dict:
        """
        Check for timesheet conflicts when submitting leave applications.
        Returns conflict information if there are submitted or approved timesheets
        for the leave period.
        """
        from datetime import timedelta
        
        # Get all timesheets for the employee that overlap with the leave period
        # and are in submitted or approved status
        conflicting_timesheets = db.query(models.Timesheet).filter(
            models.Timesheet.EmployeeID == employee_id,
            models.Timesheet.StatusCode.in_(["Submitted", "Approved"]),
            # Check for overlap: timesheet week overlaps with leave period
            models.Timesheet.WeekStartDate <= end_date,
            models.Timesheet.WeekEndDate >= start_date
        ).all()
        
        if not conflicting_timesheets:
            return {
                "has_conflict": False,
                "message": None,
                "conflicting_dates": []
            }
        
        # Get specific dates that have timesheet entries
        conflicting_dates = []
        for timesheet in conflicting_timesheets:
            # Get timesheet details for the specific dates
            details = db.query(models.TimesheetDetail).filter(
                models.TimesheetDetail.TimesheetID == timesheet.TimesheetID,
                models.TimesheetDetail.WorkDate >= start_date,
                models.TimesheetDetail.WorkDate <= end_date
            ).all()
            
            for detail in details:
                conflicting_dates.append(detail.WorkDate.strftime("%Y-%m-%d"))
        
        if conflicting_dates:
            return {
                "has_conflict": True,
                "message": f"Timesheet conflicts detected for the selected leave period. You have submitted or approved timesheets for: {', '.join(conflicting_dates)}. Please contact your manager to resolve this conflict.",
                "conflicting_dates": conflicting_dates
            }
        
        return {
            "has_conflict": False,
            "message": None,
            "conflicting_dates": []
        } 