#!/usr/bin/env python3
"""
seed_tickets.py
───────────────
Produces three CSVs
    • Tickets.csv
    • TicketActivities.csv
    • TicketAttachments.csv

Highlights
• ~200 tickets; status distribution from ddl (Open, Assigned, In-Progress, …).
• Priority mix LOW 40 % / MED 35 % / HIGH 20 % / CRIT+URG 5 %.
• 35 % of tickets link to an asset (pick first open assignment; else asset only).
• Activities track status changes & assignments.
• 25 % tickets get a dummy attachment row.
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
Faker.seed(42)

TICKET_STATUSES = [
    "Open",
    "Assigned",
    "In-Progress",
    "Pending-User",
    "Pending-Vendor",
    "Resolved",
    "Closed",
    "Escalated",
    "Cancelled",
    "On-Hold",
]

_STATUS_FLOW = {
    "Open": ["Assigned"],
    "Assigned": ["In-Progress", "Pending-User"],
    "In-Progress": ["Resolved", "Pending-Vendor", "Escalated"],
    "Pending-User": ["In-Progress", "Resolved"],
    "Pending-Vendor": ["In-Progress", "Resolved"],
    "Escalated": ["Resolved"],
    "Resolved": ["Closed"],
}

PRIORITIES = [
    ("LOW", 0.4),
    ("MED", 0.35),
    ("HIGH", 0.2),
    ("CRIT", 0.03),
    ("URG", 0.02),
]

CATEGORY_ROOTS = [
    "Hardware Issues",
    "Software Issues",
    "Network & Connectivity",
    "Access & Permissions",
    "Email & Communication",
    "Security Issues",
    "Mobile Devices",
    "Printing & Scanning",
    "General IT Support",
]

TOTAL_TICKETS = 200

# ---------------------------------------------------------------------------

def _load_csv(path: Path) -> List[Dict]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _weighted_choice(weight_map):
    r = random.random()
    cum = 0.0
    for val, w in weight_map:
        cum += w
        if r <= cum:
            return val
    return weight_map[-1][0]

# ---------------------------------------------------------------------------

def generate_tickets(employees: List[Dict], assets: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    it_staff_ids = random.sample([int(e["EmployeeID"]) for e in employees], k=50)
    emp_ids = [int(e["EmployeeID"]) for e in employees if int(e["EmployeeID"]) not in it_staff_ids]

    # Simple category id mapping (1-9 roots same order)
    cat_id = {name: idx + 1 for idx, name in enumerate(CATEGORY_ROOTS)}

    tickets: List[Dict] = []
    activities: List[Dict] = []
    attachments: List[Dict] = []

    ticket_id = 1
    activity_id = 1
    attach_id = 1

    today = dt.datetime.utcnow()

    for _ in range(TOTAL_TICKETS):
        opened_by = random.choice(emp_ids)
        priority = _weighted_choice(PRIORITIES)
        status = _weighted_choice([(s, 1 / len(TICKET_STATUSES)) for s in TICKET_STATUSES])
        category = random.choice(CATEGORY_ROOTS)
        assigned_to = random.choice(it_staff_ids) if status in ("Assigned", "In-Progress", "Resolved", "Closed") else ""
        asset_id = ""
        if random.random() < 0.35:
            asset_id = random.choice(assets)["AssetID"]
        opened_at = today - dt.timedelta(days=random.randint(0, 180))
        tickets.append({
            "TicketID": ticket_id,
            "TicketNumber": f"TKT-2024-{ticket_id:03d}",
            "Subject": fake.sentence(nb_words=6),
            "Description": fake.paragraph(nb_sentences=3),
            "CategoryID": cat_id[category],
            "PriorityCode": priority,
            "StatusCode": status,
            "OpenedByID": opened_by,
            "AssignedToID": assigned_to,
            "EscalatedToID": "",
            "AssetID": asset_id,
            "OpenedAt": opened_at.isoformat(),
            "AssignedAt": (opened_at + dt.timedelta(hours=2)).isoformat() if assigned_to else "",
            "ResolvedAt": "",
            "ClosedAt": "",
            "DueDate": (opened_at + dt.timedelta(hours=72)).isoformat(),
            "CreatedAt": opened_at.isoformat(),
            "UpdatedAt": opened_at.isoformat(),
        })
        # Activity log – simple two-step: Open → current status
        activities.append({
            "ActivityID": activity_id,
            "TicketID": ticket_id,
            "ActivityType": "Status_Change",
            "PerformedByID": opened_by,
            "OldValue": "",
            "NewValue": "Open",
            "PerformedAt": opened_at.isoformat(),
        })
        activity_id += 1
        if status != "Open":
            activities.append({
                "ActivityID": activity_id,
                "TicketID": ticket_id,
                "ActivityType": "Status_Change",
                "PerformedByID": assigned_to or opened_by,
                "OldValue": "Open",
                "NewValue": status,
                "PerformedAt": (opened_at + dt.timedelta(hours=4)).isoformat(),
            })
            activity_id += 1
        # Attachment chance
        if random.random() < 0.25:
            attachments.append({
                "AttachmentID": attach_id,
                "TicketID": ticket_id,
                "FileName": "screenshot.png",
                "FilePath": f"/tickets/{ticket_id}/screenshot.png",
                "FileSize": random.randint(20_000, 200_000),
                "MimeType": "image/png",
                "UploadedByID": opened_by,
                "UploadedAt": (opened_at + dt.timedelta(minutes=15)).isoformat(),
            })
            attach_id += 1

        ticket_id += 1

    return tickets, activities, attachments

# ---------------------------------------------------------------------------


def run():
    employees = _load_csv(Path("csv_out/Employees.csv"))
    assets = _load_csv(Path("csv_out/Assets.csv"))
    tickets, acts, atts = generate_tickets(employees, assets)
    write_csv("Tickets", tickets)
    write_csv("TicketActivities", acts)
    write_csv("TicketAttachments", atts)
    print("🎉  Tickets, Activities, Attachments generated")


if __name__ == "__main__":
    run()
