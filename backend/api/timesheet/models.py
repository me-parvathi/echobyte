from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, DECIMAL, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
from api.employee.models import Employee

class TimesheetStatus(Base):
    __tablename__ = "TimesheetStatuses"
    
    TimesheetStatusCode = Column(String(20), primary_key=True)
    TimesheetStatusName = Column(String(50), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())

class Timesheet(Base):
    __tablename__ = "Timesheets"
    
    TimesheetID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    WeekStartDate = Column(Date, nullable=False)
    WeekEndDate = Column(Date, nullable=False)
    TotalHours = Column(DECIMAL(5,2), nullable=False, default=0)
    StatusCode = Column(String(20), ForeignKey("TimesheetStatuses.TimesheetStatusCode"), nullable=False)
    SubmittedAt = Column(DateTime)
    ApprovedByID = Column(Integer, ForeignKey("Employees.EmployeeID"))
    ApprovedAt = Column(DateTime)
    Comments = Column(Text)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[EmployeeID])
    status = relationship("TimesheetStatus")
    approved_by = relationship("Employee", foreign_keys=[ApprovedByID])
    details = relationship("TimesheetDetail", back_populates="timesheet", cascade="all, delete-orphan")
    
    # Check constraints
    __table_args__ = (
        CheckConstraint('WeekEndDate >= WeekStartDate', name='CHK_Timesheets_Dates'),
    )

class TimesheetDetail(Base):
    __tablename__ = "TimesheetDetails"
    
    DetailID = Column(Integer, primary_key=True, autoincrement=True)
    TimesheetID = Column(Integer, ForeignKey("Timesheets.TimesheetID"), nullable=False)
    WorkDate = Column(Date, nullable=False)
    ProjectCode = Column(String(50))
    TaskDescription = Column(String(200))
    HoursWorked = Column(DECIMAL(4,2), nullable=False)
    IsOvertime = Column(Boolean, nullable=False, default=False)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    
    # Relationships
    timesheet = relationship("Timesheet", back_populates="details")
    
    # Check constraints
    __table_args__ = (
        CheckConstraint('HoursWorked BETWEEN 0 AND 24', name='CHK_TimesheetDetails_Hours'),
    ) 