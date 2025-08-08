from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from . import models, schemas
from fastapi import HTTPException
from datetime import datetime, timedelta, date
from decimal import Decimal
import calendar
from core.timesheet_utils import check_timesheet_conflicts_for_leave_application
from core.pagination import paginate_query

def is_sick_leave_type(leave_type_name: str) -> bool:
    """Check if the leave type is sick leave"""
    return 'sick' in leave_type_name.lower()

def calculate_business_days(start_date: date, end_date: date, exclude_holidays: bool = True) -> Decimal:
    """
    Calculate the number of business days between two dates.
    
    Args:
        start_date: Start date of the leave period
        end_date: End date of the leave period
        exclude_holidays: Whether to exclude holidays (default: True)
    
    Returns:
        Number of business days as Decimal
    """
    if start_date > end_date:
        raise ValueError("Start date cannot be after end date")
    
    # List of common holidays (you can expand this or load from database)
    holidays = [
        # New Year's Day
        date(start_date.year, 1, 1),
        # Independence Day (US) - adjust for your country
        date(start_date.year, 7, 4),
        # Christmas Day
        date(start_date.year, 12, 25),
        # Add more holidays as needed
    ]
    
    # If end date is in different year, add holidays for that year too
    if end_date.year != start_date.year:
        holidays.extend([
            date(end_date.year, 1, 1),
            date(end_date.year, 7, 4),
            date(end_date.year, 12, 25),
        ])
    
    business_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # Check if it's a weekday (Monday = 0, Sunday = 6)
        if current_date.weekday() < 5:  # Monday to Friday
            # Check if it's not a holiday
            if not exclude_holidays or current_date not in holidays:
                business_days += 1
        current_date += timedelta(days=1)
    
    return Decimal(str(business_days))

def calculate_calendar_days(start_date: date, end_date: date) -> Decimal:
    """
    Calculate the number of calendar days between two dates (inclusive).
    
    Args:
        start_date: Start date of the leave period
        end_date: End date of the leave period
    
    Returns:
        Number of calendar days as Decimal
    """
    if start_date > end_date:
        raise ValueError("Start date cannot be after end date")
    
    delta = end_date - start_date
    return Decimal(str(delta.days + 1))  # +1 to include both start and end dates

