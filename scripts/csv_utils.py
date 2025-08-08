#!/usr/bin/env python3
"""Light-weight CSV writer shared by seeder modules."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Dict

_OUT_DIR = Path("csv_out")
_OUT_DIR.mkdir(exist_ok=True)


def write_csv(filename_no_ext: str, rows: List[Dict]) -> None:
    """Write *rows* (list of dicts) to `csv_out/<filename_no_ext>.csv`.

    The header is the union of all dict keys; missing values in a row are
    written as blank strings.
    """
    if not rows:
        print(f"⚠️  write_csv: no rows for {filename_no_ext}; skipping file.")
        return

    fieldnames = sorted({k for row in rows for k in row.keys()})
    path = _OUT_DIR / f"{filename_no_ext}.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})
    print(f"✅  CSV written → {path}  ({len(rows)} rows)")
