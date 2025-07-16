from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...services.getters import (
    list_LeaveTypes,
    get_LeaveTypes,
    list_LeaveApplications,
    get_LeaveApplications,
)

router = APIRouter(prefix="/leave", tags=["Leave"])

# ---------------------------------------------------------------------------
# Leave types
# ---------------------------------------------------------------------------

@router.get("/types", response_model=List[dict])
def list_leave_types(db: Session = Depends(get_db)):
    return list_LeaveTypes(db)


@router.get("/types/{leave_type_id}")
def get_leave_type(leave_type_id: int, db: Session = Depends(get_db)):
    obj = get_LeaveTypes(leave_type_id, db)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave type not found")
    return obj

# ---------------------------------------------------------------------------
# Leave applications
# ---------------------------------------------------------------------------

@router.get("/applications", response_model=List[dict])
def list_leave_applications(db: Session = Depends(get_db)):
    return list_LeaveApplications(db)


@router.get("/applications/{application_id}")
def get_leave_application(application_id: int, db: Session = Depends(get_db)):
    obj = get_LeaveApplications(application_id, db)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave application not found")
    return obj 