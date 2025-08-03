"""Extensions for generate_data.py

Adds generation of EmployeeRoles and LeaveBalances CSVs so the dataset
fully covers the security-model and leave-tracking tables required by
the echobyte company-portal schema.

This extension provides additional functions for role assignment and
leave balance tracking that complement the main data generation script.

Usage:
  Drop this file next to the main script and:
  from faker_employee_roles_leave_balance_extensions import (
      gen_employee_roles,
      gen_leave_balances,
  )
  ...then call those functions in main() right before writing CSVs.
  
Note: This appears to be an older extension that may not be fully
compatible with the current generate_data.py script structure.
"""
from __future__ import annotations

import datetime as dt
import random
from collections import defaultdict
from typing import List, Dict, Any

# ────────────────────────────────
# CONSTANTS — keep in sync with DDL seed data
# ────────────────────────────────
# Role assignments for employee security model
# These IDs must match the Roles table in the database schema
ROLE_IDS: Dict[str, int] = {
    "Employee": 1,      # Base role for all employees
    "Manager": 2,       # Team and department managers
    "HR": 3,           # Human Resources staff
    "IT Support": 4,    # IT support and technical staff
    "Admin": 5,         # System administrators
    "CEO": 6,          # Chief Executive Officer
}

# Leave type entitlements - annual days per leave type
# These values define the standard annual leave entitlements
LEAVE_ENTITLEMENTS: Dict[int, float | None] = {
    1: 15.0,   # PTO (Paid Time Off)
    2: 10.0,   # Sick Leave
    3: 90.0,   # Maternity Leave
    4: 10.0,   # Paternity Leave
    5: 5.0,    # Bereavement Leave
    6: 0.0,    # Unpaid Leave – no entitlement
}

# ────────────────────────────────
# Helper Functions
# ────────────────────────────────

def _append_role(rows: list[dict],
                 row_id: int,
                 employee_id: int,
                 role_id: int,
                 assigned_by: int,
                 timestamp: str) -> None:
    """
    Helper function to append a role assignment to the rows list.
    
    Creates a standardized role assignment record with proper formatting
    and consistent field names for the EmployeeRoles table.
    
    Args:
        rows: List to append the role assignment to
        row_id: Unique identifier for the role assignment
        employee_id: ID of the employee being assigned the role
        role_id: ID of the role being assigned
        assigned_by: ID of the employee who assigned this role
        timestamp: ISO format timestamp for when the role was assigned
    """
    rows.append({
        "employee_role_id": row_id,
        "employee_id": employee_id,
        "role_id": role_id,
        "assigned_at": timestamp,
        "assigned_by_id": assigned_by,
        "is_active": True,
    })

# ────────────────────────────────
# 1. Employee Role Generation
# ────────────────────────────────

def gen_employee_roles(employees: list[dict],
                       teams: list[dict],
                       departments: list[dict]) -> list[dict]:
    """
    Create employee role assignments based on organizational hierarchy and department.
    
    Assigns roles to employees following these business rules:
    • Everyone gets the Employee role (id 1) as their base role
    • Anyone referenced as a manager receives Manager role (id 2)
    • Staff in HR departments get HR role (id 3) with 60% probability
    • Staff in IT departments get IT Support role (id 4) with 70% probability
    • Exactly one employee is randomly selected as CEO (id 6)
    • Exactly two employees are randomly selected as Admins (id 5)
    
    Args:
        employees: List of employee dictionaries
        teams: List of team dictionaries for department lookup
        departments: List of department dictionaries
        
    Returns:
        List of employee role assignment dictionaries
    """

    now = dt.datetime.utcnow().isoformat(sep=" ")
    rows: list[dict] = []
    next_id = 1

    # Build quick look-ups for efficient department and team access
    dept_by_id = {d["department_id"]: d for d in departments}
    team_by_id = {t["team_id"]: t for t in teams}

    # Identify managers and active employees
    manager_ids = {emp["manager_id"] for emp in employees if emp["manager_id"]}
    active_ids  = [emp["employee_id"] for emp in employees if not emp["is_deleted"]]

    # Select leadership positions randomly
    ceo_id   = random.choice(active_ids)
    admin_ids = random.sample([eid for eid in active_ids if eid != ceo_id], k=2)

    for emp in employees:
        eid = emp["employee_id"]
        # Always assign Employee role as base role
        _append_role(rows, next_id, eid, ROLE_IDS["Employee"], ceo_id, now)
        next_id += 1

        # Assign Manager role if employee leads others
        if eid in manager_ids:
            _append_role(rows, next_id, eid, ROLE_IDS["Manager"], ceo_id, now)
            next_id += 1

        # Assign department-specific roles based on team assignment
        dept_name = dept_by_id[team_by_id[emp["team_id"]]["department_id"]]["name"].lower()
        if "hr" in dept_name and random.random() < 0.60:
            _append_role(rows, next_id, eid, ROLE_IDS["HR"], ceo_id, now)
            next_id += 1
        if "it" in dept_name and random.random() < 0.70:
            _append_role(rows, next_id, eid, ROLE_IDS["IT Support"], ceo_id, now)
            next_id += 1

        # Assign leadership roles
        if eid in admin_ids:
            _append_role(rows, next_id, eid, ROLE_IDS["Admin"], ceo_id, now)
            next_id += 1
        if eid == ceo_id:
            _append_role(rows, next_id, eid, ROLE_IDS["CEO"], ceo_id, now)
            next_id += 1

    return rows

# ────────────────────────────────
# 2. Leave Balance Generation
# ────────────────────────────────

def gen_leave_balances(employees: list[dict],
                       leave_requests: list[dict],
                       year: int) -> list[dict]:
    """
    Generate leave balance records by aggregating approved leave usage.
    
    Creates leave balance entries for each employee and leave type combination
    for the specified year. Calculates used days by summing approved leave
    requests and compares against annual entitlements.
    
    Args:
        employees: List of employee dictionaries
        leave_requests: List of leave request dictionaries
        year: Year for which to generate leave balances
        
    Returns:
        List of leave balance dictionaries with entitled and used days
    """

    now = dt.datetime.utcnow().isoformat(sep=" ")

    # Calculate used leave days by aggregating approved leave requests
    used_map: dict[tuple[int,int], float] = defaultdict(float)
    for req in leave_requests:
        if req["leave_status_id"] == 2:  # approved status
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
        # Create balance record for each leave type
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
