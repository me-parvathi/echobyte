from __future__ import annotations

from typing import Any, Dict, List

from fastapi import Body, Depends, FastAPI, HTTPException, Path
from sqlalchemy.inspection import inspect as sql_inspect
from sqlalchemy.orm import Session

from .database import Base, get_db
# Import domain routers (designed API)
from .api.v1.routers import org, employees, assets, leave, timesheets

app = FastAPI(
    title="EchoByte REST API",
    description="Auto-generated CRUD endpoints for every table defined in ddl.sql.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Mount higher-level domain routers (designed API)
# ---------------------------------------------------------------------------

app.include_router(org.router, prefix="/api")
app.include_router(employees.router, prefix="/api")
app.include_router(leave.router, prefix="/api")
app.include_router(timesheets.router, prefix="/api")
app.include_router(assets.router, prefix="/api")


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _model_to_dict(instance) -> Dict[str, Any]:
    """Convert an SQLAlchemy model instance to a plain dict (JSON-serialisable)."""
    return {
        attr.key: getattr(instance, attr.key)
        for attr in sql_inspect(instance).mapper.column_attrs
    }


# ---------------------------------------------------------------------------
# Dynamic route generator – one set of CRUD endpoints per table with a simple
# primary key. Composite-key tables are skipped for brevity but can be added
# later with a custom router.
# ---------------------------------------------------------------------------

def _register_routes() -> None:
    for table_name, model in Base.classes.items():
        mapper = sql_inspect(model)
        pk_cols = [col for col in mapper.primary_key]

        # Skip views + composite-PK tables for now
        if len(pk_cols) != 1:
            continue

        pk_col = pk_cols[0]
        pk_name: str = pk_col.name
        path_prefix = f"/api/{table_name.lower()}"

        # ------------------ CRUD handlers ------------------
        async def list_rows(db: Session = Depends(get_db), _model=model):
            rows: List[Any] = db.query(_model).all()
            return [_model_to_dict(r) for r in rows]

        async def get_row(
            pk: Any = Path(..., description=f"Primary key of {table_name}"),
            db: Session = Depends(get_db),
            _model=model,
        ):
            obj = db.query(_model).get(pk)
            if not obj:
                raise HTTPException(status_code=404, detail="Item not found")
            return _model_to_dict(obj)

        async def create_row(
            payload: Dict[str, Any] = Body(..., description="JSON body representing the row"),
            db: Session = Depends(get_db),
            _model=model,
        ):
            obj = _model(**payload)
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return _model_to_dict(obj)

        async def update_row(
            pk: Any = Path(..., description=f"Primary key of {table_name}"),
            payload: Dict[str, Any] = Body(...),
            db: Session = Depends(get_db),
            _model=model,
        ):
            obj = db.query(_model).get(pk)
            if not obj:
                raise HTTPException(status_code=404, detail="Item not found")
            for key, value in payload.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            db.commit()
            db.refresh(obj)
            return _model_to_dict(obj)

        async def delete_row(
            pk: Any = Path(..., description=f"Primary key of {table_name}"),
            db: Session = Depends(get_db),
            _model=model,
        ):
            obj = db.query(_model).get(pk)
            if not obj:
                raise HTTPException(status_code=404, detail="Item not found")
            db.delete(obj)
            db.commit()
            return {"detail": "Deleted"}

        # ------------------ Route registration ------------------
        app.get(path_prefix, tags=[table_name])(list_rows)
        app.get(f"{path_prefix}/{{{pk_name}}}", tags=[table_name])(get_row)
        app.post(path_prefix, tags=[table_name])(create_row)
        app.put(f"{path_prefix}/{{{pk_name}}}", tags=[table_name])(update_row)
        app.delete(f"{path_prefix}/{{{pk_name}}}", tags=[table_name])(delete_row)


_register_routes()

# Root endpoint
@app.get("/", tags=["meta"])
async def root() -> Dict[str, str]:
    return {"message": "EchoByte API is running"}
