#!/usr/bin/env python3
"""generate_fake_company_portal_data.py
-------------------------------------------------------------------
Builds realistic, referential‑integrity‑preserving test data for the
“echobyte” company‑portal schema and saves one CSV per table in
./csv_out/.

Edge‑cases & realism covered (2025‑07‑09 revision):
•  Soft‑deleted employees (~3 %) and varied employment‑status mix.
•  Leave‑request mix pending/approved/rejected plus half‑day requests.
•  Assets across in‑stock / assigned / maintenance / retired states.
•  Timesheets with variable start/end, realistic breaks & overtime.
•  Multiple addresses (25 % of staff have secondary address).

The script keeps probabilities configurable via CFG and matches lookup‑
ID order exactly as per the DDL (assertions check at startup).
-------------------------------------------------------------------"""

from __future__ import annotations
import os, random, csv, datetime as dt
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from faker import Faker
import pandas as pd

# ────────────────────────────────
# CONFIG – tweak to taste
# ────────────────────────────────
CFG = {
    "seed":                42,
    "csv_out":             "csv_out",

    # ─── Org structure volumes ─────────────────────────────
    "n_locations":         4,
    "departments": [
        {"name": "Corporate",   "children": ["HR", "IT", "Finance", "Operations"]},
        {"name": "Engineering", "children": ["Platform", "Data", "QA"]},
    ],
    "teams_per_dept":      (1, 3),          # min / max teams per department
    "n_employees":         350,

    # ─── Mixes & probabilities ─────────────────────────────
    "soft_delete_pct":     0.03,            # 3 % rows flagged is_deleted
    "employment_status_mix": {             # DDL order: active/on_leave/terminated/retired
        1: 0.90,
        2: 0.05,
        3: 0.03,
        4: 0.02,
    },
    # leave_request_status: 1=pending, 2=approved, 3=rejected
    "leave_status_mix": {
        1: 0.15,
        2: 0.75,
        3: 0.10,
    },

    # asset_status: 1 in_stock, 2 assigned, 3 maintenance, 4 retired
    "asset_status_mix": {
        1: 0.30,
        2: 0.50,
        3: 0.15,
        4: 0.05,
    },

    "manager_ratio":       0.10,            # fallback when teams too small

    # Asset catalogue & count
    "asset_types": [
        "Laptop", "Monitor", "Keyboard", "Mouse", "HDMI Cable", "Headphones",
        "Chair", "Desk", "Docking Station", "Mobile Phone", "Printer", "WebCam",
    ],
    "n_assets":            5000,

    # Project counts (same logic as original script)
    "project_past":        4,
    "project_current":     5,
    "project_future":      3,
    
    # ─── Leave-type mix (ID → weight) ─────────────────────────
    # Use the exact primary-key IDs from the DDL insert order
    "leave_type_weights": {
        1: 60,   # VAC
        2: 25,   # SICK
        3: 3,    # PARENTAL
        4: 2,    # BEREAVEMENT
        5: 2,    # JURY
        6: 8,    # UNPAID
    },

    # Leave / timesheet windows
    "weeks_of_timesheets": 52,             # one year of periods per employee
    "leave_request_prob":  0.25,           # ~¼ of employees file each month

    # Timesheet realism knobs
    "daily_hours_range":   (7, 9),         # worked hours before break
    "break_range_min":     30,             # mins
    "break_range_max":     75,


}
LEAVE_REASONS = {
    1: ["Family vacation", "Personal time", "Wedding", "Travel"],
    2: ["Flu", "Medical appointment", "Recovery", "Migraine"],
    6: ["Sabbatical", "Personal matters", "Extended leave"],
}
OVERTIME_NOTES = [
    "Client deadline", "Emergency fix", "Release prep",
    "Quarter-end crunch", "Production issue",
]
# ─── Seed & Faker init ───────────────────────────────────
random.seed(CFG["seed"])
fake = Faker("en_US")
Faker.seed(CFG["seed"])

# ─── Output dir ──────────────────────────────────────────
os.makedirs(CFG["csv_out"], exist_ok=True)

# ────────────────────────────────
# Utility helpers
# ────────────────────────────────

def weighted_choice(weight_map: dict[int, float]) -> int:
    """Return a key chosen according to its relative weight."""
    r, accum = random.random(), 0.0
    for k, w in weight_map.items():
        accum += w
        if r < accum:
            return k
    # numerical rounding fall‑through → return last key
    return next(reversed(weight_map))

# ────────────────────────────────
# 1. Locations
# ────────────────────────────────

