from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class User(Base):
    __tablename__ = "Users"
    
    UserID = Column(String(50), primary_key=True)
    Username = Column(String(100), nullable=False, unique=True)
    Email = Column(String(100), nullable=False, unique=True)
    Password = Column("HashedPassword", String(255), nullable=False)  # Hashed password
    IsActive = Column(Boolean, nullable=False, default=True)
    LastLoginAt = Column(DateTime)
    PasswordChangedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate(), onupdate=func.getutcdate())

class Role(Base):
    __tablename__ = "Roles"
    
    RoleID = Column(Integer, primary_key=True, autoincrement=True)
    RoleName = Column(String(50), nullable=False, unique=True)
    Description = Column(String(200))
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())

class EmployeeRole(Base):
    __tablename__ = "EmployeeRoles"
    
    EmployeeRoleID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    RoleID = Column(Integer, ForeignKey("Roles.RoleID"), nullable=False)
    AssignedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    AssignedByID = Column(Integer, ForeignKey("Employees.EmployeeID"))
    IsActive = Column(Boolean, nullable=False, default=True) 