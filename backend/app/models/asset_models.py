from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class AssetStatuses(Base):
    """Asset status lookup table"""
    __tablename__ = "AssetStatuses"
    
    AssetStatusCode = Column(String(20), primary_key=True)
    AssetStatusName = Column(String(50), nullable=False)
    IsAssignable = Column(Boolean, nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    
    # Relationships
    assets = relationship("Assets", back_populates="asset_status")


class AssetTypes(Base):
    """Asset type lookup table"""
    __tablename__ = "AssetTypes"
    
    AssetTypeID = Column(Integer, primary_key=True, autoincrement=True)
    AssetTypeName = Column(String(100), nullable=False, unique=True)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    
    # Relationships
    assets = relationship("Assets", back_populates="asset_type")


class Assets(Base):
    """Assets table"""
    __tablename__ = "Assets"
    
    AssetID = Column(Integer, primary_key=True, autoincrement=True)
    AssetTag = Column(String(50), nullable=False, unique=True)
    SerialNumber = Column(String(100), nullable=True, unique=True)
    MACAddress = Column(String(100), nullable=True, unique=True)
    AssetTypeID = Column(Integer, ForeignKey("AssetTypes.AssetTypeID"), nullable=False)
    AssetStatusCode = Column(String(20), ForeignKey("AssetStatuses.AssetStatusCode"), nullable=False)
    Model = Column(String(100), nullable=True)
    Vendor = Column(String(100), nullable=True)
    PurchaseDate = Column(Date, nullable=True)
    WarrantyEndDate = Column(Date, nullable=True)
    IsUnderContract = Column(Boolean, nullable=False, default=False)
    ContractStartDate = Column(Date, nullable=True)
    ContractExpiryDate = Column(Date, nullable=True)
    LocationID = Column(Integer, ForeignKey("Locations.LocationID"), nullable=True)
    Notes = Column(String(500), nullable=True)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime(), onupdate=func.sysutcdatetime())
    
    # Relationships
    asset_type = relationship("AssetTypes", back_populates="assets")
    asset_status = relationship("AssetStatuses", back_populates="assets")
    location = relationship("Locations", back_populates="assets")
    asset_assignments = relationship("AssetAssignments", back_populates="asset")


class AssetAssignments(Base):
    """Asset assignments table"""
    __tablename__ = "AssetAssignments"
    
    AssignmentID = Column(Integer, primary_key=True, autoincrement=True)
    AssetID = Column(Integer, ForeignKey("Assets.AssetID"), nullable=False)
    EmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    AssignedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    DueReturnDate = Column(Date, nullable=True)
    ReturnedAt = Column(DateTime, nullable=True)
    ConditionAtAssign = Column(String(200), nullable=True)
    ConditionAtReturn = Column(String(200), nullable=True)
    AssignedByID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    ReceivedByID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=True)
    Notes = Column(String(500), nullable=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime(), onupdate=func.sysutcdatetime())
    
    # Relationships
    asset = relationship("Assets", back_populates="asset_assignments")
    employee = relationship("Employees", foreign_keys=[EmployeeID], back_populates="asset_assignments")
    assigned_by = relationship("Employees", foreign_keys=[AssignedByID])
    received_by = relationship("Employees", foreign_keys=[ReceivedByID]) 