def gen_locations(n: int):
    now = dt.datetime.now().isoformat(sep=" ")
    rows = []
    for lid in range(1, n+1):
        city = fake.city()
        rows.append({
            "location_id": lid,
            "name": f"Office – {city}",
            "address_line1": fake.street_address(),
            "address_line2": "",
            "city": city,
            "state": fake.state(),
            "postal_code": fake.postcode(),
            "country": "USA",
            "timezone": "America/Los_Angeles",
            "created_at": now,
            "updated_at": now,
        })
    return rows

# ────────────────────────────────
# 2. Departments & Teams
# ────────────────────────────────

def gen_departments(structure):
    now, dept_id, rows = dt.datetime.now().isoformat(sep=" "), 1, []
    for node in structure:
        parent = dept_id
        rows.append({
            "department_id": parent,
            "parent_department_id": None,
            "name": node["name"],
            "description": f"{node['name']} Division",
            "created_at": now,
            "updated_at": now,
        })
        dept_id += 1
        for child in node["children"]:
            rows.append({
                "department_id": dept_id,
                "parent_department_id": parent,
                "name": child,
                "description": f"{child} Department",
                "created_at": now,
                "updated_at": now,
            })
            dept_id += 1
    return rows


def gen_teams(departments, locations, rng):
    now, team_id, rows = dt.datetime.now().isoformat(sep=" "), 1, []
    for dept in departments:
        for _ in range(random.randint(*rng)):
            rows.append({
                "team_id": team_id,
                "department_id": dept["department_id"],
                "name": f"{dept['name']} Team {fake.bothify(text='??').upper()}",
                "headquarters_location_id": random.choice(locations)["location_id"],
                "created_at": now,
                "updated_at": now,
            })
            team_id += 1
    return rows

# ────────────────────────────────
# 3. Asset Types & Assets
# ────────────────────────────────

def gen_asset_types(catalogue):
    now = dt.datetime.now().isoformat(sep=" ")
    return [{
        "asset_type_id": idx,
        "name": name,
        "description": f"{name} asset type",
        "created_at": now,
    } for idx, name in enumerate(catalogue, start=1)]


def gen_assets(asset_types, total):
    now, rows = dt.datetime.now().isoformat(sep=" "), []
    for aid in range(1, total+1):
        atype  = random.choice(asset_types)
        status = weighted_choice(CFG["asset_status_mix"])
        rows.append({
            "asset_id": aid,
            "asset_type_id": atype["asset_type_id"],
            "mac_address": fake.mac_address() if atype["name"] in ("Laptop","Docking Station","Monitor","Mobile Phone") else None,
            "serial_number": fake.uuid4(),
            "purchase_date": (dt.date.today() - relativedelta(months=random.randint(0,36))).isoformat(),
            "purchase_cost": round(random.uniform(50, 2500), 2),
            "asset_status_id": status,
            "created_at": now,
            "updated_at": now,
        })
    return rows


def gen_asset_assignments(assets, employees):
    rows, assign_id = [], 1
    assets_assigned = [a for a in assets if a["asset_status_id"] == 2]
    eligible_emp    = [e for e in employees if e["employment_status_id"] == 1 and not e["is_deleted"]]
    if not eligible_emp:
        return rows
    for asset in assets_assigned:
        emp = random.choice(eligible_emp)
        rows.append({
            "assignment_id": assign_id,
            "employee_id": emp["employee_id"],
            "asset_id": asset["asset_id"],
            "assigned_date": (dt.datetime.now() - relativedelta(days=random.randint(1,365))).isoformat(sep=" "),
            "returned_date": None,
            "notes": "",
        })
        assign_id += 1
    return rows

# ────────────────────────────────
# 4. Employees
# ────────────────────────────────

