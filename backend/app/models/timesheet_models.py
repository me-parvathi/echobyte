from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Timesheets(Base):
    """Timesheets table"""
    __tablename__ = "Timesheets"
    
    TimesheetID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    WeekStartDate = Column(Date, nullable=False)
    WeekEndDate = Column(Date, nullable=False)
    TotalHours = Column(Numeric(5, 2), nullable=False, default=0)
    StatusCode = Column(String(20), ForeignKey("TimesheetStatuses.TimesheetStatusCode"), nullable=False)
    SubmittedAt = Column(DateTime, nullable=True)
    ApprovedByID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=True)
    ApprovedAt = Column(DateTime, nullable=True)
    Comments = Column(String(500), nullable=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime(), onupdate=func.sysutcdatetime())
    
    # Relationships
    employee = relationship("Employees", foreign_keys=[EmployeeID], back_populates="timesheets")
    status = relationship("TimesheetStatuses")
    approved_by = relationship("Employees", foreign_keys=[ApprovedByID])
    timesheet_details = relationship("TimesheetDetails", back_populates="timesheet", cascade="all, delete-orphan")


class TimesheetDetails(Base):
    """Timesheet details table"""
    __tablename__ = "TimesheetDetails"
    
    DetailID = Column(Integer, primary_key=True, autoincrement=True)
    TimesheetID = Column(Integer, ForeignKey("Timesheets.TimesheetID"), nullable=False)
    WorkDate = Column(Date, nullable=False)
    ProjectCode = Column(String(50), nullable=True)
    TaskDescription = Column(String(200), nullable=True)
    HoursWorked = Column(Numeric(4, 2), nullable=False)
    IsOvertime = Column(Boolean, nullable=False, default=False)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    
    # Relationships
    timesheet = relationship("Timesheets", back_populates="timesheet_details") 