from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...services.getters import (
    list_Assets,
    get_Assets,
    list_AssetAssignments,
)

router = APIRouter(prefix="/assets", tags=["Assets"])

# ---------------------------------------------------------------------------
# Assets (list + retrieve)
# ---------------------------------------------------------------------------

@router.get("/", response_model=List[dict])
def list_assets(db: Session = Depends(get_db)):
    return list_Assets(db)


@router.get("/{asset_id}")
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    obj = get_Assets(asset_id, db)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return obj

# ---------------------------------------------------------------------------
# Current assignment helper (if one exists and not ReturnedAt)
# ---------------------------------------------------------------------------

@router.get("/{asset_id}/assignment", response_model=dict | None)
def get_current_assignment(asset_id: int, db: Session = Depends(get_db)):
    assignments = list_AssetAssignments(db)
    for row in assignments:
        if row.get("AssetID") == asset_id and row.get("ReturnedAt") is None:
            return row
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active assignment") 