from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, DECIMAL, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

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
        CheckConstraint('HoursWorked BETWEEN 0 AND 24', name='CHK_TimesheetDetails_Hours'),
    )

class EmployeeOvertimePTO(Base):
    __tablename__ = "EmployeeOvertimePTO"

    OvertimePTOID = Column(Integer, primary_key=True, autoincrement=True)
    OvertimeHours = Column(DECIMAL(6,2), nullable=False, default=0)
    PTOGranted = Column(Integer, nullable=False, default=0)
    LastCalculated = Column(DateTime, nullable=False, server_default=func.getutcdate())
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate(), onupdate=func.getutcdate())

    employee = relationship("Employee", foreign_keys=[EmployeeID])