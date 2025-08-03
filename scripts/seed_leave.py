#!/usr/bin/env python3
"""
seed_leave.py
─────────────
Generates
    • LeaveBalances.csv
    • LeaveApplications.csv

Guaranteed no overlap with the weeks used in Timesheets:
    Timesheets cover the most recent 60 ISO weeks; all leave applications are
    placed **two years earlier** (2021–2022), so backend validation sees no
    conflict.
"""
from __future__ import annotations

import csv
import random
import json
from pathlib import Path
from typing import List, Dict, Tuple
import datetime as dt

from scripts.csv_utils import write_csv

random.seed(42)

LEAVE_TYPES = {
    1: ("PTO", 15.0),
    2: ("SICK", 10.0),
    3: ("MAT", 90.0),
    4: ("PAT", 10.0),
    5: ("BRV", 5.0),
    6: ("UNPD", 0.0),
}

_STATUS_MIX = [
    ("Submitted", 0.15),
    ("Manager-Approved", 0.70),
    ("HR-Approved", 0.05),
    ("Rejected", 0.10),
]

# ---------------------------------------------------------------------------
# LOADERS
# ---------------------------------------------------------------------------

def _load_csv(path: Path) -> List[Dict]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

# ---------------------------------------------------------------------------


def _weighted_status():
    r = random.random()
    cum = 0.0
    for s, w in _STATUS_MIX:
        cum += w
        if r <= cum:
            return s
    return _STATUS_MIX[-1][0]


# ---------------------------------------------------------------------------
# GENERATORS
# ---------------------------------------------------------------------------

def generate_balances(emp_rows: List[Dict]) -> List[Dict]:
    rows: List[Dict] = []
    year = 2024  # current year baseline
    bal_id = 1
    for emp in emp_rows:
        eid = emp["EmployeeID"]
        for lt_id, (_, default_days) in LEAVE_TYPES.items():
            rows.append({
                "BalanceID": bal_id,
                "EmployeeID": eid,
                "LeaveTypeID": lt_id,
                "Year": year,
                "EntitledDays": default_days or 0,
                "UsedDays": 0,
                "CreatedAt": dt.datetime.utcnow().isoformat(),
                "UpdatedAt": dt.datetime.utcnow().isoformat(),
            })
            bal_id += 1
    return rows


def generate_leave_applications(emp_rows: List[Dict]) -> List[Dict]:
    rows: List[Dict] = []
    app_id = 1
    for emp in emp_rows:
        eid = int(emp["EmployeeID"])
        mgr = emp["ManagerID"] or ""
        # approx 25 % of employees will have leave requests
        if random.random() > 0.25:
            continue
        n_apps = random.randint(1, 4)
        for _ in range(n_apps):
            lt_id, (code, _) = random.choice(list(LEAVE_TYPES.items()))
            year = random.choice([2021, 2022])
            start = dt.date(year, random.randint(1, 12), random.randint(1, 25))
            length = random.randint(1, 5)
            end = start + dt.timedelta(days=length - 1)
            status = _weighted_status()
            rows.append({
                "LeaveApplicationID": app_id,
                "EmployeeID": eid,
                "LeaveTypeID": lt_id,
                "StartDate": start.isoformat(),
                "EndDate": end.isoformat(),
                "NumberOfDays": float(length),
                "Reason": "Personal leave",
                "StatusCode": status,
                "SubmittedAt": dt.datetime.utcnow().isoformat(),
                "ManagerID": mgr,
                "ManagerApprovalStatus": "Approved" if status.startswith("Manager") or status.startswith("HR") else "",
                "HRApproverID": "",
                "HRApprovalStatus": "Approved" if status == "HR-Approved" else "",
                "CreatedAt": dt.datetime.utcnow().isoformat(),
                "UpdatedAt": dt.datetime.utcnow().isoformat(),
            })
            app_id += 1
    return rows


# ---------------------------------------------------------------------------
# DRIVER
# ---------------------------------------------------------------------------

def run():
    employees = _load_csv(Path("csv_out/Employees.csv"))
    balances = generate_balances(employees)
    applications = generate_leave_applications(employees)

    write_csv("LeaveBalances", balances)
    write_csv("LeaveApplications", applications)
    print("🎉  LeaveBalances and LeaveApplications generated")


if __name__ == "__main__":
    run()
