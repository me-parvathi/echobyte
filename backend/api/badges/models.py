from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, Text, DECIMAL, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
from api.employee.models import Employee
from api.learning.models import BadgeDefinition, EmployeeBadge

# Re-export badge models from learning module for consistency
__all__ = [
    'BadgeDefinition',
    'EmployeeBadge'
] 