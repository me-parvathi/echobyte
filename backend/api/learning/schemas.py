from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

# Base schemas
class CourseBase(BaseModel):
    CourseCode: str
    Title: str
    Difficulty: str
    EstimatedHours: Decimal
    IsActive: bool = True

class CourseModuleBase(BaseModel):
    ModuleSeq: int
    Title: str
    VideoURL: str
    VideoType: str = 'I'

class EmployeeCourseBase(BaseModel):
    Status: str = 'In-Progress'

class EmployeeModuleProgressBase(BaseModel):
    TimeSpentMinutes: Optional[int] = None

class BadgeDefinitionBase(BaseModel):
    BadgeCode: str
    Name: str
    Description: Optional[str] = None
    IconURL: Optional[str] = None
    IsActive: bool = True
    CourseID: Optional[int] = None
    QuizID: Optional[int] = None
    
    @validator('CourseID', 'QuizID')
    def validate_course_quiz_relationship(cls, v, values):
        """Validate that either CourseID or QuizID is provided, but not both (unless it's a general badge)"""
        course_id = values.get('CourseID') if 'CourseID' in values else None
        quiz_id = values.get('QuizID') if 'QuizID' in values else None
        
        # If we're validating CourseID, get the current value
        if 'CourseID' in values:
            course_id = v
        if 'QuizID' in values:
            quiz_id = v
            
        # Both can be None (general badge) or exactly one should be set
        if course_id is not None and quiz_id is not None:
            raise ValueError("A badge cannot be associated with both a course and a quiz simultaneously")
        
        return v

class QuizBase(BaseModel):
    Title: str
    QuestionCount: int
    TimeLimitMin: int
    PassingPct: Decimal
    IsActive: bool = True

class QuizQuestionBase(BaseModel):
    QuestionSeq: int
    QuestionText: str
    Explanation: Optional[str] = None
    IsActive: bool = True

class QuizOptionBase(BaseModel):
    OptionSeq: int
    OptionText: str
    IsCorrect: bool

class QuizAttemptBase(BaseModel):
    QuizID: int

class QuizResponseBase(BaseModel):
    QuestionID: int
    OptionID: int

# Create schemas
class CourseCreate(CourseBase):
    pass

class CourseModuleCreate(CourseModuleBase):
    CourseID: int

class EmployeeCourseCreate(BaseModel):
    CourseID: int

class EmployeeModuleProgressCreate(EmployeeModuleProgressBase):
    ModuleID: int

class BadgeDefinitionCreate(BadgeDefinitionBase):
    pass

class QuizCreate(QuizBase):
    CourseID: Optional[int] = None

class QuizQuestionCreate(QuizQuestionBase):
    QuizID: int

class QuizOptionCreate(QuizOptionBase):
    QuestionID: int

class QuizAttemptCreate(QuizAttemptBase):
    pass

class QuizResponseCreate(QuizResponseBase):
    pass

# Update schemas
class CourseUpdate(BaseModel):
    CourseCode: Optional[str] = None
    Title: Optional[str] = None
    Difficulty: Optional[str] = None
    EstimatedHours: Optional[Decimal] = None
    IsActive: Optional[bool] = None

class CourseModuleUpdate(BaseModel):
    ModuleSeq: Optional[int] = None
    Title: Optional[str] = None
    VideoURL: Optional[str] = None
    VideoType: Optional[str] = None

class EmployeeCourseUpdate(BaseModel):
    Status: Optional[str] = None
    CompletedAt: Optional[datetime] = None

class EmployeeModuleProgressUpdate(BaseModel):
    TimeSpentMinutes: Optional[int] = None

class BadgeDefinitionUpdate(BaseModel):
    BadgeCode: Optional[str] = None
    Name: Optional[str] = None
    Description: Optional[str] = None
    IconURL: Optional[str] = None
    IsActive: Optional[bool] = None
    CourseID: Optional[int] = None
    QuizID: Optional[int] = None
    
    @validator('CourseID', 'QuizID')
    def validate_course_quiz_relationship(cls, v, values):
        """Validate that either CourseID or QuizID is provided, but not both (unless it's a general badge)"""
        course_id = values.get('CourseID')
        quiz_id = values.get('QuizID')
        
        # If we're validating CourseID, get the current value
        if 'CourseID' in values:
            course_id = v
        if 'QuizID' in values:
            quiz_id = v
            
        # Both can be None (general badge) or exactly one should be set
        if course_id is not None and quiz_id is not None:
            raise ValueError("A badge cannot be associated with both a course and a quiz simultaneously")
        
        return v

