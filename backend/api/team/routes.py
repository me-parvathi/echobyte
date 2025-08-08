from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from . import schemas, service

router = APIRouter()

# Team routes
@router.get("/", response_model=schemas.TeamListResponse)
def get_teams(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get list of teams with optional filtering"""
    teams = service.TeamService.get_teams(
        db, skip=skip, limit=limit, 
        is_active=is_active, department_id=department_id
    )
    total = len(teams)
    return schemas.TeamListResponse(
        teams=teams, total=total, page=skip//limit + 1, size=limit
    )

@router.get("/{team_id}", response_model=schemas.TeamResponse)
def get_team(team_id: int, db: Session = Depends(get_db)):
    """Get a specific team by ID"""
    team = service.TeamService.get_team(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.post("/", response_model=schemas.TeamResponse, status_code=201)
def create_team(team: schemas.TeamCreate, db: Session = Depends(get_db)):
    """Create a new team"""
    return service.TeamService.create_team(db, team)

@router.put("/{team_id}", response_model=schemas.TeamResponse)
def update_team(
    team_id: int, 
    team_update: schemas.TeamUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing team"""
    return service.TeamService.update_team(db, team_id, team_update)

@router.delete("/{team_id}", status_code=204)
def delete_team(team_id: int, db: Session = Depends(get_db)):
    """Soft delete a team (set IsActive to False)"""
    service.TeamService.delete_team(db, team_id)
    return None

@router.get("/{team_id}/members")
def get_team_members(team_id: int, db: Session = Depends(get_db)):
    """Get all employees in a team"""
    members = service.TeamService.get_team_members(db, team_id)
    return members 