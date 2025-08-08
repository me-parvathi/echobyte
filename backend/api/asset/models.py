from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class AssetStatus(Base):
    __tablename__ = "AssetStatuses"
    
    AssetStatusCode = Column(String(20), primary_key=True)
    AssetStatusName = Column(String(50), nullable=False)
    IsAssignable = Column(Boolean, nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())

class AssetType(Base):
    __tablename__ = "AssetTypes"
    
    AssetTypeID = Column(Integer, primary_key=True, autoincrement=True)
    AssetTypeName = Column(String(100), nullable=False, unique=True)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())

class Asset(Base):
    __tablename__ = "Assets"
    
    AssetID = Column(Integer, primary_key=True, autoincrement=True)
    AssetTag = Column(String(50), nullable=False, unique=True)
    SerialNumber = Column(String(100), unique=True)
    MACAddress = Column(String(100), unique=True)
    AssetTypeID = Column(Integer, ForeignKey("AssetTypes.AssetTypeID"), nullable=False)
    AssetStatusCode = Column(String(20), ForeignKey("AssetStatuses.AssetStatusCode"), nullable=False)
    Model = Column(String(100))
    Vendor = Column(String(100))
    PurchaseDate = Column(Date)
    WarrantyEndDate = Column(Date)
    IsUnderContract = Column(Boolean, nullable=False, default=False)
    ContractStartDate = Column(Date)
    ContractExpiryDate = Column(Date)
    LocationID = Column(Integer, ForeignKey("Locations.LocationID"))
    Notes = Column(Text)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    asset_type = relationship("AssetType")
    asset_status = relationship("AssetStatus")
    location = relationship("Location")
    assignments = relationship("AssetAssignment", back_populates="asset")
    
    # Check constraint for contract dates
    __table_args__ = (
        CheckConstraint(
            '(IsUnderContract = 0 AND ContractStartDate IS NULL AND ContractExpiryDate IS NULL) OR '
            '(IsUnderContract = 1 AND ContractStartDate IS NOT NULL AND ContractExpiryDate IS NOT NULL AND ContractExpiryDate >= ContractStartDate)',
            name='CHK_Asst_ContractDates'
        ),
    )

class AssetAssignment(Base):
    __tablename__ = "AssetAssignments"
    
    AssignmentID = Column(Integer, primary_key=True, autoincrement=True)
    AssetID = Column(Integer, ForeignKey("Assets.AssetID"), nullable=False)
    EmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    AssignedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    DueReturnDate = Column(Date)
    ReturnedAt = Column(DateTime)
    ConditionAtAssign = Column(String(200))
    ConditionAtReturn = Column(String(200))
    AssignedByID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    ReceivedByID = Column(Integer, ForeignKey("Employees.EmployeeID"))
    Notes = Column(Text)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    asset = relationship("Asset", back_populates="assignments")
    employee = relationship("Employee", foreign_keys=[EmployeeID])
    assigned_by = relationship("Employee", foreign_keys=[AssignedByID])
    received_by = relationship("Employee", foreign_keys=[ReceivedByID])
    
    # Check constraint for due date
    __table_args__ = (
        CheckConstraint('DueReturnDate IS NULL OR DueReturnDate >= CAST(AssignedAt AS DATE)', name='CHK_Asg_DueDate'),
    ) 