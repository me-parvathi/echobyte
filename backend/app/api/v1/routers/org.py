from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db  # relative to backend/app/api/v1/routers, ... brings us to backend/app
from ...services.getters import (
    list_Locations,
    get_Locations,
    list_Departments,
    get_Departments,
    list_Teams,
    get_Teams,
)

router = APIRouter(prefix="/org", tags=["Organisation"])

# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------

@router.get("/locations", response_model=List[dict])
def list_locations(db: Session = Depends(get_db)):
    return list_Locations(db)


@router.get("/locations/{location_id}")
def get_location(location_id: int, db: Session = Depends(get_db)):
    obj = get_Locations(location_id, db)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return obj

# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------

@router.get("/departments", response_model=List[dict])
def list_departments(db: Session = Depends(get_db)):
    return list_Departments(db)


@router.get("/departments/{department_id}")
def get_department(department_id: int, db: Session = Depends(get_db)):
    obj = get_Departments(department_id, db)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return obj

# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------

@router.get("/teams", response_model=List[dict])
def list_teams(db: Session = Depends(get_db)):
    return list_Teams(db)


@router.get("/teams/{team_id}")
def get_team(team_id: int, db: Session = Depends(get_db)):
    obj = get_Teams(team_id, db)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return obj 