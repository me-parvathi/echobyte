from sqlalchemy.orm import Session
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
        """Get employees with total count for pagination"""
        # Build the base query
        query = db.query(models.Employee)
        
        if is_active is not None:
            query = query.filter(models.Employee.IsActive == is_active)
        
        if team_id:
            query = query.filter(models.Employee.TeamID == team_id)
        
        if department_id:
            query = query.join(Team, models.Employee.TeamID == Team.TeamID).filter(Team.DepartmentID == department_id)
        
        # Add search filter
        if search:
            print(f"DEBUG: Searching for '{search}'")
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    models.Employee.FirstName.ilike(search_term),
                    models.Employee.LastName.ilike(search_term),
                    models.Employee.EmployeeCode.ilike(search_term),
                    models.Employee.CompanyEmail.ilike(search_term)
                )
            )
            print(f"DEBUG: Search query applied")
        
        # Get total count before pagination
        total_count = query.count()
        print(f"DEBUG: Total count after search: {total_count}")
        
        # Get paginated results
        employees = query.order_by(models.Employee.EmployeeID).offset(skip).limit(limit).all()
        print(f"DEBUG: Returning {len(employees)} employees")
        
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
        """Get manager data and subordinates in a single optimized request"""
        from datetime import datetime
        from api.team.models import Team
        from api.department.models import Department
        
        # Get manager details
        manager = EmployeeService.get_employee(db, manager_id)
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        
        # Get all subordinates
        subordinates = EmployeeService.get_subordinates(db, manager_id)
        
        # Get team and department information in the same session
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
        
        active_subordinates = [s for s in subordinates if s.IsActive]
        
        return schemas.ManagerBatchResponse(
            manager=manager,
            subordinates=subordinates,
            total_subordinates=len(subordinates),
            active_subordinates=len(active_subordinates),
            team_info=team_info,
            last_updated=datetime.utcnow().isoformat()
        )

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