def gen_employees(teams, count):
    now, emp_id, rows, managers = dt.datetime.now().isoformat(sep=" "), 1, [], {}

    # Ensure one manager (active) per team
    for team in teams:
        first, last = fake.first_name(), fake.last_name()
        rows.append({
            "employee_id": emp_id,
            "team_id": team["team_id"],
            "manager_id": None,
            "work_location_id": team["headquarters_location_id"],
            "first_name": first,
            "last_name": last,
            "email": f"{first.lower()}.{last.lower()}@echobyte.com",
            "phone_primary": fake.phone_number(),
            "phone_secondary": "",
            "date_of_birth": (dt.date.today()-relativedelta(years=random.randint(28,58))).isoformat(),
            "date_of_joining": (dt.date.today()-relativedelta(years=random.randint(3,12))).isoformat(),
            "gender_id": random.randint(1,4),
            "pronouns": "",
            "employment_status_id": 1,
            "is_deleted": False,
            "deleted_at": None,
            "deleted_by": None,
            "created_at": now,
            "updated_at": now,
        })
        managers[team["team_id"]] = emp_id
        emp_id += 1

    # Remaining staff with mixed statuses & deletions
    remaining = count - len(rows)
    while remaining > 0:
        team           = random.choice(teams)
        first, last    = fake.first_name(), fake.last_name()
        status_id      = weighted_choice(CFG["employment_status_mix"])
        deleted_flag   = random.random() < CFG["soft_delete_pct"]
        rows.append({
            "employee_id": emp_id,
            "team_id": team["team_id"],
            "manager_id": managers[team["team_id"]],
            "work_location_id": team["headquarters_location_id"],
            "first_name": first,
            "last_name": last,
            "email": f"{first.lower()}.{last.lower()}{random.randint(1,9999)}@echobyte.com",
            "phone_primary": fake.phone_number(),
            "phone_secondary": "",
            "date_of_birth": (dt.date.today()-relativedelta(years=random.randint(21,58))).isoformat(),
            "date_of_joining": (dt.date.today()-relativedelta(years=random.randint(0,8))).isoformat(),
            "gender_id": random.randint(1,4),
            "pronouns": "",
            "employment_status_id": status_id,
            "is_deleted": deleted_flag,
            "deleted_at": (dt.datetime.now() - relativedelta(days=random.randint(1,365))).isoformat(sep=" ") if deleted_flag else None,
            "deleted_by": managers[team["team_id"]] if deleted_flag else None,
            "created_at": now,
            "updated_at": now,
        })
        emp_id    += 1
        remaining -= 1
    return rows

# ────────────────────────────────
# 5. Addresses & Emergency contacts
# ────────────────────────────────

def gen_addresses(employees):
    now, addr_id, rows = dt.datetime.now().isoformat(sep=" "), 1, []
    for emp in employees:
        # Home
        rows.append({
            "address_id": addr_id,
            "employee_id": emp["employee_id"],
            "address_type_id": 1,
            "address_line1": fake.street_address(),
            "address_line2": "",
            "city": fake.city(),
            "state": fake.state(),
            "postal_code": fake.postcode(),
            "country": "USA",
            "created_at": now,
            "updated_at": now,
        })
        addr_id += 1
        # Optional secondary
        if random.random() < 0.25:
            rows.append({
                "address_id": addr_id,
                "employee_id": emp["employee_id"],
                "address_type_id": random.choice([2,3]),
                "address_line1": fake.street_address(),
                "address_line2": "",
                "city": fake.city(),
                "state": fake.state(),
                "postal_code": fake.postcode(),
                "country": "USA",
                "created_at": now,
                "updated_at": now,
            })
            addr_id += 1
    return rows


def gen_contacts(employees):
    now, cid, rows = dt.datetime.now().isoformat(sep=" "), 1, []
    for emp in employees:
        if random.random() < 0.8:
            rows.append({
                "contact_id": cid,
                "employee_id": emp["employee_id"],
                "name": fake.name(),
                "relationship": random.choice(["Spouse","Parent","Sibling","Friend"]),
                "phone": fake.phone_number(),
                "email": fake.email(),
                "created_at": now,
            })
            cid += 1
    return rows

# ────────────────────────────────
# 6. Leave requests & history
# ────────────────────────────────

def gen_leave_requests(employees):
    rows_req, rows_hist = [], []
    req_id = hist_id = 1
    now    = dt.datetime.now().isoformat(sep=" ")
    start_window = dt.date.today() - relativedelta(weeks=52)
    weights = CFG["leave_type_weights"]
    leave_type_pool = [
        lt_id
        for lt_id, wt in weights.items()
        for _ in range(wt)
    ]

    active_staff = [e for e in employees if e["employment_status_id"] == 1 and not e["is_deleted"]]

    for emp in active_staff:
        for month in range(12):
            if random.random() < CFG["leave_request_prob"]:
                leave_type = random.choice(leave_type_pool)
                days_req   = random.choice([0.5, 1, 2, 3, 4, 5])
                start_date = start_window + relativedelta(weeks=4*month, days=random.randint(0,27))
                end_date   = start_date + dt.timedelta(days=int(days_req-1e-6))
                status_id  = weighted_choice(CFG["leave_status_mix"])
                decision_dt = None
                if status_id in (2,3):
                    decision_dt = dt.datetime.combine(end_date, dt.time(17)) + dt.timedelta(days=2)

                rows_req.append({
                    "request_id": req_id,
                    "employee_id": emp["employee_id"],
                    "leave_type_id": leave_type,
                    "manager_id": emp["manager_id"] or emp["employee_id"],
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days_requested": days_req,
                    "reason": random.choice(LEAVE_REASONS.get(leave_type, [""])),
                    "leave_status_id": status_id,
                    "decision_date": decision_dt.isoformat(sep=" ") if decision_dt else None,
                    "decision_notes": "",
                    "created_at": dt.datetime.combine(start_date, dt.time()).isoformat(sep=" "),
                    "updated_at": now,
                })
                rows_hist.append({
                    "history_id": hist_id,
                    "request_id": req_id,
                    "changed_by": emp["manager_id"] or emp["employee_id"],
                    "old_status_id": 1,
                    "new_status_id": status_id,
                    "change_date": decision_dt.isoformat(sep=" ") if decision_dt else now,
                    "notes": "",
                })
                req_id += 1
                hist_id += 1
    return rows_req, rows_hist

