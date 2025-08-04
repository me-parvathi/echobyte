from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

# Re-export quiz schemas from learning module for consistency
from api.learning.schemas import (
    QuizBase,
    QuizCreate,
    QuizUpdate,
    QuizResponse,
    QuizQuestionBase,
    QuizQuestionCreate,
    QuizQuestionResponse,
    QuizOptionBase,
    QuizOptionCreate,
    QuizOptionResponse,
    QuizAttemptBase,
    QuizAttemptCreate,
    QuizAttemptUpdate,
    QuizAttemptResponse,
    QuizResponseBase,
    QuizResponseCreate,
    QuizResponseResponse,
    QuizSubmissionRequest,
    QuizAttemptLimitResponse
)

__all__ = [
    'QuizBase',
    'QuizCreate',
    'QuizUpdate', 
    'QuizResponse',
    'QuizQuestionBase',
    'QuizQuestionCreate',
    'QuizQuestionResponse',
    'QuizOptionBase',
    'QuizOptionCreate',
    'QuizOptionResponse',
    'QuizAttemptBase',
    'QuizAttemptCreate',
    'QuizAttemptUpdate',
    'QuizAttemptResponse',
    'QuizResponseBase',
    'QuizResponseCreate',
    'QuizResponseResponse',
    'QuizSubmissionRequest',
    'QuizAttemptLimitResponse'
] 