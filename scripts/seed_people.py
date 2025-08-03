#!/usr/bin/env python3
"""
seed_people.py
──────────────
Creates the core HR-centric CSVs:
    • Employees.csv
    • EmployeeRoles.csv
    • EmergencyContacts.csv

Assumptions
• Users.csv already exists with 870 rows and unique UserID column.
• Organisation IDs (LocationID, DepartmentID, TeamID) are stored in
  csv_out/org_ids.json (written by seed_org_structure.py).
• RoleID mapping is fixed based on insertion order in ddl.sql:
        1 Employee  2 Manager  3 HR  4 IT Support  5 Admin  6 CEO
• We generate explicit EmployeeID values (1..870) so downstream tables can
  reference them directly.  These IDs must be loaded with
    SET IDENTITY_INSERT dbo.Employees ON;  <bulk insert>  OFF;
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import List, Dict, Tuple
import datetime as dt
import hashlib

from faker import Faker

from scripts.data_utils import rand_past_datetime, ensure_created_before_updated
from scripts.csv_utils import write_csv

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------
TOTAL_EMPLOYEES = 870
CEO_COUNT = 1
SR_MANAGER_COUNT = 10
MANAGER_COUNT = 79  # includes HR+IT managers
HR_MANAGER_COUNT = 4
IT_MANAGER_COUNT = 6
HR_NONMANAGER_COUNT = 48  # 52 total HR minus 4 managers
IT_NONMANAGER_COUNT = 39  # 45 total IT minus 6 managers
# remaining are general employees

ROLE_EMPLOYEE = 1
ROLE_MANAGER = 2
ROLE_HR = 3
ROLE_IT = 4
ROLE_ADMIN = 5
ROLE_CEO = 6

DESIGNATIONS = {
    "CEO": ["Principal Engineer", "Product Manager"],
    "SR_MANAGER": ["Principal Engineer", "Product Manager"],
    "MANAGER": [
        "Senior Software Engineer",
        "Senior QA Engineer",
        "DevOps Engineer",
        "Product Manager",
    ],
    "HR_MANAGER": ["Senior HR Executive"],
    "HR": ["HR Executive"],
    "IT_MANAGER": ["Senior IT Support Specialist"],
    "IT": ["IT Support Specialist", "IT Systems Administrator"],
    "EMPLOYEE": [
        "Software Engineer I",
        "Software Engineer II",
        "QA Engineer",
        "UX Designer",
        "Product Manager",
    ],
}

# Map designation display names -> ID values as inserted in ddl.sql
DESIGNATION_ID_MAP = {
    "Software Engineer I": 1,
    "Software Engineer II": 2,
    "Senior Software Engineer": 3,
    "Staff Engineer": 4,
    "Principal Engineer": 5,
    "QA Engineer": 6,
    "Senior QA Engineer": 7,
    "DevOps Engineer": 8,
    "UX Designer": 9,
    "Product Manager": 10,
    "CEO": 11,
    "Senior HR Executive": 12,
    "HR Executive": 13,
    "IT Support Specialist": 14,
    "Senior IT Support Specialist": 15,
    "IT Systems Administrator": 16,
}

fake = Faker()
random.seed(42)
Faker.seed(42)

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _load_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_users_csv(path: Path) -> List[Dict]:
    import csv
    with path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def _choose(seq):
    return random.choice(seq)


def _random_date_between(start_year: int = 2015, end_year: int = 2023) -> dt.date:
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # safe day
    return dt.date(year, month, day)

# ---------------------------------------------------------------------------
# MAIN GENERATORS
# ---------------------------------------------------------------------------

def generate_employees(users: List[Dict], org_ids: Dict) -> Tuple[List[Dict], Dict[int, Dict]]:
    """Return (employees_rows, meta_by_emp_id). meta contains keys we need later."""
    assert len(users) >= TOTAL_EMPLOYEES, "Need at least 870 users"

    employees: List[Dict] = []
    meta: Dict[int, Dict] = {}

    # helpers
    all_team_ids = list(org_ids["teams"].values())
    all_location_ids = list(org_ids["locations"].values())

    next_emp_id = 1

    def _mk_row(user_row: Dict, designation: str, manager_id: int | None,
                 hr_rep_id: int | None, is_active: int = 1) -> Dict:
        nonlocal next_emp_id
        emp_id = next_emp_id
        next_emp_id += 1

        team_id = _choose(all_team_ids)
        location_id = _choose(all_location_ids)

        hire_date = _random_date_between()
        created_at = rand_past_datetime()
        created_at, updated_at = ensure_created_before_updated(created_at)

        row = {
            "EmployeeID": emp_id,
            "EmployeeCode": f"EMP-{emp_id:04d}",
            "UserID": user_row["UserID"],
            "CompanyEmail": user_row["Email"],
            "FirstName": fake.first_name(),
            "MiddleName": "",
            "LastName": fake.last_name(),
            "DateOfBirth": _random_date_between(1970, 2002).isoformat(),
            "GenderCode": random.choice(["M", "F", "NB", "O"]),
            "PersonalEmail": fake.free_email(),
            "PersonalPhone": fake.phone_number(),
            "TeamID": team_id,
            "LocationID": location_id,
            "ManagerID": manager_id or "",
            "HREmployeeID": hr_rep_id or "",
            "DesignationID": DESIGNATION_ID_MAP[designation.strip()],
            "EmploymentTypeCode": random.choices(
                ["Full-Time", "Part-Time", "Contract", "Intern"], weights=[0.75, 0.1, 0.1, 0.05]
            )[0],
            "WorkModeCode": random.choices(
                ["Remote", "Hybrid", "In-Person"], weights=[0.35, 0.5, 0.15]
            )[0],
            "HireDate": hire_date.isoformat(),
            "TerminationDate": "",  # most still employed
            "IsActive": is_active,
            "CreatedAt": created_at.isoformat(),
            "UpdatedAt": updated_at.isoformat(),
        }
        employees.append(row)
        meta[emp_id] = {
            "designation": designation,
            "manager_id": manager_id,
        }
        return row

    # --- 1) CEO ---
    ceo_user = users.pop(0)
    _mk_row(ceo_user, _choose(DESIGNATIONS["CEO"]), manager_id=None, hr_rep_id=None)
    ceo_id = 1

    # --- 2) Senior Managers ---
    sr_mgr_ids = []
    for _ in range(SR_MANAGER_COUNT):
        user = users.pop(0)
        row = _mk_row(user, _choose(DESIGNATIONS["SR_MANAGER"]), manager_id=ceo_id, hr_rep_id=None)
        sr_mgr_ids.append(row["EmployeeID"])

    # --- 3) Managers (79) ---
    mgr_ids: List[int] = []
    # HR managers
    for _ in range(HR_MANAGER_COUNT):
        user = users.pop(0)
        mgr_id = _mk_row(user, _choose(DESIGNATIONS["HR_MANAGER"]), manager_id=_choose(sr_mgr_ids), hr_rep_id=None)[
            "EmployeeID"
        ]
        mgr_ids.append(mgr_id)
    # IT managers
    for _ in range(IT_MANAGER_COUNT):
        user = users.pop(0)
        mgr_id = _mk_row(user, _choose(DESIGNATIONS["IT_MANAGER"]), manager_id=_choose(sr_mgr_ids), hr_rep_id=None)[
            "EmployeeID"
        ]
        mgr_ids.append(mgr_id)
    # Other managers
    remaining_mgrs = MANAGER_COUNT - HR_MANAGER_COUNT - IT_MANAGER_COUNT
    for _ in range(remaining_mgrs):
        user = users.pop(0)
        mgr_id = _mk_row(user, _choose(DESIGNATIONS["MANAGER"]), manager_id=_choose(sr_mgr_ids), hr_rep_id=None)[
            "EmployeeID"
        ]
        mgr_ids.append(mgr_id)

    # --- 4) HR non-managers ---
    hr_rep_ids: List[int] = []
    for _ in range(HR_NONMANAGER_COUNT):
        user = users.pop(0)
        emp_id = _mk_row(user, _choose(DESIGNATIONS["HR"]), manager_id=_choose(mgr_ids), hr_rep_id=None)["EmployeeID"]
        hr_rep_ids.append(emp_id)

    # include HR managers too as representatives
    hr_rep_ids.extend(mgr_ids[:HR_MANAGER_COUNT])

    # --- 5) IT non-managers ---
    for _ in range(IT_NONMANAGER_COUNT):
        user = users.pop(0)
        _mk_row(user, _choose(DESIGNATIONS["IT"]), manager_id=_choose(mgr_ids), hr_rep_id=None)

    # --- 6) Remaining general employees ---
    remaining = TOTAL_EMPLOYEES - len(employees)
    for _ in range(remaining):
        user = users.pop(0)
        _mk_row(user, _choose(DESIGNATIONS["EMPLOYEE"]), manager_id=_choose(mgr_ids), hr_rep_id=None)

    # --- Assign HR representatives (balanced 10–20 each) ---
    non_hr_emp_ids = [eid for eid in meta if eid not in hr_rep_ids]
    random.shuffle(non_hr_emp_ids)

    # initialize counts with zero
    hr_load: Dict[int, int] = {hid: 1 for hid in hr_rep_ids}  # count self

    # First give each HR rep 10 employees to guarantee minimum load
    idx = 0
    for hid in hr_rep_ids:
        for _ in range(10):
            if idx >= len(non_hr_emp_ids):
                break
            emp_id = non_hr_emp_ids[idx]; idx += 1
            hr_load[hid] += 1
            for row in employees:
                if row["EmployeeID"] == emp_id:
                    row["HREmployeeID"] = hid
                    break

    # Distribute remaining employees ensuring no HR exceeds 20
    remaining = non_hr_emp_ids[idx:]
    # ensure cap remains 20
    for emp_id in remaining:
        # pick HR with current minimum load (<20)
        eligible = [hid for hid, cnt in hr_load.items() if cnt < 20]
        if not eligible:
            eligible = list(hr_rep_ids)  # fallback; shouldn't happen
        hid = random.choice(eligible)
        hr_load[hid] += 1
        for row in employees:
            if row["EmployeeID"] == emp_id:
                row["HREmployeeID"] = hid
                break

    # Final sweep: any employee still blank gets an HR rep (HR reps point to self)
    for row in employees:
        if not row["HREmployeeID"]:
            if row["EmployeeID"] in hr_rep_ids:
                row["HREmployeeID"] = row["EmployeeID"]
            else:
                row["HREmployeeID"] = random.choice(hr_rep_ids)

    return employees, meta


def generate_employee_roles(meta: Dict[int, Dict]) -> List[Dict]:
    rows: List[Dict] = []
    next_id = 1
    for emp_id, m in meta.items():
        roles: List[int] = []
        designation = m["designation"]
        if emp_id == 1:
            roles = [ROLE_CEO, ROLE_ADMIN]
        elif designation in DESIGNATIONS["SR_MANAGER"] or designation in DESIGNATIONS["MANAGER"] or designation in DESIGNATIONS["HR_MANAGER"] or designation in DESIGNATIONS["IT_MANAGER"]:
            roles.append(ROLE_MANAGER)
        if designation in DESIGNATIONS["HR"] or designation in DESIGNATIONS["HR_MANAGER"]:
            roles.append(ROLE_HR)
        if designation in DESIGNATIONS["IT"] or designation in DESIGNATIONS["IT_MANAGER"]:
            roles.append(ROLE_IT)
        if not roles:
            roles.append(ROLE_EMPLOYEE)

        for rid in roles:
            rows.append({
                "EmployeeRoleID": next_id,
                "EmployeeID": emp_id,
                "RoleID": rid,
                "AssignedAt": dt.datetime.utcnow().isoformat(),
                "AssignedByID": 1,
                "IsActive": 1,
            })
            next_id += 1
    return rows


def generate_emergency_contacts(employees: List[Dict]) -> List[Dict]:
    rows: List[Dict] = []
    next_id = 1
    for emp in employees:
        n_contacts = random.randint(1, 2)
        for i in range(n_contacts):
            created = rand_past_datetime()
            created, updated = ensure_created_before_updated(created)
            rows.append({
                "ContactID": next_id,
                "EmployeeID": emp["EmployeeID"],
                "ContactName": fake.name(),
                "Relationship": random.choice(["Spouse", "Parent", "Sibling", "Friend"]),
                "Phone1": fake.phone_number(),
                "Phone2": fake.phone_number() if random.random() < 0.3 else "",
                "Email": fake.free_email(),
                "Address": fake.address().replace("\n", ", "),
                "IsPrimary": 1 if i == 0 else 0,
                "IsActive": 1,
                "CreatedAt": created.isoformat(),
                "UpdatedAt": updated.isoformat(),
            })
            next_id += 1
    return rows


# ---------------------------------------------------------------------------
# DRIVER
# ---------------------------------------------------------------------------

def run():
    org_ids = _load_json(Path("csv_out/org_ids.json"))
    users = _load_users_csv(Path("csv_out/Users.csv"))

    employees, meta = generate_employees(users, org_ids)
    emp_roles = generate_employee_roles(meta)
    emergency = generate_emergency_contacts(employees)

    write_csv("Employees", employees)
    write_csv("EmployeeRoles", emp_roles)
    write_csv("EmergencyContacts", emergency)

    print("🎉  Employees / Roles / EmergencyContacts generated")


if __name__ == "__main__":
    run()
