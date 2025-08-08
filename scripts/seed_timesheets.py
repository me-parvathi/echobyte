#!/usr/bin/env python3
"""
seed_timesheets.py
──────────────────
Generates two CSVs
    • Timesheets.csv         (explicit TimesheetID)
    • TimesheetDetails.csv   (explicit DetailID)

Rules recap
• 60 ISO weeks ending the last Friday before today.
• Every active employee receives a sheet for each of those weeks.
• Timesheet.Status mix: Submitted 10 %, Approved 88 %, Rejected 2 %.
• Approved sheets set ApprovedByID to the employee's ManagerID.
• For each weekday create a detail row (Mon–Fri) with 6-9 h. >8 h → IsOvertime = 1.
• ProjectID on each detail must belong to one of the employee's project assignments.
  If employee has no assignment yet (rare) use blank ProjectID.
"""
from __future__ import annotations

import csv
import json
import random
import datetime as dt
from pathlib import Path
from typing import List, Dict, Tuple

from scripts.csv_utils import write_csv

random.seed(42)

_STATUS_MIX = [
    ("Submitted", 0.10),
    ("Approved", 0.88),
    ("Rejected", 0.02),
]

START_WEEKS_AGO = 59  # 0-based → 60 weeks total

# ---------------------------------------------------------------------------
# LOADERS
# ---------------------------------------------------------------------------

def _load_csv(path: Path) -> List[Dict]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _load_org():
    return json.loads(Path("csv_out/org_ids.json").read_text())

# ---------------------------------------------------------------------------


def _weighted_status() -> str:
    r = random.random()
    cum = 0.0
    for name, w in _STATUS_MIX:
        cum += w
        if r <= cum:
            return name
    return _STATUS_MIX[-1][0]


def _last_friday(ref: dt.date) -> dt.date:
    offset = (ref.weekday() - 4) % 7
    return ref - dt.timedelta(days=offset)


# ---------------------------------------------------------------------------
# GENERATORS
# ---------------------------------------------------------------------------

def generate_timesheets(emp_rows: List[Dict], assignments: Dict[int, List[int]]) -> Tuple[List[Dict], List[Dict]]:
    today = dt.date.today()
    week_end = _last_friday(today)
    week_starts = [week_end - dt.timedelta(days=7 * i + 6) for i in range(START_WEEKS_AGO, -1, -1)]

    ts_rows: List[Dict] = []
    detail_rows: List[Dict] = []
    ts_id = 1
    det_id = 1

    for emp in emp_rows:
        emp_id = int(emp["EmployeeID"])
        mgr_id = emp["ManagerID"] or ""
        projects = assignments.get(emp_id, [])

        for ws in week_starts:
            we = ws + dt.timedelta(days=4)
            status = _weighted_status()
            sheet = {
                "TimesheetID": ts_id,
                "EmployeeID": emp_id,
                "WeekStartDate": ws.isoformat(),
                "WeekEndDate": we.isoformat(),
                "TotalHours": 0,  # filled later
                "StatusCode": status,
                "SubmittedAt": "",
                "ApprovedByID": mgr_id if status == "Approved" else "",
                "ApprovedAt": "",
                "CreatedAt": dt.datetime.utcnow().isoformat(),
                "UpdatedAt": dt.datetime.utcnow().isoformat(),
            }
            total_h = 0.0
            for d in range(5):  # Mon-Fri
                work_date = ws + dt.timedelta(days=d)
                hrs = random.randint(6, 9)
                is_ot = 1 if hrs > 8 else 0
                proj_id = random.choice(projects) if projects else None
                detail_rows.append({
                    "DetailID": det_id,
                    "TimesheetID": ts_id,
                    "WorkDate": work_date.isoformat(),
                    "TaskDescription": "Work on project tasks",
                    "HoursWorked": hrs,
                    "IsOvertime": is_ot,
                    "ProjectID": proj_id or "",
                    "CreatedAt": dt.datetime.utcnow().isoformat(),
                })
                det_id += 1
                total_h += hrs
            sheet["TotalHours"] = round(total_h, 2)
            ts_rows.append(sheet)
            ts_id += 1
    return ts_rows, detail_rows

# ---------------------------------------------------------------------------
# DRIVER
# ---------------------------------------------------------------------------

def run():
    employees = _load_csv(Path("csv_out/Employees.csv"))
    # Build assignment index employee_id -> list[ProjectID]
    assignments = {}
    for row in _load_csv(Path("csv_out/ProjectAssignments.csv")):
        eid = int(row["EmployeeID"])
        assignments.setdefault(eid, []).append(int(row["ProjectID"]))

    ts, details = generate_timesheets(employees, assignments)
    write_csv("Timesheets", ts)
    write_csv("TimesheetDetails", details)
    print("🎉  Timesheets and Details generated")


if __name__ == "__main__":
    run()
