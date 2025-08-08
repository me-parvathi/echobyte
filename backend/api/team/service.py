from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from . import models, schemas
from fastapi import HTTPException

class TeamService:
    
    @staticmethod
    def get_team(db: Session, team_id: int) -> Optional[models.Team]:
        return db.query(models.Team).filter(models.Team.TeamID == team_id).first()
    
    @staticmethod
    def get_team_by_code(db: Session, team_code: str) -> Optional[models.Team]:
        return db.query(models.Team).filter(models.Team.TeamCode == team_code).first()
    
    @staticmethod
    def get_teams(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None,
        department_id: Optional[int] = None
    ) -> List[models.Team]:
        query = db.query(models.Team)
        
        if is_active is not None:
            query = query.filter(models.Team.IsActive == is_active)
        
        if department_id:
            query = query.filter(models.Team.DepartmentID == department_id)
        
        return query.order_by(models.Team.TeamID).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_team(db: Session, team: schemas.TeamCreate) -> models.Team:
        # Check if team code already exists
        if TeamService.get_team_by_code(db, team.TeamCode):
            raise HTTPException(status_code=400, detail="Team code already exists")
        
        # Validate department exists
        from api.department.models import Department
        department = db.query(Department).filter(Department.DepartmentID == team.DepartmentID).first()
        if not department:
            raise HTTPException(status_code=400, detail="Department not found")
        
        # Validate team lead exists if provided
        if team.TeamLeadEmployeeID:
            from api.employee.models import Employee
            employee = db.query(Employee).filter(Employee.EmployeeID == team.TeamLeadEmployeeID).first()
            if not employee:
                raise HTTPException(status_code=400, detail="Team lead employee not found")
        
        db_team = models.Team(**team.dict())
        db.add(db_team)
        db.commit()
        db.refresh(db_team)
        return db_team
    
    @staticmethod
    def update_team(db: Session, team_id: int, team_update: schemas.TeamUpdate) -> Optional[models.Team]:
        db_team = TeamService.get_team(db, team_id)
        if not db_team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        update_data = team_update.dict(exclude_unset=True)
        
        # Check for unique constraints
        if 'TeamCode' in update_data:
            existing = TeamService.get_team_by_code(db, update_data['TeamCode'])
            if existing and existing.TeamID != team_id:
                raise HTTPException(status_code=400, detail="Team code already exists")
        
        # Validate department exists
        if 'DepartmentID' in update_data:
            from api.department.models import Department
            department = db.query(Department).filter(Department.DepartmentID == update_data['DepartmentID']).first()
            if not department:
                raise HTTPException(status_code=400, detail="Department not found")
        
        # Validate team lead exists if provided
        if 'TeamLeadEmployeeID' in update_data and update_data['TeamLeadEmployeeID']:
            from api.employee.models import Employee
            employee = db.query(Employee).filter(Employee.EmployeeID == update_data['TeamLeadEmployeeID']).first()
            if not employee:
                raise HTTPException(status_code=400, detail="Team lead employee not found")
        
        for field, value in update_data.items():
            setattr(db_team, field, value)
        
        db.commit()
        db.refresh(db_team)
        return db_team
    
    @staticmethod
    def delete_team(db: Session, team_id: int) -> bool:
        db_team = TeamService.get_team(db, team_id)
        if not db_team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Check if team has employees
        from api.employee.models import Employee
        employees_count = db.query(Employee).filter(Employee.TeamID == team_id).count()
        
        if employees_count > 0:
            raise HTTPException(status_code=400, detail="Cannot delete team with employees")
        
        # Soft delete - set IsActive to False
        db_team.IsActive = False
        db.commit()
        return True
    
    @staticmethod
    def get_team_members(db: Session, team_id: int) -> List:
        """Get all employees in a team"""
        from api.employee.models import Employee
        return db.query(Employee).filter(
            and_(
                Employee.TeamID == team_id,
                Employee.IsActive == True
            )
        ).all() 