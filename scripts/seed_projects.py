#!/usr/bin/env python3
"""
seed_projects.py
────────────────
Generates project master data and employee allocation data:
    • Projects.csv              (explicit ProjectID)
    • ProjectAssignments.csv    (explicit AssignmentID)

Logic
• Reads `org_ids.json` to get Department and Team IDs.
• Reads `Employees.csv` to learn each employee's Department via Team → Department map.
• Creates ~120 projects distributed across root departments (Engineering, …).
• Manager for a project is randomly chosen from managers in that department.
• Each non-manager employee is assigned 1–3 projects from their department.
• Allocation percentages and dates are realistic.
"""

import csv
import datetime as dt
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple

from faker import Faker

fake = Faker()

# Constants
PROJECT_COUNT = 120

# Status codes with weights for realistic distribution
_STATUS_CODES = [
    ("Active", 0.6),
    ("Completed", 0.25),
    ("On-Hold", 0.1),
    ("Planned", 0.05),
]


# ---------------------------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> Dict:
    with open(path) as f:
        return json.load(f)


def _load_employees(path: Path) -> List[Dict]:
    with open(path) as f:
        return list(csv.DictReader(f))


def write_csv(name: str, data: List[Dict]):
    if not data:
        return
    path = Path(f"csv_out/{name}.csv")
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


# ---------------------------------------------------------------------------
# CORE LOGIC
# ---------------------------------------------------------------------------

def generate_projects(org: Dict, employees: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    # Get root departments (all departments are root level in this structure)
    dept_ids_root = list(org["departments"].values())
    
    # Build reverse index: TeamID -> DepartmentID
    team_to_dept: Dict[int, int] = {int(tid): int(did) for tid, did in org["team_to_department"].items()}
    
    # Build teams by department for project assignment
    teams_by_dept: Dict[int, List[int]] = {}
    for team_id, dept_id in team_to_dept.items():
        teams_by_dept.setdefault(dept_id, []).append(team_id)

    # Build manager and staff lists by department
    manager_ids: Dict[int, int] = {}  # emp_id -> dept_id
    staff_by_dept: Dict[int, List[int]] = {d: [] for d in dept_ids_root}

    for row in employees:
        emp_id = int(row["EmployeeID"])
        dept_id = team_to_dept.get(int(row["TeamID"]), None)
        if dept_id is None:
            continue
        
        # Check designation ID as integer for manager roles
        # Designation IDs: 3=Senior Software Engineer, 5=Principal Engineer, 7=Senior QA Engineer, 8=DevOps Engineer, 10=Product Manager
        designation_id = int(row["DesignationID"])
        if designation_id in [3, 5, 7, 8, 10]:  # Manager designations
            manager_ids[emp_id] = dept_id
        else:
            staff_by_dept.setdefault(dept_id, []).append(emp_id)

    # Generate projects
    projects: List[Dict] = []
    proj_assignments: List[Dict] = []

    next_proj_id = 1
    next_asg_id = 1

    def _weighted_status():
        r = random.random()
        cum = 0.0
        for code, w in _STATUS_CODES:
            cum += w
            if r <= cum:
                return code
        return _STATUS_CODES[-1][0]

    for dept_id in dept_ids_root:
        n = PROJECT_COUNT // len(dept_ids_root)
        for _ in range(n):
            start = dt.date(2023, random.randint(1, 12), random.randint(1, 28))
            end = start + dt.timedelta(days=random.randint(60, 540))
            status = _weighted_status()
            
            # Get managers for this department
            mgr_choices = [eid for eid, did in manager_ids.items() if did == dept_id]
            
            # If no managers in this department, get managers from other departments
            if not mgr_choices:
                mgr_choices = list(manager_ids.keys())
            
            # Ensure we have a manager - if still none, create a fallback
            if not mgr_choices:
                # This should not happen if employees were generated properly
                # But as a safety measure, use the first employee as manager
                mgr_choices = [int(employees[0]["EmployeeID"])]
            
            manager_id = random.choice(mgr_choices)
            
            # Assign a team from this department (or leave empty if no teams exist)
            available_teams = teams_by_dept.get(dept_id, [])
            team_id = random.choice(available_teams) if available_teams else ""
            
            proj = {
                "ProjectID": next_proj_id,
                "ProjectCode": f"PROJ-2024-{next_proj_id:03d}",
                "ProjectName": fake.bs().title(),
                "DepartmentID": dept_id,
                "TeamID": team_id,  # Assign a team from the department
                "ManagerID": manager_id,  # Always a valid integer, never None or empty string
                "StartDate": start.isoformat(),
                "EndDate": end.isoformat(),
                "StatusCode": status,
                "IsActive": 1 if status in ("Active", "Planned") else 0,
                "CreatedAt": dt.datetime.utcnow().isoformat(),
                "UpdatedAt": dt.datetime.utcnow().isoformat(),
            }
            projects.append(proj)

            # Staff assignments (only Active / Planned)
            if status in ("Active", "Planned"):
                candidates = staff_by_dept.get(dept_id, [])
                random.shuffle(candidates)
                take = random.randint(5, 20)
                for emp_id in candidates[:take]:
                    pct = random.randint(20, 100)
                    start_alloc = start
                    end_alloc = end if random.random() < 0.7 else ""
                    proj_assignments.append({
                        "AssignmentID": next_asg_id,
                        "ProjectID": next_proj_id,
                        "EmployeeID": emp_id,
                        "RoleInProject": random.choice(["Developer", "QA", "Analyst", "Designer"]),
                        "AllocationPct": pct,
                        "StartDate": start_alloc.isoformat(),
                        "EndDate": end_alloc if end_alloc else "",
                        "CreatedAt": dt.datetime.utcnow().isoformat(),
                        "UpdatedAt": dt.datetime.utcnow().isoformat(),
                    })
                    next_asg_id += 1

            next_proj_id += 1

    return projects, proj_assignments


# ---------------------------------------------------------------------------
# DRIVER
# ---------------------------------------------------------------------------

def run():
    org = _load_json(Path("csv_out/org_ids.json"))
    employees = _load_employees(Path("csv_out/Employees.csv"))

    projects, assignments = generate_projects(org, employees)
    write_csv("Projects", projects)
    write_csv("ProjectAssignments", assignments)
    print("🎉  Projects and Assignments generated")


if __name__ == "__main__":
    run()
