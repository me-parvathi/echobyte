from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional
from . import models, schemas
from fastapi import HTTPException
from api.team.models import Team

class EmployeeService:
    
    @staticmethod
    def get_employee(db: Session, employee_id: int) -> Optional[models.Employee]:
        return db.query(models.Employee).filter(models.Employee.EmployeeID == employee_id).first()
    
    @staticmethod
    def get_employee_by_email(db: Session, email: str) -> Optional[models.Employee]:
        return db.query(models.Employee).filter(models.Employee.CompanyEmail == email).first()
    
    @staticmethod
    def get_employee_by_code(db: Session, employee_code: str) -> Optional[models.Employee]:
        return db.query(models.Employee).filter(models.Employee.EmployeeCode == employee_code).first()
    
    @staticmethod
    def get_employee_by_user_id(db: Session, user_id: str) -> Optional[models.Employee]:
        return db.query(models.Employee).filter(models.Employee.UserID == user_id).first()
    
    @staticmethod
    def get_comprehensive_employee_profile(db: Session, user_id: str) -> Optional[dict]:
        """Get comprehensive employee profile with all relationships for the current user"""
        from api.department.models import Department
        from api.location.models import Location
        
        # Get employee with all relationships
        employee = db.query(models.Employee).options(
            joinedload(models.Employee.gender),
            joinedload(models.Employee.employment_type),
            joinedload(models.Employee.work_mode),
            joinedload(models.Employee.designation),
            joinedload(models.Employee.manager),
            joinedload(models.Employee.emergency_contacts)
        ).filter(models.Employee.UserID == user_id).first()
        
        if not employee:
            return None
        
        # Get team and department information
        team_info = db.query(
            Team.TeamID,
            Team.TeamName,
            Team.TeamCode,
            Department.DepartmentID,
            Department.DepartmentName,
            Department.DepartmentCode,
            Location.LocationID,
            Location.LocationName,
            Location.City,
            Location.State,
            Location.Country
        ).join(
            Department, Team.DepartmentID == Department.DepartmentID
        ).join(
            Location, Department.LocationID == Location.LocationID
        ).filter(
            Team.TeamID == employee.TeamID
        ).first()
        
        # Get manager information if exists
        manager_info = None
        if employee.ManagerID:
            manager = db.query(
                models.Employee.EmployeeID,
                models.Employee.FirstName,
                models.Employee.LastName,
                models.Employee.EmployeeCode,
                models.Designation.DesignationName
            ).join(
                models.Designation, models.Employee.DesignationID == models.Designation.DesignationID
            ).filter(
                models.Employee.EmployeeID == employee.ManagerID,
                models.Employee.IsActive == True
            ).first()
            
            if manager:
                manager_info = {
                    "EmployeeID": manager.EmployeeID,
                    "EmployeeCode": manager.EmployeeCode,
                    "Name": f"{manager.FirstName} {manager.LastName}",
                    "Designation": manager.DesignationName
                }
        
        # Calculate employment duration
        from datetime import date
        hire_date = employee.HireDate
        today = date.today()
        employment_years = (today - hire_date).days // 365 if hire_date else 0
        
        return {
            "EmployeeID": employee.EmployeeID,
            "EmployeeCode": employee.EmployeeCode,
            "UserID": employee.UserID,
            "CompanyEmail": employee.CompanyEmail,
            "FirstName": employee.FirstName,
            "MiddleName": employee.MiddleName,
            "LastName": employee.LastName,
            "FullName": f"{employee.FirstName} {employee.MiddleName or ''} {employee.LastName}".strip(),
            "DateOfBirth": employee.DateOfBirth,
            "GenderCode": employee.GenderCode,
            "GenderName": employee.gender.GenderName if employee.gender else None,
            "MaritalStatus": employee.MaritalStatus,
            "PersonalEmail": employee.PersonalEmail,
            "PersonalPhone": employee.PersonalPhone,
            "WorkPhone": employee.WorkPhone,
            "Address1": employee.Address1,
            "Address2": employee.Address2,
            "City": employee.City,
            "State": employee.State,
            "Country": employee.Country,
            "PostalCode": employee.PostalCode,
            "HireDate": employee.HireDate,
            "TerminationDate": employee.TerminationDate,
            "EmploymentDuration": employment_years,
            "IsActive": employee.IsActive,
            "CreatedAt": employee.CreatedAt,
            "UpdatedAt": employee.UpdatedAt,
            "Designation": {
                "DesignationID": employee.designation.DesignationID,
                "DesignationName": employee.designation.DesignationName
            } if employee.designation else None,
            "EmploymentType": {
                "EmploymentTypeCode": employee.employment_type.EmploymentTypeCode,
                "EmploymentTypeName": employee.employment_type.EmploymentTypeName
            } if employee.employment_type else None,
            "WorkMode": {
                "WorkModeCode": employee.work_mode.WorkModeCode,
                "WorkModeName": employee.work_mode.WorkModeName
            } if employee.work_mode else None,
            "Team": {
                "TeamID": team_info.TeamID,
                "TeamName": team_info.TeamName,
                "TeamCode": team_info.TeamCode
            } if team_info else None,
            "Department": {
                "DepartmentID": team_info.DepartmentID,
                "DepartmentName": team_info.DepartmentName,
                "DepartmentCode": team_info.DepartmentCode
            } if team_info else None,
            "Location": {
                "LocationID": team_info.LocationID,
                "LocationName": team_info.LocationName,
                "City": team_info.City,
                "State": team_info.State,
                "Country": team_info.Country
            } if team_info else None,
            "Manager": manager_info,
            "EmergencyContacts": [
                {
                    "ContactID": contact.ContactID,
                    "ContactName": contact.ContactName,
                    "Relationship": contact.Relationship,
                    "Phone1": contact.Phone1,
                    "Phone2": contact.Phone2,
                    "Email": contact.Email,
                    "Address": contact.Address,
                    "IsPrimary": contact.IsPrimary,
                    "IsActive": contact.IsActive
                }
                for contact in employee.emergency_contacts
                if contact.IsActive
            ] if employee.emergency_contacts else []
        }
    
    @staticmethod
    def get_employees(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None,
        team_id: Optional[int] = None,
        department_id: Optional[int] = None
    ) -> List[models.Employee]:
        query = db.query(models.Employee)
        
        if is_active is not None:
            query = query.filter(models.Employee.IsActive == is_active)
        
        if team_id:
            query = query.filter(models.Employee.TeamID == team_id)
        
        if department_id:
            query = query.join(Team, models.Employee.TeamID == Team.TeamID).filter(Team.DepartmentID == department_id)
        
        # SQL Server requires ORDER BY when using OFFSET
        return query.order_by(models.Employee.EmployeeID).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_employees_with_count(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        team_id: Optional[int] = None,
        department_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> tuple[List[models.Employee], int]:
        """Get employees with total count for pagination.
        Optimisation notes:
        1. We first fetch the paginated slice.  When the slice size is < limit and we are on the first
           page (skip == 0) we know we already have every row, so we can derive the total count without
           issuing a second COUNT(*) query.
        2. This saves one full-table scan for the common case where the UI asks for a very large limit
           just to get "all" employees (e.g. limit=1000).
        """
        # Build the base query
        base_query = db.query(models.Employee)

        if is_active is not None:
            base_query = base_query.filter(models.Employee.IsActive == is_active)

        if team_id:
            base_query = base_query.filter(models.Employee.TeamID == team_id)

        if department_id:
            base_query = base_query.join(Team, models.Employee.TeamID == Team.TeamID).filter(Team.DepartmentID == department_id)

        # Add search filter
        if search:
            print(f"DEBUG: Searching for '{search}'")
            search_term = f"%{search}%"
            base_query = base_query.filter(
                or_(
                    models.Employee.FirstName.ilike(search_term),
                    models.Employee.LastName.ilike(search_term),
                    models.Employee.EmployeeCode.ilike(search_term),
                    models.Employee.CompanyEmail.ilike(search_term)
                )
            )
            print("DEBUG: Search query applied")

        # Apply ordering and pagination to a clone of the query
        pagination_query = base_query.order_by(models.Employee.EmployeeID).offset(skip).limit(limit)
        employees = pagination_query.all()

        # Derive/compute total count efficiently
        if skip == 0 and len(employees) < limit:
            # We already have all the rows – no need for an extra COUNT(*)
            total_count = len(employees)
        else:
            total_count = base_query.count()

        print(f"DEBUG: Returning {len(employees)} employees (total {total_count})")

        return employees, total_count
    
    @staticmethod
    def create_employee(db: Session, employee: schemas.EmployeeCreate) -> models.Employee:
        # Check if employee code already exists
        if EmployeeService.get_employee_by_code(db, employee.EmployeeCode):
            raise HTTPException(status_code=400, detail="Employee code already exists")
        
        # Check if email already exists
        if EmployeeService.get_employee_by_email(db, employee.CompanyEmail):
            raise HTTPException(status_code=400, detail="Company email already exists")
        
        db_employee = models.Employee(**employee.dict())
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee
    
    @staticmethod
    def update_employee(db: Session, employee_id: int, employee_update: schemas.EmployeeUpdate) -> Optional[models.Employee]:
        db_employee = EmployeeService.get_employee(db, employee_id)
        if not db_employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        update_data = employee_update.dict(exclude_unset=True)
        
        # Check for unique constraints
        if 'EmployeeCode' in update_data:
            existing = EmployeeService.get_employee_by_code(db, update_data['EmployeeCode'])
            if existing and existing.EmployeeID != employee_id:
                raise HTTPException(status_code=400, detail="Employee code already exists")
        
        if 'CompanyEmail' in update_data:
            existing = EmployeeService.get_employee_by_email(db, update_data['CompanyEmail'])
            if existing and existing.EmployeeID != employee_id:
                raise HTTPException(status_code=400, detail="Company email already exists")
        
        for field, value in update_data.items():
            setattr(db_employee, field, value)
        
        db.commit()
        db.refresh(db_employee)
        return db_employee
    
    @staticmethod
    def delete_employee(db: Session, employee_id: int) -> bool:
        db_employee = EmployeeService.get_employee(db, employee_id)
        if not db_employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Soft delete - set IsActive to False
        db_employee.IsActive = False
        db.commit()
        return True
    
    @staticmethod
    def get_employee_hierarchy(db: Session, employee_id: int) -> List[models.Employee]:
        """Get employee hierarchy (manager chain)"""
        hierarchy = []
        current_employee = EmployeeService.get_employee(db, employee_id)
        
        while current_employee and current_employee.ManagerID:
            manager = EmployeeService.get_employee(db, current_employee.ManagerID)
            if manager:
                hierarchy.append(manager)
                current_employee = manager
            else:
                break
        
        return hierarchy
    
    @staticmethod
    def get_subordinates(db: Session, manager_id: int) -> List[models.Employee]:
        """Get all direct subordinates of a manager"""
        return db.query(models.Employee).filter(
            and_(
                models.Employee.ManagerID == manager_id,
                models.Employee.IsActive == True
            )
        ).all()
    
    @staticmethod
    def get_manager_team_overview(db: Session, manager_id: int) -> schemas.ManagerTeamOverviewResponse:
        """Get comprehensive team overview for a manager"""
        # Get manager details
        manager = EmployeeService.get_employee(db, manager_id)
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        
        # Get all subordinates
        subordinates = EmployeeService.get_subordinates(db, manager_id)
        
        # Get team and department information
        from api.team.models import Team
        from api.department.models import Department
        
        team = db.query(Team).filter(Team.TeamID == manager.TeamID).first()
        department = None
        if team:
            department = db.query(Department).filter(Department.DepartmentID == team.DepartmentID).first()
        
        team_info = {
            "team": {
                "TeamID": team.TeamID if team else None,
                "TeamName": team.TeamName if team else None,
                "TeamCode": team.TeamCode if team else None
            },
            "department": {
                "DepartmentID": department.DepartmentID if department else None,
                "DepartmentName": department.DepartmentName if department else None,
                "DepartmentCode": department.DepartmentCode if department else None
            }
        }
        
        return schemas.ManagerTeamOverviewResponse(
            manager=manager,
            subordinates=subordinates,
            total_subordinates=len(subordinates),
            active_subordinates=len([s for s in subordinates if s.IsActive]),
            team_info=team_info
        )

    @staticmethod
    def get_manager_batch_data(db: Session, manager_id: int) -> schemas.ManagerBatchResponse:
        """Get batch data for manager dashboard"""
        # Get manager's team members
        team_members = EmployeeService.get_subordinates(db, manager_id)
        
        # Get team overview
        team_overview = EmployeeService.get_manager_team_overview(db, manager_id)
        
        return schemas.ManagerBatchResponse(
            team_members=team_members,
            team_overview=team_overview
        )

    @staticmethod
    def get_current_user_manager(db: Session, user_id: str) -> Optional[dict]:
        """Get current user's manager information"""
        from api.auth.models import EmployeeRole, Role
        from api.department.models import Department
        from api.team.models import Team
        
        # Get current employee
        employee = EmployeeService.get_employee_by_user_id(db, user_id)
        if not employee:
            return None
        
        # Check if employee has a manager
        if not employee.ManagerID:
            return None
        
        # Get manager information
        manager = db.query(
            models.Employee.EmployeeID,
            models.Employee.FirstName,
            models.Employee.LastName,
            models.Designation.DesignationName,
            Department.DepartmentName
        ).join(
            models.Designation, models.Employee.DesignationID == models.Designation.DesignationID
        ).join(
            Team, models.Employee.TeamID == Team.TeamID
        ).join(
            Department, Team.DepartmentID == Department.DepartmentID
        ).filter(
            models.Employee.EmployeeID == employee.ManagerID,
            models.Employee.IsActive == True
        ).first()
        
        if not manager:
            return None
        
        # Check if manager has manager role
        roles = db.query(Role.RoleName).join(
            EmployeeRole, Role.RoleID == EmployeeRole.RoleID
        ).filter(
            EmployeeRole.EmployeeID == manager.EmployeeID,
            EmployeeRole.IsActive == True
        ).all()
        
        role_names = [role.RoleName for role in roles]
        is_manager = any('Manager' in role for role in role_names)
        is_hr = any('HR' in role for role in role_names)
        
        return {
            "EmployeeID": manager.EmployeeID,
            "EmployeeName": f"{manager.FirstName} {manager.LastName}",
            "DesignationName": manager.DesignationName,
            "DepartmentName": manager.DepartmentName,
            "isManager": is_manager,
            "isHR": is_hr
        }

class EmergencyContactService:
    
    @staticmethod
    def get_emergency_contacts(db: Session, employee_id: int) -> List[models.EmergencyContact]:
        return db.query(models.EmergencyContact).filter(
            and_(
                models.EmergencyContact.EmployeeID == employee_id,
                models.EmergencyContact.IsActive == True
            )
        ).all()
    
    @staticmethod
    def create_emergency_contact(db: Session, employee_id: int, contact: schemas.EmergencyContactCreate) -> models.EmergencyContact:
        # If this is a primary contact, unset other primary contacts
        if contact.IsPrimary:
            db.query(models.EmergencyContact).filter(
                and_(
                    models.EmergencyContact.EmployeeID == employee_id,
                    models.EmergencyContact.IsPrimary == True,
                    models.EmergencyContact.IsActive == True
                )
            ).update({"IsPrimary": False})
        
        contact_data = contact.dict()
        contact_data['EmployeeID'] = employee_id
        db_contact = models.EmergencyContact(**contact_data)
        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)
        return db_contact
    
    @staticmethod
    def update_emergency_contact(db: Session, contact_id: int, contact_update: schemas.EmergencyContactUpdate) -> Optional[models.EmergencyContact]:
        db_contact = db.query(models.EmergencyContact).filter(models.EmergencyContact.ContactID == contact_id).first()
        if not db_contact:
            raise HTTPException(status_code=404, detail="Emergency contact not found")
        
        update_data = contact_update.dict(exclude_unset=True)
        
        # Handle primary contact logic
        if update_data.get('IsPrimary', False):
            db.query(models.EmergencyContact).filter(
                and_(
                    models.EmergencyContact.EmployeeID == db_contact.EmployeeID,
                    models.EmergencyContact.ContactID != contact_id,
                    models.EmergencyContact.IsPrimary == True,
                    models.EmergencyContact.IsActive == True
                )
            ).update({"IsPrimary": False})
        
        for field, value in update_data.items():
            setattr(db_contact, field, value)
        
        db.commit()
        db.refresh(db_contact)
        return db_contact
    
    @staticmethod
    def delete_emergency_contact(db: Session, contact_id: int) -> bool:
        db_contact = db.query(models.EmergencyContact).filter(models.EmergencyContact.ContactID == contact_id).first()
        if not db_contact:
            raise HTTPException(status_code=404, detail="Emergency contact not found")
        
        db_contact.IsActive = False
        db.commit()
        return True

