from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
from api.location.models import Location

class Department(Base):
    __tablename__ = "Departments"
    
    DepartmentID = Column(Integer, primary_key=True, autoincrement=True)
    DepartmentName = Column(String(100), nullable=False)
    DepartmentCode = Column(String(20), nullable=False, unique=True)
    ParentDepartmentID = Column(Integer, ForeignKey("Departments.DepartmentID"))
    LocationID = Column(Integer, ForeignKey("Locations.LocationID"), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    location = relationship("Location", back_populates="departments")
    parent_department = relationship("Department", remote_side=[DepartmentID], backref="child_departments")
    teams = relationship("Team", back_populates="department") 