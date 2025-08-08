#!/usr/bin/env python3
"""
Debug script to test admin authentication
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.auth import has_admin_access
from api.auth.models import User
from api.employee.models import Employee
from api.auth.models import Role, EmployeeRole
from core.database import get_db

def debug_admin_auth():
    """Debug admin authentication"""
    print("Debugging Admin Authentication...")
    print("=" * 50)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Find the user from the token
        username = "andrew.hickman"
        user = db.query(User).filter(User.Username == username).first()
        
        if not user:
            print(f"❌ User {username} not found")
            return
        
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
            return
        
        print(f"✅ Found employee: {employee.EmployeeCode} ({employee.FirstName} {employee.LastName})")
        
        # Check for Admin role
        admin_role = db.query(Role).filter(Role.RoleName == "Admin").first()
        if not admin_role:
            print("❌ Admin role not found in database")
            return
        
        print(f"✅ Found Admin role: {admin_role.RoleName} (ID: {admin_role.RoleID})")
        
        # Check if employee has admin role
        employee_role = db.query(EmployeeRole).filter(
            EmployeeRole.EmployeeID == employee.EmployeeID,
            EmployeeRole.RoleID == admin_role.RoleID,
            EmployeeRole.IsActive == True
        ).first()
        
        if employee_role:
            print("✅ Employee has Admin role assigned")
        else:
            print("❌ Employee does NOT have Admin role assigned")
            
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
        
        # Test the has_admin_access function
        is_admin = has_admin_access(user, db)
        print(f"\n🔍 has_admin_access() result: {is_admin}")
        
        if not is_admin:
            print("❌ User should NOT have access to admin endpoints")
        else:
            print("✅ User should have access to admin endpoints")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_admin_auth() 