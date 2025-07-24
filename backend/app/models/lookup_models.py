from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base


class Genders(Base):
    """Gender lookup table"""
    __tablename__ = "Genders"
    
    GenderCode = Column(String(10), primary_key=True)
    GenderName = Column(String(50), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())


class EmploymentTypes(Base):
    """Employment type lookup table"""
    __tablename__ = "EmploymentTypes"
    
    EmploymentTypeCode = Column(String(20), primary_key=True)
    EmploymentTypeName = Column(String(50), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())


class WorkModes(Base):
    """Work mode lookup table"""
    __tablename__ = "WorkModes"
    
    WorkModeCode = Column(String(20), primary_key=True)
    WorkModeName = Column(String(50), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())


class LeaveApplicationStatuses(Base):
    """Leave application status lookup table"""
    __tablename__ = "LeaveApplicationStatuses"
    
    StatusCode = Column(String(25), primary_key=True)
    StatusName = Column(String(50), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())


class ApprovalStatuses(Base):
    """Approval status lookup table"""
    __tablename__ = "ApprovalStatuses"
    
    ApprovalStatusCode = Column(String(20), primary_key=True)
    ApprovalStatusName = Column(String(50), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())


class TimesheetStatuses(Base):
    """Timesheet status lookup table"""
    __tablename__ = "TimesheetStatuses"
    
    TimesheetStatusCode = Column(String(20), primary_key=True)
    TimesheetStatusName = Column(String(50), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())


class FeedbackTypes(Base):
    """Feedback type lookup table"""
    __tablename__ = "FeedbackTypes"
    
    FeedbackTypeCode = Column(String(20), primary_key=True)
    FeedbackTypeName = Column(String(50), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())


class Designations(Base):
    """Employee designation lookup table"""
    __tablename__ = "Designations"
    
    DesignationID = Column(Integer, primary_key=True, autoincrement=True)
    DesignationName = Column(String(100), nullable=False, unique=True)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime()) 