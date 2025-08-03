#!/usr/bin/env python3
"""
seed_comments.py
────────────────
Generates Comments.csv linked to LeaveApplications and Tickets.
• 20 % of leave applications get 2–4 comments.
• 40 % of tickets get 1–3 comments.
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

# ---------------------------------------------------------------------------

def _load(name: str) -> List[Dict]:
    with Path(f"csv_out/{name}.csv").open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

# ---------------------------------------------------------------------------

def run():
    leaves = _load("LeaveApplications")
    tickets = _load("Tickets")
    comments: List[Dict] = []
    cid = 1

    # Leave comments (20 %)
    for la in leaves:
        if random.random() > 0.20:
            continue
        num = random.randint(2, 4)
        for _ in range(num):
            comments.append({
                "CommentID": cid,
                "EntityType": "LeaveApplication",
                "EntityID": la["LeaveApplicationID"],
                "CommenterID": la["EmployeeID"],
                "CommenterRole": "Employee",
                "CommentText": fake.sentence(),
                "CreatedAt": dt.datetime.utcnow().isoformat(),
                "UpdatedAt": "",
                "IsEdited": 0,
                "IsActive": 1,
            })
            cid += 1

    # Ticket comments (40 %)
    for tk in tickets:
        if random.random() > 0.40:
            continue
        num = random.randint(1, 3)
        for _ in range(num):
            comments.append({
                "CommentID": cid,
                "EntityType": "Ticket",
                "EntityID": tk["TicketID"],
                "CommenterID": tk["OpenedByID"],
                "CommenterRole": "Employee",
                "CommentText": fake.sentence(),
                "CreatedAt": dt.datetime.utcnow().isoformat(),
                "UpdatedAt": "",
                "IsEdited": 0,
                "IsActive": 1,
            })
            cid += 1

    write_csv("Comments", comments)
    print("🎉  Comments generated")


if __name__ == "__main__":
    run()
