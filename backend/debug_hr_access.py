#!/usr/bin/env python3
"""
Debug script to test HR authentication and role assignment
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.auth import require_hr
from api.auth.models import User, Role, EmployeeRole
from api.employee.models import Employee
from core.database import get_db

def debug_hr_access():
    """Debug HR authentication"""
    print("🔍 Debugging HR Access...")
    print("=" * 50)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Test with a known HR user (you may need to adjust this)
        test_usernames = ["andrew.hickman", "sarah.johnson", "michael.brown"]
        
        for username in test_usernames:
            print(f"\n🔍 Testing user: {username}")
            print("-" * 30)
            
            # Find the user
            user = db.query(User).filter(User.Username == username).first()
            
            if not user:
                print(f"❌ User {username} not found")
                continue
            
            print(f"✅ Found user: {user.Username}")
            print(f"   UserID: {user.UserID}")
            print(f"   IsActive: {user.IsActive}")
            
            # Check employee record
            employee = db.query(Employee).filter(
                Employee.UserID == user.UserID,
                Employee.IsActive == True
            ).first()
            
            if not employee:
                print("❌ No active employee record found for user")
                continue
            
            print(f"✅ Found employee: {employee.EmployeeCode} ({employee.FirstName} {employee.LastName})")
            
            # Check for HR role
            hr_role = db.query(Role).filter(Role.RoleName == "HR").first()
            if not hr_role:
                print("❌ HR role not found in database")
                continue
            
            print(f"✅ Found HR role: {hr_role.RoleName} (ID: {hr_role.RoleID})")
            
            # Check if employee has HR role
            employee_role = db.query(EmployeeRole).filter(
                EmployeeRole.EmployeeID == employee.EmployeeID,
                EmployeeRole.RoleID == hr_role.RoleID,
                EmployeeRole.IsActive == True
            ).first()
            
            if employee_role:
                print("✅ Employee has HR role assigned")
                
                # Test the require_hr function
                try:
                    hr_checker = require_hr
                    print("✅ require_hr function is properly defined")
                except Exception as e:
                    print(f"❌ require_hr function error: {e}")
                
            else:
                print("❌ Employee does NOT have HR role assigned")
                
                # Show what roles they do have
                user_roles = db.query(EmployeeRole, Role).join(
                    Role, EmployeeRole.RoleID == Role.RoleID
                ).filter(
                    EmployeeRole.EmployeeID == employee.EmployeeID,
                    EmployeeRole.IsActive == True
                ).all()
                
                if user_roles:
                    print("   User has these roles:")
                    for emp_role, role in user_roles:
                        print(f"   - {role.RoleName}")
                else:
                    print("   User has no roles assigned")
        
        # Check all HR users in the system
        print(f"\n🔍 Checking all HR users in the system:")
        print("-" * 30)
        
        hr_users = db.query(EmployeeRole, Employee, Role).join(
            Employee, EmployeeRole.EmployeeID == Employee.EmployeeID
        ).join(
            Role, EmployeeRole.RoleID == Role.RoleID
        ).filter(
            Role.RoleName == "HR",
            EmployeeRole.IsActive == True,
            Employee.IsActive == True
        ).all()
        
        if hr_users:
            print(f"✅ Found {len(hr_users)} HR users:")
            for emp_role, employee, role in hr_users:
                print(f"   - {employee.FirstName} {employee.LastName} ({employee.EmployeeCode})")
        else:
            print("❌ No HR users found in the system")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_hr_access() 