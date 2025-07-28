from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, Text, DECIMAL, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class Gender(Base):
    __tablename__ = "Genders"
    
    GenderCode = Column(String(10), primary_key=True)
    GenderName = Column(String(50), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())

class EmploymentType(Base):
    __tablename__ = "EmploymentTypes"
    
    EmploymentTypeCode = Column(String(20), primary_key=True)
    EmploymentTypeName = Column(String(50), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())

class WorkMode(Base):
    __tablename__ = "WorkModes"
    
    WorkModeCode = Column(String(20), primary_key=True)
    WorkModeName = Column(String(50), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())

class Designation(Base):
    __tablename__ = "Designations"
    
    DesignationID = Column(Integer, primary_key=True, autoincrement=True)
    DesignationName = Column(String(100), nullable=False, unique=True)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())

class Employee(Base):
    __tablename__ = "Employees"
    
    EmployeeID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeCode = Column(String(20), nullable=False, unique=True)
    UserID = Column(String(50), ForeignKey("Users.UserID"), nullable=False, unique=True)
    CompanyEmail = Column(String(100), nullable=False, unique=True)
    FirstName = Column(String(50), nullable=False)
    MiddleName = Column(String(50))
    LastName = Column(String(50), nullable=False)
    DateOfBirth = Column(Date)
    GenderCode = Column(String(10), ForeignKey("Genders.GenderCode"), nullable=False)
    MaritalStatus = Column(String(20))
    PersonalEmail = Column(String(100))
    PersonalPhone = Column(String(50))
    WorkPhone = Column(String(50))
    
    # Address
    Address1 = Column(String(200))
    Address2 = Column(String(200))
    City = Column(String(100))
    State = Column(String(100))
    Country = Column(String(100))
    PostalCode = Column(String(20))
    
    # Work details
    TeamID = Column(Integer, ForeignKey("Teams.TeamID"), nullable=False)
    LocationID = Column(Integer, ForeignKey("Locations.LocationID"), nullable=False)
    ManagerID = Column(Integer, ForeignKey("Employees.EmployeeID"))
    DesignationID = Column(Integer, ForeignKey("Designations.DesignationID"), nullable=False)
    EmploymentTypeCode = Column(String(20), ForeignKey("EmploymentTypes.EmploymentTypeCode"), nullable=False)
    WorkModeCode = Column(String(20), ForeignKey("WorkModes.WorkModeCode"), nullable=False)
    HireDate = Column(Date, nullable=False)
    TerminationDate = Column(Date)
    
    # System fields
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    gender = relationship("Gender")
    employment_type = relationship("EmploymentType")
    work_mode = relationship("WorkMode")
    designation = relationship("Designation")
    emergency_contacts = relationship("EmergencyContact", back_populates="employee")
    user = relationship("User", foreign_keys=[UserID])
    comments = relationship("Comment", back_populates="commenter")

class EmergencyContact(Base):
    __tablename__ = "EmergencyContacts"
    
    ContactID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    ContactName = Column(String(100), nullable=False)
    Relationship = Column(String(50), nullable=False)
    Phone1 = Column(String(50), nullable=False)
    Phone2 = Column(String(50))
    Email = Column(String(100))
    Address = Column(String(200))
    IsPrimary = Column(Boolean, nullable=False, default=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    employee = relationship("Employee", back_populates="emergency_contacts")

class AuditLog(Base):
    __tablename__ = "AuditLogs"
    
    AuditID = Column(Integer, primary_key=True, autoincrement=True)
    TableName = Column(String(128), nullable=False)
    Operation = Column(String(10), nullable=False)
    RecordID = Column(Integer, nullable=False)
    ChangedBy = Column(String(100), nullable=False)
    ChangedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    OldValues = Column(Text)
    NewValues = Column(Text) 