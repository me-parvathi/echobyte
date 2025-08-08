from sqlalchemy import Column, BigInteger, String, Integer, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class Comment(Base):
    __tablename__ = "Comments"
    
    CommentID = Column(BigInteger, primary_key=True, autoincrement=True)
    EntityType = Column(String(30), nullable=False)
    EntityID = Column(Integer, nullable=False)
    CommenterID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    CommenterRole = Column(String(20), nullable=True)
    CommentText = Column(Text, nullable=False)
    CreatedAt = Column(DateTime(3), nullable=False, default=func.getutcdate())
    UpdatedAt = Column(DateTime(3), nullable=True)
    IsEdited = Column(Boolean, nullable=False, default=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    
    # Relationships
    commenter = relationship("Employee", back_populates="comments") 