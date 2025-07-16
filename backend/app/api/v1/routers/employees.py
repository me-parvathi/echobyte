from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...services.getters import (
    list_Employees,
    get_Employees,
    list_EmergencyContacts,
)

router = APIRouter(prefix="/employees", tags=["Employees"])

# ---------------------------------------------------------------------------
# Employees (basic list + retrieve)
# ---------------------------------------------------------------------------

@router.get("/", response_model=List[dict])
def list_employees(db: Session = Depends(get_db)):
    return list_Employees(db)


@router.get("/{employee_id}")
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    obj = get_Employees(employee_id, db)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return obj

# ---------------------------------------------------------------------------
# Emergency contacts (nested resource)
# ---------------------------------------------------------------------------

@router.get("/{employee_id}/contacts", response_model=List[dict])
def list_contacts(employee_id: int, db: Session = Depends(get_db)):
    contacts = list_EmergencyContacts(db)
    return [c for c in contacts if c.get("EmployeeID") == employee_id] 