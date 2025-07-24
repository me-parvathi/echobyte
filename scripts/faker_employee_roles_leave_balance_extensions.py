"""Extensions for generate_fake_company_portal_data.py

Adds generation of EmployeeRoles and LeaveBalances CSVs so the dataset
fully covers the security‑model and leave‑tracking tables required by
the echobyte company‑portal schema.

Drop this file next to the original script and:
  from faker_employee_roles_leave_balance_extensions import (
      gen_employee_roles,
      gen_leave_balances,
  )
...then call those functions in main() right before writing CSVs.
"""
from __future__ import annotations

import datetime as dt
import random
from collections import defaultdict
from typing import List, Dict, Any

# ────────────────────────────────
# CONSTANTS — keep in sync with DDL seed data
# ────────────────────────────────
ROLE_IDS: Dict[str, int] = {
    "Employee": 1,
    "Manager": 2,
    "HR": 3,
    "IT Support": 4,
    "Admin": 5,
    "CEO": 6,
}

# Leave‑type PK → annual entitlement (days)
LEAVE_ENTITLEMENTS: Dict[int, float | None] = {
    1: 15.0,   # PTO
    2: 10.0,   # Sick
    3: 90.0,   # Maternity
    4: 10.0,   # Paternity
    5: 5.0,    # Bereavement
    6: 0.0,    # Unpaid – no entitlement
}

# ────────────────────────────────
# Helper – assign a role row
# ────────────────────────────────

def _append_role(rows: list[dict],
                 row_id: int,
                 employee_id: int,
                 role_id: int,
                 assigned_by: int,
                 timestamp: str) -> None:
    rows.append({
        "employee_role_id": row_id,
        "employee_id": employee_id,
        "role_id": role_id,
        "assigned_at": timestamp,
        "assigned_by_id": assigned_by,
        "is_active": True,
    })

# ────────────────────────────────
# 1. EmployeeRoles
# ────────────────────────────────

def gen_employee_roles(employees: list[dict],
                       teams: list[dict],
                       departments: list[dict]) -> list[dict]:
    """Create rows for dbo.EmployeeRoles

    Logic:
      • Everyone gets the **Employee** role (id 1).
      • Anyone referenced as a manager receives **Manager** (id 2).
      • Staff in the HR / IT departments get their respective roles with
        60 % / 70 % probabilities.
      • Elect exactly one CEO and two Admins for flavour.
    """

    now = dt.datetime.utcnow().isoformat(sep=" ")
    rows: list[dict] = []
    next_id = 1

    # Build quick look‑ups
    dept_by_id = {d["department_id"]: d for d in departments}
    team_by_id = {t["team_id"]: t for t in teams}

    manager_ids = {emp["manager_id"] for emp in employees if emp["manager_id"]}
    active_ids  = [emp["employee_id"] for emp in employees if not emp["is_deleted"]]

    ceo_id   = random.choice(active_ids)
    admin_ids = random.sample([eid for eid in active_ids if eid != ceo_id], k=2)

    for emp in employees:
        eid = emp["employee_id"]
        # Always Employee
        _append_role(rows, next_id, eid, ROLE_IDS["Employee"], ceo_id, now)
        next_id += 1

        # Manager if leads someone
        if eid in manager_ids:
            _append_role(rows, next_id, eid, ROLE_IDS["Manager"], ceo_id, now)
            next_id += 1

        # Department‑based roles
        dept_name = dept_by_id[team_by_id[emp["team_id"]]["department_id"]]["name"].lower()
        if "hr" in dept_name and random.random() < 0.60:
            _append_role(rows, next_id, eid, ROLE_IDS["HR"], ceo_id, now)
            next_id += 1
        if "it" in dept_name and random.random() < 0.70:
            _append_role(rows, next_id, eid, ROLE_IDS["IT Support"], ceo_id, now)
            next_id += 1

        # Admin / CEO picks
        if eid in admin_ids:
            _append_role(rows, next_id, eid, ROLE_IDS["Admin"], ceo_id, now)
            next_id += 1
        if eid == ceo_id:
            _append_role(rows, next_id, eid, ROLE_IDS["CEO"], ceo_id, now)
            next_id += 1

    return rows

# ────────────────────────────────
# 2. LeaveBalances
# ────────────────────────────────

def gen_leave_balances(employees: list[dict],
                       leave_requests: list[dict],
                       year: int) -> list[dict]:
    """Aggregate leave usage per (Employee, LeaveType, Year)."""

    now = dt.datetime.utcnow().isoformat(sep=" ")

    # Sum approved leave by employee & type
    used_map: dict[tuple[int,int], float] = defaultdict(float)
    for req in leave_requests:
        if req["leave_status_id"] == 2:  # approved
            start_year = dt.date.fromisoformat(req["start_date"]).year
            if start_year == year:
                key = (req["employee_id"], req["leave_type_id"])
                used_map[key] += req["days_requested"]

    rows: list[dict] = []
    next_id = 1
    for emp in employees:
        if emp["is_deleted"]:
            continue  # skip deleted staff
        eid = emp["employee_id"]
        for lt_id, entitled in LEAVE_ENTITLEMENTS.items():
            rows.append({
                "balance_id": next_id,
                "employee_id": eid,
                "leave_type_id": lt_id,
                "year": year,
                "entitled_days": entitled,
                "used_days": round(used_map.get((eid, lt_id), 0.0), 1),
                "created_at": now,
                "updated_at": now,
            })
            next_id += 1
    return rows
