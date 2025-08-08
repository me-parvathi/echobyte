# Import all models to ensure they are registered with SQLAlchemy
from api.employee.models import *
from api.department.models import *
from api.team.models import *
from api.location.models import *
from api.leave.models import *
from api.timesheet.models import *
from api.asset.models import *
from api.feedback.models import *
from api.auth.models import *
from api.comments.models import *

# -------------------------------------------------------------------------
# Notification subsystem models (SQLAlchemy ORM)
# -------------------------------------------------------------------------
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey, CheckConstraint, Index, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class Notification(Base):
    __tablename__ = "Notifications"

    Id = Column(String(36), primary_key=True)
    UserID = Column(String(50), ForeignKey("Users.UserID"), nullable=False)
    Type = Column(String(50), nullable=False)
    Category = Column(String(50), nullable=False)
    Title = Column(String(200), nullable=False)
    Message = Column(Text, nullable=False)
    Priority = Column(String(10), nullable=False)
    Metadata = Column(Text)
    IsRead = Column(Boolean, nullable=False, default=False)
    ReadAt = Column(DateTime)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    ExpiresAt = Column(DateTime)

    # Relationships
    deliveries = relationship(
        "NotificationDelivery",
        back_populates="notification",
        cascade="all, delete-orphan",
    )
    learning_notification = relationship(
        "LearningNotification",
        back_populates="notification",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("Priority IN ('low','normal','high','urgent')", name="CHK_Notifications_Priority"),
        Index("IX_Notifications_UserRead", "UserID", "IsRead"),
        Index("IX_Notifications_UserType", "UserID", "Type"),
        Index("IX_Notifications_CreatedAt", "CreatedAt"),
    )


class NotificationDelivery(Base):
    __tablename__ = "NotificationDeliveries"

    Id = Column(String(36), primary_key=True)
    NotificationID = Column(String(36), ForeignKey("Notifications.Id", ondelete="CASCADE"), nullable=False)
    Channel = Column(String(20), nullable=False)
    Status = Column(String(10), nullable=False, default="pending")
    SentAt = Column(DateTime)
    DeliveredAt = Column(DateTime)
    ErrorMessage = Column(Text)
    RetryCount = Column(Integer, nullable=False, default=0)
    MaxRetries = Column(Integer, nullable=False, default=3)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())

    # Relationships
    notification = relationship("Notification", back_populates="deliveries")

    __table_args__ = (
        CheckConstraint("Channel IN ('email','push','desktop','sms')", name="CHK_NotifDel_Channel"),
        CheckConstraint("Status IN ('pending','sent','delivered','failed')", name="CHK_NotifDel_Status"),
        Index("IX_NotifDel_NotifChannel", "NotificationID", "Channel"),
        Index("IX_NotifDel_Status", "Status"),
    )


class UserNotificationPreference(Base):
    __tablename__ = "UserNotificationPreferences"

    UserID = Column(String(50), ForeignKey("Users.UserID"), primary_key=True)
    EmailEnabled = Column(Boolean, nullable=False, default=True)
    PushEnabled = Column(Boolean, nullable=False, default=True)
    DesktopEnabled = Column(Boolean, nullable=False, default=True)
    SoundEnabled = Column(Boolean, nullable=False, default=True)
    QuietHoursStart = Column(Time)
    QuietHoursEnd = Column(Time)
    Timezone = Column(String(50), nullable=False, default="UTC")
    Preferences = Column(Text)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate(), onupdate=func.getutcdate())

    # Relationships
    user = relationship("User")


class LearningNotification(Base):
    __tablename__ = "LearningNotifications"

    Id = Column(String(36), primary_key=True)
    NotificationID = Column(String(36), ForeignKey("Notifications.Id", ondelete="CASCADE"), nullable=False)
    CourseID = Column(Integer, ForeignKey("Courses.CourseID"), nullable=False)
    ActionType = Column(String(20), nullable=False)
    CourseName = Column(String(200))
    ProgressPercentage = Column(Integer)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())

    # Relationships
    notification = relationship("Notification", back_populates="learning_notification")

    __table_args__ = (
        Index("IX_LearnNotif_Course", "CourseID"),
    ) 