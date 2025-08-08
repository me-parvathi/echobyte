#!/usr/bin/env python3
"""
seed_users.py
─────────────
Generates Users.csv with one row per future employee (default 870) so that
Employees.csv can reference them via FK `UserID`.

At this stage we do NOT yet know the employees' names; we create plausible
place-holder usernames / emails that will later be reconciled by `seed_people.py`.
The important thing is that `UserID` values are unique, stable and available
for FK reference.
"""
from __future__ import annotations

import uuid
import random
import hashlib
import datetime as dt
from typing import List, Dict

from faker import Faker

from scripts.data_utils import rand_past_datetime, ensure_created_before_updated
from scripts.csv_utils import write_csv

TOTAL_USERS = 870  # keep in sync with workforce size; parameterisable later
_PASSWORD_PLAIN = "P@ssw0rd!"  # same base pwd for everyone; hashed before storing

fake = Faker()
random.seed(42)
Faker.seed(42)


def _hash_pwd(pwd: str) -> str:
    return hashlib.sha256(pwd.encode("utf-8")).hexdigest()


def generate_users(n: int = TOTAL_USERS) -> Tuple[List[Dict], List[Dict]]:
    rows: List[Dict] = []
    usernames_seen: set[str] = set()

    pwd_rows: List[Dict] = []

    for i in range(n):
        user_id = str(uuid.uuid4())

        # Simple username pattern: first initial + lastname (unique check)
        first = fake.first_name()
        last = fake.last_name()
        base_username = f"{first[0].lower()}{last.lower()}"
        username = base_username
        suffix = 1
        while username in usernames_seen:
            suffix += 1
            username = f"{base_username}{suffix}"
        usernames_seen.add(username)

        email = f"{username}@example.com"

        created_at = rand_past_datetime()
        created_at, updated_at = ensure_created_before_updated(created_at)
        last_login = created_at + dt.timedelta(days=random.randint(1, 365))
        if last_login > dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc):
            last_login = None  # never logged in yet

        row = {
            "UserID": user_id,
            "Username": username,
            "Email": email,
            "HashedPassword": _hash_pwd(_PASSWORD_PLAIN),
            "IsActive": 1,
            "IsSuperuser": 1 if i == 0 else 0,  # make first user superuser (CEO)
            "LastLoginAt": last_login.isoformat() if last_login else "",
            "PasswordChangedAt": created_at.isoformat(),
            "CreatedAt": created_at.isoformat(),
            "UpdatedAt": updated_at.isoformat(),
        }
        rows.append(row)
        pwd_rows.append({
            "UserID": user_id,
            "Username": username,
            "PlainPassword": _PASSWORD_PLAIN,
        })
    return rows, pwd_rows


def run():
    users, passwords = generate_users()
    write_csv("Users", users)
    write_csv("UserPasswords", passwords)
    print("🎉  Users and Passwords generated")


if __name__ == "__main__":
    run()
