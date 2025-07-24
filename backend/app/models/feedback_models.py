from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class EmployeeFeedbacks(Base):
    """Employee feedback table"""
    __tablename__ = "EmployeeFeedbacks"
    
    FeedbackID = Column(Integer, primary_key=True, autoincrement=True)
    FeedbackAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    FeedbackTypeCode = Column(String(20), ForeignKey("FeedbackTypes.FeedbackTypeCode"), nullable=False)
    Category = Column(String(50), nullable=True)
    Subject = Column(String(200), nullable=True)
    FeedbackText = Column(Text, nullable=False)
    
    TargetManagerID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=True)
    TargetDepartmentID = Column(Integer, ForeignKey("Departments.DepartmentID"), nullable=True)
    
    FeedbackHash = Column(String(64), nullable=True)
    IsRead = Column(Boolean, nullable=False, default=False)
    ReadByID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=True)
    ReadAt = Column(DateTime, nullable=True)
    
    # Relationships
    feedback_type = relationship("FeedbackTypes")
    target_manager = relationship("Employees", foreign_keys=[TargetManagerID])
    target_department = relationship("Departments", back_populates="employee_feedbacks")
    read_by = relationship("Employees", foreign_keys=[ReadByID])


class AuditLogs(Base):
    """Audit logs table"""
    __tablename__ = "AuditLogs"
    
    AuditID = Column(Integer, primary_key=True, autoincrement=True)
    TableName = Column(String(128), nullable=False)
    Operation = Column(String(10), nullable=False)  # INSERT, UPDATE, DELETE
    RecordID = Column(Integer, nullable=False)
    ChangedBy = Column(String(100), nullable=False)
    ChangedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    OldValues = Column(Text, nullable=True)
    NewValues = Column(Text, nullable=True) 