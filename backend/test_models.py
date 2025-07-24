#!/usr/bin/env python3
"""
Test script to verify SQLAlchemy models are working correctly
Run this script to test model imports and structure
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_model_imports():
    """Test that all models can be imported successfully"""
    try:
        print("🔍 Testing model imports...")
        print("=" * 50)
        
        # Import all models
        from app.models import (
            Genders, EmploymentTypes, WorkModes, LeaveApplicationStatuses,
            ApprovalStatuses, TimesheetStatuses, FeedbackTypes, Designations,
            Locations, Departments, Teams,
            Employees, EmergencyContacts, Roles, EmployeeRoles,
            LeaveTypes, LeaveBalances, LeaveApplications,
            Timesheets, TimesheetDetails,
            EmployeeFeedbacks, AuditLogs,
            AssetStatuses, AssetTypes, Assets, AssetAssignments
        )
        
        print("✅ All models imported successfully!")
        
        # List all imported models
        print("\n📋 Imported models:")
        models = [
            # Lookup models
            'Genders', 'EmploymentTypes', 'WorkModes', 'LeaveApplicationStatuses',
            'ApprovalStatuses', 'TimesheetStatuses', 'FeedbackTypes', 'Designations',
            
            # Core models
            'Locations', 'Departments', 'Teams',
            
            # Employee models
            'Employees', 'EmergencyContacts', 'Roles', 'EmployeeRoles',
            
            # Leave models
            'LeaveTypes', 'LeaveBalances', 'LeaveApplications',
            
            # Timesheet models
            'Timesheets', 'TimesheetDetails',
            
            # Feedback models
            'EmployeeFeedbacks', 'AuditLogs',
            
            # Asset models
            'AssetStatuses', 'AssetTypes', 'Assets', 'AssetAssignments'
        ]
        
        for model_name in models:
            if model_name in globals():
                model_class = globals()[model_name]
                table_name = getattr(model_class, '__tablename__', 'Unknown')
                print(f"   ✅ {model_name} -> {table_name}")
            else:
                print(f"   ❌ {model_name} -> Not found")
        
        print(f"\n📊 Total models: {len(models)}")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False
    
    return True

def test_model_structure():
    """Test that models have the expected structure"""
    try:
        print("\n🔍 Testing model structure...")
        print("=" * 50)
        
        from app.models import Employees, Teams, Departments
        
        # Test Employees model
        print("📋 Testing Employees model:")
        employee_columns = [col.name for col in Employees.__table__.columns]
        print(f"   Columns: {len(employee_columns)}")
        print(f"   Primary key: {Employees.__table__.primary_key}")
        
        # Test relationships
        print(f"   Relationships: {len(Employees.__mapper__.relationships)}")
        for rel_name, rel in Employees.__mapper__.relationships.items():
            print(f"     - {rel_name} -> {rel.mapper.class_.__name__}")
        
        # Test Teams model
        print("\n📋 Testing Teams model:")
        team_columns = [col.name for col in Teams.__table__.columns]
        print(f"   Columns: {len(team_columns)}")
        
        # Test Departments model
        print("\n📋 Testing Departments model:")
        dept_columns = [col.name for col in Departments.__table__.columns]
        print(f"   Columns: {len(dept_columns)}")
        
        print("\n✅ Model structure tests passed!")
        
    except Exception as e:
        print(f"❌ Model structure test failed: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection with models"""
    try:
        print("\n🔍 Testing database connection with models...")
        print("=" * 50)
        
        from app.db.database import engine
        from sqlalchemy import text
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test_value"))
            if result.fetchone():
                print("✅ Database connection successful!")
                return True
            else:
                print("❌ Database connection failed!")
                return False
                
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 EchoByte Model Testing")
    print("=" * 50)
    print()
    
    # Test model imports
    if not test_model_imports():
        print("\n❌ Model import tests failed!")
        sys.exit(1)
    
    # Test model structure
    if not test_model_structure():
        print("\n❌ Model structure tests failed!")
        sys.exit(1)
    
    # Test database connection
    if not test_database_connection():
        print("\n❌ Database connection test failed!")
        sys.exit(1)
    
    print("\n🎉 All tests passed successfully!")
    print("✅ Your SQLAlchemy models are ready to use!")
    
    print("\n📝 Next steps:")
    print("1. Run 'python create_tables.py' to create all tables")
    print("2. Start building your API endpoints")
    print("3. Create Pydantic schemas for data validation")
    print("4. Implement CRUD operations for each model") 