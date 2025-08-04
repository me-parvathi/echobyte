from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import random
from . import models, schemas
from fastapi import HTTPException
from api.employee.models import Employee

class CourseService:
    
    @staticmethod
    def get_courses(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None,
        difficulty: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[models.Course]:
        query = db.query(models.Course)
        
        if is_active is not None:
            query = query.filter(models.Course.IsActive == is_active)
        
        if difficulty:
            query = query.filter(models.Course.Difficulty == difficulty)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    models.Course.Title.ilike(search_term),
                    models.Course.CourseCode.ilike(search_term)
                )
            )
        
        return query.order_by(models.Course.CourseID).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_courses_with_count(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        difficulty: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[models.Course], int]:
        query = db.query(models.Course)
        
        if is_active is not None:
            query = query.filter(models.Course.IsActive == is_active)
        
        if difficulty:
            query = query.filter(models.Course.Difficulty == difficulty)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    models.Course.Title.ilike(search_term),
                    models.Course.CourseCode.ilike(search_term)
                )
            )
        
        # Load modules relationship for each course
        courses = query.options(
            joinedload(models.Course.modules)
        ).order_by(models.Course.CourseID).offset(skip).limit(limit).all()
        
        # Efficient count calculation
        if skip == 0 and len(courses) < limit:
            total_count = len(courses)
        else:
            total_count = query.count()
        
        return courses, total_count
    
    @staticmethod
    def get_course(db: Session, course_id: int) -> Optional[models.Course]:
        return db.query(models.Course).filter(models.Course.CourseID == course_id).first()
    
    @staticmethod
    def get_course_with_modules(db: Session, course_id: int) -> Optional[models.Course]:
        return db.query(models.Course).options(
            joinedload(models.Course.modules)
        ).filter(models.Course.CourseID == course_id).first()
    
    @staticmethod
    def get_course_modules(db: Session, course_id: int) -> List[models.CourseModule]:
        return db.query(models.CourseModule).filter(
            models.CourseModule.CourseID == course_id
        ).order_by(models.CourseModule.ModuleSeq).all()
    
    @staticmethod
    def get_module(db: Session, module_id: int) -> Optional[models.CourseModule]:
        return db.query(models.CourseModule).filter(models.CourseModule.ModuleID == module_id).first()

