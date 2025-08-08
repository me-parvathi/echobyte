"""
Test file for timesheet and leave conflict checking logic
"""

import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.timesheet import models as timesheet_models
from api.leave import models as leave_models
from api.employee.models import Employee
from api.timesheet.service import TimesheetService
from api.leave.service import LeaveService
from core.timesheet_utils import (
    check_leave_conflicts_for_timesheet_upload,
    check_timesheet_conflicts_for_leave_application,
    check_leave_conflicts_for_timesheet_submission,
    get_week_dates
)


class TestTimesheetLeaveConflicts:
    """Test class for timesheet and leave conflict checking"""
    
    def setup_method(self):
        """Setup test data"""
        self.employee_id = 1
        self.manager_id = 2
        self.hr_approver_id = 3
        
        # Test dates
        self.test_week_start = date(2024, 1, 15)  # Monday
        self.test_week_end = date(2024, 1, 21)    # Sunday
        self.test_work_date = date(2024, 1, 16)   # Tuesday
        
        # Leave dates that overlap with timesheet week
        self.leave_start = date(2024, 1, 17)  # Wednesday
        self.leave_end = date(2024, 1, 19)    # Friday
    
    def create_test_employee(self, db: Session, employee_id: int, name: str = "Test Employee"):
        """Create a test employee"""
        employee = Employee(
            EmployeeID=employee_id,
            FirstName=name,
            LastName="Test",
            Email=f"{name.lower()}@test.com",
            IsActive=True
        )
        db.add(employee)
        db.commit()
        return employee
    
    def create_test_timesheet(self, db: Session, status: str = "Draft"):
        """Create a test timesheet"""
        timesheet = timesheet_models.Timesheet(
            EmployeeID=self.employee_id,
            WeekStartDate=self.test_week_start,
            WeekEndDate=self.test_week_end,
            StatusCode=status,
            TotalHours=40.0
        )
        db.add(timesheet)
        db.commit()
        db.refresh(timesheet)
        return timesheet
    
    def create_test_leave_application(self, db: Session, status: str = "Submitted"):
        """Create a test leave application"""
        leave = leave_models.LeaveApplication(
            EmployeeID=self.employee_id,
            LeaveTypeID=1,  # Assuming leave type 1 exists
            StartDate=self.leave_start,
            EndDate=self.leave_end,
            NumberOfDays=3.0,
            Reason="Test leave",
            StatusCode=status
        )
        db.add(leave)
        db.commit()
        db.refresh(leave)
        return leave
    
    def test_check_leave_conflicts_for_timesheet_upload_no_conflicts(self, db: Session):
        """Test that timesheet upload is allowed when no leave conflicts exist"""
        # Create test employee
        self.create_test_employee(db, self.employee_id)
        
        # Should not raise any exception
        result = check_leave_conflicts_for_timesheet_upload(db, self.employee_id, self.test_work_date)
        assert result is False
    
    def test_check_leave_conflicts_for_timesheet_upload_with_conflicts(self, db: Session):
        """Test that timesheet upload is blocked when leave conflicts exist"""
        # Create test employee and leave application
        self.create_test_employee(db, self.employee_id)
        self.create_test_leave_application(db, "Submitted")
        
        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            check_leave_conflicts_for_timesheet_upload(db, self.employee_id, self.test_work_date)
        
        assert exc_info.value.status_code == 400
        assert "Cannot upload timesheet data" in str(exc_info.value.detail)
        assert "conflicting leave applications" in str(exc_info.value.detail)
    
    def test_check_leave_conflicts_for_timesheet_upload_draft_leave_allowed(self, db: Session):
        """Test that timesheet upload is allowed when leave is in draft status"""
        # Create test employee and leave application in draft status
        self.create_test_employee(db, self.employee_id)
        self.create_test_leave_application(db, "Draft")
        
        # Should not raise any exception
        result = check_leave_conflicts_for_timesheet_upload(db, self.employee_id, self.test_work_date)
        assert result is False
    
    def test_check_timesheet_conflicts_for_leave_application_no_conflicts(self, db: Session):
        """Test that leave application is allowed when no timesheet conflicts exist"""
        # Create test employee
        self.create_test_employee(db, self.employee_id)
        
        # Should not raise any exception
        result = check_timesheet_conflicts_for_leave_application(db, self.employee_id, self.leave_start, self.leave_end)
        assert result is False
    
    def test_check_timesheet_conflicts_for_leave_application_with_conflicts(self, db: Session):
        """Test that leave application is blocked when timesheet conflicts exist"""
        # Create test employee and timesheet in submitted status
        self.create_test_employee(db, self.employee_id)
        self.create_test_timesheet(db, "Submitted")
        
        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            check_timesheet_conflicts_for_leave_application(db, self.employee_id, self.leave_start, self.leave_end)
        
        assert exc_info.value.status_code == 400
        assert "Cannot apply for leave" in str(exc_info.value.detail)
        assert "conflicting timesheets" in str(exc_info.value.detail)
    
    def test_check_timesheet_conflicts_for_leave_application_draft_timesheet_allowed(self, db: Session):
        """Test that leave application is allowed when timesheet is in draft status"""
        # Create test employee and timesheet in draft status
        self.create_test_employee(db, self.employee_id)
        self.create_test_timesheet(db, "Draft")
        
        # Should not raise any exception
        result = check_timesheet_conflicts_for_leave_application(db, self.employee_id, self.leave_start, self.leave_end)
        assert result is False
    
    def test_check_leave_conflicts_for_timesheet_submission_no_conflicts(self, db: Session):
        """Test that timesheet submission is allowed when no leave conflicts exist"""
        # Create test employee and timesheet
        self.create_test_employee(db, self.employee_id)
        timesheet = self.create_test_timesheet(db, "Draft")
        
        # Should not raise any exception
        result = check_leave_conflicts_for_timesheet_submission(db, timesheet.TimesheetID)
        assert result is False
    
    def test_check_leave_conflicts_for_timesheet_submission_with_conflicts(self, db: Session):
        """Test that timesheet submission is blocked when leave conflicts exist"""
        # Create test employee, timesheet, and leave application
        self.create_test_employee(db, self.employee_id)
        timesheet = self.create_test_timesheet(db, "Draft")
        self.create_test_leave_application(db, "Submitted")
        
        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            check_leave_conflicts_for_timesheet_submission(db, timesheet.TimesheetID)
        
        assert exc_info.value.status_code == 400
        assert "Cannot submit timesheet" in str(exc_info.value.detail)
        assert "conflicting leave applications" in str(exc_info.value.detail)
    
    def test_timesheet_service_create_weekly_timesheet_with_leave_conflict(self, db: Session):
        """Test that weekly timesheet creation is blocked when leave conflicts exist"""
        from api.timesheet import schemas as timesheet_schemas
        
        # Create test employee and leave application
        self.create_test_employee(db, self.employee_id)
        self.create_test_leave_application(db, "Submitted")
        
        # Create weekly timesheet data
        weekly_data = timesheet_schemas.WeeklyTimesheetCreate(
            EmployeeID=self.employee_id,
            WeekStartDate=self.test_week_start,
            WeekEndDate=self.test_week_end,
            Comments="Test weekly timesheet",
            details=[
                timesheet_schemas.DailyEntryCreate(
                    EmployeeID=self.employee_id,
                    WorkDate=self.test_work_date,
                    TaskDescription="Test task",
                    HoursWorked=8.0,
                    IsOvertime=False
                )
            ]
        )
        
        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            TimesheetService.create_weekly_timesheet(db, weekly_data)
        
        assert exc_info.value.status_code == 400
        assert "Cannot upload timesheet data" in str(exc_info.value.detail)
    
    def test_timesheet_service_create_daily_entry_with_leave_conflict(self, db: Session):
        """Test that daily entry creation is blocked when leave conflicts exist"""
        from api.timesheet import schemas as timesheet_schemas
        
        # Create test employee and leave application
        self.create_test_employee(db, self.employee_id)
        self.create_test_leave_application(db, "Submitted")
        
        # Create daily entry data
        daily_data = timesheet_schemas.DailyEntryCreate(
            EmployeeID=self.employee_id,
            WorkDate=self.test_work_date,
            TaskDescription="Test task",
            HoursWorked=8.0,
            IsOvertime=False
        )
        
        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            TimesheetService.create_or_update_daily_entry(db, daily_data)
        
        assert exc_info.value.status_code == 400
        assert "Cannot upload timesheet data" in str(exc_info.value.detail)
    
    def test_timesheet_service_submit_timesheet_with_leave_conflict(self, db: Session):
        """Test that timesheet submission is blocked when leave conflicts exist"""
        # Create test employee, timesheet, and leave application
        self.create_test_employee(db, self.employee_id)
        timesheet = self.create_test_timesheet(db, "Draft")
        self.create_test_leave_application(db, "Submitted")
        
        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            TimesheetService.submit_timesheet(db, timesheet.TimesheetID)
        
        assert exc_info.value.status_code == 400
        assert "Cannot submit timesheet" in str(exc_info.value.detail)
    
    def test_leave_service_create_leave_application_with_timesheet_conflict(self, db: Session):
        """Test that leave application creation is blocked when timesheet conflicts exist"""
        from api.leave import schemas as leave_schemas
        
        # Create test employee and timesheet in submitted status
        self.create_test_employee(db, self.employee_id)
        self.create_test_timesheet(db, "Submitted")
        
        # Create leave application data
        leave_data = leave_schemas.LeaveApplicationCreate(
            EmployeeID=self.employee_id,
            LeaveTypeID=1,
            StartDate=self.leave_start,
            EndDate=self.leave_end,
            Reason="Test leave",
            StatusCode="Submitted",
            calculation_type="business"
        )
        
        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            LeaveService.create_leave_application(db, leave_data)
        
        assert exc_info.value.status_code == 400
        assert "Cannot apply for leave" in str(exc_info.value.detail)
    
    def test_overlapping_date_ranges(self, db: Session):
        """Test various overlapping date range scenarios"""
        self.create_test_employee(db, self.employee_id)
        
        # Test case 1: Leave completely within timesheet week
        leave_start = date(2024, 1, 16)  # Tuesday
        leave_end = date(2024, 1, 18)    # Thursday
        timesheet = self.create_test_timesheet(db, "Submitted")
        
        with pytest.raises(HTTPException):
            check_timesheet_conflicts_for_leave_application(db, self.employee_id, leave_start, leave_end)
        
        # Test case 2: Leave overlaps with start of timesheet week
        leave_start = date(2024, 1, 14)  # Sunday (before week)
        leave_end = date(2024, 1, 16)    # Tuesday (within week)
        
        with pytest.raises(HTTPException):
            check_timesheet_conflicts_for_leave_application(db, self.employee_id, leave_start, leave_end)
        
        # Test case 3: Leave overlaps with end of timesheet week
        leave_start = date(2024, 1, 19)  # Friday (within week)
        leave_end = date(2024, 1, 21)    # Sunday (after week)
        
        with pytest.raises(HTTPException):
            check_timesheet_conflicts_for_leave_application(db, self.employee_id, leave_start, leave_end)
    
    def test_non_overlapping_dates_allowed(self, db: Session):
        """Test that non-overlapping dates are allowed"""
        self.create_test_employee(db, self.employee_id)
        self.create_test_timesheet(db, "Submitted")
        
        # Leave completely before timesheet week
        leave_start = date(2024, 1, 8)   # Monday of previous week
        leave_end = date(2024, 1, 12)    # Friday of previous week
        
        result = check_timesheet_conflicts_for_leave_application(db, self.employee_id, leave_start, leave_end)
        assert result is False
        
        # Leave completely after timesheet week
        leave_start = date(2024, 1, 22)  # Monday of next week
        leave_end = date(2024, 1, 26)    # Friday of next week
        
        result = check_timesheet_conflicts_for_leave_application(db, self.employee_id, leave_start, leave_end)
        assert result is False


if __name__ == "__main__":
    # This can be run directly for testing
    pytest.main([__file__, "-v"]) 