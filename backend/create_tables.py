#!/usr/bin/env python3
"""
Script to create all database tables using SQLAlchemy models
Run this script to create all tables in your Azure SQL Database
"""

import sys
import os
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_all_tables():
    """Create all database tables using SQLAlchemy models"""
    try:
        print("🔍 Creating database tables...")
        print("=" * 50)
        
        # Import after adding to path
        from app.db.database import engine, Base
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
        
        # Print connection info (without password)
        from app.core.config import settings
        print(f"📊 Connection Details:")
        print(f"   Server: {settings.AZURE_SQL_SERVER}")
        print(f"   Database: {settings.AZURE_SQL_DATABASE}")
        print(f"   Username: {settings.AZURE_SQL_USERNAME}")
        print(f"   Port: {settings.AZURE_SQL_PORT}")
        print()
        
        # Test connection first
        print("🔌 Testing connection...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test_value"))
            if result.fetchone():
                print("   ✅ Connection successful!")
            else:
                print("   ❌ Connection failed!")
                return
        
        print()
        print("🏗️  Creating tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("   ✅ All tables created successfully!")
        
        # List all tables
        print()
        print("📋 Created tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"   - {table_name}")
        
        print()
        print("🎉 Database setup completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure you're running this script from the backend directory")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
        
    except SQLAlchemyError as e:
        print(f"❌ Database Error: {e}")
        print()
        print("🔧 Troubleshooting steps:")
        print("1. Check your .env file has correct Azure SQL Database credentials")
        print("2. Verify Azure SQL Database server is running and accessible")
        print("3. Check firewall rules allow your IP address")
        print("4. Ensure ODBC Driver 18 for SQL Server is installed")
        print("5. Verify username and password are correct")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print(f"   Error type: {type(e).__name__}")

def check_existing_tables():
    """Check what tables already exist in the database"""
    try:
        print("🔍 Checking existing tables...")
        print("=" * 50)
        
        from app.db.database import engine
        
        with engine.connect() as connection:
            # Query to get all user tables
            result = connection.execute(text("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE' 
                AND TABLE_SCHEMA = 'dbo'
                ORDER BY TABLE_NAME
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print("📋 Existing tables:")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("📋 No existing tables found")
                
            print(f"\n📊 Total tables: {len(tables)}")
            
    except Exception as e:
        print(f"❌ Error checking tables: {e}")

if __name__ == "__main__":
    print("🚀 EchoByte Database Table Creation")
    print("=" * 50)
    print()
    
    # Check existing tables first
    check_existing_tables()
    print()
    
    # Create tables
    create_all_tables()
    
    print("=" * 50)
    print("🏁 Table creation completed!") 