from __future__ import annotations

"""Generic list/get helper functions for every table that SQLAlchemy reflects at runtime.

Usage:
    from app.services.getters import list_Employees, get_Employees

    rows   = list_Employees(db)
    single = get_Employees(emp_id, db)

Two helpers are created per table at import-time and also stored in the
`GETTERS` dict for programmatic access.
"""

from typing import Any, Dict, List, Callable, Type

from sqlalchemy.orm import Session

from ..database import Base

# ---------------------------------------------------------------------------
# Utility – convert ORM instance → plain dict (JSON-serialisable)
# ---------------------------------------------------------------------------

def _model_to_dict(instance) -> Dict[str, Any]:
    """Lightweight instance → dict conversion without recursion/relationships."""
    return {
        attr.key: getattr(instance, attr.key)
        for attr in instance.__mapper__.column_attrs
    }

# Mapping: {TableName: {"list": callable, "get": callable}}
GETTERS: Dict[str, Dict[str, Callable]] = {}


def _register_getters() -> None:  # noqa: C901  (complexity from closure pattern)
    """Walk all mapped classes and create list_/get_ helpers dynamically."""
    for table_name, model in Base.classes.items():
        # Grab the first PK column (multi-col PKs handled elsewhere)
        pk_column = next(iter(model.__table__.primary_key.columns))

        # --- list helper ----------------------------------------------------
        def _list(db: Session, _m: Type[model] = model) -> List[Dict[str, Any]]:  # type: ignore[name-defined]
            rows = db.query(_m).all()
            return [_model_to_dict(r) for r in rows]

        # --- get helper -----------------------------------------------------
        def _get(
            pk: Any,
            db: Session,
            _m: Type[model] = model,  # type: ignore[name-defined]
            _pk_name: str = pk_column.name,
        ) -> Dict[str, Any] | None:
            obj = db.query(_m).get(pk)
            return _model_to_dict(obj) if obj else None

        # Export helpers to module globals so that they can be imported by name
        list_name = f"list_{table_name}"
        get_name = f"get_{table_name}"
        globals()[list_name] = _list
        globals()[get_name] = _get

        GETTERS[table_name] = {"list": _list, "get": _get}


# Register helpers immediately on import
_register_getters() 