#!/usr/bin/env python3
"""
Test script to verify Azure SQL Database connection
Run this script to test if your database connection is working properly.
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

def test_database_connection():
    """Test the database connection and print detailed results"""
    try:
        print("🔍 Testing Azure SQL Database connection...")
        print("=" * 50)
        
        # Import after adding to path
        from app.db.database import engine
        from app.core.config import settings
        
        # Print connection info (without password)
        print(f"📊 Connection Details:")
        print(f"   Server: {settings.AZURE_SQL_SERVER}")
        print(f"   Database: {settings.AZURE_SQL_DATABASE}")
        print(f"   Username: {settings.AZURE_SQL_USERNAME}")
        print(f"   Port: {settings.AZURE_SQL_PORT}")
        print(f"   Environment: {settings.ENVIRONMENT}")
        print()
        
        # Test basic connection
        print("🔌 Testing basic connection...")
        with engine.connect() as connection:
            print("   ✅ Connection established successfully!")
            
            # Test simple query
            print("🔍 Testing simple query...")
            result = connection.execute(text("SELECT 1 as test_value"))
            row = result.fetchone()
            if row and row[0]:
                print(f"   ✅ Query executed successfully! Result: {row[0]}")
            else:
                print("   ⚠️  Query executed but no result returned")
            
            # Test SQL Server version
            print("🔍 Testing SQL Server version...")
            result = connection.execute(text("SELECT @@VERSION as version"))
            version = result.fetchone()
            if version and version[0]:
                print(f"   ✅ SQL Server version retrieved!")
                print(f"   📋 Version: {version[0][:100]}...")
            else:
                print("   ⚠️  Could not retrieve SQL Server version")
            
            # Test database name
            print("🔍 Testing current database...")
            result = connection.execute(text("SELECT DB_NAME() as current_db"))
            db_name = result.fetchone()
            if db_name and db_name[0]:
                print(f"   ✅ Current database: {db_name[0]}")
            else:
                print("   ⚠️  Could not retrieve database name")
            
        print()
        print("🎉 All connection tests passed successfully!")
        print("✅ Your Azure SQL Database connection is working properly!")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure you're running this script from the backend directory")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
        
    except SQLAlchemyError as e:
        print(f"❌ Database Connection Error: {e}")
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

def test_environment_variables():
    """Test if required environment variables are set"""
    print("🔍 Checking environment variables...")
    print("=" * 50)
    
    required_vars = [
        'AZURE_SQL_SERVER',
        'AZURE_SQL_DATABASE', 
        'AZURE_SQL_USERNAME',
        'AZURE_SQL_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask password for security
            if 'PASSWORD' in var:
                print(f"   ✅ {var}: {'*' * len(value)}")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print()
        print("⚠️  Missing environment variables detected!")
        print("💡 Create a .env file in the backend directory with:")
        for var in missing_vars:
            print(f"   {var}=your_value_here")
    else:
        print()
        print("✅ All required environment variables are set!")
    
    print()

if __name__ == "__main__":
    print("🚀 EchoByte Database Connection Test")
    print("=" * 50)
    print()
    
    # Test environment variables first
    test_environment_variables()
    
    # Test database connection
    test_database_connection()
    
    print("=" * 50)
    print("🏁 Test completed!") 