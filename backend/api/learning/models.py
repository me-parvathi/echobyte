from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, Text, DECIMAL, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
from api.employee.models import Employee

class Course(Base):
    __tablename__ = "Courses"
    
    CourseID = Column(Integer, primary_key=True, autoincrement=True)
    CourseCode = Column(String(50), nullable=False, unique=True)
    Title = Column(String(200), nullable=False)
    Difficulty = Column(String(20), nullable=False)  # Beginner, Intermediate, Advanced
    EstimatedHours = Column(DECIMAL(5, 2), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    modules = relationship("CourseModule", back_populates="course", order_by="CourseModule.ModuleSeq")
    enrollments = relationship("EmployeeCourse", back_populates="course")
    quizzes = relationship("Quiz", back_populates="course")

class CourseModule(Base):
    __tablename__ = "CourseModules"
    
    ModuleID = Column(Integer, primary_key=True, autoincrement=True)
    CourseID = Column(Integer, ForeignKey("Courses.CourseID"), nullable=False)
    ModuleSeq = Column(Integer, nullable=False)  # controls ordering
    Title = Column(String(200), nullable=False)
    VideoURL = Column(String(500), nullable=False)
    VideoType = Column(String(1), nullable=False, default='I')  # 'I'=iframe/embed, 'L'=link
    
    # Relationships
    course = relationship("Course", back_populates="modules")
    progress_records = relationship("EmployeeModuleProgress", back_populates="module")
    
    __table_args__ = (
        CheckConstraint("VideoType IN ('I','L')", name="CHK_CourseModules_VideoType"),
    )

class EmployeeCourse(Base):
    __tablename__ = "EmployeeCourses"
    
    EmployeeCourseID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    CourseID = Column(Integer, ForeignKey("Courses.CourseID"), nullable=False)
    Status = Column(String(20), nullable=False, default='In-Progress')  # In-Progress, Completed, Dropped
    EnrolledAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    CompletedAt = Column(DateTime, nullable=True)
    
    # Relationships
    employee = relationship("Employee")
    course = relationship("Course", back_populates="enrollments")
    module_progress = relationship("EmployeeModuleProgress", back_populates="enrollment")
    
    __table_args__ = (
        CheckConstraint("Status IN ('In-Progress', 'Completed', 'Dropped')", name="CHK_EmployeeCourses_Status"),
    )

class EmployeeModuleProgress(Base):
    __tablename__ = "EmployeeModuleProgress"
    
    EmpCourseID = Column(Integer, ForeignKey("EmployeeCourses.EmployeeCourseID"), primary_key=True)
    ModuleID = Column(Integer, ForeignKey("CourseModules.ModuleID"), primary_key=True)
    CompletedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    TimeSpentMinutes = Column(Integer, nullable=True)  # Track time spent on module
    
    # Relationships
    enrollment = relationship("EmployeeCourse", back_populates="module_progress")
    module = relationship("CourseModule", back_populates="progress_records")

class BadgeDefinition(Base):
    __tablename__ = "BadgeDefinitions"
    
    BadgeID = Column(Integer, primary_key=True, autoincrement=True)
    BadgeCode = Column(String(50), nullable=False, unique=True)
    Name = Column(String(200), nullable=False)
    Description = Column(String(500), nullable=True)
    IconURL = Column(String(500), nullable=True)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    CourseID = Column(Integer, ForeignKey("Courses.CourseID"), nullable=True)
    QuizID = Column(Integer, ForeignKey("Quizzes.QuizID"), nullable=True)
    
    # Relationships
    employee_badges = relationship("EmployeeBadge", back_populates="badge")
    course = relationship("Course")
    quiz = relationship("Quiz")

class EmployeeBadge(Base):
    __tablename__ = "EmployeeBadges"
    
    EmployeeBadgeID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    BadgeID = Column(Integer, ForeignKey("BadgeDefinitions.BadgeID"), nullable=False)
    EarnedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    
    # Relationships
    employee = relationship("Employee")
    badge = relationship("BadgeDefinition", back_populates="employee_badges")

class Quiz(Base):
    __tablename__ = "Quizzes"
    
    QuizID = Column(Integer, primary_key=True, autoincrement=True)
    CourseID = Column(Integer, ForeignKey("Courses.CourseID"), nullable=True)  # optional link to course
    Title = Column(String(200), nullable=False)
    QuestionCount = Column(Integer, nullable=False)
    TimeLimitMin = Column(Integer, nullable=False)  # in minutes
    PassingPct = Column(DECIMAL(5, 2), nullable=False)  # e.g. 70.00
    IsActive = Column(Boolean, nullable=False, default=True)
    
    # Relationships
    course = relationship("Course", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", order_by="QuizQuestion.QuestionSeq")
    attempts = relationship("QuizAttempt", back_populates="quiz")

class QuizQuestion(Base):
    __tablename__ = "QuizQuestions"
    
    QuestionID = Column(Integer, primary_key=True, autoincrement=True)
    QuizID = Column(Integer, ForeignKey("Quizzes.QuizID"), nullable=False)
    QuestionSeq = Column(Integer, nullable=False)  # display order within the quiz
    QuestionText = Column(Text, nullable=False)
    Explanation = Column(Text, nullable=True)  # optional
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    options = relationship("QuizOption", back_populates="question", order_by="QuizOption.OptionSeq")
    responses = relationship("QuizResponse", back_populates="question")
    response_scores = relationship("QuizResponseScore", back_populates="question")

class QuizOption(Base):
    __tablename__ = "QuizOptions"
    
    OptionID = Column(Integer, primary_key=True, autoincrement=True)
    QuestionID = Column(Integer, ForeignKey("QuizQuestions.QuestionID"), nullable=False)
    OptionSeq = Column(Integer, nullable=False)  # A/B/C… or 1/2/3…
    OptionText = Column(Text, nullable=False)
    IsCorrect = Column(Boolean, nullable=False)
    
    # Relationships
    question = relationship("QuizQuestion", back_populates="options")
    responses = relationship("QuizResponse", back_populates="option")

class QuizAttempt(Base):
    __tablename__ = "QuizAttempts"
    
    AttemptID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    QuizID = Column(Integer, ForeignKey("Quizzes.QuizID"), nullable=False)
    StartedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    CompletedAt = Column(DateTime, nullable=True)
    ScorePct = Column(DECIMAL(5, 2), nullable=True)
    IsPassed = Column(Boolean, nullable=True)
    
    # Relationships
    employee = relationship("Employee")
    quiz = relationship("Quiz", back_populates="attempts")
    responses = relationship("QuizResponse", back_populates="attempt")
    response_scores = relationship("QuizResponseScore", back_populates="attempt")

class QuizResponse(Base):
    __tablename__ = "QuizResponses"
    
    AttemptID = Column(Integer, ForeignKey("QuizAttempts.AttemptID"), primary_key=True)
    QuestionID = Column(Integer, ForeignKey("QuizQuestions.QuestionID"), primary_key=True)
    OptionID = Column(Integer, ForeignKey("QuizOptions.OptionID"), primary_key=True)
    
    # Relationships
    attempt = relationship("QuizAttempt", back_populates="responses")
    question = relationship("QuizQuestion", back_populates="responses")
    option = relationship("QuizOption", back_populates="responses")

class QuizResponseScore(Base):
    __tablename__ = "QuizResponseScores"
    
    AttemptID = Column(Integer, ForeignKey("QuizAttempts.AttemptID"), primary_key=True)
    QuestionID = Column(Integer, ForeignKey("QuizQuestions.QuestionID"), primary_key=True)
    IsCorrect = Column(Boolean, nullable=False)
    
    # Relationships
    attempt = relationship("QuizAttempt", back_populates="response_scores")
    question = relationship("QuizQuestion", back_populates="response_scores")

class QuizAttemptLimit(Base):
    __tablename__ = "QuizAttemptLimits"
    
    LimitID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"), nullable=False)
    QuizID = Column(Integer, ForeignKey("Quizzes.QuizID"), nullable=False)
    AttemptCount = Column(Integer, nullable=False, default=0)
    LastAttemptDate = Column(DateTime, nullable=True)
    CooldownUntil = Column(DateTime, nullable=True)  # When cooldown period ends
    CreatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate())
    UpdatedAt = Column(DateTime, nullable=False, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    employee = relationship("Employee")
    quiz = relationship("Quiz")
    
    __table_args__ = (
        CheckConstraint("AttemptCount >= 0", name="CHK_QuizAttemptLimits_AttemptCount"),
    ) 