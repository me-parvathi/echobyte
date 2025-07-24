from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Locations(Base):
    """Company locations table"""
    __tablename__ = "Locations"
    
    LocationID = Column(Integer, primary_key=True, autoincrement=True)
    LocationName = Column(String(100), nullable=False, unique=True)
    Address1 = Column(String(200), nullable=False)
    Address2 = Column(String(200), nullable=True)
    City = Column(String(100), nullable=False)
    State = Column(String(100), nullable=True)
    Country = Column(String(100), nullable=False)
    PostalCode = Column(String(20), nullable=True)
    Phone = Column(String(50), nullable=True)
    TimeZone = Column(String(50), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime(), onupdate=func.sysutcdatetime())
    
    # Relationships
    departments = relationship("Departments", back_populates="location")
    employees = relationship("Employees", back_populates="location")
    assets = relationship("Assets", back_populates="location")


class Departments(Base):
    """Company departments table"""
    __tablename__ = "Departments"
    
    DepartmentID = Column(Integer, primary_key=True, autoincrement=True)
    DepartmentName = Column(String(100), nullable=False)
    DepartmentCode = Column(String(20), nullable=False, unique=True)
    ParentDepartmentID = Column(Integer, ForeignKey("Departments.DepartmentID"), nullable=True)
    LocationID = Column(Integer, ForeignKey("Locations.LocationID"), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime(), onupdate=func.sysutcdatetime())
    
    # Relationships
    location = relationship("Locations", back_populates="departments")
    parent_department = relationship("Departments", remote_side=[DepartmentID], back_populates="child_departments")
    child_departments = relationship("Departments", back_populates="parent_department")
    teams = relationship("Teams", back_populates="department")
    employee_feedbacks = relationship("EmployeeFeedbacks", back_populates="target_department")


class Teams(Base):
    """Company teams table"""
    __tablename__ = "Teams"
    
    TeamID = Column(Integer, primary_key=True, autoincrement=True)
    TeamName = Column(String(100), nullable=False)
    TeamCode = Column(String(20), nullable=False, unique=True)
    DepartmentID = Column(Integer, ForeignKey("Departments.DepartmentID"), nullable=False)
    TeamLeadEmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=True)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime(), onupdate=func.sysutcdatetime())
    
    # Relationships
    department = relationship("Departments", back_populates="teams")
    team_lead = relationship("Employees", foreign_keys=[TeamLeadEmployeeID], back_populates="led_teams")
    employees = relationship("Employees", foreign_keys="Employees.TeamID", back_populates="team") 