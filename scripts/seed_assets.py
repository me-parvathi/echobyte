#!/usr/bin/env python3
"""
seed_assets.py
──────────────
Creates:
    • Assets.csv
    • AssetAssignments.csv

Rules
• 500 assets across 7 types.
• Status mix from ddl lookup table.
• About 40 % of assets assigned to employees; trigger sync will mark status
  "Assigned".  DueReturnDate never exceeds ContractExpiryDate.
"""
from __future__ import annotations

import csv
import random
import datetime as dt
from pathlib import Path
from typing import List, Dict, Tuple

from faker import Faker

from scripts.csv_utils import write_csv

fake = Faker()
random.seed(42)

ASSET_TYPES = [
    (1, "Laptop"),
    (2, "Monitor"),
    (3, "Keyboard"),
    (4, "Mouse"),
    (5, "Docking Station"),
    (6, "Mobile Phone"),
    (7, "Headset"),
]

_STATUS_MIX = [
    ("In-Stock", 0.25),
    ("Available", 0.25),
    ("Assigned", 0.35),
    ("Maintenance", 0.10),
    ("Decommissioning", 0.03),
    ("Retired", 0.02),
]

TOTAL_ASSETS = 500

# ---------------------------------------------------------------------------

def _load_csv(path: Path) -> List[Dict]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _weighted_status():
    r = random.random()
    cum = 0.0
    for s, w in _STATUS_MIX:
        cum += w
        if r <= cum:
            return s
    return _STATUS_MIX[-1][0]

# ---------------------------------------------------------------------------

