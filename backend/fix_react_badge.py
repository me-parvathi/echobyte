#!/usr/bin/env python3
"""
Fix React Badge Script
======================

This script manually awards the React badge to EmployeeID = 1
and tests the badge awarding logic.
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import get_db
from api.learning.service import BadgeService
from api.learning import models

def main():
    """Main function to fix the React badge issue"""
    print("🔧 Fixing React Badge Issue...")
    
    # Load environment variables
    load_dotenv()
    
    # Get database session
    db = next(get_db())
    
    try:
        employee_id = 1
        course_id = 4  # React course
        
        print(f"📋 Checking current state...")
        
        # Check if employee has the React badge
        existing_badge = db.query(models.EmployeeBadge).filter(
            models.EmployeeBadge.EmployeeID == employee_id,
            models.EmployeeBadge.BadgeID == 10  # REACT_EXPERT badge
        ).first()
        
        if existing_badge:
            print(f"✅ Employee {employee_id} already has React badge (BadgeID: 10)")
            return
        
        # Check if React badge exists
        react_badge = db.query(models.BadgeDefinition).filter(
            models.BadgeDefinition.BadgeID == 10
        ).first()
        
        if not react_badge:
            print(f"❌ React badge (BadgeID: 10) not found in database")
            return
        
        print(f"✅ Found React badge: {react_badge.Name} (BadgeID: {react_badge.BadgeID})")
        
        # Check if course is completed
        enrollment = db.query(models.EmployeeCourse).filter(
            models.EmployeeCourse.EmployeeID == employee_id,
            models.EmployeeCourse.CourseID == course_id
        ).first()
        
        if not enrollment:
            print(f"❌ Employee {employee_id} not enrolled in React course")
            return
        
        print(f"📊 Course Status: {enrollment.Status}")
        print(f"📊 Course Completed At: {enrollment.CompletedAt}")
        
        if enrollment.Status != 'Completed':
            print(f"❌ React course is not completed (Status: {enrollment.Status})")
            return
        
        print(f"✅ React course is completed, awarding badge...")
        
        # Manually award the badge
        employee_badge = models.EmployeeBadge(
            EmployeeID=employee_id,
            BadgeID=10  # REACT_EXPERT badge
        )
        
        db.add(employee_badge)
        db.commit()
        db.refresh(employee_badge)
        
        print(f"🎉 Successfully awarded React badge to Employee {employee_id}")
        print(f"📅 Badge awarded at: {employee_badge.EarnedAt}")
        
        # Test the badge awarding function
        print(f"\n🧪 Testing badge awarding function...")
        BadgeService.award_course_completion_badge(db, employee_id, course_id)
        
        print(f"✅ Badge awarding function completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 