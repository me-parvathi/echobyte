#!/usr/bin/env python3
"""
LMS Seed Data Runner
Runs the seed data script to populate the Learning Management System
"""

import os
import sys
import subprocess
from pathlib import Path

def run_sql_script(script_path: str, database_url: str = None):
    """Run a SQL script using sqlcmd"""
    try:
        # Get database connection details from environment
        if not database_url:
            database_url = os.getenv('DATABASE_URL', '')
        
        if not database_url:
            print("❌ DATABASE_URL environment variable not set")
            print("Please set DATABASE_URL or provide it as an argument")
            return False
        
        # Parse connection string (assuming SQL Server format)
        # Example: mssql+pyodbc://username:password@server/database
        if 'mssql+' in database_url:
            # Extract connection details
            connection_parts = database_url.replace('mssql+pyodbc://', '').split('@')
            if len(connection_parts) != 2:
                print("❌ Invalid DATABASE_URL format")
                return False
            
            auth_part = connection_parts[0]
            server_db_part = connection_parts[1]
            
            username, password = auth_part.split(':')
            server, database = server_db_part.split('/')
            
            # Build sqlcmd command
            cmd = [
                'sqlcmd',
                '-S', server,
                '-U', username,
                '-P', password,
                '-d', database,
                '-i', script_path
            ]
            
            print(f"🔧 Running: {' '.join(cmd[:4])}... -i {script_path}")
            
            # Run the command
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Seed data script executed successfully")
                print(result.stdout)
                return True
            else:
                print("❌ Failed to execute seed data script")
                print("Error:", result.stderr)
                return False
                
        else:
            print("❌ Unsupported database URL format")
            return False
            
    except FileNotFoundError:
        print("❌ sqlcmd not found. Please install SQL Server Command Line Utilities")
        return False
    except Exception as e:
        print(f"❌ Error running seed script: {e}")
        return False

def main():
    """Main function"""
    print("🌱 LMS Seed Data Runner")
    print("=" * 50)
    
    # Get script directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Path to seed script
    seed_script = project_root / "database" / "seed_lms_data.sql"
    
    if not seed_script.exists():
        print(f"❌ Seed script not found at: {seed_script}")
        return False
    
    print(f"📁 Seed script: {seed_script}")
    
    # Check if we're in the right directory
    backend_dir = project_root / "backend"
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Change to backend directory to load environment
    os.chdir(backend_dir)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the seed script
    success = run_sql_script(str(seed_script))
    
    if success:
        print("\n🎉 LMS seed data completed successfully!")
        print("\n📊 What was created:")
        print("   • 5 courses with modules")
        print("   • Sample enrollments for EmployeeID = 1")
        print("   • Module progress records")
        print("   • Quiz attempts")
        print("   • Badge definitions and earned badges")
        print("\n🔗 Next steps:")
        print("   1. Start your backend server")
        print("   2. Navigate to the Learning & Development page")
        print("   3. You should see populated learning tracks!")
    else:
        print("\n❌ Failed to seed LMS data")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 