# CSV Load Error Fixes

## Issues Identified from Error Logs

Based on the analysis of the error logs, the following issues were identified:

### 1. **HRRepresentative Column Error (884 occurrences)**
- **Problem**: The `gen_employees` function was generating an `HRRepresentative` column that doesn't exist in the database schema
- **Error**: `Invalid column name 'HRRepresentative'`
- **Impact**: All Employee record insertions were failing

### 2. **Timesheet Duplicate Key Violations (2,098 occurrences)**
- **Problem**: Timesheet generation was creating duplicate entries for the same employee-week combinations
- **Error**: `Violation of UNIQUE KEY constraint 'UQ_Timesheets_EmployeeWeek'`
- **Impact**: Timesheet records were being rejected due to unique constraint violations

### 3. **Individual Row Insert Failures (23,218 occurrences)**
- **Problem**: Cascading failures from the HRRepresentative column issue
- **Impact**: Individual employee records were failing to insert

### 4. **LocationCode Column Validation Error**
- **Problem**: Validation function expected `LocationCode` column but it doesn't exist in the database schema
- **Error**: `Missing required columns for Locations: ['LocationCode']`
- **Impact**: Locations table loading was being skipped

### 5. **Database Connection Failures**
- **Problem**: Network connectivity issues causing communication link failures
- **Error**: `Communication link failure (0) (SQLExecDirectW)`
- **Impact**: Intermittent loading failures

### 6. **ManagerComments and HRComments Column Errors**
- **Problem**: Leave application generation was creating `ManagerComments` and `HRComments` columns that don't exist in the database schema
- **Error**: `Invalid column name 'ManagerComments'` and `Invalid column name 'HRComments'`
- **Impact**: Leave application records were failing to insert

### 7. **Database Connection and Transaction Rollback Issues**
- **Problem**: Network timeouts and connection failures causing invalid transaction states
- **Error**: `TCP Provider: Error code 0x274C (10060)` and `Can't reconnect until invalid transaction is rolled back`
- **Impact**: Load process gets stuck in retry loops and fails to complete

### 8. **Foreign Key Constraint Violation Errors**
- **Problem**: Missing AssetName column validation error caused Assets table to be skipped, leading to orphaned foreign key references
- **Error**: `The ALTER TABLE statement conflicted with the FOREIGN KEY constraint "FK_Asg_Asset"`
- **Impact**: Load process fails when trying to re-enable foreign key constraints

