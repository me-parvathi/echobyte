#!/usr/bin/env python3
"""
Script to assign HR role to marie.wise
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_marie_hr_role():
    """Assign HR role to marie.wise"""
    print("🔧 Fixing HR Role for marie.wise...")
    print("=" * 50)
    
    try:
        from core.database import get_db
        from api.auth.models import Role, EmployeeRole
        from api.employee.models import Employee
        
        db = next(get_db())
        
        # Find marie.wise
        user = db.query(Employee).filter(
            Employee.UserID == "marie.wise",
            Employee.IsActive == True
        ).first()
        
        if not user:
            print("❌ User marie.wise not found")
            return
        
        print(f"✅ Found user: {user.FirstName} {user.LastName} ({user.EmployeeCode})")
        
        # Find HR role
        hr_role = db.query(Role).filter(Role.RoleName == "HR").first()
        if not hr_role:
            print("❌ HR role not found, creating it...")
            hr_role = Role(RoleName="HR", Description="HR staff, access to employee records")
            db.add(hr_role)
            db.commit()
            db.refresh(hr_role)
            print("✅ HR role created")
        else:
            print(f"✅ HR role found: {hr_role.RoleName} (ID: {hr_role.RoleID})")
        
        # Check current roles
        current_roles = db.query(EmployeeRole, Role).join(
            Role, EmployeeRole.RoleID == Role.RoleID
        ).filter(
            EmployeeRole.EmployeeID == user.EmployeeID,
            EmployeeRole.IsActive == True
        ).all()
        
        print(f"📋 Current roles for {user.FirstName}:")
        for emp_role, role in current_roles:
            print(f"   - {role.RoleName} (ID: {role.RoleID})")
        
        # Check if already has HR role
        existing_hr = db.query(EmployeeRole).filter(
            EmployeeRole.EmployeeID == user.EmployeeID,
            EmployeeRole.RoleID == hr_role.RoleID,
            EmployeeRole.IsActive == True
        ).first()
        
        if existing_hr:
            print("✅ User already has HR role")
        else:
            print("➕ Assigning HR role...")
            # Create HR role assignment
            hr_assignment = EmployeeRole(
                EmployeeID=user.EmployeeID,
                RoleID=hr_role.RoleID,
                AssignedByID=user.EmployeeID,
                IsActive=True
            )
            db.add(hr_assignment)
            db.commit()
            print("✅ HR role assigned successfully")
        
        # Verify final roles
        final_roles = db.query(EmployeeRole, Role).join(
            Role, EmployeeRole.RoleID == Role.RoleID
        ).filter(
            EmployeeRole.EmployeeID == user.EmployeeID,
            EmployeeRole.IsActive == True
        ).all()
        
        print(f"\n📋 Final roles for {user.FirstName}:")
        for emp_role, role in final_roles:
            print(f"   - {role.RoleName} (ID: {role.RoleID})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    fix_marie_hr_role() 