from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.auth import get_current_active_user
from api.employee.service import EmployeeService
from . import schemas, service
from sqlalchemy import func, and_
from . import models

router = APIRouter()

# Course Management Routes
@router.get("/courses", response_model=schemas.CourseListResponse)
def get_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty level"),
    search: Optional[str] = Query(None, description="Search in title and course code"),
    db: Session = Depends(get_db)
):
    """Get list of all courses with filtering and pagination"""
    courses, total = service.CourseService.get_courses_with_count(
        db, skip=skip, limit=limit, is_active=is_active, 
        difficulty=difficulty, search=search
    )
    
    return schemas.CourseListResponse(
        courses=courses,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/courses/{course_id}", response_model=schemas.CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get course details with modules"""
    course = service.CourseService.get_course_with_modules(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.get("/courses/{course_id}/modules", response_model=List[schemas.CourseModuleResponse])
def get_course_modules(course_id: int, db: Session = Depends(get_db)):
    """Get modules for a specific course"""
    modules = service.CourseService.get_course_modules(db, course_id)
    return modules

@router.get("/modules/{module_id}", response_model=schemas.CourseModuleResponse)
def get_module(module_id: int, db: Session = Depends(get_db)):
    """Get specific module details"""
    module = service.CourseService.get_module(db, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module

# Enrollment Management Routes
@router.get("/enrollments", response_model=List[schemas.EmployeeCourseResponse])
def get_enrollments(
    status: Optional[str] = Query(None, description="Filter by enrollment status"),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's course enrollments"""
    employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    enrollments = service.EnrollmentService.get_employee_enrollments(
        db, employee.EmployeeID, status=status
    )
    return enrollments

@router.post("/enrollments", response_model=schemas.EmployeeCourseResponse, status_code=201)
def create_enrollment(
    enrollment: schemas.EmployeeCourseCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enroll current user in a course"""
    employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    enrollment_record = service.EnrollmentService.create_enrollment(
        db, employee.EmployeeID, enrollment.CourseID
    )
    return enrollment_record

@router.put("/enrollments/{enrollment_id}", response_model=schemas.EmployeeCourseResponse)
def update_enrollment(
    enrollment_id: int,
    enrollment_update: schemas.EmployeeCourseUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update enrollment status"""
    employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    # Verify enrollment belongs to current user
    enrollment = service.EnrollmentService.get_enrollment(db, enrollment_id)
    if not enrollment or enrollment.EmployeeID != employee.EmployeeID:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    updated_enrollment = service.EnrollmentService.update_enrollment(
        db, enrollment_id, enrollment_update
    )
    if not updated_enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    return updated_enrollment

@router.get("/employee-courses/{enrollment_id}", response_model=schemas.EmployeeCourseResponse)
def get_enrollment_details(
    enrollment_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed enrollment information"""
    employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    enrollment = service.EnrollmentService.get_enrollment(db, enrollment_id)
    if not enrollment or enrollment.EmployeeID != employee.EmployeeID:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    return enrollment

# Progress Tracking Routes
@router.get("/employeeModuleProgress", response_model=List[schemas.EmployeeModuleProgressResponse])
def get_module_progress(
    course_id: Optional[int] = Query(None, description="Filter by course ID"),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get module progress for current user"""
    employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    progress_records = service.ProgressService.get_module_progress(
        db, employee.EmployeeID, course_id=course_id
    )
    return progress_records

@router.post("/employeeModuleProgress", response_model=schemas.EmployeeModuleProgressResponse)
def mark_module_completed(
    progress: schemas.EmployeeModuleProgressCreate,
    completion: schemas.ModuleCompletionRequest,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a module as completed"""
    print(f"DEBUG: Route called - ModuleID: {progress.ModuleID}, TimeSpent: {completion.time_spent_minutes}")
    
    employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        print(f"DEBUG: Employee not found for user {current_user.UserID}")
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    print(f"DEBUG: Found employee {employee.EmployeeID}")
    
    # Find enrollment for this course
    enrollment = service.EnrollmentService.get_employee_enrollments(
        db, employee.EmployeeID
    )
    
    print(f"DEBUG: Found {len(enrollment)} enrollments for employee {employee.EmployeeID}")
    
    # Find the enrollment that matches the course of this module
    module = service.CourseService.get_module(db, progress.ModuleID)
    if not module:
        print(f"DEBUG: Module {progress.ModuleID} not found")
        raise HTTPException(status_code=404, detail="Module not found")
    
    print(f"DEBUG: Found module {progress.ModuleID} for course {module.CourseID}")
    
    matching_enrollment = None
    for enrollment_record in enrollment:
        if enrollment_record.CourseID == module.CourseID:
            matching_enrollment = enrollment_record
            break
    
    if not matching_enrollment:
        print(f"DEBUG: No matching enrollment found for course {module.CourseID}")
        raise HTTPException(status_code=404, detail="Not enrolled in this course")
    
    print(f"DEBUG: Found matching enrollment {matching_enrollment.EmployeeCourseID} for course {module.CourseID}")
    
    progress_record = service.ProgressService.mark_module_completed(
        db, matching_enrollment.EmployeeCourseID, progress.ModuleID, 
        completion.time_spent_minutes
    )
    
    print(f"DEBUG: Progress record created successfully")
    return progress_record

@router.get("/employee/progress-summary", response_model=schemas.EmployeeProgressSummaryResponse)
def get_employee_progress_summary(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get employee progress summary"""
    employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    return service.ProgressService.get_employee_progress_summary(db, employee.EmployeeID)

@router.get("/employee/progress-summary/debug")
def get_employee_progress_summary_debug(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Debug endpoint to show detailed learning hours calculation"""
    employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    # Get detailed breakdown
    actual_time_minutes = db.query(func.sum(models.EmployeeModuleProgress.TimeSpentMinutes)).join(
        models.EmployeeCourse
    ).filter(
        and_(
            models.EmployeeCourse.EmployeeID == employee.EmployeeID,
            models.EmployeeModuleProgress.TimeSpentMinutes.isnot(None)
        )
    ).scalar() or 0
    
    # Get completed courses with estimated hours
    completed_courses_data = db.query(models.EmployeeCourse, models.Course).join(
        models.Course
    ).filter(
        and_(
            models.EmployeeCourse.EmployeeID == employee.EmployeeID,
            models.EmployeeCourse.Status == 'Completed'
        )
    ).all()
    
    estimated_time_minutes = 0
    completed_courses_breakdown = []
    for enrollment, course in completed_courses_data:
        course_hours = float(course.EstimatedHours) if course.EstimatedHours else 0
        course_minutes = course_hours * 60
        estimated_time_minutes += course_minutes
        completed_courses_breakdown.append({
            "course_id": course.CourseID,
            "course_title": course.Title,
            "estimated_hours": course_hours,
            "estimated_minutes": course_minutes
        })
    
    # Get in-progress courses
    in_progress_courses_data = db.query(models.EmployeeCourse, models.Course).join(
        models.Course
    ).filter(
        and_(
            models.EmployeeCourse.EmployeeID == employee.EmployeeID,
            models.EmployeeCourse.Status == 'In-Progress'
        )
    ).all()
    
    partial_time_minutes = 0
    in_progress_breakdown = []
    for enrollment, course in in_progress_courses_data:
        total_modules = db.query(models.CourseModule).filter(
            models.CourseModule.CourseID == course.CourseID
        ).count()
        
        completed_modules = db.query(models.EmployeeModuleProgress).filter(
            models.EmployeeModuleProgress.EmpCourseID == enrollment.EmployeeCourseID
        ).count()
        
        course_hours = float(course.EstimatedHours) if course.EstimatedHours else 0
        course_minutes = course_hours * 60
        
        if total_modules > 0:
            completion_percentage = completed_modules / total_modules
            partial_minutes = course_minutes * completion_percentage
            partial_time_minutes += partial_minutes
            
            in_progress_breakdown.append({
                "course_id": course.CourseID,
                "course_title": course.Title,
                "estimated_hours": course_hours,
                "total_modules": total_modules,
                "completed_modules": completed_modules,
                "completion_percentage": round(completion_percentage * 100, 1),
                "partial_minutes": round(partial_minutes, 1)
            })
    
    total_time_minutes = max(actual_time_minutes, estimated_time_minutes)
    
    # Add partial time for in-progress courses
    total_time_minutes += partial_time_minutes
    
    total_time_hours = total_time_minutes / 60
    
    return {
        "employee_id": employee.EmployeeID,
        "actual_time_minutes": actual_time_minutes,
        "actual_time_hours": round(actual_time_minutes / 60, 2),
        "estimated_time_minutes": estimated_time_minutes,
        "estimated_time_hours": round(estimated_time_minutes / 60, 2),
        "partial_time_minutes": partial_time_minutes,
        "partial_time_hours": round(partial_time_minutes / 60, 2),
        "total_time_minutes": total_time_minutes,
        "total_time_hours": round(total_time_hours, 2),
        "completed_courses": completed_courses_breakdown,
        "in_progress_courses": in_progress_breakdown
    }

@router.get("/employee/{employee_id}/progress-summary", response_model=schemas.EmployeeProgressSummaryResponse)
def get_employee_progress_summary(
    employee_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get overall progress dashboard for an employee"""
    # Verify current user is requesting their own progress or has appropriate permissions
    current_employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not current_employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    if current_employee.EmployeeID != employee_id:
        raise HTTPException(status_code=403, detail="Can only view own progress")
    
    progress_summary = service.ProgressService.get_employee_progress_summary(db, employee_id)
    return progress_summary

@router.get("/courses/{course_id}/progress", response_model=schemas.CourseProgressResponse)
def get_course_progress(
    course_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed progress for a specific course"""
    employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    progress = service.ProgressService.get_course_progress(db, employee.EmployeeID, course_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Not enrolled in this course")
    
    return progress

# Quiz System Routes
@router.get("/quizzes", response_model=List[schemas.QuizResponse])
def get_quizzes(
    course_id: Optional[int] = Query(None, description="Filter by course ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """Get list of all quizzes"""
    quizzes = service.QuizService.get_quizzes(db, course_id=course_id, is_active=is_active)
    return quizzes

@router.get("/quizzes/{quiz_id}", response_model=schemas.QuizResponse)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Get quiz details"""
    quiz = service.QuizService.get_quiz_with_questions(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@router.get("/quizzes/{quiz_id}/questions", response_model=List[schemas.QuizQuestionResponse])
def get_quiz_questions(quiz_id: int, db: Session = Depends(get_db)):
    """Get quiz questions with options"""
    quiz = service.QuizService.get_quiz_with_questions(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz.questions

@router.get("/quizzes/{quiz_id}/questions/random", response_model=List[schemas.QuizQuestionResponse])
def get_random_quiz_questions(
    quiz_id: int, 
    question_count: int = Query(5, ge=1, le=20, description="Number of random questions to return"),
    db: Session = Depends(get_db)
):
    """Get random questions for a quiz with their options"""
    # Verify quiz exists
    quiz = service.QuizService.get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    questions = service.QuizService.get_random_quiz_questions(db, quiz_id, question_count)
    return questions

@router.get("/quizzes/{quiz_id}/random-questions", response_model=List[schemas.QuizQuestionResponse])
def get_authenticated_random_quiz_questions(
    quiz_id: int,
    question_count: int = Query(5, ge=1, le=20),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    questions = service.QuizService.get_random_quiz_questions(db, quiz_id, question_count)
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this quiz")
    
    return questions

@router.get("/quizzes/{quiz_id}/cooldown-info")
def get_quiz_cooldown_info(
    quiz_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get cooldown information for a quiz without starting an attempt"""
    employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    cooldown_info = service.QuizService.get_quiz_cooldown_info(db, employee.EmployeeID, quiz_id)
    return cooldown_info

@router.get("/quiz-questions/{question_id}/options", response_model=List[schemas.QuizOptionResponse])
def get_question_options(question_id: int, db: Session = Depends(get_db)):
    """Get answer options for a specific question"""
    question = db.query(models.QuizQuestion).options(
        joinedload(models.QuizQuestion.options)
    ).filter(models.QuizQuestion.QuestionID == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return question.options

@router.get("/quizAttempts", response_model=List[schemas.QuizAttemptResponse])
def get_quiz_attempts(
    quiz_id: Optional[int] = Query(None, description="Filter by quiz ID"),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's quiz attempts"""
    employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    attempts = service.QuizService.get_employee_attempts(
        db, employee.EmployeeID, quiz_id=quiz_id
    )
    return attempts

@router.post("/quizAttempts", response_model=schemas.QuizAttemptResponse, status_code=201)
def start_quiz_attempt(
    attempt: schemas.QuizAttemptCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start a new quiz attempt"""
    employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    quiz_attempt = service.QuizService.start_quiz_attempt(
        db, employee.EmployeeID, attempt.QuizID
    )
    return quiz_attempt

@router.put("/quizAttempts/{attempt_id}", response_model=schemas.QuizAttemptResponse)
def submit_quiz_attempt(
    attempt_id: int,
    submission: schemas.QuizSubmissionRequest,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit completed quiz attempt"""
    employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    # Verify attempt belongs to current user
    attempt = db.query(models.QuizAttempt).filter(
        models.QuizAttempt.AttemptID == attempt_id
    ).first()
    
    if not attempt or attempt.EmployeeID != employee.EmployeeID:
        raise HTTPException(status_code=404, detail="Quiz attempt not found")
    
    completed_attempt = service.QuizService.submit_quiz_attempt(
        db, attempt_id, submission.responses
    )
    return completed_attempt

@router.get("/quizAttempts/{attempt_id}/results")
def get_quiz_results(
    attempt_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed quiz results with correct answers and explanations"""
    employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    # Verify attempt belongs to current user
    attempt = db.query(models.QuizAttempt).filter(
        models.QuizAttempt.AttemptID == attempt_id
    ).first()
    
    if not attempt or attempt.EmployeeID != employee.EmployeeID:
        raise HTTPException(status_code=404, detail="Quiz attempt not found")
    
    results = service.QuizService.get_quiz_results(db, attempt_id)
    return results

# Badge System Routes
@router.get("/badges", response_model=List[schemas.BadgeDefinitionResponse])
def get_badges(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """Get list of all available badges"""
    badges = service.BadgeService.get_badges(db, is_active=is_active)
    return badges

@router.get("/employeeBadges", response_model=List[schemas.EmployeeBadgeResponse])
def get_employee_badges(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's earned badges"""
    employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    badges = service.BadgeService.get_employee_badges(db, employee.EmployeeID)
    return badges

@router.post("/employeeBadges", response_model=schemas.EmployeeBadgeResponse, status_code=201)
def award_badge(
    badge_award: schemas.BadgeDefinitionCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Award a badge to current user (for testing purposes)"""
    employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    # Find badge by code
    badge = db.query(models.BadgeDefinition).filter(
        models.BadgeDefinition.BadgeCode == badge_award.BadgeCode
    ).first()
    
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")
    
    employee_badge = service.BadgeService.award_badge(
        db, employee.EmployeeID, badge.BadgeID, "Manual Award"
    )
    return employee_badge

# Course Badge Routes
@router.get("/courses/{course_id}/badges", response_model=List[schemas.BadgeDefinitionResponse])
def get_course_badges(course_id: int, db: Session = Depends(get_db)):
    """Get all badges linked to a specific course"""
    badges = service.BadgeService.get_course_badges(db, course_id)
    return badges

@router.get("/courses/{course_id}/available-badges", response_model=List[schemas.BadgeDefinitionResponse])
def get_available_badges_for_course(course_id: int, db: Session = Depends(get_db)):
    """Get all badges that can be earned for a specific course"""
    badges = service.BadgeService.get_available_badges_for_course(db, course_id)
    return badges

# Quiz Badge Routes
@router.get("/quizzes/{quiz_id}/badges", response_model=List[schemas.BadgeDefinitionResponse])
def get_quiz_badges(quiz_id: int, db: Session = Depends(get_db)):
    """Get all badges linked to a specific quiz"""
    badges = service.BadgeService.get_quiz_badges(db, quiz_id)
    return badges

# Employee Course Badge Routes
@router.get("/employees/{employee_id}/course-badges/{course_id}", response_model=List[schemas.EmployeeBadgeResponse])
def get_employee_course_badges(
    employee_id: int, 
    course_id: int, 
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get badges earned by employee for a specific course"""
    # Verify current user is requesting their own badges or has appropriate permissions
    current_employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not current_employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    if current_employee.EmployeeID != employee_id:
        raise HTTPException(status_code=403, detail="Can only view own badges")
    
    # Get all employee badges
    employee_badges = service.BadgeService.get_employee_badges(db, employee_id)
    
    # Filter badges that are linked to the specific course
    course_badges = []
    for employee_badge in employee_badges:
        if employee_badge.badge and employee_badge.badge.CourseID == course_id:
            course_badges.append(employee_badge)
    
    return course_badges

@router.post("/employees/{employee_id}/check-missing-badges")
def check_and_award_missing_badges(
    employee_id: int, 
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check for completed courses and award missing badges"""
    # Check if user is requesting their own badges or is admin
    current_employee = EmployeeService.get_employee_by_user_id(db, current_user.UserID)
    if not current_employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    if current_employee.EmployeeID != employee_id:
        raise HTTPException(status_code=403, detail="Can only check own missing badges")
    
    print(f"DEBUG: Route called to check missing badges for employee {employee_id}")
    service.BadgeService.check_and_award_missing_badges(db, employee_id)
    
    return {"message": "Missing badges check completed", "employee_id": employee_id} 