# ────────────────────────────────
# 7. Timesheets
# ────────────────────────────────

def gen_timesheets(employees):
    period_rows, entry_rows, hist_rows = [], [], []
    period_id = entry_id = hist_id = 1

    today = dt.date.today()
    first_monday = today - relativedelta(weeks=CFG["weeks_of_timesheets"])
    first_monday -= dt.timedelta(days=first_monday.weekday())

    active_staff = [e for e in employees if e["employment_status_id"] == 1 and not e["is_deleted"]]

    for emp in active_staff:
        period_start = first_monday
        for _ in range(CFG["weeks_of_timesheets"]):
            period_end = period_start + dt.timedelta(days=6)
            weekly_hours, overtime_hours = 0.0, 0.0
            # Mon‑Fri entries
            for d in range(5):
                work_date = period_start + dt.timedelta(days=d)
                start_hour = random.randint(8, 10)
                worked = random.uniform(*CFG["daily_hours_range"])
                break_min = random.randint(CFG["break_range_min"], CFG["break_range_max"])
                net = round(worked - break_min/60.0, 2)
                is_ot = net > 8
                note_text = random.choice(OVERTIME_NOTES) if is_ot else ""
                weekly_hours += net
                end_dt = dt.datetime.combine(work_date, dt.time(start_hour)) + dt.timedelta(hours=worked, minutes=break_min)
                entry_rows.append({
                    "entry_id": entry_id,
                    "period_id": period_id,
                    "work_date": work_date.isoformat(),
                    "start_time": dt.time(start_hour).isoformat(),
                    "end_time": end_dt.time().isoformat(),
                    "break_minutes": break_min,
                    "is_overtime": is_ot,
                    "notes": note_text,
                    "created_at": dt.datetime.combine(work_date, dt.time()).isoformat(sep=" "),
                })
                entry_id += 1
            overtime_hours = max(0.0, round(weekly_hours - 40.0, 2))
            approved_at = dt.datetime.combine(period_end + dt.timedelta(days=2), dt.time(12))
            period_rows.append({
                "period_id": period_id,
                "employee_id": emp["employee_id"],
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "submitted_at": dt.datetime.combine(period_end, dt.time(18)).isoformat(sep=" "),
                "approved_by": emp["manager_id"] or emp["employee_id"],
                "approved_at": approved_at.isoformat(sep=" "),
                "timesheet_status_id": 3,  # approved
                "total_hours": round(weekly_hours, 2),
                "overtime_hours": overtime_hours,
                "created_at": dt.datetime.combine(period_start, dt.time()).isoformat(sep=" "),
                "updated_at": dt.datetime.now().isoformat(sep=" "),
            })
            hist_rows.append({
                "history_id": hist_id,
                "period_id": period_id,
                "changed_by": emp["manager_id"] or emp["employee_id"],
                "old_status_id": 2,  # submitted
                "new_status_id": 3,  # approved
                "change_date": approved_at.isoformat(sep=" "),
                "note": "",
            })
            hist_id += 1
            period_id += 1
            period_start += dt.timedelta(days=7)
    return period_rows, entry_rows, hist_rows

# ────────────────────────────────
# 8. Projects (logic unchanged from original)
# ────────────────────────────────

