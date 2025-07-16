#!/usr/bin/env python3
"""
load_csvs_to_sqlserver.py
──────────────────────────────────────────────────────────────────
Loads every CSV produced by generate_fake_echobyte_data.py into a
SQL Server database that's running in a Docker container.

- Requires: pandas, sqlalchemy, pyodbc  (install via pip)
- Each CSV file name must match the target table (case-insensitive).
- Parent-before-child load order is hard-coded for FK safety.
- Existing table contents are truncated first.

Usage:
    python load_csvs_to_sqlserver.py --server localhost --port 1433 \
          --user sa --password 'YourStrong!Passw0rd' --database echobyte
"""

import argparse
import os
from pathlib import Path
import uuid

import pandas as pd
import sqlalchemy as sa
import pyodbc


# ─── Load order (parents first) ────────────────────────────────────────────
TABLE_ORDER = [
    "Locations",
    "Departments",
    "Teams",

    "Employees",
    "EmergencyContacts",
    "EmployeeRoles",

    "LeaveBalances",
    "LeaveApplications",

    "Timesheets",
    "TimesheetDetails",

    "Assets",
    "AssetAssignments",

    "EmployeeFeedbacks",
]


# ─── Helpers ───────────────────────────────────────────────────────────────
def identity_insert_sql(schema_table: str, on: bool) -> str:
    state = "ON" if on else "OFF"
    return f"SET IDENTITY_INSERT {schema_table} {state};"


def delete_sql(schema_table: str) -> str:
    return f"DELETE FROM {schema_table};"


def disable_foreign_keys_sql() -> str:
    return "EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT all'"


def enable_foreign_keys_sql() -> str:
    return "EXEC sp_MSforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT all'"


def clean_dataframe(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """
    Clean DataFrame to handle SQL Server constraints and data issues.
    """
    df_clean = df.copy()
    
    # Handle Assets table UNIQUE constraints
    if table_name.lower() == "assets":
        # For SerialNumber: Replace NaN/None with unique values
        if 'SerialNumber' in df_clean.columns:
            mask = df_clean['SerialNumber'].isna() | (df_clean['SerialNumber'] == '')
            for idx in df_clean[mask].index:
                df_clean.loc[idx, 'SerialNumber'] = f"SN-{uuid.uuid4().hex[:12].upper()}"
        
        # For MACAddress: Replace NaN/None with unique values only if the asset type needs it
        if 'MACAddress' in df_clean.columns:
            mask = df_clean['MACAddress'].isna() | (df_clean['MACAddress'] == '')
            for idx in df_clean[mask].index:
                # Only generate MAC addresses for devices that typically have them
                asset_type_id = df_clean.loc[idx, 'AssetTypeID'] if 'AssetTypeID' in df_clean.columns else None
                # Assuming asset types 1=Laptop, 6=Mobile Phone typically have MAC addresses
                if asset_type_id in [1, 6]:  # Adjust these IDs based on your AssetTypes
                    # Generate a fake MAC address
                    mac_parts = [f"{x:02x}" for x in [0x02] + [ord(x) for x in uuid.uuid4().hex[:5]]]
                    df_clean.loc[idx, 'MACAddress'] = ":".join(mac_parts)
                else:
                    # For other asset types, use a unique identifier
                    df_clean.loc[idx, 'MACAddress'] = f"MAC-{uuid.uuid4().hex[:12].upper()}"
    
    # Convert pandas NaN to None (SQL NULL)
    df_clean = df_clean.where(pd.notnull(df_clean), None)
    
    return df_clean


def stage_csv_to_sql(df: pd.DataFrame,
                     engine: sa.Engine,
                     schema_table: str,
                     preserve_identity: bool = False) -> None:
    """
    Fast-loads the DataFrame into SQL Server using smaller chunks to avoid parameter limits.
    """
    table_name = schema_table.split(".")[1]
    schema_name = schema_table.split(".")[0]
    
    # Clean the data first
    df_clean = clean_dataframe(df, table_name)
    
    # Calculate appropriate chunk size based on number of columns
    # SQL Server has a limit of ~2100 parameters, so we need to be conservative
    num_columns = len(df_clean.columns)
    max_chunk_size = max(1, min(1000, 2000 // num_columns))  # Conservative estimate
    
    with engine.begin() as conn:
        if preserve_identity:
            conn.exec_driver_sql(identity_insert_sql(schema_table, True))

        # Insert data in chunks
        for start_idx in range(0, len(df_clean), max_chunk_size):
            end_idx = min(start_idx + max_chunk_size, len(df_clean))
            chunk = df_clean.iloc[start_idx:end_idx]
            
            chunk.to_sql(
                name=table_name,
                schema=schema_name,
                con=conn,
                if_exists="append",
                index=False,
                method="multi"
            )

        if preserve_identity:
            conn.exec_driver_sql(identity_insert_sql(schema_table, False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_dir", default="csv_out",
                        help="Folder containing the CSV files")
    parser.add_argument("--server", required=True)
    parser.add_argument("--port",   default=1433, type=int)
    parser.add_argument("--user",   required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--database", required=True)
    args = parser.parse_args()

    # ODBC connection string (Driver 18 is the current official image default)
    connect_str = (
        f"mssql+pyodbc://{args.user}:{args.password}"
        f"@{args.server},{args.port}/{args.database}"
        "?driver=ODBC+Driver+18+for+SQL+Server"
        "&TrustServerCertificate=yes"
    )

    engine = sa.create_engine(connect_str, fast_executemany=True)

    csv_root = Path(args.csv_dir)
    if not csv_root.exists():
        raise SystemExit(f"CSV directory not found: {csv_root.resolve()}")

    print(f"Connecting to {args.server}:{args.port}/{args.database} …")
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT 1")
    print("Connection OK\n")

    # First, disable all foreign key constraints
    print("→ Disabling foreign key constraints...")
    with engine.begin() as conn:
        conn.exec_driver_sql(disable_foreign_keys_sql())

    # Clear all tables in reverse order (child tables first)
    print("→ Clearing existing data...")
    for table in reversed(TABLE_ORDER):
        csv_path = csv_root / f"{table}.csv"
        if csv_path.exists():
            schema_table = f"dbo.{table}"
            with engine.begin() as conn:
                conn.exec_driver_sql(delete_sql(schema_table))
            print(f"  Cleared {table}")

    # Load data in correct order (parent tables first)
    for table in TABLE_ORDER:
        csv_path = csv_root / f"{table}.csv"
        if not csv_path.exists():
            print(f"⚠️  Skipping {table}: CSV not found")
            continue

        print(f"→ Loading {table} …", end="", flush=True)
        df = pd.read_csv(csv_path)

        schema_table = f"dbo.{table}"

        # if the first column looks like an identity PK, switch IDENTITY_INSERT on
        preserve_identity = df.columns[0].lower().endswith("id")
        stage_csv_to_sql(df, engine, schema_table, preserve_identity)
        print(f" done ({len(df):,} rows).")

    # Re-enable foreign key constraints
    print("→ Re-enabling foreign key constraints...")
    with engine.begin() as conn:
        conn.exec_driver_sql(enable_foreign_keys_sql())

    print("\nAll tables populated successfully.")


if __name__ == "__main__":
    main()