def generate_assets(employees: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    assets: List[Dict] = []
    assignments: List[Dict] = []

    emp_ids = [int(e["EmployeeID"]) for e in employees]
    it_staff = random.sample(emp_ids, k=50)  # pretend 50 employees are IT staff

    asset_id = 1
    assign_id = 1
    used_serial_numbers = set()  # Track used serial numbers to avoid duplicates

    for _ in range(TOTAL_ASSETS):
        type_id, type_name = random.choice(ASSET_TYPES)
        status = _weighted_status()
        tag = f"AST-{asset_id:05d}"
        
        # Generate unique serial number
        while True:
            serial = f"SN{random.randint(100000,999999)}"
            if serial not in used_serial_numbers:
                used_serial_numbers.add(serial)
                break
        
        today = dt.date.today()
        under_contract = random.random() < 0.4
        
        # Generate purchase date (1-4 years ago)
        purchase_date = today - dt.timedelta(days=random.randint(365, 1460))
        
        # Generate contract dates if under contract
        contract_start = ""
        contract_end = ""
        if under_contract:
            # Contract starts 6-18 months after purchase
            contract_start = purchase_date + dt.timedelta(days=random.randint(180, 540))
            # Contract lasts 1-3 years
            contract_end = contract_start + dt.timedelta(days=random.randint(365, 1095))
        
        assets.append({
            "AssetID": asset_id,
            "AssetTag": tag,
            "SerialNumber": serial,
            "MACAddress": "",
            "AssetTypeID": type_id,
            "AssetStatusCode": status,
            "Model": type_name + " Model",  # simple
            "Vendor": random.choice(["Dell", "HP", "Apple", "Lenovo", "Asus"]),
            "PurchaseDate": purchase_date.isoformat(),
            "WarrantyEndDate": (purchase_date + dt.timedelta(days=random.randint(365, 1095))).isoformat(),
            "IsUnderContract": 1 if under_contract else 0,
            "ContractStartDate": contract_start.isoformat() if under_contract else "",
            "ContractExpiryDate": contract_end.isoformat() if under_contract else "",
            "LocationID": "",
            "Notes": "",
            "IsActive": 1 if status not in ("Retired",) else 0,
            "CreatedAt": dt.datetime.utcnow().isoformat(),
            "UpdatedAt": dt.datetime.utcnow().isoformat(),
        })

        if status == "Assigned":
            # create assignment row
            emp_id = random.choice(emp_ids)
            assigned_by = random.choice(it_staff)
            
            # Generate assignment date that ensures proper timeline
            if under_contract and contract_end:
                # For assets under contract, assignment must be before contract end
                max_assignment_date = contract_end - dt.timedelta(days=30)  # Leave 30 days buffer
                min_assignment_date = contract_start if contract_start else (purchase_date + dt.timedelta(days=180))
                
                # Ensure assignment date is within valid range
                if min_assignment_date < max_assignment_date:
                    days_range = (max_assignment_date - min_assignment_date).days
                    random_days = random.randint(0, min(days_range, 365))  # Max 1 year
                    assigned_at = min_assignment_date + dt.timedelta(days=random_days)
                else:
                    # Fallback: assignment 6 months after purchase
                    assigned_at = purchase_date + dt.timedelta(days=180)
            else:
                # For assets not under contract, assignment can be 1-12 months ago
                assigned_at = dt.datetime.utcnow() - dt.timedelta(days=random.randint(30, 365))
            
            # Calculate due return date with proper validation
            due = ""
            if under_contract and contract_end:
                # If under contract, due date cannot exceed contract end
                max_due_date = contract_end
                min_due_date = assigned_at + dt.timedelta(days=30)  # Minimum 30 days
                
                # Ensure min_due_date doesn't exceed max_due_date
                if min_due_date <= max_due_date:
                    # Generate a random due date between min and max
                    days_range = (max_due_date - min_due_date).days
                    if days_range > 0:
                        random_days = random.randint(0, days_range)
                        due = min_due_date + dt.timedelta(days=random_days)
                    else:
                        due = min_due_date
                else:
                    # If minimum due date exceeds contract end, use contract end
                    due = contract_end
            else:
                # For non-contract assets, due date is 30-180 days after assignment
                due = assigned_at + dt.timedelta(days=random.randint(30, 180))
            
            # Final validation: ensure due date doesn't exceed contract end
            if under_contract and contract_end and due > contract_end:
                due = contract_end
                print(f"⚠️  Asset {asset_id}: Adjusted DueReturnDate to ContractExpiryDate ({due})")
            
            # Additional validation: ensure due date is after assignment date
            if due and due <= assigned_at:
                print(f"⚠️  Asset {asset_id}: Invalid DueReturnDate ({due}) <= AssignedAt ({assigned_at})")
                # Set due date to 30 days after assignment
                due = assigned_at + dt.timedelta(days=30)
            
            # Final check: ensure assignment date is before contract end
            if under_contract and contract_end and assigned_at >= contract_end:
                print(f"⚠️  Asset {asset_id}: Assignment date ({assigned_at}) >= Contract end ({contract_end})")
                # Adjust assignment date to be before contract end
                assigned_at = contract_end - dt.timedelta(days=random.randint(30, 90))
            
            assignments.append({
                "AssignmentID": assign_id,
                "AssetID": asset_id,
                "EmployeeID": emp_id,
                "AssignedAt": assigned_at.isoformat(),
                "DueReturnDate": due.isoformat() if due else "",
                "ReturnedAt": "",
                "ConditionAtAssign": "Good",
                "ConditionAtReturn": "",
                "AssignedByID": assigned_by,
                "ReceivedByID": "",
                "Notes": "",
                "CreatedAt": assigned_at.isoformat(),
                "UpdatedAt": assigned_at.isoformat(),
            })
            assign_id += 1

        asset_id += 1

    return assets, assignments

# ---------------------------------------------------------------------------
# DRIVER
# ---------------------------------------------------------------------------

def run():
    employees = _load_csv(Path("csv_out/Employees.csv"))
    assets, assigns = generate_assets(employees)
    write_csv("Assets", assets)
    write_csv("AssetAssignments", assigns)
    print("🎉  Assets and Assignments generated")


if __name__ == "__main__":
    run()
