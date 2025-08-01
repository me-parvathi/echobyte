#!/usr/bin/env python3
"""
Test script to demonstrate the new timesheet workflow functionality
"""

import requests
import json
from datetime import date, timedelta
from typing import List

# Base URL for the API
BASE_URL = "http://localhost:8000"

def get_week_dates(work_date: date) -> tuple[date, date]:
    """Calculate week start (Monday) and end (Sunday) for a given date"""
    days_since_monday = work_date.weekday()
    week_start = work_date - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end

def test_weekly_timesheet_creation():
    """Test creating a weekly timesheet with all details at once"""
    print("\n1. Testing Weekly Timesheet Creation")
    print("=" * 50)
    
    # Get current week dates
    today = date.today()
    week_start, week_end = get_week_dates(today)
    
    # Create weekly data
    weekly_data = {
        "EmployeeID": 1,  # Assuming employee 1 exists
        "WeekStartDate": week_start.isoformat(),
        "WeekEndDate": week_end.isoformat(),
        "Comments": "Weekly timesheet created via API",
        "details": [
            {
                "EmployeeID": 1,
                "WorkDate": (week_start + timedelta(days=0)).isoformat(),  # Monday
                "ProjectCode": "PROJ-001",
                "TaskDescription": "Feature development",
                "HoursWorked": 8.0,
                "IsOvertime": False
            },
            {
                "EmployeeID": 1,
                "WorkDate": (week_start + timedelta(days=1)).isoformat(),  # Tuesday
                "ProjectCode": "PROJ-001",
                "TaskDescription": "Bug fixes",
                "HoursWorked": 7.5,
                "IsOvertime": False
            },
            {
                "EmployeeID": 1,
                "WorkDate": (week_start + timedelta(days=2)).isoformat(),  # Wednesday
                "ProjectCode": "PROJ-002",
                "TaskDescription": "Code review",
                "HoursWorked": 6.0,
                "IsOvertime": False
            },
            {
                "EmployeeID": 1,
                "WorkDate": (week_start + timedelta(days=3)).isoformat(),  # Thursday
                "ProjectCode": "PROJ-001",
                "TaskDescription": "Testing",
                "HoursWorked": 8.5,
                "IsOvertime": True
            },
            {
                "EmployeeID": 1,
                "WorkDate": (week_start + timedelta(days=4)).isoformat(),  # Friday
                "ProjectCode": "PROJ-002",
                "TaskDescription": "Documentation",
                "HoursWorked": 4.0,
                "IsOvertime": False
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/timesheets/weekly",
            json=weekly_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Weekly timesheet created successfully!")
            print(f"Timesheet ID: {data['TimesheetID']}")
            print(f"Week: {data['WeekStartDate']} to {data['WeekEndDate']}")
            print(f"Total Hours: {data['TotalHours']}")
            print(f"Status: {data['StatusCode']}")
            return data['TimesheetID']
        else:
            print(f"❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error making request: {e}")
        return None

def test_daily_entry_creation():
    """Test creating individual daily entries"""
    print("\n2. Testing Daily Entry Creation")
    print("=" * 50)
    
    # Test creating entries for next week
    next_week_start, next_week_end = get_week_dates(date.today() + timedelta(days=7))
    
    daily_entries = [
        {
            "EmployeeID": 2,  # Different employee
            "WorkDate": (next_week_start + timedelta(days=0)).isoformat(),  # Monday
            "ProjectCode": "PROJ-003",
            "TaskDescription": "Daily entry test - Monday",
            "HoursWorked": 8.0,
            "IsOvertime": False
        },
        {
            "EmployeeID": 2,
            "WorkDate": (next_week_start + timedelta(days=1)).isoformat(),  # Tuesday
            "ProjectCode": "PROJ-003",
            "TaskDescription": "Daily entry test - Tuesday",
            "HoursWorked": 7.0,
            "IsOvertime": False
        },
        {
            "EmployeeID": 2,
            "WorkDate": (next_week_start + timedelta(days=2)).isoformat(),  # Wednesday
            "ProjectCode": "PROJ-004",
            "TaskDescription": "Daily entry test - Wednesday",
            "HoursWorked": 9.0,
            "IsOvertime": True
        }
    ]
    
    for i, entry in enumerate(daily_entries, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/api/timesheets/daily",
                json=entry,
                headers={"Content-Type": "application/json"}
            )
            print(f"Entry {i} - Status Code: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                print(f"✅ Daily entry created/updated successfully!")
                print(f"  Work Date: {data['WorkDate']}")
                print(f"  Hours: {data['HoursWorked']}")
                print(f"  Project: {data['ProjectCode']}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"Error making request: {e}")

def test_daily_entry_update():
    """Test updating an existing daily entry"""
    print("\n3. Testing Daily Entry Update")
    print("=" * 50)
    
    # Use the same date as one of the entries we just created
    next_week_start, _ = get_week_dates(date.today() + timedelta(days=7))
    work_date = next_week_start + timedelta(days=1)  # Tuesday
    
    update_data = {
        "EmployeeID": 2,
        "WorkDate": work_date.isoformat(),
        "ProjectCode": "PROJ-003-UPDATED",
        "TaskDescription": "Updated task description",
        "HoursWorked": 8.5,
        "IsOvertime": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/timesheets/daily",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Daily entry updated successfully!")
            print(f"  Work Date: {data['WorkDate']}")
            print(f"  Updated Hours: {data['HoursWorked']}")
            print(f"  Updated Project: {data['ProjectCode']}")
            print(f"  Updated Description: {data['TaskDescription']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"Error making request: {e}")

def test_get_daily_entry():
    """Test retrieving a daily entry"""
    print("\n4. Testing Get Daily Entry")
    print("=" * 50)
    
    # Get today's date
    today = date.today()
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/timesheets/employee/1/daily/{today.isoformat()}",
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Daily entry retrieved successfully!")
            print(f"  Work Date: {data['WorkDate']}")
            print(f"  Hours: {data['HoursWorked']}")
            print(f"  Project: {data['ProjectCode']}")
        elif response.status_code == 404:
            print("ℹ️ No daily entry found for this date (expected if no entry exists)")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"Error making request: {e}")

def test_get_weekly_timesheet():
    """Test retrieving a weekly timesheet"""
    print("\n5. Testing Get Weekly Timesheet")
    print("=" * 50)
    
    # Get current week start
    today = date.today()
    week_start, _ = get_week_dates(today)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/timesheets/employee/1/week/{week_start.isoformat()}",
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Weekly timesheet retrieved successfully!")
            print(f"  Timesheet ID: {data['TimesheetID']}")
            print(f"  Week: {data['WeekStartDate']} to {data['WeekEndDate']}")
            print(f"  Total Hours: {data['TotalHours']}")
            print(f"  Status: {data['StatusCode']}")
        elif response.status_code == 404:
            print("ℹ️ No weekly timesheet found for this week (expected if no timesheet exists)")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"Error making request: {e}")

def test_timesheet_submission(timesheet_id: int):
    """Test submitting a timesheet"""
    print("\n6. Testing Timesheet Submission")
    print("=" * 50)
    
    if not timesheet_id:
        print("⚠️ Skipping submission test - no timesheet ID available")
        return
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/timesheets/{timesheet_id}/submit",
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Timesheet submitted successfully!")
            print(f"  Status: {data['StatusCode']}")
            print(f"  Submitted At: {data['SubmittedAt']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"Error making request: {e}")

def test_list_timesheets():
    """Test listing timesheets"""
    print("\n7. Testing List Timesheets")
    print("=" * 50)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/timesheets/",
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Timesheets retrieved successfully!")
            print(f"  Total Count: {data['total_count']}")
            print(f"  Page: {data['page']}")
            print(f"  Items: {len(data['items'])}")
            
            if data['items']:
                print("  Sample timesheet:")
                sample = data['items'][0]
                print(f"    ID: {sample['TimesheetID']}")
                print(f"    Employee: {sample['EmployeeID']}")
                print(f"    Week: {sample['WeekStartDate']} to {sample['WeekEndDate']}")
                print(f"    Status: {sample['StatusCode']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"Error making request: {e}")

def main():
    """Run all tests"""
    print("Testing Timesheet Workflow Implementation")
    print("=" * 60)
    
    # Run tests
    timesheet_id = test_weekly_timesheet_creation()
    test_daily_entry_creation()
    test_daily_entry_update()
    test_get_daily_entry()
    test_get_weekly_timesheet()
    test_timesheet_submission(timesheet_id)
    test_list_timesheets()
    
    print("\n" + "=" * 60)
    print("Timesheet workflow testing completed!")

if __name__ == "__main__":
    main() 