#!/usr/bin/env python3
"""
generate_fake_echobyte_data.py
────────────────────────────────────────────────────────────────────────────
Creates realistic, referential-integrity-safe CSVs for the July-2025
*echobyte* schema (see ddl.sql) and drops them in ./csv_out/.

Volumetrics (CFG defaults)
•  4  locations     •  ~14 departments (2-tier)   •  25-40 teams
•  800 employees    •  5 % terminated / 3 % inactive
•  8 years of leave balances (1 row / emp / type / year)
•  1 year weekly timesheets with daily details for all active staff
•  8 000 IT assets with realistic status / contracts / assignments
All numbers are tweakable via CFG.

Faker seed = 42 → deterministic output.
────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
import csv, os, random, datetime as dt
from collections import defaultdict
from pathlib import Path

import pandas as pd
from faker import Faker
from dateutil.relativedelta import relativedelta

# ────────────────────────────────
# CONFIGURATION
# ────────────────────────────────
CFG = {
    # housekeeping
    "seed":          42,
    "csv_out":       Path("csv_out"),

    # organisation shape
    "n_locations":   4,
    "dept_structure": [                # root → children
        ("Corporate", ["HR", "IT", "Finance", "Operations"]),
        ("Engineering", ["Platform", "Data", "QA"]),
        ("Product",    ["Design", "PM", "Research"]),
    ],
    "teams_per_dept": (1, 3),
    "n_employees":   800,

    # status mixes (lookup PK → probability)
    "emp_type_mix": {                  # EmploymentTypes
        "Full-Time":  0.86,
        "Part-Time":  0.06,
        "Contract":   0.06,
        "Intern":     0.02,
    },
    "employment_active_pct": 0.92,     # others marked inactive
    "work_mode_mix": {
        "Remote":     0.55,
        "Hybrid":     0.30,
        "In-Person":  0.15,
    },
    "leave_type_years_back": 8,        # LeaveBalances horizon
    "leave_type_defaults": {           # LeaveTypes.LeaveCode → days/yr
        "VAC": 20, "SICK": 10, "PARENT": 90,
        "BEREAVE": 5, "UNPAID": 0,
    },
    # leave application status mix (LeaveApplicationStatuses)
    "leave_app_status_mix": {
        "Submitted":         0.15,
        "Manager-Approved":  0.70,
        "HR-Approved":       0.05,
        "Rejected":          0.10,
    },
    # timesheet status mix (TimesheetStatuses)
    "timesheet_status_mix": {
        "Submitted": 0.10,
        "Approved":  0.88,
        "Rejected":  0.02,
    },

    # IT assets
    "n_assets":        8000,
    "asset_status_mix": {
        "In-Stock":        0.25,
        "Available":       0.25,
        "Assigned":        0.35,
        "Maintenance":     0.10,
        "Decommissioning": 0.03,
        "Retired":         0.02,
    },
    "assignable_codes": {"In-Stock", "Available", "Assigned"},

    # timesheet realism
    "weeks_of_timesheets": 52,
    "daily_hours_range": (7, 9),        # before break
    "break_range_min": 30,              # minutes
    "break_range_max": 75,
}

# ─── Faker init ─────────────────────────────────────────────
random.seed(CFG["seed"])
fake = Faker("en_US")
Faker.seed(CFG["seed"])

# ─── Output dir ────────────────────────────────────────────
CFG["csv_out"].mkdir(exist_ok=True)

# ────────────────────────────────
# Helpers
# ────────────────────────────────
def weighted_choice(weight_map: dict[str, float]) -> str:
    r, acc = random.random(), 0.0
    for key, w in weight_map.items():
        acc += w
        if r < acc:
            return key
    return next(reversed(weight_map))

def wr(csv_name: str, rows: list[dict]) -> None:
    if not rows:
        return
    pd.DataFrame(rows).to_csv(
        CFG["csv_out"] / f"{csv_name}.csv",
        index=False,
        quoting=csv.QUOTE_MINIMAL,
    )
    print(f"  · {csv_name}.csv  ({len(rows):,} rows)")

def today() -> dt.date:            # convenience
    return dt.date.today()

NOW_ISO = dt.datetime.now().isoformat(sep=" ")

# ────────────────────────────────
# 1. Lookup helpers (IDs fixed by DDL seeds)
# ────────────────────────────────
GENDER_CODES  = ["M", "F", "O", "NB"]
EMP_TYPES     = ["Full-Time", "Part-Time", "Contract", "Intern"]
WORK_MODES    = ["Remote", "Hybrid", "In-Person"]

APPROVAL_STAT = ["Pending", "Approved", "Rejected"]
LA_STATUSES   = ["Draft", "Submitted", "Manager-Approved",
                 "HR-Approved", "Rejected", "Cancelled"]
TS_STATUSES   = ["Draft", "Submitted", "Approved", "Rejected"]

ASSET_STATUS_CODES = [
    "In-Stock", "Available", "Assigned",
    "Maintenance", "Decommissioning", "Retired",
]

# quick sanity to catch future DDL changes
assert set(CFG["emp_type_mix"]) == set(EMP_TYPES)
assert set(CFG["work_mode_mix"]) == set(WORK_MODES)
assert set(CFG["asset_status_mix"]) == set(ASSET_STATUS_CODES)

# ────────────────────────────────
# 2. Core structure
# ────────────────────────────────
def gen_locations(n: int):
    rows = []
    for lid in range(1, n + 1):
        city = fake.city()
        rows.append({
            "LocationID":   lid,
            "LocationName": f"Office – {city}",
            "Address1":     fake.street_address(),
            "Address2":     "",
            "City":         city,
            "State":        fake.state(),
            "Country":      "USA",
            "PostalCode":   fake.postcode(),
            "Phone":        fake.phone_number(),
            "TimeZone":     "America/Los_Angeles",
            "IsActive":     1,
            "CreatedAt":    NOW_ISO,
            "UpdatedAt":    NOW_ISO,
        })
    return rows

def gen_departments(structure, locations):
    rows, did = [], 1
    for root, children in structure:
        parent_id = did
        rows.append({
            "DepartmentID":       parent_id,
            "DepartmentName":     root,
            "DepartmentCode":     f"{root[:3].upper()}{parent_id:02d}",
            "ParentDepartmentID": None,
            "LocationID":         random.choice(locations)["LocationID"],
            "IsActive":           1,
            "CreatedAt":          NOW_ISO,
            "UpdatedAt":          NOW_ISO,
        })
        did += 1
        for ch in children:
            rows.append({
                "DepartmentID":   did,
                "DepartmentName": ch,
                "DepartmentCode": f"{ch[:3].upper()}{did:02d}",
                "ParentDepartmentID": parent_id,
                "LocationID":     random.choice(locations)["LocationID"],
                "IsActive":       1,
                "CreatedAt":      NOW_ISO,
                "UpdatedAt":      NOW_ISO,
            })
            did += 1
    return rows

def gen_teams(departments, rng):
    rows, tid = [], 1
    for d in departments:
        for _ in range(random.randint(*rng)):
            code = f"T{tid:04d}"
            rows.append({
                "TeamID":             tid,
                "TeamName":           f"{d['DepartmentName']} Team {fake.bothify('??').upper()}",
                "TeamCode":           code,
                "DepartmentID":       d["DepartmentID"],
                "TeamLeadEmployeeID": None,   # filled later
                "IsActive":           1,
                "CreatedAt":          NOW_ISO,
                "UpdatedAt":          NOW_ISO,
            })
            tid += 1
    return rows

# ────────────────────────────────
# 3. Employees & security
# ────────────────────────────────
def gen_designations():
    # designation rows already seeded in DDL; grab their IDs dynamically 1..10
    return list(range(1, 11))

def gen_employees(teams, locations, n):
    rows, eid = [], 1
    managers = {}
    active_pct = CFG["employment_active_pct"]

    # always one active manager per team
    for tm in teams:
        first, last = fake.first_name(), fake.last_name()
        etype  = weighted_choice(CFG["emp_type_mix"])
        wmode  = weighted_choice(CFG["work_mode_mix"])

        rows.append({
            "EmployeeID":         eid,
            "EmployeeCode":       f"EMP{eid:05d}",
            "UserID":             f"{first.lower()}.{last.lower()}",
            "CompanyEmail":       f"{first.lower()}.{last.lower()}@echobyte.com",
            "FirstName":          first,
            "MiddleName":         "",
            "LastName":           last,
            "DateOfBirth":        (today() - relativedelta(years=random.randint(28, 58))).isoformat(),
            "GenderCode":         random.choice(GENDER_CODES),
            "MaritalStatus":      random.choice(["Single", "Married", ""]),
            "PersonalEmail":      fake.email(),
            "PersonalPhone":      fake.phone_number(),
            "WorkPhone":          fake.phone_number(),
            # inline address
            "Address1":           fake.street_address(),
            "Address2":           "",
            "City":               fake.city(),
            "State":              fake.state(),
            "Country":            "USA",
            "PostalCode":         fake.postcode(),

            "TeamID":             tm["TeamID"],
            "LocationID":         random.choice(locations)["LocationID"],
            "ManagerID":          None,
            "DesignationID":      random.choice(gen_designations()),
            "EmploymentTypeCode": etype,
            "WorkModeCode":       wmode,
            "HireDate":           (today() - relativedelta(years=random.randint(3, 10))).isoformat(),
            "TerminationDate":    None,
            "IsActive":           1,
            "CreatedAt":          NOW_ISO,
            "UpdatedAt":          NOW_ISO,
        })
        managers[tm["TeamID"]] = eid
        tm["TeamLeadEmployeeID"] = eid
        eid += 1

    remaining = n - len(rows)
    while remaining > 0:
        tm        = random.choice(teams)
        first, last = fake.first_name(), fake.last_name()
        active    = random.random() < active_pct
        etype     = weighted_choice(CFG["emp_type_mix"])
        wmode     = weighted_choice(CFG["work_mode_mix"])
        rows.append({
            "EmployeeID":         eid,
            "EmployeeCode":       f"EMP{eid:05d}",
            "UserID":             f"{first.lower()}.{last.lower()}{random.randint(1, 9999)}",
            "CompanyEmail":       f"{first.lower()}.{last.lower()}{random.randint(1,9999)}@echobyte.com",
            "FirstName":          first,
            "MiddleName":         "",
            "LastName":           last,
            "DateOfBirth":        (today() - relativedelta(years=random.randint(21, 58))).isoformat(),
            "GenderCode":         random.choice(GENDER_CODES),
            "MaritalStatus":      random.choice(["Single", "Married", ""]),
            "PersonalEmail":      fake.email(),
            "PersonalPhone":      fake.phone_number() if random.random() < 0.9 else None,
            "WorkPhone":          fake.phone_number() if active else None,

            "Address1":           fake.street_address(),
            "Address2":           "" if random.random() < 0.8 else fake.secondary_address(),
            "City":               fake.city(),
            "State":              fake.state(),
            "Country":            "USA",
            "PostalCode":         fake.postcode(),

            "TeamID":             tm["TeamID"],
            "LocationID":         random.choice(locations)["LocationID"],
            "ManagerID":          managers[tm["TeamID"]],
            "DesignationID":      random.choice(gen_designations()),
            "EmploymentTypeCode": etype,
            "WorkModeCode":       wmode,
            "HireDate":           (today() - relativedelta(years=random.randint(0, 7))).isoformat(),
            "TerminationDate":    (today() - relativedelta(days=random.randint(30, 900))).isoformat()
                                  if not active else None,
            "IsActive":           1 if active else 0,
            "CreatedAt":          NOW_ISO,
            "UpdatedAt":          NOW_ISO,
        })
        eid += 1
        remaining -= 1
    return rows, managers

def gen_emergency_contacts(employees):
    rows, cid = [], 1
    for emp in employees:
        if random.random() < 0.9:
            rows.append({
                "ContactID":    cid,
                "EmployeeID":   emp["EmployeeID"],
                "ContactName":  fake.name(),
                "Relationship": random.choice(["Spouse", "Parent", "Sibling", "Friend"]),
                "Phone1":       fake.phone_number(),
                "Phone2":       fake.phone_number() if random.random() < 0.3 else None,
                "Email":        fake.email(),
                "Address":      fake.address().replace("\n", ", "),
                "IsPrimary":    1,
                "IsActive":     1,
                "CreatedAt":    NOW_ISO,
                "UpdatedAt":    NOW_ISO,
            })
            cid += 1
    return rows

def gen_roles_and_emp_roles(employees, managers):
    # Role IDs seeded in DDL: 1..11   (Employee, Manager, HR, Admin, CEO, ...)
    rows_roles = []        # not needed – already seeded
    rows_emp_roles, erid = [], 1
    for emp in employees:
        base_role = 2 if emp["EmployeeID"] in managers.values() else 1  # Manager vs Employee
        rows_emp_roles.append({
            "EmployeeRoleID": erid,
            "EmployeeID":     emp["EmployeeID"],
            "RoleID":         base_role,
            "AssignedAt":     NOW_ISO,
            "AssignedByID":   emp["ManagerID"] or emp["EmployeeID"],
            "IsActive":       1,
        })
        erid += 1
    return rows_roles, rows_emp_roles

# ────────────────────────────────
# 4. Leave management
# ────────────────────────────────
def gen_leave_types():
    # Use those seeded, but map code → ID (Identity starts at 1)
    return [
        (1, "VAC", 20),
        (2, "SICK", 10),
        (3, "PARENT", 90),
        (4, "BEREAVE", 5),
        (5, "UNPAID", 0),
    ]

def gen_leave_balances(employees):
    rows, bid = [], 1
    types = gen_leave_types()
    years_back = CFG["leave_type_years_back"]
    current_year = today().year
    for emp in employees:
        for leave_id, code, days in types:
            for y in range(current_year - years_back + 1, current_year + 1):
                used = round(random.uniform(0, min(days, days*0.6)), 1) if days else 0
                rows.append({
                    "BalanceID":     bid,
                    "EmployeeID":    emp["EmployeeID"],
                    "LeaveTypeID":   leave_id,
                    "Year":          y,
                    "EntitledDays":  days,
                    "UsedDays":      used,
                    "CreatedAt":     NOW_ISO,
                    "UpdatedAt":     NOW_ISO,
                })
                bid += 1
    return rows

def gen_leave_applications(employees, managers):
    rows, lid = [], 1
    status_mix = CFG["leave_app_status_mix"]
    leave_types = gen_leave_types()
    for emp in employees:
        if not emp["IsActive"] or random.random() > 0.3:
            continue
        for _ in range(random.randint(0, 3)):
            ltype = random.choice(leave_types)
            days = random.choice([1, 2, 3, 4, 5, 0.5])
            start = today() - relativedelta(weeks=random.randint(1, 52))
            end   = start + dt.timedelta(days=int(days - 1e-6))
            stat  = weighted_choice(status_mix)
            rows.append({
                "LeaveApplicationID": lid,
                "EmployeeID":         emp["EmployeeID"],
                "LeaveTypeID":        ltype[0],
                "StartDate":          start.isoformat(),
                "EndDate":            end.isoformat(),
                "NumberOfDays":       days,
                "Reason":             random.choice(["Family trip", "Medical", "Personal", ""]),
                "StatusCode":         stat,
                "SubmittedAt":        dt.datetime.combine(start, dt.time()).isoformat(sep=" "),
                "ManagerID":          emp["ManagerID"],
                "ManagerApprovalStatus":  "Approved" if stat in ("Manager-Approved", "HR-Approved") else
                                           ("Rejected" if stat == "Rejected" else None),
                "ManagerApprovalAt":  NOW_ISO if stat in ("Manager-Approved", "Rejected") else None,
                "ManagerComments":    "",
                "HRApproverID":       None,
                "HRApprovalStatus":   "Approved" if stat == "HR-Approved" else None,
                "HRApprovalAt":       NOW_ISO if stat == "HR-Approved" else None,
                "HRComments":         "",
                "CreatedAt":          NOW_ISO,
                "UpdatedAt":          NOW_ISO,
            })
            lid += 1
    return rows

# ────────────────────────────────
# 5. Timesheets
# ────────────────────────────────
def gen_timesheets_and_details(employees):
    ts_rows, det_rows = [], []
    tsid = detid = 1
    status_mix = CFG["timesheet_status_mix"]

    first_monday = today() - relativedelta(weeks=CFG["weeks_of_timesheets"])
    first_monday -= dt.timedelta(days=first_monday.weekday())  # Monday

    for emp in employees:
        if not emp["IsActive"]:
            continue
        period_start = first_monday
        for _ in range(CFG["weeks_of_timesheets"]):
            period_end = period_start + dt.timedelta(days=6)
            status = weighted_choice(status_mix)
            weekly_hours = 0.0
            for d in range(5):
                work_date = period_start + dt.timedelta(days=d)
                start_hr  = random.randint(8, 10)
                worked    = random.uniform(*CFG["daily_hours_range"])
                break_m   = random.randint(CFG["break_range_min"], CFG["break_range_max"])
                net       = round(worked - break_m/60.0, 2)
                end_dt    = dt.datetime.combine(work_date, dt.time(start_hr)) + \
                            dt.timedelta(hours=worked, minutes=break_m)
                det_rows.append({
                    "DetailID":       detid,
                    "TimesheetID":    tsid,
                    "WorkDate":       work_date.isoformat(),
                    "ProjectCode":    None,
                    "TaskDescription": "Feature work" if random.random()<0.7 else "Bug fix",
                    "HoursWorked":    net,
                    "IsOvertime":     1 if net > 8 else 0,
                    "CreatedAt":      dt.datetime.combine(work_date, dt.time()).isoformat(sep=" "),
                })
                detid          += 1
                weekly_hours   += net
            ts_rows.append({
                "TimesheetID":   tsid,
                "EmployeeID":    emp["EmployeeID"],
                "WeekStartDate": period_start.isoformat(),
                "WeekEndDate":   period_end.isoformat(),
                "TotalHours":    round(weekly_hours, 2),
                "StatusCode":    status,
                "SubmittedAt":   dt.datetime.combine(period_end, dt.time()).isoformat(sep=" "),
                "ApprovedByID":  emp["ManagerID"] if status == "Approved" else None,
                "ApprovedAt":    dt.datetime.combine(period_end + dt.timedelta(days=2), dt.time())
                                 .isoformat(sep=" ") if status == "Approved" else None,
                "Comments":      "",
                "CreatedAt":     dt.datetime.combine(period_start, dt.time()).isoformat(sep=" "),
                "UpdatedAt":     NOW_ISO,
            })
            tsid += 1
            period_start += dt.timedelta(days=7)
    return ts_rows, det_rows

# ────────────────────────────────
# 6. Assets
# ────────────────────────────────
LAPTOP_MODELS = ["Dell Latitude 7440", "MacBook Pro 14”, M3", "Lenovo ThinkPad X1"]
def gen_assets(asset_types, locations):
    rows, aid = [], 1
    for _ in range(CFG["n_assets"]):
        status = weighted_choice(CFG["asset_status_mix"])
        atype  = random.choice(asset_types)
        contract = random.random() < 0.25
        purchase = today() - relativedelta(months=random.randint(0, 60))
        rows.append({
            "AssetID":            aid,
            "AssetTag":           f"AS{aid:06d}",
            "SerialNumber":       fake.uuid4() if random.random()<0.9 else None,
            "MACAddress":         fake.mac_address() if atype["AssetTypeName"] in
                                                   ("Laptop", "Docking Station", "Monitor") else None,
            "AssetTypeID":        atype["AssetTypeID"],
            "AssetStatusCode":    status,
            "Model":              random.choice(LAPTOP_MODELS) if atype["AssetTypeName"]=="Laptop" else None,
            "Vendor":             random.choice(["Dell", "Apple", "Lenovo", "HP", ""]) ,
            "PurchaseDate":       purchase.isoformat(),
            "WarrantyEndDate":    (purchase + relativedelta(years=3)).isoformat(),
            "IsUnderContract":    1 if contract else 0,
            "ContractStartDate":  purchase if contract else None,
            "ContractExpiryDate": (purchase + relativedelta(years=3)) if contract else None,
            "LocationID":         random.choice(locations)["LocationID"],
            "Notes":              "",
            "IsActive":           1,
            "CreatedAt":          NOW_ISO,
            "UpdatedAt":          NOW_ISO,
        })
        aid += 1
    return rows

def gen_asset_assignments(assets, employees):
    rows, asid = [], 1
    active_emp = [e for e in employees if e["IsActive"]]
    assignable_assets = [a for a in assets if a["AssetStatusCode"] in CFG["assignable_codes"]]
    for asset in assignable_assets:
        if random.random() > 0.5:
            continue
        emp = random.choice(active_emp)
        due = asset["ContractExpiryDate"]
        rows.append({
            "AssignmentID":      asid,
            "AssetID":           asset["AssetID"],
            "EmployeeID":        emp["EmployeeID"],
            "AssignedAt":        NOW_ISO,
            "DueReturnDate":     due.isoformat() if due else None,
            "ReturnedAt":        None,
            "ConditionAtAssign": "Working",
            "ConditionAtReturn": None,
            "AssignedByID":      emp["ManagerID"] or emp["EmployeeID"],
            "ReceivedByID":      None,
            "Notes":             "",
            "CreatedAt":         NOW_ISO,
            "UpdatedAt":         NOW_ISO,
        })
        # mark status so trigger won't complain
        asset["AssetStatusCode"] = "Assigned"
        asid += 1
    return rows

# ────────────────────────────────
# 7. Feedback
# ────────────────────────────────
def gen_feedbacks(employees, departments):
    rows, fid = [], 1
    for _ in range(random.randint(100, 200)):
        emp = random.choice(employees)
        rows.append({
            "FeedbackID":         fid,
            "FeedbackAt":         NOW_ISO,
            "FeedbackTypeCode":   random.choice(["General","Manager","Department","Other"]),
            "Category":           random.choice(["Process","Culture","Workload",""]),
            "Subject":            random.choice(["Suggestion","Issue","Praise",""]) ,
            "FeedbackText":       fake.paragraph(nb_sentences=5),
            "TargetManagerID":    emp["ManagerID"],
            "TargetDepartmentID": emp["TeamID"],
            "FeedbackHash":       fake.sha256(raw_output=False),
            "IsRead":             0,
            "ReadByID":           None,
            "ReadAt":             None,
        })
        fid += 1
    return rows

# ────────────────────────────────
# MAIN
# ────────────────────────────────
def main():
    print("Generating fake echobyte data …")

    # build hierarchy
    locations     = gen_locations(CFG["n_locations"])
    departments   = gen_departments(CFG["dept_structure"], locations)
    teams         = gen_teams(departments, CFG["teams_per_dept"])
    employees, mgrs = gen_employees(teams, locations, CFG["n_employees"])
    e_contacts    = gen_emergency_contacts(employees)
    _, emp_roles  = gen_roles_and_emp_roles(employees, mgrs)
    leave_bal     = gen_leave_balances(employees)
    leave_apps    = gen_leave_applications(employees, mgrs)
    ts_periods, ts_details = gen_timesheets_and_details(employees)

    # assets / assignments
    asset_types = [{"AssetTypeID": i+1, "AssetTypeName": name}
                   for i, name in enumerate(["Laptop","Monitor","Keyboard","Mouse",
                                             "Docking Station","Mobile Phone",
                                             "Headset"])]
    assets      = gen_assets(asset_types, locations)
    assignments = gen_asset_assignments(assets, employees)

    feedbacks   = gen_feedbacks(employees, departments)

    # write csvs (parents first)
    wr("Locations",    locations)
    wr("Departments",  departments)
    wr("Teams",        teams)
    wr("Employees",    employees)
    wr("EmergencyContacts", e_contacts)
    wr("EmployeeRoles", emp_roles)

    wr("LeaveBalances",       leave_bal)
    wr("LeaveApplications",   leave_apps)

    wr("Timesheets",          ts_periods)
    wr("TimesheetDetails",    ts_details)

    wr("Assets",              assets)
    wr("AssetAssignments",    assignments)

    wr("EmployeeFeedbacks",   feedbacks)

    print("\nAll done! CSVs live under:", CFG["csv_out"].resolve())

if __name__ == "__main__":
    main()
