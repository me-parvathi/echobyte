from datetime import datetime, time
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class NotificationBase(BaseModel):
    type: str = Field(..., max_length=50)
    category: str = Field(..., max_length=50)
    title: str = Field(..., max_length=200)
    message: str
    priority: str = Field(..., max_length=10)
    metadata: Optional[str] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationCreate(NotificationBase):
    user_id: str = Field(..., max_length=50)


class NotificationRead(NotificationBase):
    id: str = Field(..., max_length=36)
    user_id: str = Field(..., max_length=50)
    is_read: bool = Field(default=False)
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationDeliveryRead(BaseModel):
    id: str = Field(..., max_length=36)
    channel: str = Field(..., max_length=20)
    status: str = Field(..., max_length=10)
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class UserNotificationPreferenceRead(BaseModel):
    email_enabled: bool = Field(default=True)
    push_enabled: bool = Field(default=True)
    desktop_enabled: bool = Field(default=True)
    sound_enabled: bool = Field(default=True)
    quiet_hours_start: Optional[time] = None
    quiet_hours_end: Optional[time] = None
    timezone: str = Field(default="UTC", max_length=50)
    preferences: Optional[str] = None

    class Config:
        from_attributes = True


class UserNotificationPreferenceUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    desktop_enabled: Optional[bool] = None
    sound_enabled: Optional[bool] = None
    quiet_hours_start: Optional[time] = None
    quiet_hours_end: Optional[time] = None
    timezone: Optional[str] = Field(None, max_length=50)
    preferences: Optional[str] = None


class LearningNotificationCreate(BaseModel):
    notification_id: str = Field(..., max_length=36)
    course_id: int
    action_type: str = Field(..., max_length=20)
    course_name: Optional[str] = Field(None, max_length=200)
    progress_percentage: Optional[int] = None


class LearningNotificationRead(BaseModel):
    id: str = Field(..., max_length=36)
    notification_id: str = Field(..., max_length=36)
    course_id: int
    action_type: str = Field(..., max_length=20)
    course_name: Optional[str] = Field(None, max_length=200)
    progress_percentage: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True 