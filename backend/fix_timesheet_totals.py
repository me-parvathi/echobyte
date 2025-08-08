#!/usr/bin/env python3
"""
Script to fix timesheet total hours by recalculating them from timesheet details.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import get_database_url
from core.timesheet_utils import update_timesheet_total_hours
from api.timesheet import models

def fix_timesheet_totals():
    """Fix total hours for all timesheets by recalculating from details."""
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get all timesheets
        timesheets = db.query(models.Timesheet).all()
        print(f"Found {len(timesheets)} timesheets to update")
        
        updated_count = 0
        for timesheet in timesheets:
            old_total = timesheet.TotalHours
            update_timesheet_total_hours(db, timesheet.TimesheetID)
            db.refresh(timesheet)
            new_total = timesheet.TotalHours
            
            if old_total != new_total:
                print(f"Updated timesheet {timesheet.TimesheetID}: {old_total} -> {new_total} hours")
                updated_count += 1
        
        print(f"Updated {updated_count} timesheets")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_timesheet_totals() 