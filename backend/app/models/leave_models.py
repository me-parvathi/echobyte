from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class LeaveTypes(Base):
    """Leave types table"""
    __tablename__ = "LeaveTypes"
    
    LeaveTypeID = Column(Integer, primary_key=True, autoincrement=True)
    LeaveTypeName = Column(String(50), nullable=False)
    LeaveCode = Column(String(10), nullable=False, unique=True)
    DefaultDaysPerYear = Column(Numeric(4, 1), nullable=True)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    
    # Relationships
    leave_balances = relationship("LeaveBalances", back_populates="leave_type")
    leave_applications = relationship("LeaveApplications", back_populates="leave_type")


class LeaveBalances(Base):
    """Leave balances table"""
    __tablename__ = "LeaveBalances"
    
    BalanceID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    LeaveTypeID = Column(Integer, ForeignKey("LeaveTypes.LeaveTypeID"), nullable=False)
    Year = Column(Integer, nullable=False)
    EntitledDays = Column(Numeric(4, 1), nullable=False)
    UsedDays = Column(Numeric(4, 1), nullable=False, default=0)
    RemainingDays = Column(Numeric(4, 1), nullable=False, default=0)  # Computed column
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime(), onupdate=func.sysutcdatetime())
    
    # Relationships
    employee = relationship("Employees", back_populates="leave_balances")
    leave_type = relationship("LeaveTypes", back_populates="leave_balances")


class LeaveApplications(Base):
    """Leave applications table"""
    __tablename__ = "LeaveApplications"
    
    LeaveApplicationID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    LeaveTypeID = Column(Integer, ForeignKey("LeaveTypes.LeaveTypeID"), nullable=False)
    StartDate = Column(Date, nullable=False)
    EndDate = Column(Date, nullable=False)
    NumberOfDays = Column(Numeric(4, 1), nullable=False)
    Reason = Column(String(500), nullable=True)
    
    StatusCode = Column(String(25), ForeignKey("LeaveApplicationStatuses.StatusCode"), nullable=False)
    SubmittedAt = Column(DateTime, nullable=True)
    
    ManagerID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=True)
    ManagerApprovalStatus = Column(String(20), ForeignKey("ApprovalStatuses.ApprovalStatusCode"), nullable=True)
    ManagerApprovalAt = Column(DateTime, nullable=True)
    ManagerComments = Column(String(500), nullable=True)
    
    HRApproverID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=True)
    HRApprovalStatus = Column(String(20), ForeignKey("ApprovalStatuses.ApprovalStatusCode"), nullable=True)
    HRApprovalAt = Column(DateTime, nullable=True)
    HRComments = Column(String(500), nullable=True)
    
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime(), onupdate=func.sysutcdatetime())
    
    # Relationships
    employee = relationship("Employees", foreign_keys=[EmployeeID], back_populates="leave_applications")
    leave_type = relationship("LeaveTypes", back_populates="leave_applications")
    status = relationship("LeaveApplicationStatuses")
    manager = relationship("Employees", foreign_keys=[ManagerID])
    manager_approval_status = relationship("ApprovalStatuses", foreign_keys=[ManagerApprovalStatus])
    hr_approver = relationship("Employees", foreign_keys=[HRApproverID])
    hr_approval_status = relationship("ApprovalStatuses", foreign_keys=[HRApprovalStatus]) 