def gen_projects(departments, teams, employees):
    proj_rows, dept_proj_rows, team_proj_rows, assign_rows = [], [], [], []
    project_id = assign_id = 1
    today = dt.date.today()
    status_lookup = {"past": 4, "current": 2, "future": 1}  # completed, active, planning

    def create_project(category: str, idx: int):
        nonlocal project_id, assign_id
        code = f"PRJ{project_id:04d}"
        if category == "past":
            start = today - relativedelta(months=random.randint(12,36))
            end   = start + relativedelta(months=random.randint(3,12))
        elif category == "current":
            start = today - relativedelta(months=random.randint(1,12))
            end   = today + relativedelta(months=random.randint(1,12))
        else:  # future
            start = today + relativedelta(months=random.randint(1,6))
            end   = start + relativedelta(months=random.randint(6,18))
        now = dt.datetime.now().isoformat(sep=" ")
        proj_rows.append({
            "project_id": project_id,
            "name": f"{category.title()} Project {idx+1}",
            "code": code,
            "description": f"A {category} project for testing",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "project_status_id": status_lookup[category],
            "created_at": now,
            "updated_at": now,
        })
        # link 1‑3 departments
        for dep in random.sample(departments, k=random.randint(1,3)):
            dept_proj_rows.append({
                "department_id": dep["department_id"],
                "project_id": project_id,
                "assigned_date": start.isoformat(),
            })
        # link 1‑4 teams & some employees
        for tm in random.sample(teams, k=random.randint(1,4)):
            team_proj_rows.append({
                "team_id": tm["team_id"],
                "project_id": project_id,
                "assigned_date": start.isoformat(),
            })
            team_emp = [e for e in employees if e["team_id"] == tm["team_id"] and e["employment_status_id"] == 1 and not e["is_deleted"]]
            for emp in random.sample(team_emp, k=min(3, len(team_emp))):
                assign_rows.append({
                    "assignment_id": assign_id,
                    "project_id": project_id,
                    "employee_id": emp["employee_id"],
                    "role": random.choice(["Developer","QA","PM","BA"]),
                    "assigned_date": start.isoformat(),
                })
                assign_id += 1
        project_id += 1

    for cat, cnt in [("past", CFG["project_past"]), ("current", CFG["project_current"]), ("future", CFG["project_future"])]:
        for idx in range(cnt):
            create_project(cat, idx)
    return proj_rows, dept_proj_rows, team_proj_rows, assign_rows

# ────────────────────────────────
# CSV helper
# ────────────────────────────────

def write_csv(name: str, rows: list[dict]):
    if not rows:
        return
    pd.DataFrame(rows).to_csv(os.path.join(CFG["csv_out"], f"{name}.csv"), index=False, quoting=csv.QUOTE_MINIMAL)
    print(f" → {name}.csv ({len(rows):,} rows)")

# ────────────────────────────────
# Main generator
# ────────────────────────────────

def main():
    # Sanity: leave‑status mix keys match DDL IDs (1,2,3)
    assert set(CFG["leave_status_mix"].keys()) == {1,2,3}, "leave_status_mix must map 1,2,3 exactly"
    assert set(CFG["leave_type_weights"]) == {1,2,3,4,5,6}, \
    "leave_type_weights must map all six IDs 1–6 exactly"

    print("Generating fake company‑portal data …")

    # Org & assets
    locations   = gen_locations(CFG["n_locations"])
    departments = gen_departments(CFG["departments"])
    teams       = gen_teams(departments, locations, CFG["teams_per_dept"])
    asset_types = gen_asset_types(CFG["asset_types"])
    assets      = gen_assets(asset_types, CFG["n_assets"])

    # People
    employees = gen_employees(teams, CFG["n_employees"])
    addresses = gen_addresses(employees)
    contacts  = gen_contacts(employees)

    # Links & workflow data
    asset_assign = gen_asset_assignments(assets, employees)
    leave_req, leave_hist = gen_leave_requests(employees)
    ts_period, ts_entry, ts_hist = gen_timesheets(employees)
    projects, dept_proj, team_proj, proj_assign = gen_projects(departments, teams, employees)

    # Write CSVs (parents first)
    write_csv("location", locations)
    write_csv("department", departments)
    write_csv("team", teams)
    write_csv("asset_type", asset_types)
    write_csv("asset", assets)
    write_csv("employee", employees)
    write_csv("employee_address", addresses)
    write_csv("emergency_contact", contacts)
    write_csv("employee_asset_assignment", asset_assign)
    write_csv("leave_request", leave_req)
    write_csv("leave_request_history", leave_hist)
    write_csv("timesheet_period", ts_period)
    write_csv("timesheet_entry", ts_entry)
    write_csv("timesheet_period_history", ts_hist)
    write_csv("project", projects)
    write_csv("department_project", dept_proj)
    write_csv("team_project", team_proj)
    write_csv("project_assignment", proj_assign)

    print("\nAll CSVs written to", CFG["csv_out"])

# ────────────────────────────────
# Run as script
# ────────────────────────────────
if __name__ == "__main__":
    main()
