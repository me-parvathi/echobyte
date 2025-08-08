#!/usr/bin/env python3
"""
Script to check if ProfilePictures table exists and can be accessed.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from core.database import get_db_session

def check_profile_table():
    """Check if ProfilePictures table exists."""
    try:
        print("🔍 Checking ProfilePictures table...")
        
        with get_db_session() as db:
            # Check if table exists
            result = db.execute(text("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'ProfilePictures'
            """))
            table_exists = result.scalar() > 0
            
            if table_exists:
                print("✅ ProfilePictures table exists")
                
                # Check table structure
                result = db.execute(text("""
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = 'ProfilePictures'
                    ORDER BY ORDINAL_POSITION
                """))
                
                columns = result.fetchall()
                print(f"📋 Table has {len(columns)} columns:")
                for column in columns:
                    print(f"   - {column[0]} ({column[1]}, {'NULL' if column[2] == 'YES' else 'NOT NULL'})")
                
                # Check if table has any data
                result = db.execute(text("SELECT COUNT(*) FROM ProfilePictures"))
                count = result.scalar()
                print(f"📊 Table has {count} records")
                
                return True
            else:
                print("❌ ProfilePictures table does not exist")
                return False
                
    except Exception as e:
        print(f"❌ Error checking ProfilePictures table: {e}")
        return False

def test_profile_service():
    """Test profile service functionality."""
    try:
        print("\n🔍 Testing profile service...")
        
        from api.profile.service import ProfilePictureService
        
        service = ProfilePictureService()
        print("✅ Profile service initialized successfully")
        
        # Test employee validation
        with get_db_session() as db:
            # Get first employee
            from api.employee.models import Employee
            employee = db.query(Employee).first()
            
            if employee:
                print(f"✅ Found employee: {employee.EmployeeID}")
                
                # Test validation
                is_valid = service.validate_employee_id(db, employee.EmployeeID)
                print(f"✅ Employee validation: {'Valid' if is_valid else 'Invalid'}")
                
                return True
            else:
                print("⚠️ No employees found in database")
                return False
                
    except Exception as e:
        print(f"❌ Error testing profile service: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Checking Profile Pictures Setup...")
    print("=" * 50)
    
    tests = [
        ("ProfilePictures Table", check_profile_table),
        ("Profile Service", test_profile_service)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Profile pictures should work correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the setup.") 