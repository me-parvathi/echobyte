from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "Users"  # Match DDL table name
    
    UserID = Column(String(50), primary_key=True, index=True)
    Username = Column(String(100), unique=True, index=True, nullable=False)
    Email = Column(String(100), unique=True, index=True, nullable=False)
    HashedPassword = Column(String(255), nullable=False)
    IsActive = Column(Boolean, default=True)
    IsSuperuser = Column(Boolean, default=False)
    LastLoginAt = Column(DateTime, nullable=True)
    PasswordChangedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    CreatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.sysutcdatetime(), onupdate=func.sysutcdatetime())
    
    # Relationship to Employee
    employee = relationship("Employees", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>" 