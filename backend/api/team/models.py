from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class Team(Base):
    __tablename__ = "Teams"
    
    TeamID = Column(Integer, primary_key=True, autoincrement=True)
    TeamName = Column(String(100), nullable=False)
    TeamCode = Column(String(20), nullable=False, unique=True)
    DepartmentID = Column(Integer, ForeignKey("Departments.DepartmentID"), nullable=False)
    TeamLeadEmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"))
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    department = relationship("Department", back_populates="teams")
    team_lead = relationship("Employee", foreign_keys=[TeamLeadEmployeeID]) 