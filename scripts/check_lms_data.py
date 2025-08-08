#!/usr/bin/env python3
"""
LMS Data Checker
Checks what data exists in the Learning Management System
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_dir))

def check_lms_data():
    """Check what LMS data exists in the database"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        
        # Get database URL
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL environment variable not set")
            return False
        
        # Create engine
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("🔍 Checking LMS Data...")
        print("=" * 50)
        
        # Check Courses
        print("\n📚 Courses:")
        try:
            result = session.execute(text("SELECT COUNT(*) as count FROM dbo.Courses"))
            course_count = result.fetchone()[0]
            print(f"   Total Courses: {course_count}")
            
            if course_count > 0:
                result = session.execute(text("SELECT CourseID, CourseCode, Title, Difficulty, EstimatedHours FROM dbo.Courses"))
                courses = result.fetchall()
                for course in courses:
                    print(f"   - {course.CourseCode}: {course.Title} ({course.Difficulty}, {course.EstimatedHours}h)")
        except Exception as e:
            print(f"   ❌ Error checking courses: {e}")
        
        # Check Course Modules
        print("\n📖 Course Modules:")
        try:
            result = session.execute(text("SELECT COUNT(*) as count FROM dbo.CourseModules"))
            module_count = result.fetchone()[0]
            print(f"   Total Modules: {module_count}")
            
            if module_count > 0:
                result = session.execute(text("""
                    SELECT c.CourseCode, c.Title, COUNT(cm.ModuleID) as module_count
                    FROM dbo.Courses c
                    LEFT JOIN dbo.CourseModules cm ON c.CourseID = cm.CourseID
                    GROUP BY c.CourseID, c.CourseCode, c.Title
                """))
                course_modules = result.fetchall()
                for course in course_modules:
                    print(f"   - {course.CourseCode}: {course.module_count} modules")
        except Exception as e:
            print(f"   ❌ Error checking modules: {e}")
        
        # Check Quizzes
        print("\n🎯 Quizzes:")
        try:
            result = session.execute(text("SELECT COUNT(*) as count FROM dbo.Quizzes"))
            quiz_count = result.fetchone()[0]
            print(f"   Total Quizzes: {quiz_count}")
            
            if quiz_count > 0:
                result = session.execute(text("SELECT QuizID, Title, QuestionCount, TimeLimitMin FROM dbo.Quizzes"))
                quizzes = result.fetchall()
                for quiz in quizzes:
                    print(f"   - {quiz.Title} ({quiz.QuestionCount} questions, {quiz.TimeLimitMin} min)")
        except Exception as e:
            print(f"   ❌ Error checking quizzes: {e}")
        
        # Check Badge Definitions
        print("\n🏆 Badge Definitions:")
        try:
            result = session.execute(text("SELECT COUNT(*) as count FROM dbo.BadgeDefinitions"))
            badge_count = result.fetchone()[0]
            print(f"   Total Badges: {badge_count}")
            
            if badge_count > 0:
                result = session.execute(text("SELECT BadgeCode, Name, Description FROM dbo.BadgeDefinitions"))
                badges = result.fetchall()
                for badge in badges:
                    print(f"   - {badge.BadgeCode}: {badge.Name}")
        except Exception as e:
            print(f"   ❌ Error checking badges: {e}")
        
        # Check Employee Enrollments
        print("\n👤 Employee Enrollments:")
        try:
            result = session.execute(text("SELECT COUNT(*) as count FROM dbo.EmployeeCourses"))
            enrollment_count = result.fetchone()[0]
            print(f"   Total Enrollments: {enrollment_count}")
            
            if enrollment_count > 0:
                result = session.execute(text("""
                    SELECT ec.EmployeeID, c.Title, ec.Status, ec.EnrolledAt
                    FROM dbo.EmployeeCourses ec
                    JOIN dbo.Courses c ON ec.CourseID = c.CourseID
                    ORDER BY ec.EmployeeID, c.Title
                """))
                enrollments = result.fetchall()
                for enrollment in enrollments:
                    print(f"   - Employee {enrollment.EmployeeID}: {enrollment.Title} ({enrollment.Status})")
        except Exception as e:
            print(f"   ❌ Error checking enrollments: {e}")
        
        # Check Quiz Attempts
        print("\n📝 Quiz Attempts:")
        try:
            result = session.execute(text("SELECT COUNT(*) as count FROM dbo.QuizAttempts"))
            attempt_count = result.fetchone()[0]
            print(f"   Total Attempts: {attempt_count}")
            
            if attempt_count > 0:
                result = session.execute(text("""
                    SELECT qa.EmployeeID, q.Title, qa.ScorePct, qa.IsPassed
                    FROM dbo.QuizAttempts qa
                    JOIN dbo.Quizzes q ON qa.QuizID = q.QuizID
                    ORDER BY qa.EmployeeID, q.Title
                """))
                attempts = result.fetchall()
                for attempt in attempts:
                    status = "Passed" if attempt.IsPassed else "Failed"
                    print(f"   - Employee {attempt.EmployeeID}: {attempt.Title} ({attempt.ScorePct}%, {status})")
        except Exception as e:
            print(f"   ❌ Error checking quiz attempts: {e}")
        
        session.close()
        
        print("\n" + "=" * 50)
        print("✅ Data check completed!")
        
        if course_count == 0:
            print("\n⚠️  No courses found! Run the seed script:")
            print("   python scripts/run_lms_seed.py")
            print("   OR run database/seed_lms_simple.sql in your SQL client")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking LMS data: {e}")
        return False

if __name__ == "__main__":
    success = check_lms_data()
    sys.exit(0 if success else 1) 