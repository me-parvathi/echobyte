from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, DECIMAL, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class LeaveApplicationStatus(Base):
    __tablename__ = "LeaveApplicationStatuses"
    
    StatusCode = Column(String(25), primary_key=True)
    StatusName = Column(String(50), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())

class ApprovalStatus(Base):
    __tablename__ = "ApprovalStatuses"
    
    ApprovalStatusCode = Column(String(20), primary_key=True)
    ApprovalStatusName = Column(String(50), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())

class LeaveType(Base):
    __tablename__ = "LeaveTypes"
    
    LeaveTypeID = Column(Integer, primary_key=True, autoincrement=True)
    LeaveTypeName = Column(String(50), nullable=False)
    LeaveCode = Column(String(10), nullable=False, unique=True)
    DefaultDaysPerYear = Column(DECIMAL(4,1))
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())

class LeaveBalance(Base):
    __tablename__ = "LeaveBalances"
    
    BalanceID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    LeaveTypeID = Column(Integer, ForeignKey("LeaveTypes.LeaveTypeID"), nullable=False)
    Year = Column(Integer, nullable=False)
    EntitledDays = Column(DECIMAL(4,1), nullable=False)
    UsedDays = Column(DECIMAL(4,1), nullable=False, default=0)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    employee = relationship("Employee")
    leave_type = relationship("LeaveType")
    
    # Unique constraint
    __table_args__ = (
        CheckConstraint('Year > 0', name='CHK_LeaveBalances_Year'),
    )

class LeaveApplication(Base):
    __tablename__ = "LeaveApplications"
    
    LeaveApplicationID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    LeaveTypeID = Column(Integer, ForeignKey("LeaveTypes.LeaveTypeID"), nullable=False)
    StartDate = Column(Date, nullable=False)
    EndDate = Column(Date, nullable=False)
    NumberOfDays = Column(DECIMAL(4,1), nullable=False)
    Reason = Column(Text)
    
    StatusCode = Column(String(25), ForeignKey("LeaveApplicationStatuses.StatusCode"), nullable=False)
    SubmittedAt = Column(DateTime)
    
    ManagerID = Column(Integer, ForeignKey("Employees.EmployeeID"))
    ManagerApprovalStatus = Column(String(20), ForeignKey("ApprovalStatuses.ApprovalStatusCode"))
    ManagerApprovalAt = Column(DateTime)
    
    HRApproverID = Column(Integer, ForeignKey("Employees.EmployeeID"))
    HRApprovalStatus = Column(String(20), ForeignKey("ApprovalStatuses.ApprovalStatusCode"))
    HRApprovalAt = Column(DateTime)
    
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[EmployeeID])
    leave_type = relationship("LeaveType")
    status = relationship("LeaveApplicationStatus")
    manager = relationship("Employee", foreign_keys=[ManagerID])
    hr_approver = relationship("Employee", foreign_keys=[HRApproverID])
    manager_approval_status = relationship("ApprovalStatus", foreign_keys=[ManagerApprovalStatus])
    hr_approval_status = relationship("ApprovalStatus", foreign_keys=[HRApprovalStatus])
    
    # Check constraint
    __table_args__ = (
        CheckConstraint('EndDate >= StartDate', name='CHK_LeaveApplications_Dates'),
    ) 