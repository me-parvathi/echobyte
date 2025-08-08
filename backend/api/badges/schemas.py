from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

# Re-export badge schemas from learning module for consistency
from api.learning.schemas import (
    BadgeDefinitionBase,
    BadgeDefinitionCreate,
    BadgeDefinitionUpdate,
    BadgeDefinitionResponse,
    EmployeeBadgeResponse,
    BadgeEarningResponse
)

__all__ = [
    'BadgeDefinitionBase',
    'BadgeDefinitionCreate',
    'BadgeDefinitionUpdate',
    'BadgeDefinitionResponse',
    'EmployeeBadgeResponse',
    'BadgeEarningResponse'
] 