class LeaveService:
    @staticmethod
    def get_leave_applications(
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        employee_id: Optional[int] = None, 
        status_code: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type_id: Optional[int] = None
    ):
        """Get leave applications with optional filtering and pagination"""
        query = db.query(models.LeaveApplication)
        
        # Apply filters
        if employee_id is not None:
            query = query.filter(models.LeaveApplication.EmployeeID == employee_id)
        
        if status_code is not None:
            query = query.filter(models.LeaveApplication.StatusCode == status_code)
        
        if leave_type_id is not None:
            query = query.filter(models.LeaveApplication.LeaveTypeID == leave_type_id)
        
        # Date range filters
        if start_date is not None:
            query = query.filter(models.LeaveApplication.StartDate >= start_date)
        
        if end_date is not None:
            query = query.filter(models.LeaveApplication.EndDate <= end_date)
        
        # Use pagination utility with StartDate ordering
        return paginate_query(
            query=query,
            skip=skip,
            limit=limit,
            order_by_column=models.LeaveApplication.StartDate,
            order_desc=True
        )

    @staticmethod
    def get_leave_application(db: Session, application_id: int):
        """Get a specific leave application by ID"""
        return db.query(models.LeaveApplication).filter(models.LeaveApplication.LeaveApplicationID == application_id).first()

    @staticmethod
    def create_leave_application(db: Session, application: schemas.LeaveApplicationCreate):
        """Create a new leave application"""
        # Check for timesheet conflicts before creating leave application
        check_timesheet_conflicts_for_leave_application(db, application.EmployeeID, application.StartDate, application.EndDate)

        # Prevent overlapping leave applications for the same employee
        overlapping = db.query(models.LeaveApplication).filter(
            models.LeaveApplication.EmployeeID == application.EmployeeID,
            models.LeaveApplication.StatusCode.in_(["Submitted", "Draft", "Manager-Approved", "HR-Approved"]),
            models.LeaveApplication.StartDate <= application.EndDate,
            models.LeaveApplication.EndDate >= application.StartDate
        ).first()
        if overlapping:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Employee already has a leave application (ID: {overlapping.LeaveApplicationID}) "
                    f"from {overlapping.StartDate} to {overlapping.EndDate} that overlaps with the requested dates."
                )
            )
        
        # Business logic: Sick leaves cannot be submitted for future dates
        leave_type = db.query(models.LeaveType).filter(models.LeaveType.LeaveTypeID == application.LeaveTypeID).first()
        if leave_type and is_sick_leave_type(leave_type.LeaveTypeName):
            today = date.today()
            if application.StartDate > today or application.EndDate > today:
                raise HTTPException(
                    status_code=400, 
                    detail="Sick leave cannot be submitted for future dates. Please select past or current dates only."
                )
        
        # Calculate NumberOfDays if not provided
        if application.NumberOfDays is None:
            try:
                # Use the calculation type specified in the request
                if application.calculation_type == "business":
                    application.NumberOfDays = calculate_business_days(
                        application.StartDate, 
                        application.EndDate, 
                        exclude_holidays=application.exclude_holidays
                    )
                elif application.calculation_type == "calendar":
                    application.NumberOfDays = calculate_calendar_days(
                        application.StartDate, 
                        application.EndDate
                    )
                else:
                    raise HTTPException(status_code=400, detail="calculation_type must be 'business' or 'calendar'")
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        db_application = models.LeaveApplication(
            EmployeeID=application.EmployeeID,
            LeaveTypeID=application.LeaveTypeID,
            StartDate=application.StartDate,
            EndDate=application.EndDate,
            NumberOfDays=application.NumberOfDays,
            Reason=application.Reason,
            StatusCode=application.StatusCode,
            SubmittedAt=datetime.utcnow()
        )
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
        return db_application

    @staticmethod
    def update_leave_application(db: Session, application_id: int, application_update: schemas.LeaveApplicationUpdate):
        """Update an existing leave application"""
        db_application = db.query(models.LeaveApplication).filter(models.LeaveApplication.LeaveApplicationID == application_id).first()
        if not db_application:
            raise HTTPException(status_code=404, detail="Leave application not found")
        
        # If dates are being updated, check for timesheet conflicts
        if hasattr(application_update, 'StartDate') and hasattr(application_update, 'EndDate'):
            if application_update.StartDate and application_update.EndDate:
                check_timesheet_conflicts_for_leave_application(db, db_application.EmployeeID, application_update.StartDate, application_update.EndDate)
        
        # Business logic: Sick leaves cannot be submitted for future dates
        if hasattr(application_update, 'StartDate') and hasattr(application_update, 'EndDate') and application_update.StartDate and application_update.EndDate:
            leave_type = db.query(models.LeaveType).filter(models.LeaveType.LeaveTypeID == db_application.LeaveTypeID).first()
            if leave_type and is_sick_leave_type(leave_type.LeaveTypeName):
                today = date.today()
                if application_update.StartDate > today or application_update.EndDate > today:
                    raise HTTPException(
                        status_code=400, 
                        detail="Sick leave cannot be submitted for future dates. Please select past or current dates only."
                    )
        
        update_data = application_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_application, field, value)
        
        db.commit()
        db.refresh(db_application)
        return db_application

    @staticmethod
    def delete_leave_application(db: Session, application_id: int):
        """Delete a leave application"""
        db_application = db.query(models.LeaveApplication).filter(models.LeaveApplication.LeaveApplicationID == application_id).first()
        if not db_application:
            raise HTTPException(status_code=404, detail="Leave application not found")
        
        db.delete(db_application)
        db.commit()

    @staticmethod
    def cancel_leave_application(db: Session, application_id: int):
        """Cancel a leave application (only if it's in Draft or Submitted status)"""
        db_application = db.query(models.LeaveApplication).filter(models.LeaveApplication.LeaveApplicationID == application_id).first()
        if not db_application:
            raise HTTPException(status_code=404, detail="Leave application not found")
        
        # Only allow cancellation if application is in Draft or Submitted status
        if db_application.StatusCode not in ["Draft", "Submitted"]:
            raise HTTPException(
                status_code=400, 
                detail="Cannot cancel leave application. Only Draft or Submitted applications can be cancelled."
            )
        
        # Update status to Cancelled
        db_application.StatusCode = "Cancelled"
        db_application.UpdatedAt = datetime.utcnow()
        
        db.commit()
        db.refresh(db_application)
        return db_application

    @staticmethod
    def get_leave_types(db: Session):
        """Get list of leave types"""
        return db.query(models.LeaveType).filter(models.LeaveType.IsActive == True).all()

    @staticmethod
    def get_leave_type(db: Session, type_id: int):
        """Get a specific leave type by ID"""
        return db.query(models.LeaveType).filter(models.LeaveType.LeaveTypeID == type_id).first()

    @staticmethod
    def create_leave_type(db: Session, leave_type: schemas.LeaveTypeCreate):
        """Create a new leave type"""
        db_leave_type = models.LeaveType(
            LeaveTypeName=leave_type.LeaveTypeName,
            LeaveCode=leave_type.LeaveCode,
            DefaultDaysPerYear=leave_type.DefaultDaysPerYear
        )
        db.add(db_leave_type)
        db.commit()
        db.refresh(db_leave_type)
        return db_leave_type

    @staticmethod
    def update_leave_type(db: Session, type_id: int, leave_type_update: schemas.LeaveTypeUpdate):
        """Update an existing leave type"""
        db_leave_type = db.query(models.LeaveType).filter(models.LeaveType.LeaveTypeID == type_id).first()
        if not db_leave_type:
            raise HTTPException(status_code=404, detail="Leave type not found")
        
        update_data = leave_type_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_leave_type, field, value)
        
        db.commit()
        db.refresh(db_leave_type)
        return db_leave_type

    @staticmethod
    def delete_leave_type(db: Session, type_id: int):
        """Delete a leave type"""
        db_leave_type = db.query(models.LeaveType).filter(models.LeaveType.LeaveTypeID == type_id).first()
        if not db_leave_type:
            raise HTTPException(status_code=404, detail="Leave type not found")
        
        db.delete(db_leave_type)
        db.commit()

    @staticmethod
    def get_leave_balances(db: Session, employee_id: Optional[int] = None, year: Optional[int] = None):
        """Get leave balances with optional filtering"""
        query = db.query(models.LeaveBalance)
        
        if employee_id is not None:
            query = query.filter(models.LeaveBalance.EmployeeID == employee_id)
        
        if year is not None:
            query = query.filter(models.LeaveBalance.Year == year)
        
        return query.all()

    @staticmethod
    def get_leave_balances_by_type_codes(db: Session, employee_id: Optional[int] = None, year: Optional[int] = None, leave_codes: Optional[List[str]] = None):
        """Get leave balances with optional filtering by leave type codes"""
        query = db.query(models.LeaveBalance).join(models.LeaveType)
        
        if employee_id is not None:
            query = query.filter(models.LeaveBalance.EmployeeID == employee_id)
        
        if year is not None:
            query = query.filter(models.LeaveBalance.Year == year)
        
        if leave_codes is not None:
            query = query.filter(models.LeaveType.LeaveCode.in_(leave_codes))
        
        return query.all()

    @staticmethod
    def get_leave_balance(db: Session, balance_id: int):
        """Get a specific leave balance by ID"""
        return db.query(models.LeaveBalance).filter(models.LeaveBalance.BalanceID == balance_id).first()

    @staticmethod
    def create_leave_balance(db: Session, balance: schemas.LeaveBalanceCreate):
        """Create a new leave balance"""
        db_balance = models.LeaveBalance(
            EmployeeID=balance.EmployeeID,
            LeaveTypeID=balance.LeaveTypeID,
            Year=balance.Year,
            EntitledDays=balance.EntitledDays,
            UsedDays=balance.UsedDays
        )
        db.add(db_balance)
        db.commit()
        db.refresh(db_balance)
        return db_balance

    @staticmethod
    def update_leave_balance(db: Session, balance_id: int, balance_update: schemas.LeaveBalanceUpdate):
        """Update an existing leave balance"""
        db_balance = db.query(models.LeaveBalance).filter(models.LeaveBalance.BalanceID == balance_id).first()
        if not db_balance:
            raise HTTPException(status_code=404, detail="Leave balance not found")
        
        update_data = balance_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_balance, field, value)
        
        db.commit()
        db.refresh(db_balance)
        return db_balance

    @staticmethod
    def delete_leave_balance(db: Session, balance_id: int):
        """Delete a leave balance"""
        db_balance = db.query(models.LeaveBalance).filter(models.LeaveBalance.BalanceID == balance_id).first()
        if not db_balance:
            raise HTTPException(status_code=404, detail="Leave balance not found")
        
        db.delete(db_balance)
        db.commit()

    @staticmethod
    def approve_leave_application(db: Session, application_id: int, approval: schemas.LeaveApprovalRequest):
        """Approve or reject a leave application"""
        db_application = db.query(models.LeaveApplication).filter(models.LeaveApplication.LeaveApplicationID == application_id).first()
        if not db_application:
            raise HTTPException(status_code=404, detail="Leave application not found")
        
        # Update approval status based on the approval request
        if approval.is_manager_approval:
            db_application.ManagerApprovalStatus = approval.approval_status
            db_application.ManagerApprovalAt = datetime.utcnow()
            # Store manager approval comment in Comments table
            if approval.comments:
                from api.comments.models import Comment
                comment = Comment(
                    EntityType="LeaveApplication",
                    EntityID=application_id,
                    CommenterID=approval.manager_id if hasattr(approval, 'manager_id') else None,
                    CommenterRole="Manager",
                    CommentText=f"Manager Approval: {approval.approval_status} - {approval.comments}"
                )
                db.add(comment)
        else:
            db_application.HRApprovalStatus = approval.approval_status
            db_application.HRApprovalAt = datetime.utcnow()
            # Store HR approval comment in Comments table
            if approval.comments:
                from api.comments.models import Comment
                comment = Comment(
                    EntityType="LeaveApplication",
                    EntityID=application_id,
                    CommenterID=approval.hr_approver_id if hasattr(approval, 'hr_approver_id') else None,
                    CommenterRole="HR",
                    CommentText=f"HR Approval: {approval.approval_status} - {approval.comments}"
                )
                db.add(comment)
        
        db.commit()
        db.refresh(db_application)
        return db_application

    @staticmethod
    def manager_approve_leave_application(db: Session, application_id: int, approval: schemas.ManagerApprovalRequest):
        """Manager approval for leave application"""
        db_application = db.query(models.LeaveApplication).filter(models.LeaveApplication.LeaveApplicationID == application_id).first()
        if not db_application:
            raise HTTPException(status_code=404, detail="Leave application not found")
        
        # Check if application is in a state that can be approved by manager
        if db_application.StatusCode not in ["Submitted", "Draft"]:
            raise HTTPException(status_code=400, detail="Application is not in a state that can be approved by manager")
        
        # Validate approval status
        if approval.approval_status not in ["Approved", "Rejected"]:
            raise HTTPException(status_code=400, detail="Approval status must be 'Approved' or 'Rejected'")
        
        # Validate that manager_id exists in Employees table
        from api.employee.models import Employee
        manager = db.query(Employee).filter(Employee.EmployeeID == approval.manager_id).first()
        if not manager:
            raise HTTPException(status_code=400, detail=f"Manager with ID {approval.manager_id} does not exist")
        
        # Update manager approval details
        db_application.ManagerID = approval.manager_id
        db_application.ManagerApprovalStatus = approval.approval_status
        db_application.ManagerApprovalAt = datetime.utcnow()
        
        # Store manager approval comment in Comments table
        if approval.comments:
            from api.comments.models import Comment
            comment = Comment(
                EntityType="LeaveApplication",
                EntityID=application_id,
                CommenterID=approval.manager_id,
                CommenterRole="Manager",
                CommentText=f"Manager Approval: {approval.approval_status} - {approval.comments}"
            )
            db.add(comment)
        
        # Update overall status based on manager decision
        if approval.approval_status == "Approved":
            db_application.StatusCode = "Manager-Approved"
        else:  # Rejected
            db_application.StatusCode = "Rejected"
        
        db.commit()
        db.refresh(db_application)
        return db_application

    @staticmethod
    def hr_approve_leave_application(db: Session, application_id: int, approval: schemas.HRApprovalRequest):
        """HR approval for leave application (only after manager approval)"""
        db_application = db.query(models.LeaveApplication).filter(models.LeaveApplication.LeaveApplicationID == application_id).first()
        if not db_application:
            raise HTTPException(status_code=404, detail="Leave application not found")
        
        # Check if manager has already approved
        if db_application.StatusCode != "Manager-Approved":
            raise HTTPException(status_code=400, detail="HR approval can only be done after manager approval")
        
        # Validate approval status
        if approval.approval_status not in ["Approved", "Rejected"]:
            raise HTTPException(status_code=400, detail="Approval status must be 'Approved' or 'Rejected'")
        
        # Validate that hr_approver_id exists in Employees table
        from api.employee.models import Employee
        hr_approver = db.query(Employee).filter(Employee.EmployeeID == approval.hr_approver_id).first()
        if not hr_approver:
            raise HTTPException(status_code=400, detail=f"HR approver with ID {approval.hr_approver_id} does not exist")
        
        # Update HR approval details
        db_application.HRApproverID = approval.hr_approver_id
        db_application.HRApprovalStatus = approval.approval_status
        db_application.HRApprovalAt = datetime.utcnow()
        
        # Store HR approval comment in Comments table
        if approval.comments:
            from api.comments.models import Comment
            comment = Comment(
                EntityType="LeaveApplication",
                EntityID=application_id,
                CommenterID=approval.hr_approver_id,
                CommenterRole="HR",
                CommentText=f"HR Approval: {approval.approval_status} - {approval.comments}"
            )
            db.add(comment)
        
        # Update overall status based on HR decision
        if approval.approval_status == "Approved":
            db_application.StatusCode = "HR-Approved"
            # Update leave balance when HR approves
            LeaveService._update_leave_balance_on_approval(db, db_application)
        else:  # Rejected
            db_application.StatusCode = "Rejected"
        
        db.commit()
        db.refresh(db_application)
        return db_application

    @staticmethod
    def _update_leave_balance_on_approval(db: Session, application):
        """Update leave balance when an application is approved by HR"""
        # Find the leave balance for this employee, leave type, and year
        balance = db.query(models.LeaveBalance).filter(
            models.LeaveBalance.EmployeeID == application.EmployeeID,
            models.LeaveBalance.LeaveTypeID == application.LeaveTypeID,
            models.LeaveBalance.Year == application.StartDate.year
        ).first()
        
        if balance:
            # Update used days
            balance.UsedDays += application.NumberOfDays
            balance.UpdatedAt = datetime.utcnow()
        else:
            # Create a new balance record if it doesn't exist
            # This might happen for new employees or new leave types
            new_balance = models.LeaveBalance(
                EmployeeID=application.EmployeeID,
                LeaveTypeID=application.LeaveTypeID,
                Year=application.StartDate.year,
                EntitledDays=Decimal('0'),  # Default to 0, should be set by HR
                UsedDays=application.NumberOfDays
            )
            db.add(new_balance)

    @staticmethod
    def check_leave_conflicts(db: Session, start_date: date, end_date: date, manager_id: Optional[int] = None):
        """Check for leave conflicts among employees under a manager"""
        from api.employee.models import Employee
        from api.leave.models import LeaveType
        
        # If manager_id not supplied return no conflict
        if manager_id is None:
            return {
                "has_conflict": False,
                "message": "Manager ID not provided"
            }
        
        # Get all employees under this manager
        subordinates = db.query(Employee).filter(
            Employee.ManagerID == manager_id,
            Employee.IsActive == True
        ).all()
        
        if not subordinates:
            return {
                "has_conflict": False,
                "message": "No subordinates found for this manager"
            }
        
        subordinate_ids = [emp.EmployeeID for emp in subordinates]
        
        # Find overlapping leave applications
        conflicting_applications = db.query(models.LeaveApplication).filter(
            models.LeaveApplication.EmployeeID.in_(subordinate_ids),
            models.LeaveApplication.StatusCode.in_(["Submitted", "Manager-Approved", "HR-Approved"]),
            # Check for date overlap
            models.LeaveApplication.StartDate <= end_date,
            models.LeaveApplication.EndDate >= start_date
        ).all()
        
        if not conflicting_applications:
            return {
                "has_conflict": False,
                "message": "No conflicts found"
            }
        
        # Get leave types for better information
        leave_types = {lt.LeaveTypeID: lt.LeaveTypeName for lt in db.query(LeaveType).all()}
        
        conflicting_employees = []
        for app in conflicting_applications:
            # Skip the current application being checked
            if app.StartDate == start_date and app.EndDate == end_date:
                continue
                
            employee = db.query(Employee).filter(Employee.EmployeeID == app.EmployeeID).first()
            if employee:
                conflicting_employees.append({
                    "employee_id": app.EmployeeID,
                    "employee_name": f"{employee.FirstName} {employee.LastName}",
                    "leave_dates": [app.StartDate.strftime("%Y-%m-%d"), app.EndDate.strftime("%Y-%m-%d")],
                    "leave_type": leave_types.get(app.LeaveTypeID, "Unknown")
                })
        
        # Check if we have 2 or more conflicting employees
        unique_employees = len(set(emp["employee_id"] for emp in conflicting_employees))
        
        return {
            "has_conflict": unique_employees >= 2,
            "conflicting_employees": conflicting_employees if unique_employees >= 2 else [],
            "message": f"Found {unique_employees} employees with overlapping leave dates" if unique_employees >= 2 else "No significant conflicts"
        } 