class EnrollmentService:
    
    @staticmethod
    def get_employee_enrollments(
        db: Session, 
        employee_id: int,
        status: Optional[str] = None
    ) -> List[models.EmployeeCourse]:
        query = db.query(models.EmployeeCourse).filter(
            models.EmployeeCourse.EmployeeID == employee_id
        )
        
        if status:
            query = query.filter(models.EmployeeCourse.Status == status)
        
        return query.order_by(desc(models.EmployeeCourse.EnrolledAt)).all()
    
    @staticmethod
    def get_enrollment(db: Session, enrollment_id: int) -> Optional[models.EmployeeCourse]:
        return db.query(models.EmployeeCourse).options(
            joinedload(models.EmployeeCourse.course)
        ).filter(models.EmployeeCourse.EmployeeCourseID == enrollment_id).first()
    
    @staticmethod
    def create_enrollment(
        db: Session, 
        employee_id: int, 
        course_id: int
    ) -> models.EmployeeCourse:
        # Check if already enrolled
        existing = db.query(models.EmployeeCourse).filter(
            and_(
                models.EmployeeCourse.EmployeeID == employee_id,
                models.EmployeeCourse.CourseID == course_id
            )
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Already enrolled in this course")
        
        # Check if course exists and is active
        course = db.query(models.Course).filter(
            and_(
                models.Course.CourseID == course_id,
                models.Course.IsActive == True
            )
        ).first()
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found or inactive")
        
        enrollment = models.EmployeeCourse(
            EmployeeID=employee_id,
            CourseID=course_id,
            Status='In-Progress'
        )
        
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        return enrollment
    
    @staticmethod
    def update_enrollment(
        db: Session, 
        enrollment_id: int, 
        enrollment_update: schemas.EmployeeCourseUpdate
    ) -> Optional[models.EmployeeCourse]:
        enrollment = db.query(models.EmployeeCourse).filter(
            models.EmployeeCourse.EmployeeCourseID == enrollment_id
        ).first()
        
        if not enrollment:
            return None
        
        for field, value in enrollment_update.dict(exclude_unset=True).items():
            setattr(enrollment, field, value)
        
        db.commit()
        db.refresh(enrollment)
        return enrollment

class ProgressService:
    
    @staticmethod
    def get_module_progress(
        db: Session, 
        employee_id: int,
        course_id: Optional[int] = None
    ) -> List[models.EmployeeModuleProgress]:
        query = db.query(models.EmployeeModuleProgress).join(
            models.EmployeeCourse
        ).filter(models.EmployeeCourse.EmployeeID == employee_id)
        
        if course_id:
            query = query.filter(models.EmployeeCourse.CourseID == course_id)
        
        return query.all()
    
    @staticmethod
    def mark_module_completed(
        db: Session, 
        enrollment_id: int, 
        module_id: int,
        time_spent_minutes: Optional[int] = None
    ) -> models.EmployeeModuleProgress:
        print(f"DEBUG: mark_module_completed called - enrollment_id: {enrollment_id}, module_id: {module_id}")
        
        # Check if enrollment exists
        enrollment = db.query(models.EmployeeCourse).filter(
            models.EmployeeCourse.EmployeeCourseID == enrollment_id
        ).first()
        
        if not enrollment:
            print(f"DEBUG: No enrollment found for enrollment_id {enrollment_id}")
            raise HTTPException(status_code=404, detail="Enrollment not found")
        
        print(f"DEBUG: Found enrollment for course {enrollment.CourseID}, employee {enrollment.EmployeeID}")
        
        # Check if module exists and belongs to the course
        module = db.query(models.CourseModule).filter(
            and_(
                models.CourseModule.ModuleID == module_id,
                models.CourseModule.CourseID == enrollment.CourseID
            )
        ).first()
        
        if not module:
            print(f"DEBUG: Module {module_id} not found or doesn't belong to course {enrollment.CourseID}")
            raise HTTPException(status_code=404, detail="Module not found or doesn't belong to course")
        
        print(f"DEBUG: Found module {module_id} ({module.Title}) for course {enrollment.CourseID}")
        
        # Check if already completed
        existing_progress = db.query(models.EmployeeModuleProgress).filter(
            and_(
                models.EmployeeModuleProgress.EmpCourseID == enrollment_id,
                models.EmployeeModuleProgress.ModuleID == module_id
            )
        ).first()
        
        if existing_progress:
            print(f"DEBUG: Module {module_id} already completed, updating time spent")
            # Update time spent if provided
            if time_spent_minutes is not None:
                existing_progress.TimeSpentMinutes = time_spent_minutes
                db.commit()
                db.refresh(existing_progress)
            return existing_progress
        
        print(f"DEBUG: Creating new progress record for module {module_id}")
        
        # Create new progress record
        progress = models.EmployeeModuleProgress(
            EmpCourseID=enrollment_id,
            ModuleID=module_id,
            TimeSpentMinutes=time_spent_minutes
        )
        
        db.add(progress)
        db.commit()
        db.refresh(progress)
        
        print(f"DEBUG: Progress record created, checking course completion")
        
        # Check if course is completed
        ProgressService._check_course_completion(db, enrollment_id)
        
        return progress
    
    @staticmethod
    def _check_course_completion(db: Session, enrollment_id: int):
        """Check if all modules are completed and update enrollment status"""
        enrollment = db.query(models.EmployeeCourse).filter(
            models.EmployeeCourse.EmployeeCourseID == enrollment_id
        ).first()
        
        if not enrollment:
            print(f"DEBUG: No enrollment found for enrollment_id {enrollment_id}")
            return
        
        # Get total modules for the course
        total_modules = db.query(models.CourseModule).filter(
            models.CourseModule.CourseID == enrollment.CourseID
        ).count()
        
        # Get completed modules
        completed_modules = db.query(models.EmployeeModuleProgress).filter(
            models.EmployeeModuleProgress.EmpCourseID == enrollment_id
        ).count()
        
        print(f"DEBUG: Course {enrollment.CourseID} - Total modules: {total_modules}, Completed modules: {completed_modules}, Current status: {enrollment.Status}")
        
        # If all modules completed, mark course as completed
        if completed_modules >= total_modules and enrollment.Status != 'Completed':
            print(f"DEBUG: Marking course {enrollment.CourseID} as completed for employee {enrollment.EmployeeID}")
            enrollment.Status = 'Completed'
            enrollment.CompletedAt = datetime.utcnow()
            db.commit()
            
            # Award course completion badge
            print(f"DEBUG: Awarding course completion badge for course {enrollment.CourseID}")
            BadgeService.award_course_completion_badge(db, enrollment.EmployeeID, enrollment.CourseID)
        else:
            print(f"DEBUG: Course {enrollment.CourseID} not completed yet. Need {total_modules} modules, have {completed_modules}")
    
    @staticmethod
    def get_course_progress(
        db: Session, 
        employee_id: int, 
        course_id: int
    ) -> Optional[schemas.CourseProgressResponse]:
        enrollment = db.query(models.EmployeeCourse).filter(
            and_(
                models.EmployeeCourse.EmployeeID == employee_id,
                models.EmployeeCourse.CourseID == course_id
            )
        ).first()
        
        if not enrollment:
            return None
        
        course = db.query(models.Course).filter(models.Course.CourseID == course_id).first()
        if not course:
            return None
        
        # Get progress data
        total_modules = db.query(models.CourseModule).filter(
            models.CourseModule.CourseID == course_id
        ).count()
        
        completed_modules = db.query(models.EmployeeModuleProgress).filter(
            models.EmployeeModuleProgress.EmpCourseID == enrollment.EmployeeCourseID
        ).count()
        
        # Calculate total time spent
        total_time = db.query(func.sum(models.EmployeeModuleProgress.TimeSpentMinutes)).filter(
            models.EmployeeModuleProgress.EmpCourseID == enrollment.EmployeeCourseID
        ).scalar() or 0
        
        progress_percentage = (completed_modules / total_modules * 100) if total_modules > 0 else 0
        estimated_remaining = (total_modules - completed_modules) * 30  # Assume 30 min per module
        
        return schemas.CourseProgressResponse(
            course=course,
            enrollment=enrollment,
            completed_modules=completed_modules,
            total_modules=total_modules,
            progress_percentage=progress_percentage,
            total_time_spent_minutes=total_time,
            estimated_time_remaining_minutes=estimated_remaining
        )
    
    @staticmethod
    def get_employee_progress_summary(db: Session, employee_id: int) -> schemas.EmployeeProgressSummaryResponse:
        # Get enrollment counts
        total_enrollments = db.query(models.EmployeeCourse).filter(
            models.EmployeeCourse.EmployeeID == employee_id
        ).count()
        
        completed_courses = db.query(models.EmployeeCourse).filter(
            and_(
                models.EmployeeCourse.EmployeeID == employee_id,
                models.EmployeeCourse.Status == 'Completed'
            )
        ).count()
        
        in_progress_courses = db.query(models.EmployeeCourse).filter(
            and_(
                models.EmployeeCourse.EmployeeID == employee_id,
                models.EmployeeCourse.Status == 'In-Progress'
            )
        ).count()
        
        # Get badge count
        total_badges = db.query(models.EmployeeBadge).filter(
            models.EmployeeBadge.EmployeeID == employee_id
        ).count()
        
        # Calculate total time spent - improved calculation
        # First, get actual time spent from completed modules
        actual_time_minutes = db.query(func.sum(models.EmployeeModuleProgress.TimeSpentMinutes)).join(
            models.EmployeeCourse
        ).filter(
            and_(
                models.EmployeeCourse.EmployeeID == employee_id,
                models.EmployeeModuleProgress.TimeSpentMinutes.isnot(None)
            )
        ).scalar() or 0
        
        # Get estimated time from completed courses
        completed_courses_data = db.query(models.EmployeeCourse, models.Course).join(
            models.Course
        ).filter(
            and_(
                models.EmployeeCourse.EmployeeID == employee_id,
                models.EmployeeCourse.Status == 'Completed'
            )
        ).all()
        
        estimated_time_minutes = 0
        for enrollment, course in completed_courses_data:
            # Convert course estimated hours to minutes
            course_hours = float(course.EstimatedHours) if course.EstimatedHours else 0
            estimated_time_minutes += course_hours * 60
        
        # For in-progress courses, calculate partial time based on completed modules
        in_progress_courses_data = db.query(models.EmployeeCourse, models.Course).join(
            models.Course
        ).filter(
            and_(
                models.EmployeeCourse.EmployeeID == employee_id,
                models.EmployeeCourse.Status == 'In-Progress'
            )
        ).all()
        
        partial_time_minutes = 0
        for enrollment, course in in_progress_courses_data:
            # Get total modules for this course
            total_modules = db.query(models.CourseModule).filter(
                models.CourseModule.CourseID == course.CourseID
            ).count()
            
            # Get completed modules for this course
            completed_modules = db.query(models.EmployeeModuleProgress).filter(
                models.EmployeeModuleProgress.EmpCourseID == enrollment.EmployeeCourseID
            ).count()
            
            if total_modules > 0:
                # Calculate partial time based on completion percentage
                completion_percentage = completed_modules / total_modules
                course_hours = float(course.EstimatedHours) if course.EstimatedHours else 0
                partial_time_minutes += (course_hours * 60) * completion_percentage
        
        # Total time calculation: Use the higher of actual or estimated time
        # This ensures we don't undercount when users complete modules
        total_time_minutes = max(actual_time_minutes, estimated_time_minutes)
        
        # Add partial time for in-progress courses
        total_time_minutes += partial_time_minutes
        
        total_time_hours = total_time_minutes / 60
        
        # Get recent activity (last 10 module completions)
        recent_activity = db.query(models.EmployeeModuleProgress).join(
            models.EmployeeCourse
        ).join(
            models.CourseModule
        ).filter(
            models.EmployeeCourse.EmployeeID == employee_id
        ).order_by(
            desc(models.EmployeeModuleProgress.CompletedAt)
        ).limit(10).all()
        
        activity_list = []
        for activity in recent_activity:
            activity_list.append({
                "type": "module_completion",
                "module_title": activity.module.Title if activity.module else "Unknown",
                "completed_at": activity.CompletedAt,
                "time_spent": activity.TimeSpentMinutes
            })
        
        return schemas.EmployeeProgressSummaryResponse(
            total_enrollments=total_enrollments,
            completed_courses=completed_courses,
            in_progress_courses=in_progress_courses,
            total_badges_earned=total_badges,
            total_time_spent_hours=total_time_hours,
            recent_activity=activity_list
        )

class QuizService:
    
    @staticmethod
    def get_quizzes(
        db: Session,
        course_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[models.Quiz]:
        query = db.query(models.Quiz)
        
        if course_id:
            query = query.filter(models.Quiz.CourseID == course_id)
        
        if is_active is not None:
            query = query.filter(models.Quiz.IsActive == is_active)
        
        return query.all()
    
    @staticmethod
    def get_quiz(db: Session, quiz_id: int) -> Optional[models.Quiz]:
        return db.query(models.Quiz).filter(models.Quiz.QuizID == quiz_id).first()
    
    @staticmethod
    def get_quiz_with_questions(db: Session, quiz_id: int) -> Optional[models.Quiz]:
        return db.query(models.Quiz).options(
            joinedload(models.Quiz.questions).joinedload(models.QuizQuestion.options)
        ).filter(models.Quiz.QuizID == quiz_id).first()
    
    @staticmethod
    def get_random_quiz_questions(db: Session, quiz_id: int, question_count: int = 5) -> List[models.QuizQuestion]:
        """Get random questions for a quiz with their options"""
        try:
            # Get total available questions
            total_questions = db.query(models.QuizQuestion).filter(
                models.QuizQuestion.QuizID == quiz_id,
                models.QuizQuestion.IsActive == True
            ).count()
            
            if total_questions == 0:
                return []
            
            # Adjust question count if needed
            actual_count = min(question_count, total_questions)
            
            # Use database-specific randomization
            query = db.query(models.QuizQuestion).options(
                joinedload(models.QuizQuestion.options)
            ).filter(
                models.QuizQuestion.QuizID == quiz_id,
                models.QuizQuestion.IsActive == True
            )
            
            # Database-specific randomization
            if hasattr(func, 'newid'):  # SQL Server
                query = query.order_by(func.newid())
            elif hasattr(func, 'rand'):  # MySQL
                query = query.order_by(func.rand())
            else:  # Fallback to application-level randomization
                questions = query.all()
                return random.sample(questions, actual_count)
            
            return query.limit(actual_count).all()
            
        except Exception as e:
            # Fallback to application-level randomization
            questions = db.query(models.QuizQuestion).options(
                joinedload(models.QuizQuestion.options)
            ).filter(
                models.QuizQuestion.QuizID == quiz_id,
                models.QuizQuestion.IsActive == True
            ).all()
            
            return random.sample(questions, min(question_count, len(questions)))

    @staticmethod
    def get_quiz_cooldown_info(db: Session, employee_id: int, quiz_id: int) -> dict:
        """Get cooldown information for a quiz without starting an attempt"""
        limit_record = db.query(models.QuizAttemptLimit).filter(
            and_(
                models.QuizAttemptLimit.EmployeeID == employee_id,
                models.QuizAttemptLimit.QuizID == quiz_id
            )
        ).first()
        
        if not limit_record:
            return {
                'can_attempt': True,
                'reason': None,
                'attempt_count': 0,
                'cooldown_until': None,
                'days_remaining': 0
            }
        
        # Check cooldown period
        if limit_record.CooldownUntil and limit_record.CooldownUntil > datetime.utcnow():
            days_remaining = (limit_record.CooldownUntil - datetime.utcnow()).days
            return {
                'can_attempt': False,
                'reason': f"Cooldown period active. {days_remaining} days remaining.",
                'attempt_count': limit_record.AttemptCount,
                'cooldown_until': limit_record.CooldownUntil,
                'days_remaining': days_remaining
            }
        
        # Check attempt count
        if limit_record.AttemptCount >= 2:
            return {
                'can_attempt': False,
                'reason': "Maximum attempts reached. Cooldown period of 4 weeks activated.",
                'attempt_count': limit_record.AttemptCount,
                'cooldown_until': limit_record.CooldownUntil,
                'days_remaining': 0
            }
        
        return {
            'can_attempt': True,
            'reason': None,
            'attempt_count': limit_record.AttemptCount,
            'cooldown_until': limit_record.CooldownUntil,
            'days_remaining': 0
        }

    @staticmethod
    def get_employee_attempts(
        db: Session, 
        employee_id: int,
        quiz_id: Optional[int] = None
    ) -> List[models.QuizAttempt]:
        query = db.query(models.QuizAttempt).filter(
            models.QuizAttempt.EmployeeID == employee_id
        )
        
        if quiz_id:
            query = query.filter(models.QuizAttempt.QuizID == quiz_id)
        
        return query.order_by(desc(models.QuizAttempt.StartedAt)).all()
    
    @staticmethod
    def start_quiz_attempt(
        db: Session, 
        employee_id: int, 
        quiz_id: int
    ) -> models.QuizAttempt:
        # Check attempt limits FIRST - before creating any records
        limit_info = QuizService._check_attempt_limits(db, employee_id, quiz_id)
        if not limit_info['can_attempt']:
            raise HTTPException(
                status_code=429, 
                detail=f"Cannot attempt quiz. {limit_info['reason']}"
            )
        
        try:
            # Create attempt only after validation passes
            attempt = models.QuizAttempt(
                EmployeeID=employee_id,
                QuizID=quiz_id
            )
            
            db.add(attempt)
            db.commit()
            db.refresh(attempt)
            
            # Update attempt count only after successful attempt creation
            QuizService._update_attempt_count(db, employee_id, quiz_id)
            
            return attempt
            
        except Exception as e:
            # Rollback on any error to prevent phantom attempts
            db.rollback()
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to start quiz attempt: {str(e)}"
            )
    
    @staticmethod
    def submit_quiz_attempt(
        db: Session,
        attempt_id: int,
        responses: List[schemas.QuizResponseCreate]
    ) -> models.QuizAttempt:
        attempt = db.query(models.QuizAttempt).filter(
            models.QuizAttempt.AttemptID == attempt_id
        ).first()
        
        if not attempt:
            raise HTTPException(status_code=404, detail="Quiz attempt not found")
        
        if attempt.CompletedAt:
            raise HTTPException(status_code=400, detail="Quiz attempt already completed")
        
        # Get quiz details
        quiz = db.query(models.Quiz).filter(models.Quiz.QuizID == attempt.QuizID).first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Process responses and calculate score
        correct_answers = 0
        total_questions = 0
        
        for response in responses:
            # Validate question belongs to quiz
            question = db.query(models.QuizQuestion).filter(
                and_(
                    models.QuizQuestion.QuestionID == response.QuestionID,
                    models.QuizQuestion.QuizID == quiz.QuizID
                )
            ).first()
            
            if not question:
                continue
            
            # Validate option belongs to question
            option = db.query(models.QuizOption).filter(
                and_(
                    models.QuizOption.OptionID == response.OptionID,
                    models.QuizOption.QuestionID == response.QuestionID
                )
            ).first()
            
            if not option:
                continue
            
            # Record response
            quiz_response = models.QuizResponse(
                AttemptID=attempt_id,
                QuestionID=response.QuestionID,
                OptionID=response.OptionID
            )
            db.add(quiz_response)
            
            # Record score
            score_record = models.QuizResponseScore(
                AttemptID=attempt_id,
                QuestionID=response.QuestionID,
                IsCorrect=option.IsCorrect
            )
            db.add(score_record)
            
            total_questions += 1
            if option.IsCorrect:
                correct_answers += 1
        
        # Calculate score percentage
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        is_passed = score_percentage >= quiz.PassingPct
        
        # Update attempt
        attempt.CompletedAt = datetime.utcnow()
        attempt.ScorePct = Decimal(str(score_percentage))
        attempt.IsPassed = is_passed
        
        db.commit()
        db.refresh(attempt)
        
        # Award badge if passed
        if is_passed:
            BadgeService.award_quiz_mastery_badge(db, attempt.EmployeeID, quiz.QuizID)
        
        return attempt
    
    @staticmethod
    def get_quiz_results(
        db: Session,
        attempt_id: int
    ) -> dict:
        """Get detailed quiz results with correct answers and explanations"""
        attempt = db.query(models.QuizAttempt).filter(
            models.QuizAttempt.AttemptID == attempt_id
        ).first()
        
        if not attempt:
            raise HTTPException(status_code=404, detail="Quiz attempt not found")
        
        # Get quiz details
        quiz = db.query(models.Quiz).filter(models.Quiz.QuizID == attempt.QuizID).first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Get user's responses with question and option details
        responses = db.query(
            models.QuizResponse,
            models.QuizQuestion,
            models.QuizOption,
            models.QuizResponseScore
        ).join(
            models.QuizQuestion, models.QuizResponse.QuestionID == models.QuizQuestion.QuestionID
        ).join(
            models.QuizOption, models.QuizResponse.OptionID == models.QuizOption.OptionID
        ).join(
            models.QuizResponseScore, 
            and_(
                models.QuizResponse.AttemptID == models.QuizResponseScore.AttemptID,
                models.QuizResponse.QuestionID == models.QuizResponseScore.QuestionID
            )
        ).filter(
            models.QuizResponse.AttemptID == attempt_id
        ).all()
        
        # Get correct answers for all questions in this quiz
        correct_options = db.query(models.QuizOption).join(
            models.QuizQuestion, models.QuizOption.QuestionID == models.QuizQuestion.QuestionID
        ).filter(
            and_(
                models.QuizQuestion.QuizID == quiz.QuizID,
                models.QuizOption.IsCorrect == True
            )
        ).all()
        
        # Create a map of question_id to correct option
        correct_answers_map = {opt.QuestionID: opt for opt in correct_options}
        
        # Build results
        results = []
        for response, question, selected_option, score in responses:
            correct_option = correct_answers_map.get(question.QuestionID)
            
            results.append({
                'question_id': question.QuestionID,
                'question_text': question.QuestionText,
                'explanation': question.Explanation,
                'user_answer': {
                    'option_id': selected_option.OptionID,
                    'option_text': selected_option.OptionText,
                    'is_correct': selected_option.IsCorrect
                },
                'correct_answer': {
                    'option_id': correct_option.OptionID if correct_option else None,
                    'option_text': correct_option.OptionText if correct_option else None
                } if correct_option else None
            })
        
        return {
            'attempt_id': attempt.AttemptID,
            'quiz_id': quiz.QuizID,
            'quiz_title': quiz.Title,
            'score_percentage': float(attempt.ScorePct) if attempt.ScorePct else 0,
            'is_passed': attempt.IsPassed,
            'passing_percentage': float(quiz.PassingPct),
            'total_questions': len(results),
            'correct_answers': sum(1 for r in results if r['user_answer']['is_correct']),
            'started_at': attempt.StartedAt,
            'completed_at': attempt.CompletedAt,
            'results': results
        }
    
    @staticmethod
    def _check_attempt_limits(db: Session, employee_id: int, quiz_id: int) -> dict:
        """Check if employee can attempt the quiz based on limits"""
        limit_record = db.query(models.QuizAttemptLimit).filter(
            and_(
                models.QuizAttemptLimit.EmployeeID == employee_id,
                models.QuizAttemptLimit.QuizID == quiz_id
            )
        ).first()
        
        if not limit_record:
            return {'can_attempt': True, 'reason': None}
        
        # Check cooldown period
        if limit_record.CooldownUntil and limit_record.CooldownUntil > datetime.utcnow():
            days_remaining = (limit_record.CooldownUntil - datetime.utcnow()).days
            return {
                'can_attempt': False,
                'reason': f"Cooldown period active. {days_remaining} days remaining."
            }
        
        # Check attempt count
        if limit_record.AttemptCount >= 2:
            return {
                'can_attempt': False,
                'reason': "Maximum attempts reached. Cooldown period of 4 weeks activated."
            }
        
        return {'can_attempt': True, 'reason': None}
    
    @staticmethod
    def _update_attempt_count(db: Session, employee_id: int, quiz_id: int):
        """Update attempt count and handle cooldown periods"""
        try:
            limit_record = db.query(models.QuizAttemptLimit).filter(
                and_(
                    models.QuizAttemptLimit.EmployeeID == employee_id,
                    models.QuizAttemptLimit.QuizID == quiz_id
                )
            ).first()
            
            if not limit_record:
                # Create new limit record
                limit_record = models.QuizAttemptLimit(
                    EmployeeID=employee_id,
                    QuizID=quiz_id,
                    AttemptCount=1,
                    LastAttemptDate=datetime.utcnow(),
                    CooldownUntil=None
                )
                db.add(limit_record)
            else:
                # Increment existing record
                limit_record.AttemptCount += 1
                limit_record.LastAttemptDate = datetime.utcnow()
                
                # If this is the second attempt, start cooldown
                if limit_record.AttemptCount >= 2:
                    limit_record.CooldownUntil = datetime.utcnow() + timedelta(weeks=4)
            
            db.commit()
            
        except Exception as e:
            # Rollback on any error
            db.rollback()
            raise Exception(f"Failed to update attempt count: {str(e)}")

class BadgeService:
    
    @staticmethod
    def get_badges(db: Session, is_active: Optional[bool] = None) -> List[models.BadgeDefinition]:
        query = db.query(models.BadgeDefinition)
        
        if is_active is not None:
            query = query.filter(models.BadgeDefinition.IsActive == is_active)
        
        return query.all()
    
    @staticmethod
    def get_employee_badges(db: Session, employee_id: int) -> List[models.EmployeeBadge]:
        return db.query(models.EmployeeBadge).options(
            joinedload(models.EmployeeBadge.badge)
        ).filter(models.EmployeeBadge.EmployeeID == employee_id).all()
    
    @staticmethod
    def get_course_badges(db: Session, course_id: int) -> List[models.BadgeDefinition]:
        """Get badges directly linked to a specific course"""
        return db.query(models.BadgeDefinition).filter(
            and_(
                models.BadgeDefinition.CourseID == course_id,
                models.BadgeDefinition.IsActive == True
            )
        ).all()
    
    @staticmethod
    def get_quiz_badges(db: Session, quiz_id: int) -> List[models.BadgeDefinition]:
        """Get badges directly linked to a specific quiz"""
        return db.query(models.BadgeDefinition).filter(
            and_(
                models.BadgeDefinition.QuizID == quiz_id,
                models.BadgeDefinition.IsActive == True
            )
        ).all()
    
    @staticmethod
    def get_available_badges_for_course(db: Session, course_id: int) -> List[models.BadgeDefinition]:
        """Get all badges that can be earned for a specific course"""
        return db.query(models.BadgeDefinition).filter(
            and_(
                models.BadgeDefinition.CourseID == course_id,
                models.BadgeDefinition.IsActive == True
            )
        ).all()
    
    @staticmethod
    def award_badge(
        db: Session, 
        employee_id: int, 
        badge_id: int,
        reason: str = "Manual Award"
    ) -> models.EmployeeBadge:
        # Check if already has badge
        existing = db.query(models.EmployeeBadge).filter(
            and_(
                models.EmployeeBadge.EmployeeID == employee_id,
                models.EmployeeBadge.BadgeID == badge_id
            )
        ).first()
        
        if existing:
            return existing
        
        # Check if badge exists and is active
        badge = db.query(models.BadgeDefinition).filter(
            and_(
                models.BadgeDefinition.BadgeID == badge_id,
                models.BadgeDefinition.IsActive == True
            )
        ).first()
        
        if not badge:
            raise HTTPException(status_code=404, detail="Badge not found or inactive")
        
        employee_badge = models.EmployeeBadge(
            EmployeeID=employee_id,
            BadgeID=badge_id
        )
        
        db.add(employee_badge)
        db.commit()
        db.refresh(employee_badge)
        
        return employee_badge
    
    @staticmethod
    def award_course_completion_badge(db: Session, employee_id: int, course_id: int):
        """Award course completion badges"""
        print(f"DEBUG: Checking for badges for course {course_id} and employee {employee_id}")
        
        # Find all course completion badges for this course
        badges = db.query(models.BadgeDefinition).filter(
            and_(
                models.BadgeDefinition.CourseID == course_id,
                models.BadgeDefinition.IsActive == True
            )
        ).all()
        
        print(f"DEBUG: Found {len(badges)} badges for course {course_id}")
        
        # Award all matching badges to the employee
        for badge in badges:
            print(f"DEBUG: Awarding badge {badge.BadgeID} ({badge.Name}) to employee {employee_id}")
            BadgeService.award_badge(db, employee_id, badge.BadgeID, "Course Completion")
    
    @staticmethod
    def check_and_award_missing_badges(db: Session, employee_id: int):
        """Check for completed courses and award missing badges"""
        print(f"DEBUG: Checking for missing badges for employee {employee_id}")
        
        # Get all completed courses for this employee
        completed_courses = db.query(models.EmployeeCourse).filter(
            and_(
                models.EmployeeCourse.EmployeeID == employee_id,
                models.EmployeeCourse.Status == 'Completed'
            )
        ).all()
        
        print(f"DEBUG: Found {len(completed_courses)} completed courses")
        
        for enrollment in completed_courses:
            print(f"DEBUG: Checking badges for course {enrollment.CourseID}")
            
            # Check if employee already has badges for this course
            existing_badges = db.query(models.EmployeeBadge).join(
                models.BadgeDefinition
            ).filter(
                and_(
                    models.EmployeeBadge.EmployeeID == employee_id,
                    models.BadgeDefinition.CourseID == enrollment.CourseID
                )
            ).all()
            
            if not existing_badges:
                print(f"DEBUG: No badges found for course {enrollment.CourseID}, awarding...")
                BadgeService.award_course_completion_badge(db, employee_id, enrollment.CourseID)
            else:
                print(f"DEBUG: Employee already has {len(existing_badges)} badges for course {enrollment.CourseID}")
    
    @staticmethod
    def award_quiz_mastery_badge(db: Session, employee_id: int, quiz_id: int):
        """Award quiz mastery badges"""
        # Find all quiz mastery badges for this quiz
        badges = db.query(models.BadgeDefinition).filter(
            and_(
                models.BadgeDefinition.QuizID == quiz_id,
                models.BadgeDefinition.IsActive == True
            )
        ).all()
        
        # Award all matching badges to the employee
        for badge in badges:
            BadgeService.award_badge(db, employee_id, badge.BadgeID, "Quiz Mastery") 