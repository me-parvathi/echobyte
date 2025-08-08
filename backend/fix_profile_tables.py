#!/usr/bin/env python3
"""
Script to fix database table creation for profile pictures.
This script ensures the ProfilePictures table exists in the database.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from core.database import engine, Base, get_db_session
from api.profile.models import ProfilePicture
from api.employee.models import Employee

def create_profile_tables():
    """Create the ProfilePictures table if it doesn't exist."""
    try:
        print("Creating ProfilePictures table...")
        
        # Import all models to ensure they are registered
        import api.employee.models
        import api.profile.models
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ ProfilePictures table created successfully")
        
        # Test the table
        with get_db_session() as db:
            # Check if table exists
            result = db.execute(text("SELECT COUNT(*) FROM ProfilePictures"))
            count = result.scalar()
            print(f"✅ ProfilePictures table verified - {count} records found")
            
    except Exception as e:
        print(f"❌ Error creating ProfilePictures table: {e}")
        raise

def test_profile_operations():
    """Test basic profile picture operations."""
    try:
        print("Testing profile picture operations...")
        
        with get_db_session() as db:
            # Test employee validation
            employee = db.query(Employee).first()
            if employee:
                print(f"✅ Employee found: {employee.EmployeeID}")
            else:
                print("⚠️ No employees found in database")
                
    except Exception as e:
        print(f"❌ Error testing profile operations: {e}")
        raise

if __name__ == "__main__":
    print("🔧 Fixing Profile Pictures Database Tables...")
    print("=" * 50)
    
    try:
        create_profile_tables()
        test_profile_operations()
        print("\n✅ All profile picture database operations completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Failed to fix profile picture tables: {e}")
        sys.exit(1) 