#!/usr/bin/env python3
"""
seed_org_structure.py
─────────────────────
Produces deterministic INSERT scripts (with explicit ID values) for
    • Locations  (optional extras)
    • Departments
    • Teams

and stores a JSON catalogue of the IDs under `csv_out/org_ids.json` so that
subsequent seeders can look them up.

Why explicit IDs?
    The user requested that, even for identity tables, we generate the PKs so
    all downstream CSVs can safely reference them.  During load you simply:
        SET IDENTITY_INSERT dbo.Departments ON;  BULK/EXEC script;  OFF;

Generated files
    04_seed_locations.sql
    05_seed_departments.sql
    06_seed_teams.sql
    org_ids.json
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List, Tuple

from faker import Faker

fake = Faker()

# ---------------------------------------------------------------------------
# CONFIGURATION (keep deterministic)
# ---------------------------------------------------------------------------
DEPARTMENTS: List[Tuple[str, str | None]] = [
    ("Engineering", None),
    ("Product", None),
    ("HR", None),
    ("IT", None),
    ("QA", None),
    ("Operations", None),
    # children (parent name must precede this row's parent in list)
    ("Recruitment", "HR"),
    ("Quality Assurance", "Engineering"),
]

TEAMS_PER_DEPT_RANGE = (2, 4)
RNG = random.Random(42)

_SQL_DIR = Path("csv_out")
_JSON_IDS = _SQL_DIR / "org_ids.json"
_SQL_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _mk_sql_file(name: str):
    fp = _SQL_DIR / name
    if fp.exists():
        fp.unlink()
    return fp.open("w", encoding="utf-8")


def _slug(name: str) -> str:
    words = [w for w in name.split() if w]
    if len(words) == 1:
        return words[0][:3].upper()
    return (words[0][0] + words[-1][0]).upper()


# ---------------------------------------------------------------------------
# MAIN SEED FUNCTIONS
# ---------------------------------------------------------------------------

def seed_locations(additional_count: int = 0, start_id: int = 5) -> Dict[str, int]:
    """Return mapping of LocationName → LocationID for any additional rows."""
    mapping: Dict[str, int] = {
        "New York HQ": 1,
        "San Francisco": 2,
        "London Office": 3,
        "Bangalore Center": 4,
    }

    if additional_count <= 0:
        return mapping

    fh = _mk_sql_file("04_seed_locations.sql")
    fh.write("SET IDENTITY_INSERT dbo.Locations ON;\n")
    next_id = start_id
    for _ in range(additional_count):
        city = fake.city()
        country = fake.country()
        name = f"{city} Office"
        addr1 = fake.street_address()
        tz = "UTC"
        esc = lambda s: s.replace("'", "''")
        fh.write(
            f"INSERT INTO dbo.Locations (LocationID, LocationName, Address1, City, Country, TimeZone) "
            f"VALUES ({next_id}, N'{esc(name)}', N'{esc(addr1)}', N'{esc(city)}', N'{esc(country)}', N'{tz}');\n"
        )
        mapping[name] = next_id
        next_id += 1
    fh.write("SET IDENTITY_INSERT dbo.Locations OFF;\n")
    fh.close()
    print("✅  Locations SQL generated")
    return mapping


def seed_departments(location_mapping: Dict[str, int]) -> Dict[str, int]:
    fh = _mk_sql_file("05_seed_departments.sql")
    fh.write("SET IDENTITY_INSERT dbo.Departments ON;\n")

    mapping: Dict[str, int] = {}
    next_id = 1

    # first pass – roots only (parent None)
    for name, parent in DEPARTMENTS:
        if parent is None:
            loc_id = location_mapping["New York HQ"]  # use HQ for simplicity
            code = _slug(name)
            fh.write(
                f"INSERT INTO dbo.Departments (DepartmentID, DepartmentName, DepartmentCode, LocationID) "
                f"VALUES ({next_id}, N'{name}', N'{code}', {loc_id});\n"
            )
            mapping[name] = next_id
            next_id += 1

    # second pass – children
    for name, parent in DEPARTMENTS:
        if parent is not None:
            parent_id = mapping[parent]
            loc_id = location_mapping["New York HQ"]
            code = _slug(name)
            fh.write(
                f"INSERT INTO dbo.Departments (DepartmentID, DepartmentName, DepartmentCode, ParentDepartmentID, LocationID) "
                f"VALUES ({next_id}, N'{name}', N'{code}', {parent_id}, {loc_id});\n"
            )
            mapping[name] = next_id
            next_id += 1

    fh.write("SET IDENTITY_INSERT dbo.Departments OFF;\n")
    fh.close()
    print("✅  Departments SQL generated")
    return mapping


def seed_teams(dept_mapping: Dict[str, int]) -> Tuple[Dict[str, int], Dict[int, int]]:
    fh = _mk_sql_file("06_seed_teams.sql")
    fh.write("SET IDENTITY_INSERT dbo.Teams ON;\n")

    mapping: Dict[str, int] = {}
    team_to_dept: Dict[int, int] = {}
    next_id = 1

    for dept_name, parent in DEPARTMENTS:
        if parent is not None:
            continue  # only root depts get teams directly
        dept_id = dept_mapping[dept_name]
        n_teams = RNG.randint(*TEAMS_PER_DEPT_RANGE)
        for i in range(1, n_teams + 1):
            team_name = f"{dept_name} Team {i}"
            code = _slug(dept_name) + str(i)
            fh.write(
                f"INSERT INTO dbo.Teams (TeamID, TeamName, TeamCode, DepartmentID) "
                f"VALUES ({next_id}, N'{team_name}', N'{code}', {dept_id});\n"
            )
            mapping[team_name] = next_id
            team_to_dept[next_id] = dept_id
            next_id += 1

    fh.write("SET IDENTITY_INSERT dbo.Teams OFF;\n")
    fh.close()
    print("✅  Teams SQL generated")
    return mapping, team_to_dept


# ---------------------------------------------------------------------------
# PUBLIC ENTRY
# ---------------------------------------------------------------------------

def run(additional_locations: int = 0):
    loc_map = seed_locations(additional_locations)
    dept_map = seed_departments(loc_map)
    team_map, team_to_dept = seed_teams(dept_map)

    cat = {
        "locations": loc_map,
        "departments": dept_map,
        "teams": team_map,
        "team_to_department": team_to_dept,
    }
    _JSON_IDS.write_text(json.dumps(cat, indent=2))
    print(f"📄  ID catalogue → {_JSON_IDS}")


if __name__ == "__main__":
    run()
