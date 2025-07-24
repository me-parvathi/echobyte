from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Employees(Base):
    """Employees table"""
    __tablename__ = "Employees"
    
    EmployeeID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeCode = Column(String(20), nullable=False, unique=True)
    UserID = Column(String(50), nullable=False, unique=True)
    CompanyEmail = Column(String(100), nullable=False, unique=True)
    FirstName = Column(String(50), nullable=False)
    MiddleName = Column(String(50), nullable=True)
    LastName = Column(String(50), nullable=False)
    DateOfBirth = Column(Date, nullable=True)
    GenderCode = Column(String(10), ForeignKey("Genders.GenderCode"), nullable=False)
    MaritalStatus = Column(String(20), nullable=True)
    PersonalEmail = Column(String(100), nullable=True)
    PersonalPhone = Column(String(50), nullable=True)
    WorkPhone = Column(String(50), nullable=True)
    
    # Address
    Address1 = Column(String(200), nullable=True)
    Address2 = Column(String(200), nullable=True)
    City = Column(String(100), nullable=True)
    State = Column(String(100), nullable=True)
    Country = Column(String(100), nullable=True)
    PostalCode = Column(String(20), nullable=True)
    
    # Work details
    TeamID = Column(Integer, ForeignKey("Teams.TeamID"), nullable=False)
    LocationID = Column(Integer, ForeignKey("Locations.LocationID"), nullable=False)
    ManagerID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=True)
    DesignationID = Column(Integer, ForeignKey("Designations.DesignationID"), nullable=False)
    EmploymentTypeCode = Column(String(20), ForeignKey("EmploymentTypes.EmploymentTypeCode"), nullable=False)
    WorkModeCode = Column(String(20), ForeignKey("WorkModes.WorkModeCode"), nullable=False)
    HireDate = Column(Date, nullable=False)
    TerminationDate = Column(Date, nullable=True)
    
    # System fields
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime(), onupdate=func.sysutcdatetime())
    
    # Relationships
    gender = relationship("Genders")
    team = relationship("Teams", foreign_keys=[TeamID], back_populates="employees")
    location = relationship("Locations", foreign_keys=[LocationID], back_populates="employees")
    manager = relationship("Employees", foreign_keys=[ManagerID], remote_side=[EmployeeID], back_populates="subordinates")
    subordinates = relationship("Employees", foreign_keys="Employees.ManagerID", back_populates="manager")
    designation = relationship("Designations")
    employment_type = relationship("EmploymentTypes")
    work_mode = relationship("WorkModes")
    led_teams = relationship("Teams", foreign_keys="Teams.TeamLeadEmployeeID", back_populates="team_lead")
    
    # Related tables
    emergency_contacts = relationship("EmergencyContacts", foreign_keys="EmergencyContacts.EmployeeID", back_populates="employee")
    employee_roles = relationship("EmployeeRoles", foreign_keys="EmployeeRoles.EmployeeID", back_populates="employee")
    leave_balances = relationship("LeaveBalances", foreign_keys="LeaveBalances.EmployeeID", back_populates="employee")
    leave_applications = relationship("LeaveApplications", foreign_keys="LeaveApplications.EmployeeID", back_populates="employee")
    timesheets = relationship("Timesheets", foreign_keys="Timesheets.EmployeeID", back_populates="employee")
    asset_assignments = relationship("AssetAssignments", foreign_keys="AssetAssignments.EmployeeID", back_populates="employee")
    user = relationship("User", back_populates="employee", uselist=False)


class EmergencyContacts(Base):
    """Emergency contacts table"""
    __tablename__ = "EmergencyContacts"
    
    ContactID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    ContactName = Column(String(100), nullable=False)
    Relationship = Column(String(50), nullable=False)
    Phone1 = Column(String(50), nullable=False)
    Phone2 = Column(String(50), nullable=True)
    Email = Column(String(100), nullable=True)
    Address = Column(String(200), nullable=True)
    IsPrimary = Column(Boolean, nullable=False, default=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime(), onupdate=func.sysutcdatetime())
    
    # Relationships
    employee = relationship("Employees", back_populates="emergency_contacts")


class Roles(Base):
    """Roles table"""
    __tablename__ = "Roles"
    
    RoleID = Column(Integer, primary_key=True, autoincrement=True)
    RoleName = Column(String(50), nullable=False, unique=True)
    Description = Column(String(200), nullable=True)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    
    # Relationships
    employee_roles = relationship("EmployeeRoles", back_populates="role")


class EmployeeRoles(Base):
    """Employee roles junction table"""
    __tablename__ = "EmployeeRoles"
    
    EmployeeRoleID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    RoleID = Column(Integer, ForeignKey("Roles.RoleID"), nullable=False)
    AssignedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    AssignedByID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=True)
    IsActive = Column(Boolean, nullable=False, default=True)
    
    # Relationships
    employee = relationship("Employees", foreign_keys=[EmployeeID], back_populates="employee_roles")
    role = relationship("Roles", back_populates="employee_roles")
    assigned_by = relationship("Employees", foreign_keys=[AssignedByID]) 