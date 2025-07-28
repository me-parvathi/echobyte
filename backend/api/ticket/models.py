from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, BigInteger, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class TicketStatus(Base):
    __tablename__ = "TicketStatuses"
    
    TicketStatusCode = Column(String(20), primary_key=True)
    TicketStatusName = Column(String(50), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())

class TicketPriority(Base):
    __tablename__ = "TicketPriorities"
    
    PriorityCode = Column(String(10), primary_key=True)
    PriorityName = Column(String(50), nullable=False)
    SLAHours = Column(Integer, nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())

class TicketCategory(Base):
    __tablename__ = "TicketCategories"
    
    CategoryID = Column(Integer, primary_key=True, autoincrement=True)
    CategoryName = Column(String(100), nullable=False, unique=True)
    ParentCategoryID = Column(Integer, ForeignKey("TicketCategories.CategoryID"), nullable=True)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    
    # Self-referencing relationship for parent-child categories
    parent = relationship("TicketCategory", remote_side=[CategoryID], back_populates="children")
    children = relationship("TicketCategory", back_populates="parent")
    tickets = relationship("Ticket", back_populates="category")

class Ticket(Base):
    __tablename__ = "Tickets"
    
    TicketID = Column(Integer, primary_key=True, autoincrement=True)
    TicketNumber = Column(String(20), nullable=False, unique=True)
    Subject = Column(String(200), nullable=False)
    Description = Column(Text, nullable=False)
    
    # Ticket Details
    CategoryID = Column(Integer, ForeignKey("TicketCategories.CategoryID"), nullable=False)
    PriorityCode = Column(String(10), ForeignKey("TicketPriorities.PriorityCode"), nullable=False)
    StatusCode = Column(String(20), ForeignKey("TicketStatuses.TicketStatusCode"), nullable=False)
    
    # People Involved
    OpenedByID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    AssignedToID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=True)
    EscalatedToID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=True)
    
    # Asset Association (Optional)
    AssetID = Column(Integer, ForeignKey("Assets.AssetID"), nullable=True)
    
    # Timestamps
    OpenedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    AssignedAt = Column(DateTime, nullable=True)
    EscalatedAt = Column(DateTime, nullable=True)
    ResolvedAt = Column(DateTime, nullable=True)
    ClosedAt = Column(DateTime, nullable=True)
    DueDate = Column(DateTime, nullable=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    category = relationship("TicketCategory", back_populates="tickets")
    priority = relationship("TicketPriority")
    status = relationship("TicketStatus")
    opened_by = relationship("Employee", foreign_keys=[OpenedByID])
    assigned_to = relationship("Employee", foreign_keys=[AssignedToID])
    escalated_to = relationship("Employee", foreign_keys=[EscalatedToID])
    asset = relationship("Asset")
    activities = relationship("TicketActivity", back_populates="ticket", cascade="all, delete-orphan")
    attachments = relationship("TicketAttachment", back_populates="ticket", cascade="all, delete-orphan")

class TicketActivity(Base):
    __tablename__ = "TicketActivities"
    
    ActivityID = Column(Integer, primary_key=True, autoincrement=True)
    TicketID = Column(Integer, ForeignKey("Tickets.TicketID"), nullable=False)
    ActivityType = Column(String(30), nullable=False)  # Status_Change, Assignment, Escalation, Comment, etc.
    PerformedByID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    OldValue = Column(String(100), nullable=True)
    NewValue = Column(String(100), nullable=True)
    ActivityDetails = Column(String(500), nullable=True)
    PerformedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    
    # Relationships
    ticket = relationship("Ticket", back_populates="activities")
    performed_by = relationship("Employee")

class TicketAttachment(Base):
    __tablename__ = "TicketAttachments"
    
    AttachmentID = Column(Integer, primary_key=True, autoincrement=True)
    TicketID = Column(Integer, ForeignKey("Tickets.TicketID"), nullable=False)
    FileName = Column(String(255), nullable=False)
    FilePath = Column(String(500), nullable=False)
    FileSize = Column(BigInteger, nullable=False)
    MimeType = Column(String(100), nullable=True)
    UploadedByID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    UploadedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    
    # Relationships
    ticket = relationship("Ticket", back_populates="attachments")
    uploaded_by = relationship("Employee") 