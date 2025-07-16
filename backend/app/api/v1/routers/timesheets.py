from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...services.getters import (
    list_Timesheets,
    get_Timesheets,
    list_TimesheetDetails,
    get_TimesheetDetails,
)

router = APIRouter(prefix="/timesheets", tags=["Timesheets"])

# ---------------------------------------------------------------------------
# Timesheets
# ---------------------------------------------------------------------------

@router.get("/", response_model=List[dict])
def list_timesheets(db: Session = Depends(get_db)):
    return list_Timesheets(db)


@router.get("/{timesheet_id}")
def get_timesheet(timesheet_id: int, db: Session = Depends(get_db)):
    obj = get_Timesheets(timesheet_id, db)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timesheet not found")
    return obj

# ---------------------------------------------------------------------------
# Timesheet details (nested)
# ---------------------------------------------------------------------------

@router.get("/{timesheet_id}/details", response_model=List[dict])
def list_details(timesheet_id: int, db: Session = Depends(get_db)):
    details = list_TimesheetDetails(db)
    return [d for d in details if d.get("TimesheetID") == timesheet_id]


@router.get("/details/{detail_id}")
def get_detail(detail_id: int, db: Session = Depends(get_db)):
    obj = get_TimesheetDetails(detail_id, db)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detail not found")
    return obj 