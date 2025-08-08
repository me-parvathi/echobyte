from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class Location(Base):
    __tablename__ = "Locations"
    
    LocationID = Column(Integer, primary_key=True, autoincrement=True)
    LocationName = Column(String(100), nullable=False, unique=True)
    Address1 = Column(String(200), nullable=False)
    Address2 = Column(String(200))
    City = Column(String(100), nullable=False)
    State = Column(String(100))
    Country = Column(String(100), nullable=False)
    PostalCode = Column(String(20))
    Phone = Column(String(50))
    TimeZone = Column(String(50), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    departments = relationship("Department", back_populates="location") 