class QuizUpdate(BaseModel):
    Title: Optional[str] = None
    QuestionCount: Optional[int] = None
    TimeLimitMin: Optional[int] = None
    PassingPct: Optional[Decimal] = None
    IsActive: Optional[bool] = None

class QuizAttemptUpdate(BaseModel):
    CompletedAt: Optional[datetime] = None
    ScorePct: Optional[Decimal] = None
    IsPassed: Optional[bool] = None

# Response schemas
class CourseModuleResponse(CourseModuleBase):
    ModuleID: int
    CourseID: int
    
    class Config:
        from_attributes = True

class CourseResponse(CourseBase):
    CourseID: int
    CreatedAt: datetime
    UpdatedAt: datetime
    modules: List[CourseModuleResponse] = []
    
    class Config:
        from_attributes = True

class CourseListResponse(BaseModel):
    courses: List[CourseResponse]
    total: int
    page: int
    size: int

class EmployeeCourseResponse(EmployeeCourseBase):
    EmployeeCourseID: int
    EmployeeID: int
    CourseID: int
    EnrolledAt: datetime
    CompletedAt: Optional[datetime] = None
    course: Optional[CourseResponse] = None
    
    class Config:
        from_attributes = True

class EmployeeModuleProgressResponse(EmployeeModuleProgressBase):
    EmpCourseID: int
    ModuleID: int
    CompletedAt: datetime
    module: Optional[CourseModuleResponse] = None
    
    class Config:
        from_attributes = True

class BadgeDefinitionResponse(BadgeDefinitionBase):
    BadgeID: int
    CreatedAt: datetime
    
    class Config:
        from_attributes = True

class EmployeeBadgeResponse(BaseModel):
    EmployeeBadgeID: int
    EmployeeID: int
    BadgeID: int
    EarnedAt: datetime
    badge: Optional[BadgeDefinitionResponse] = None
    
    class Config:
        from_attributes = True

class QuizOptionResponse(QuizOptionBase):
    OptionID: int
    QuestionID: int
    
    class Config:
        from_attributes = True

class QuizQuestionResponse(QuizQuestionBase):
    QuestionID: int
    QuizID: int
    CreatedAt: datetime
    options: List[QuizOptionResponse] = []
    
    class Config:
        from_attributes = True

class QuizResponse(QuizBase):
    QuizID: int
    CourseID: Optional[int] = None
    questions: List[QuizQuestionResponse] = []
    
    class Config:
        from_attributes = True

class QuizAttemptResponse(QuizAttemptBase):
    AttemptID: int
    EmployeeID: int
    StartedAt: datetime
    CompletedAt: Optional[datetime] = None
    ScorePct: Optional[Decimal] = None
    IsPassed: Optional[bool] = None
    quiz: Optional[QuizResponse] = None
    
    class Config:
        from_attributes = True

class QuizResponseResponse(QuizResponseBase):
    AttemptID: int
    
    class Config:
        from_attributes = True

# Progress and enrollment schemas
class CourseProgressResponse(BaseModel):
    course: CourseResponse
    enrollment: EmployeeCourseResponse
    completed_modules: int
    total_modules: int
    progress_percentage: float
    total_time_spent_minutes: int
    estimated_time_remaining_minutes: int
    
    class Config:
        from_attributes = True

class EmployeeProgressSummaryResponse(BaseModel):
    total_enrollments: int
    completed_courses: int
    in_progress_courses: int
    total_badges_earned: int
    total_time_spent_hours: float
    recent_activity: List[dict] = []
    
    class Config:
        from_attributes = True

# Quiz attempt limit schemas
class QuizAttemptLimitResponse(BaseModel):
    LimitID: int
    EmployeeID: int
    QuizID: int
    AttemptCount: int
    LastAttemptDate: Optional[datetime] = None
    CooldownUntil: Optional[datetime] = None
    CanAttempt: bool
    RemainingAttempts: int
    CooldownDaysRemaining: Optional[int] = None
    
    class Config:
        from_attributes = True

# Badge earning schemas
class BadgeEarningResponse(BaseModel):
    badge: BadgeDefinitionResponse
    earned_at: datetime
    earning_reason: str  # e.g., "Course Completion", "Quiz Mastery"
    
    class Config:
        from_attributes = True

# Validation schemas
class QuizSubmissionRequest(BaseModel):
    responses: List[QuizResponseCreate]
    
    @validator('responses')
    def validate_responses(cls, v):
        if not v:
            raise ValueError('At least one response is required')
        return v

class ModuleCompletionRequest(BaseModel):
    time_spent_minutes: Optional[int] = None
    
    @validator('time_spent_minutes')
    def validate_time_spent(cls, v):
        if v is not None and v < 0:
            raise ValueError('Time spent cannot be negative')
        return v 