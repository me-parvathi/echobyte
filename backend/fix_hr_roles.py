#!/usr/bin/env python3
"""
Script to fix HR role assignments in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_hr_roles():
    """Fix HR role assignments"""
    print("🔧 Fixing HR Role Assignments...")
    print("=" * 50)
    
    try:
        # Import after setting up path
        from core.database import get_db
        from api.auth.models import Role, EmployeeRole
        from api.employee.models import Employee
        
        db = next(get_db())
        
        # Check if HR role exists
        hr_role = db.query(Role).filter(Role.RoleName == "HR").first()
        if not hr_role:
            print("❌ HR role not found in database")
            print("Creating HR role...")
            hr_role = Role(RoleName="HR", Description="HR staff, access to employee records")
            db.add(hr_role)
            db.commit()
            db.refresh(hr_role)
            print("✅ HR role created")
        else:
            print(f"✅ HR role found: {hr_role.RoleName} (ID: {hr_role.RoleID})")
        
        # Find employees who should have HR role (you can customize this logic)
        # For now, let's assign HR role to employees in HR department or with HR in their name
        potential_hr_employees = db.query(Employee).filter(
            Employee.IsActive == True,
            Employee.FirstName.like('%HR%') | 
            Employee.LastName.like('%HR%') |
            Employee.EmployeeCode.like('%HR%')
        ).all()
        
        if not potential_hr_employees:
            print("No potential HR employees found by name/ID pattern")
            print("Assigning HR role to first few active employees for testing...")
            potential_hr_employees = db.query(Employee).filter(
                Employee.IsActive == True
            ).limit(3).all()
        
        print(f"Found {len(potential_hr_employees)} potential HR employees:")
        
        for employee in potential_hr_employees:
            print(f"  - {employee.FirstName} {employee.LastName} ({employee.EmployeeCode})")
            
            # Check if they already have HR role
            existing_hr_role = db.query(EmployeeRole).filter(
                EmployeeRole.EmployeeID == employee.EmployeeID,
                EmployeeRole.RoleID == hr_role.RoleID,
                EmployeeRole.IsActive == True
            ).first()
            
            if existing_hr_role:
                print(f"    ✅ Already has HR role")
            else:
                print(f"    ➕ Assigning HR role...")
                # Create HR role assignment
                hr_assignment = EmployeeRole(
                    EmployeeID=employee.EmployeeID,
                    RoleID=hr_role.RoleID,
                    AssignedByID=employee.EmployeeID,  # Self-assigned for now
                    IsActive=True
                )
                db.add(hr_assignment)
        
        db.commit()
        print("✅ HR role assignments completed")
        
        # Verify the assignments
        print("\n🔍 Verifying HR role assignments:")
        hr_assignments = db.query(EmployeeRole, Employee, Role).join(
            Employee, EmployeeRole.EmployeeID == Employee.EmployeeID
        ).join(
            Role, EmployeeRole.RoleID == Role.RoleID
        ).filter(
            Role.RoleName == "HR",
            EmployeeRole.IsActive == True,
            Employee.IsActive == True
        ).all()
        
        if hr_assignments:
            print(f"✅ Found {len(hr_assignments)} HR users:")
            for assignment, employee, role in hr_assignments:
                print(f"  - {employee.FirstName} {employee.LastName} ({employee.EmployeeCode})")
        else:
            print("❌ No HR users found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    fix_hr_roles() 