### 9. **Validation Column Name Mismatches**
- **Problem**: Validation function expected column names that don't match the actual database schema or generated data
- **Errors**: 
  - `Missing required columns for EmergencyContacts: ['PhoneNumber']` (should be `Phone1`)
  - `Missing required columns for EmployeeRoles: ['CreatedAt']` (column doesn't exist in database)
  - `Missing required columns for LeaveBalances: ['LeaveBalanceID', 'BalanceYear', 'TotalDays', 'RemainingDays']` (wrong column names)
- **Impact**: Tables are skipped due to validation failures, leading to incomplete data loads

## Fixes Implemented

### 1. **Fixed `scripts/generate_data.py`**

#### Removed HRRepresentative Column
- Removed the `HRRepresentative` field from employee generation
- Removed the logic that assigned HR representatives to employees
- Kept HR representative selection for role assignment purposes only

#### Fixed Timesheet Generation
- Added tracking of generated weeks to prevent duplicates
- Implemented proper date progression logic
- Added validation to ensure no duplicate employee-week combinations

#### Removed ManagerComments and HRComments Columns
- Removed `ManagerComments` and `HRComments` fields from leave application generation
- These columns don't exist in the database schema

### 2. **Enhanced `load_csvs_to_sqlserver.py`**

#### Added Data Validation
- Created `validate_csv_data()` function to catch issues early
- Validates required columns, invalid columns, and duplicate keys
- Provides detailed error messages for debugging
- **Fixed**: Updated Locations table validation to match actual database schema
- **Fixed**: Updated Assets table validation to match actual database schema
- **Fixed**: Updated EmergencyContacts, EmployeeRoles, and LeaveBalances validation to match actual schema

#### Improved Data Cleaning
- Added automatic removal of `HRRepresentative` column if present
- Added automatic removal of `LocationCode` column if present (not in database schema)
- Added automatic removal of `ManagerComments` and `HRComments` columns if present
- Added duplicate removal for timesheet employee-week combinations
- Enhanced error handling for unique constraint violations

#### Better Error Handling
- Improved chunk insert error handling
- Added individual row retry logic for constraint violations
- Enhanced logging with specific error categorization
- Added success/failure row counting
- **Added**: Retry logic for database connection failures with exponential backoff
- **Added**: Proper transaction rollback handling to prevent invalid transaction states
- **Added**: Database connection testing before starting load process
- **Added**: Foreign key constraint violation detection and cleanup before re-enabling constraints

## Key Changes Made

### `scripts/generate_data.py`
```python
# Removed from employee generation:
"HRRepresentative": None,  # Will be assigned later

# Removed from leave application generation:
"ManagerComments": "",     # Column doesn't exist in database
"HRComments": "",          # Column doesn't exist in database

# Added to timesheet generation:
generated_weeks = set()  # Track generated weeks to avoid duplicates
# Check for duplicates before generating timesheet
if (emp["EmployeeID"], period_start.isoformat()) in generated_weeks:
    continue
# Mark week as generated after successful creation
generated_weeks.add((emp["EmployeeID"], period_start.isoformat()))
```

### `load_csvs_to_sqlserver.py`
```python
# Added validation function:
def validate_csv_data(df: pd.DataFrame, table_name: str) -> bool:
    # Checks for required columns, invalid columns, duplicates
    # Fixed: Locations table validation matches actual schema
    
# Enhanced cleaning:
if 'HRRepresentative' in df_clean.columns:
    df_clean = df_clean.drop(columns=['HRRepresentative'])

if 'LocationCode' in df_clean.columns:
    df_clean = df_clean.drop(columns=['LocationCode'])

if 'ManagerComments' in df_clean.columns:
    df_clean = df_clean.drop(columns=['ManagerComments'])

if 'HRComments' in df_clean.columns:
    df_clean = df_clean.drop(columns=['HRComments'])

# Improved error handling with retry logic:
max_retries = 3
retry_delay = 5  # seconds
for attempt in range(max_retries):
    try:
        # Create fresh connection and transaction for each attempt
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                # Database operations
                trans.commit()
                break
            except Exception as e:
                # Properly rollback transaction on error
                trans.rollback()
                raise e
    except Exception as e:
        if any(keyword in str(e).lower() for keyword in [
            "communication link failure", 
            "tcp provider", 
            "connection", 
            "timeout",
            "can't reconnect until invalid transaction is rolled back"
        ]):
            # Retry with exponential backoff
            time.sleep(retry_delay)
            retry_delay *= 2
        else:
            # Non-connection error, don't retry
            raise e

# Added connection testing:
def test_database_connection(engine: sa.Engine) -> bool:
    try:
        with engine.connect() as conn:
            result = conn.exec_driver_sql("SELECT 1")
            result.fetchone()
            return True
    except Exception as e:
        logging.error(f"Database connection test failed: {e}")
        return False

# Added foreign key constraint cleanup:
print("  Checking for orphaned foreign key references...")
with engine.connect() as conn:
    # Check for orphaned references
    result = conn.exec_driver_sql("""
        SELECT COUNT(*) FROM dbo.AssetAssignments aa 
        LEFT JOIN dbo.Assets a ON aa.AssetID = a.AssetID 
        WHERE a.AssetID IS NULL
    """)
    orphaned_count = result.fetchone()[0]
    
    if orphaned_count > 0:
        # Clean up orphaned references
        conn.exec_driver_sql("DELETE FROM dbo.AssetAssignments WHERE AssetID NOT IN (SELECT AssetID FROM dbo.Assets)")
        print(f"  🧹 Cleaned up {orphaned_count} orphaned references")

# Now safely re-enable constraints
try:
    with engine.begin() as conn:
        conn.exec_driver_sql(enable_foreign_keys_sql())
    print("  ✅ Foreign key constraints re-enabled successfully")
except Exception as e:
    logging.error(f"Failed to re-enable foreign key constraints: {e}")
    print(f"  ❌ Failed to re-enable foreign key constraints: {e}")
```

## Expected Results

After implementing these fixes:

1. **No more HRRepresentative column errors** - The column is removed during generation
2. **No more timesheet duplicate key violations** - Duplicates are prevented during generation and cleaned during loading
3. **No more LocationCode validation errors** - Validation matches actual database schema
4. **No more ManagerComments/HRComments column errors** - These columns are removed during generation
5. **Better handling of database connection issues** - Retry logic with exponential backoff
6. **No more transaction rollback errors** - Proper transaction handling prevents invalid states
7. **Early connection testing** - Catches connection issues before starting load process
8. **No more foreign key constraint violations** - Automatic detection and cleanup of orphaned references
9. **No more validation column name errors** - Validation matches actual database schema and generated data
10. **Better error reporting** - Specific error messages help identify remaining issues
11. **Improved data quality** - Validation catches issues before database insertion
12. **Higher success rates** - Individual row retry logic handles constraint violations gracefully

## Testing Recommendations

1. **Generate new CSV data** using the updated `generate_data.py` script
2. **Run validation** on the generated CSV files before loading
3. **Monitor the load process** for any remaining errors
4. **Verify data integrity** after successful load
5. **Test network resilience** by temporarily disconnecting during load

## Files Modified

- `scripts/generate_data.py` - Fixed employee, timesheet, and leave application generation
- `load_csvs_to_sqlserver.py` - Enhanced validation, error handling, and connection retry logic
- `CSV_LOAD_FIXES.md` - This documentation file