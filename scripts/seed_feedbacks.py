#!/usr/bin/env python3
"""
seed_feedbacks.py
─────────────────
Port of the legacy `gen_feedbacks` – creates EmployeeFeedbacks.csv with fake
feedback entries (manager praise, department suggestions, etc.).
"""
from __future__ import annotations

import csv
import random
import datetime as dt
from pathlib import Path
from typing import List, Dict

from faker import Faker

from scripts.csv_utils import write_csv

fake = Faker()
random.seed(42)
Faker.seed(42)

import csv

TOTAL_FEEDBACKS = 200
TYPE_CODES = [
    "General",
    "Manager",
    "Department",
    "Company",
    "Other",
]

CATEGORIES = [
    "Work Environment",
    "Compensation",
    "Processes",
    "Technology",
    "Career Growth",
]

# ---------------------------------------------------------------------------


def _load_employees() -> List[Dict]:
    with Path("csv_out/Employees.csv").open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

# ---------------------------------------------------------------------------


def _load_csv(name: str) -> List[Dict]:
    with Path(f"csv_out/{name}.csv").open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def run():
    employees = _load_employees()
    emp_ids = [int(r["EmployeeID"]) for r in employees]

    # Build manager list from EmployeeRoles: RoleID 2 (Manager) or 6 (CEO)
    role_rows = _load_csv("EmployeeRoles")
    managers = [int(r["EmployeeID"]) for r in role_rows if r["RoleID"] in {"2", "6"}]

    rows: List[Dict] = []
    fid = 1
    for _ in range(TOTAL_FEEDBACKS):
        ftype = random.choice(TYPE_CODES)
        row = {
            "FeedbackID": fid,
            "FeedbackAt": dt.datetime.utcnow().isoformat(),
            "FeedbackTypeCode": ftype,
            "Category": random.choice(CATEGORIES),
            "Subject": fake.sentence(nb_words=6),
            "FeedbackText": fake.paragraph(nb_sentences=3),
            "TargetManagerID": random.choice(managers) if (ftype == "Manager" and managers) else "",
            "TargetDepartmentID": "",  # simplification
            "FeedbackHash": "",
            "IsRead": 0,
            "ReadByID": "",
            "ReadAt": "",
        }
        rows.append(row)
        fid += 1

    write_csv("EmployeeFeedbacks", rows)
    print("🎉  EmployeeFeedbacks generated")


if __name__ == "__main__":
    run()
