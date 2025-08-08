from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class ProfilePicture(Base):
    __tablename__ = "ProfilePictures"
    
    PictureID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    FileName = Column(String(255), nullable=False)
    FilePath = Column(String(500), nullable=False)
    FileSize = Column(BigInteger, nullable=False)
    MimeType = Column(String(100), nullable=True)
    UploadedByID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    UploadedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[EmployeeID])
    uploaded_by = relationship("Employee", foreign_keys=[UploadedByID]) 