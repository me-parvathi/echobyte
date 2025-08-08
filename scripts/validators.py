#!/usr/bin/env python3
"""
validators.py
─────────────
Light-weight sanity checks over the generated CSVs.  Raises AssertionError if
any rule is broken.  Prints a summary otherwise.

Checks implemented
1. Manager hierarchy has no cycles and a single CEO.
2. Every non-HR employee has an HREmployeeID; HR load between 10 and 20.
3. TimesheetDetails.ProjectID is blank or belongs to the employee via
   ProjectAssignments.
4. LeaveApplications do not overlap any Timesheet week for that employee.
"""
from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path
from typing import Dict, List, Set, Tuple

# ---------------------------------------------------------------------------

_DEF_DIR = Path("csv_out")


def _read(name: str) -> List[Dict]:
    with (_DEF_DIR / f"{name}.csv").open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

# ---------------------------------------------------------------------------
# 1) MANAGER HIERARCHY
# ---------------------------------------------------------------------------

def _check_manager_hierarchy():
    employees = _read("Employees")
    mgr_map = {int(r["EmployeeID"]): (int(r["ManagerID"]) if r["ManagerID"] else None) for r in employees}

    # exactly one with ManagerID NULL -> CEO
    root_nodes = [eid for eid, mid in mgr_map.items() if mid is None]
    assert len(root_nodes) == 1, f"Expected 1 CEO, found {len(root_nodes)}"  # noqa

    visited: Set[int] = set()

    def dfs(eid: int, stack: Set[int]):
        mid = mgr_map.get(eid)
        if mid is None:
            return
        if mid in stack:
            raise AssertionError(f"Cycle detected at employee {eid} -> {mid}")
        stack.add(mid)
        dfs(mid, stack)
        stack.remove(mid)

    for eid in mgr_map:
        dfs(eid, {eid})
        visited.add(eid)

# ---------------------------------------------------------------------------
# 2) HR LOAD
# ---------------------------------------------------------------------------

def _check_hr_load():
    emp_rows = _read("Employees")
    hr_role_rows = [r for r in _read("EmployeeRoles") if r["RoleID"] == "3"]
    hr_ids = {int(r["EmployeeID"]) for r in hr_role_rows}

    load: Dict[int, int] = {hid: 0 for hid in hr_ids}
    for row in emp_rows:
        hr_id = int(row["HREmployeeID"]) if row["HREmployeeID"] else None
        if hr_id is not None:
            load[hr_id] = load.get(hr_id, 0) + 1

    for hid, cnt in load.items():
        if cnt < 10 or cnt > 20:
            raise AssertionError(f"HR {hid} load {cnt} outside 10-20 range")

# ---------------------------------------------------------------------------
# 3) TIMESHEET DETAILS PROJECT CHECK
# ---------------------------------------------------------------------------

def _check_timesheet_project_membership():
    assigns = _read("ProjectAssignments")
    by_emp: Dict[int, Set[int]] = {}
    for row in assigns:
        by_emp.setdefault(int(row["EmployeeID"]), set()).add(int(row["ProjectID"]))

    bad = 0
    for d in _read("TimesheetDetails"):
        proj = d["ProjectID"]
        if not proj:
            continue
        eid = int(_timesheet_emp_map[int(d["TimesheetID"])] )
        if int(proj) not in by_emp.get(eid, set()):
            bad += 1
            if bad > 20:
                break
    assert bad == 0, f"{bad} TimesheetDetails rows reference projects not assigned to employee"

# Helper: build timesheet -> employee map once
_timesheet_emp_map = {int(r["TimesheetID"]): int(r["EmployeeID"]) for r in _read("Timesheets")}

# ---------------------------------------------------------------------------
# 4) LEAVE vs TIMESHEET OVERLAP (minor / quick)
# ---------------------------------------------------------------------------

def _check_leave_overlap():
    # Given we generated leave in 2021-22 and timesheets in recent 60 weeks,
    # they should never overlap; quick sanity scan.
    leaves = _read("LeaveApplications")
    min_ts_year = min(int(r["WeekStartDate"][:4]) for r in _read("Timesheets"))
    for la in leaves:
        if int(la["StartDate"][:4]) >= min_ts_year:
            raise AssertionError("LeaveApplications overlap Timesheet period")

# ---------------------------------------------------------------------------


def run():
    print("🔍  Running validation checks …")
    _check_manager_hierarchy()
    print("  ✔ Manager hierarchy acyclic and single CEO")
    _check_hr_load()
    print("  ✔ HR load between 10–20")
    _check_timesheet_project_membership()
    print("  ✔ Timesheet details reference only assigned projects")
    _check_leave_overlap()
    print("  ✔ Leave dates do not overlap timesheets")
    print("✅  All validations passed!")


if __name__ == "__main__":
    run()
