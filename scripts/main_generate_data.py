#!/usr/bin/env python3
"""
main_generate_data.py
─────────────────────
Single entry point for the *new* modular data-generation pipeline.  Each stage
writes SQL files into `csv_out/` which can be executed later, or it may push
directly to a target database when we wire that up.

Run with
    python scripts/main_generate_data.py
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

MODULES_IN_ORDER = [
    ("scripts.seed_lookup_tables", {}),
    ("scripts.seed_org_structure", {}),
    # placeholders for upcoming stages – will be added incrementally
    ("scripts.seed_users", {}),
    ("scripts.seed_people", {}),
    ("scripts.seed_projects", {}),
    ("scripts.seed_timesheets", {}),
    ("scripts.seed_leave", {}),
    ("scripts.seed_assets", {}),
    ("scripts.seed_tickets", {}),
    ("scripts.seed_feedbacks", {}),
    ("scripts.seed_comments", {}),
    ("scripts.validators", {}),
]


def main() -> None:
    # Append the **parent** of the scripts/ directory so that the package
    # name 'scripts' can be resolved by importlib.
    scripts_dir = Path(__file__).resolve().parent
    project_root = scripts_dir.parent
    sys.path.append(str(project_root))

    for mod_name, kwargs in MODULES_IN_ORDER:
        print(f"▶️  Running {mod_name} …")
        mod = importlib.import_module(mod_name)
        run_fn = getattr(mod, "run", None)
        if run_fn is None:
            raise AttributeError(f"Module {mod_name} has no 'run()' function")
        run_fn(**kwargs)
    print("🎉  Data-generation stage completed (SQL files in csv_out/)")


if __name__ == "__main__":
    main()