class LookupService:
    
    @staticmethod
    def get_genders(db: Session) -> List[models.Gender]:
        return db.query(models.Gender).filter(models.Gender.IsActive == True).all()
    
    @staticmethod
    def get_employment_types(db: Session) -> List[models.EmploymentType]:
        return db.query(models.EmploymentType).filter(models.EmploymentType.IsActive == True).all()
    
    @staticmethod
    def get_work_modes(db: Session) -> List[models.WorkMode]:
        return db.query(models.WorkMode).filter(models.WorkMode.IsActive == True).all()
    
    @staticmethod
    def get_designations(db: Session) -> List[models.Designation]:
        return db.query(models.Designation).filter(models.Designation.IsActive == True).all()

    @staticmethod
    def get_feedback_targets(db: Session) -> List[dict]:
        """Get list of employees who can receive feedback (managers and HR)"""
        from api.auth.models import EmployeeRole, Role
        from api.department.models import Department
        from api.team.models import Team
        
        # Get employees with manager or HR roles
        query = db.query(
            models.Employee.EmployeeID,
            models.Employee.FirstName,
            models.Employee.LastName,
            models.Designation.DesignationName,
            Department.DepartmentName
        ).join(
            models.Designation, models.Employee.DesignationID == models.Designation.DesignationID
        ).join(
            Team, models.Employee.TeamID == Team.TeamID
        ).join(
            Department, Team.DepartmentID == Department.DepartmentID
        ).filter(
            models.Employee.IsActive == True
        )
        
        employees = query.all()
        
        # Get role information for each employee
        targets = []
        for emp in employees:
            # Check if employee has manager or HR role
            roles = db.query(Role.RoleName).join(
                EmployeeRole, Role.RoleID == EmployeeRole.RoleID
            ).filter(
                EmployeeRole.EmployeeID == emp.EmployeeID,
                EmployeeRole.IsActive == True
            ).all()
            
            role_names = [role.RoleName for role in roles]
            is_manager = any('Manager' in role for role in role_names)
            is_hr = any('HR' in role for role in role_names)
            
            # Include if they are a manager or HR
            if is_manager or is_hr:
                targets.append({
                    "EmployeeID": emp.EmployeeID,
                    "EmployeeName": f"{emp.FirstName} {emp.LastName}",
                    "DesignationName": emp.DesignationName,
                    "DepartmentName": emp.DepartmentName,
                    "isManager": is_manager,
                    "isHR": is_hr
                })
        
        return targets 