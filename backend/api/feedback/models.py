from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class FeedbackType(Base):
    __tablename__ = "FeedbackTypes"
    
    FeedbackTypeCode = Column(String(20), primary_key=True)
    FeedbackTypeName = Column(String(50), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())

class EmployeeFeedback(Base):
    __tablename__ = "EmployeeFeedbacks"
    
    FeedbackID = Column(Integer, primary_key=True, autoincrement=True)
    FeedbackAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    FeedbackTypeCode = Column(String(20), ForeignKey("FeedbackTypes.FeedbackTypeCode"), nullable=False)
    Category = Column(String(50))
    Subject = Column(String(200))
    FeedbackText = Column(Text, nullable=False)
    
    TargetManagerID = Column(Integer, ForeignKey("Employees.EmployeeID"))
    TargetDepartmentID = Column(Integer, ForeignKey("Departments.DepartmentID"))
    
    FeedbackHash = Column(String(64))
    IsRead = Column(Boolean, nullable=False, default=False)
    ReadByID = Column(Integer, ForeignKey("Employees.EmployeeID"))
    ReadAt = Column(DateTime)
    
    # Relationships
    feedback_type = relationship("FeedbackType")
    target_manager = relationship("Employee", foreign_keys=[TargetManagerID])
    target_department = relationship("Department")
    read_by = relationship("Employee", foreign_keys=[ReadByID]) 