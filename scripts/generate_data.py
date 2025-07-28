#!/usr/bin/env python3
"""
generate_fake_echobyte_data.py
────────────────────────────────────────────────────────────────────────────
Creates realistic, referential-integrity-safe CSVs for the July-2025
*echobyte* schema (see ddl.sql) and drops them in ./csv_out/.

Volumetrics (CFG defaults)
•  4  locations     •  ~14 departments (2-tier)   •  25-40 teams
•  800 employees    •  5 % terminated / 3 % inactive
•  8 years of leave balances (1 row / emp / type / year)
•  1 year weekly timesheets with daily details for all active staff
•  8 000 IT assets with realistic status / contracts / assignments
All numbers are tweakable via CFG.

Faker seed = 42 → deterministic output.
────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
import csv, os, random, datetime as dt, time
from collections import defaultdict
from pathlib import Path
import hashlib

import pandas as pd
from faker import Faker
from dateutil.relativedelta import relativedelta

# ────────────────────────────────
# DDL CONSTANTS - Match exact values from database/ddl.sql
# ────────────────────────────────

# AssetTypes from DDL (Identity starts at 1)
ASSET_TYPES = [
    {"AssetTypeID": 1, "AssetTypeName": "Laptop"},
    {"AssetTypeID": 2, "AssetTypeName": "Monitor"},
    {"AssetTypeID": 3, "AssetTypeName": "Keyboard"},
    {"AssetTypeID": 4, "AssetTypeName": "Mouse"},
    {"AssetTypeID": 5, "AssetTypeName": "Docking Station"},
    {"AssetTypeID": 6, "AssetTypeName": "Mobile Phone"},
    {"AssetTypeID": 7, "AssetTypeName": "Headset"},
]

# TicketCategories from DDL (Identity starts at 1)
TICKET_CATEGORIES = [
    # Parent Categories
    {"CategoryID": 1, "CategoryName": "Hardware Issues", "ParentCategoryID": None},
    {"CategoryID": 2, "CategoryName": "Software Issues", "ParentCategoryID": None},
    {"CategoryID": 3, "CategoryName": "Network & Connectivity", "ParentCategoryID": None},
    {"CategoryID": 4, "CategoryName": "Access & Permissions", "ParentCategoryID": None},
    {"CategoryID": 5, "CategoryName": "Email & Communication", "ParentCategoryID": None},
    {"CategoryID": 6, "CategoryName": "Security Issues", "ParentCategoryID": None},
    {"CategoryID": 7, "CategoryName": "Mobile Devices", "ParentCategoryID": None},
    {"CategoryID": 8, "CategoryName": "Printing & Scanning", "ParentCategoryID": None},
    {"CategoryID": 9, "CategoryName": "General IT Support", "ParentCategoryID": None},
    
    # Hardware Subcategories
    {"CategoryID": 10, "CategoryName": "Laptop Issues", "ParentCategoryID": 1},
    {"CategoryID": 11, "CategoryName": "Desktop Issues", "ParentCategoryID": 1},
    {"CategoryID": 12, "CategoryName": "Monitor Problems", "ParentCategoryID": 1},
    {"CategoryID": 13, "CategoryName": "Keyboard/Mouse Issues", "ParentCategoryID": 1},
    {"CategoryID": 14, "CategoryName": "Docking Station Problems", "ParentCategoryID": 1},
    {"CategoryID": 15, "CategoryName": "Hardware Replacement", "ParentCategoryID": 1},
    {"CategoryID": 16, "CategoryName": "Hardware Repair", "ParentCategoryID": 1},
    
    # Software Subcategories
    {"CategoryID": 17, "CategoryName": "Operating System Issues", "ParentCategoryID": 2},
    {"CategoryID": 18, "CategoryName": "Application Crashes", "ParentCategoryID": 2},
    {"CategoryID": 19, "CategoryName": "Software Installation", "ParentCategoryID": 2},
    {"CategoryID": 20, "CategoryName": "Software Updates", "ParentCategoryID": 2},
    {"CategoryID": 21, "CategoryName": "License Issues", "ParentCategoryID": 2},
    {"CategoryID": 22, "CategoryName": "Performance Issues", "ParentCategoryID": 2},
    {"CategoryID": 23, "CategoryName": "Compatibility Problems", "ParentCategoryID": 2},
    
    # Network Subcategories
    {"CategoryID": 24, "CategoryName": "WiFi Connectivity", "ParentCategoryID": 3},
    {"CategoryID": 25, "CategoryName": "VPN Issues", "ParentCategoryID": 3},
    {"CategoryID": 26, "CategoryName": "Internet Access", "ParentCategoryID": 3},
    {"CategoryID": 27, "CategoryName": "Network Printer Issues", "ParentCategoryID": 3},
    {"CategoryID": 28, "CategoryName": "Network Drive Access", "ParentCategoryID": 3},
    {"CategoryID": 29, "CategoryName": "Bandwidth Issues", "ParentCategoryID": 3},
    
    # Access Subcategories
    {"CategoryID": 30, "CategoryName": "Account Creation", "ParentCategoryID": 4},
    {"CategoryID": 31, "CategoryName": "Password Reset", "ParentCategoryID": 4},
    {"CategoryID": 32, "CategoryName": "Access Rights", "ParentCategoryID": 4},
    {"CategoryID": 33, "CategoryName": "Account Lockout", "ParentCategoryID": 4},
    {"CategoryID": 34, "CategoryName": "Multi-Factor Authentication", "ParentCategoryID": 4},
    {"CategoryID": 35, "CategoryName": "System Permissions", "ParentCategoryID": 4},
    
    # Email Subcategories
    {"CategoryID": 36, "CategoryName": "Email Access Issues", "ParentCategoryID": 5},
    {"CategoryID": 37, "CategoryName": "Email Configuration", "ParentCategoryID": 5},
    {"CategoryID": 38, "CategoryName": "Spam/Phishing", "ParentCategoryID": 5},
    {"CategoryID": 39, "CategoryName": "Email Storage", "ParentCategoryID": 5},
    {"CategoryID": 40, "CategoryName": "Calendar Issues", "ParentCategoryID": 5},
    {"CategoryID": 41, "CategoryName": "Email Client Problems", "ParentCategoryID": 5},
    
    # Security Subcategories
    {"CategoryID": 42, "CategoryName": "Malware/Virus Issues", "ParentCategoryID": 6},
    {"CategoryID": 43, "CategoryName": "Security Software", "ParentCategoryID": 6},
    {"CategoryID": 44, "CategoryName": "Data Breach Concerns", "ParentCategoryID": 6},
    {"CategoryID": 45, "CategoryName": "Compliance Issues", "ParentCategoryID": 6},
    {"CategoryID": 46, "CategoryName": "Security Training", "ParentCategoryID": 6},
    
    # Mobile Device Subcategories
    {"CategoryID": 47, "CategoryName": "Mobile Phone Issues", "ParentCategoryID": 7},
    {"CategoryID": 48, "CategoryName": "Tablet Problems", "ParentCategoryID": 7},
    {"CategoryID": 49, "CategoryName": "Mobile App Issues", "ParentCategoryID": 7},
    {"CategoryID": 50, "CategoryName": "Mobile Device Setup", "ParentCategoryID": 7},
    {"CategoryID": 51, "CategoryName": "Mobile Security", "ParentCategoryID": 7},
    
    # Printing Subcategories
    {"CategoryID": 52, "CategoryName": "Printer Setup", "ParentCategoryID": 8},
    {"CategoryID": 53, "CategoryName": "Print Quality Issues", "ParentCategoryID": 8},
    {"CategoryID": 54, "CategoryName": "Scanner Problems", "ParentCategoryID": 8},
    {"CategoryID": 55, "CategoryName": "Printer Network Issues", "ParentCategoryID": 8},
    {"CategoryID": 56, "CategoryName": "Printer Maintenance", "ParentCategoryID": 8},
    
    # General IT Subcategories
    {"CategoryID": 57, "CategoryName": "Training Requests", "ParentCategoryID": 9},
    {"CategoryID": 58, "CategoryName": "Documentation Requests", "ParentCategoryID": 9},
    {"CategoryID": 59, "CategoryName": "Equipment Requests", "ParentCategoryID": 9},
    {"CategoryID": 60, "CategoryName": "General Questions", "ParentCategoryID": 9},
    {"CategoryID": 61, "CategoryName": "System Maintenance", "ParentCategoryID": 9},
]

# TicketPriorities from DDL
TICKET_PRIORITIES = [
    {"PriorityCode": "LOW", "PriorityName": "Low Priority", "SLAHours": 72},
    {"PriorityCode": "MED", "PriorityName": "Medium Priority", "SLAHours": 24},
    {"PriorityCode": "HIGH", "PriorityName": "High Priority", "SLAHours": 4},
    {"PriorityCode": "CRIT", "PriorityName": "Critical", "SLAHours": 1},
    {"PriorityCode": "URG", "PriorityName": "Urgent", "SLAHours": 2},
]

# TicketStatuses from DDL
TICKET_STATUSES = [
    {"TicketStatusCode": "Open", "TicketStatusName": "Open - Awaiting Assignment"},
    {"TicketStatusCode": "Assigned", "TicketStatusName": "Assigned - Work in Progress"},
    {"TicketStatusCode": "In-Progress", "TicketStatusName": "In Progress - Being Worked On"},
    {"TicketStatusCode": "Pending-User", "TicketStatusName": "Pending User Response"},
    {"TicketStatusCode": "Pending-Vendor", "TicketStatusName": "Pending Vendor Response"},
    {"TicketStatusCode": "Resolved", "TicketStatusName": "Resolved - Issue Fixed"},
    {"TicketStatusCode": "Closed", "TicketStatusName": "Closed - Ticket Complete"},
    {"TicketStatusCode": "Escalated", "TicketStatusName": "Escalated - Manager Review"},
    {"TicketStatusCode": "Cancelled", "TicketStatusName": "Cancelled - No Longer Needed"},
    {"TicketStatusCode": "On-Hold", "TicketStatusName": "On Hold - Temporarily Suspended"},
]

# ────────────────────────────────
# CONFIGURATION
# ────────────────────────────────
CFG = {
    # housekeeping
    "seed":          42,
    "csv_out":       Path("csv_out"),

    # organisation shape
    "n_locations":   4,
    "dept_structure": [                # root → children
        ("Corporate", ["HR", "IT", "Finance", "Operations"]),
        ("Engineering", ["Platform", "Data", "QA"]),
        ("Product",    ["Design", "PM", "Research"]),
    ],
    "teams_per_dept": (1, 3),
    "n_employees":  870, #changeme - reduced for testing

    # HR representatives configuration
    "hr_representatives_pct": 1,    # 100% of employees will have HR representatives
    "hr_role_pct": 0.08,              # 8% of employees will have HR roles

    # status mixes (lookup PK → probability)
    "emp_type_mix": {                  # EmploymentTypes
        "Full-Time":  0.86,
        "Part-Time":  0.06,
        "Contract":   0.06,
        "Intern":     0.02,
    },
    "employment_active_pct": 0.92,     # others marked inactive
    "work_mode_mix": {
        "Remote":     0.55,
        "Hybrid":     0.30,
        "In-Person":  0.15,
    },
    "leave_type_years_back": 8,        # LeaveBalances horizon
    "leave_type_defaults": {           # LeaveTypes.LeaveCode → days/yr
        "VAC": 20, "SICK": 10, "PARENT": 90,
        "BEREAVE": 5, "UNPAID": 0,
    },
    # leave application status mix (LeaveApplicationStatuses)
    "leave_app_status_mix": {
        "Submitted":         0.15,
        "Manager-Approved":  0.70,
        "HR-Approved":       0.05,
        "Rejected":          0.10,
    },
    # timesheet status mix (TimesheetStatuses)
    "timesheet_status_mix": {
        "Submitted": 0.10,
        "Approved":  0.88,
        "Rejected":  0.02,
    },

    # IT assets
    "n_assets":        500, #changeme - reduced for testing
    "asset_status_mix": {
        "In-Stock":        0.25,
        "Available":       0.25,
        "Assigned":        0.35,
        "Maintenance":     0.10,
        "Decommissioning": 0.03,
        "Retired":         0.02,
    },
    "assignable_codes": {"In-Stock", "Available", "Assigned"},

    # timesheet realism
    "weeks_of_timesheets": 60, #changeme - reduced for testing
    "daily_hours_range": (7, 9),        # before break
    "break_range_min": 30,              # minutes
    "break_range_max": 75,

    # Ticket generation configuration
    "n_tickets": 200,  # Total number of tickets to generate - reduced for testing
    "tickets_per_month": (15, 70),  # Range of tickets per month
    "ticket_status_mix": {
        "Open": 0.15,
        "Assigned": 0.20,
        "In-Progress": 0.25,
        "Pending-User": 0.10,
        "Pending-Vendor": 0.05,
        "Resolved": 0.15,
        "Closed": 0.08,
        "Escalated": 0.01,
        "Cancelled": 0.01,
    },
    "ticket_priority_mix": {
        "LOW": 0.40,
        "MED": 0.35,
        "HIGH": 0.20,
        "CRIT": 0.03,
        "URG": 0.02,
    },
    "asset_related_ticket_pct": 0.35,  # Percentage of tickets related to assets
    "escalation_pct": 0.08,  # Percentage of tickets that get escalated

    # Comment generation configuration
    "leave_comments_pct": 0.20,  # 20% of leave applications will have comments
    "leave_comments_per_app": (2, 5),  # Range of comments per leave application
    "ticket_comments_per_ticket": (2, 5),  # Range of comments per ticket (100% of tickets)
    "ticket_assignment_hours": 48,  # All tickets assigned within 48 hours
    "attachment_pct": 0.25,  # Percentage of tickets with attachments
}

# ────────────────────────────────
# SETUP
# ────────────────────────────────
fake = Faker()
random.seed(CFG["seed"])
Faker.seed(CFG["seed"])

CFG["csv_out"].mkdir(exist_ok=True)

# Performance tracking
def log_performance(operation: str, start_time: float):
    """Log performance metrics for operations"""
    elapsed = time.time() - start_time
    print(f"⏱️  {operation}: {elapsed:.2f}s")

def log_progress(current: int, total: int, operation: str):
    """Log progress for long-running operations"""
    if total > 0:
        percentage = (current / total) * 100
        print(f"📊 {operation}: {current}/{total} ({percentage:.1f}%)")
    else:
        print(f"📊 {operation}: {current} items processed")

# ────────────────────────────────
# Ticket Generation Libraries
# ────────────────────────────────

# Technical content for realistic ticket generation
TECHNICAL_CONTENT = {
    "software_versions": [
        "Windows 11 Pro 22H2", "Windows 10 Pro 21H2", "macOS Ventura 13.2.1", 
        "macOS Monterey 12.6.1", "Ubuntu 22.04 LTS", "Ubuntu 20.04 LTS",
        "Office 365", "Microsoft Office 2021", "Adobe Creative Suite 2023", 
        "Adobe Creative Suite 2022", "Chrome 120.0.6099.109", "Firefox 121.0",
        "Edge 120.0.2210.91", "Safari 17.2", "Outlook 2021", "Teams 1.7.00.6058"
    ],
    "error_messages": [
        "ERROR 0x80070002: The system cannot find the file specified",
        "BSOD: SYSTEM_SERVICE_EXCEPTION (win32kfull.sys)",
        "Application Error: The application was unable to start correctly (0xc000007b)",
        "Network Error: DNS_PROBE_FINISHED_NXDOMAIN",
        "ERROR 0x80070057: The parameter is incorrect",
        "BSOD: MEMORY_MANAGEMENT",
        "ERROR 0x80070005: Access is denied",
        "Network Error: ERR_CONNECTION_TIMED_OUT",
        "ERROR 0x8007000E: Not enough storage is available to complete this operation",
        "BSOD: PAGE_FAULT_IN_NONPAGED_AREA"
    ],
    "troubleshooting_steps": [
        "Restarted the device multiple times",
        "Cleared browser cache and cookies",
        "Ran Windows troubleshooter",
        "Updated device drivers",
        "Checked network cable connections",
        "Reset network adapter settings",
        "Uninstalled and reinstalled the application",
        "Checked Windows updates",
        "Ran system file checker (sfc /scannow)",
        "Cleared temporary files",
        "Reset password and cleared saved credentials",
        "Checked antivirus software settings"
    ],
    "hardware_models": [
        "Dell Latitude 5520", "Dell Latitude 7420", "Dell Precision 5560",
        "MacBook Pro 2021", "MacBook Pro 2022", "MacBook Air M1",
        "ThinkPad X1 Carbon", "ThinkPad T14", "ThinkPad P15",
        "HP EliteBook 840", "HP ProBook 450", "HP ZBook Studio"
    ],
    "network_issues": [
        "WiFi connection drops intermittently",
        "Cannot connect to corporate VPN",
        "Slow internet speed in specific areas",
        "Network printer not responding",
        "Cannot access shared network drives",
        "DNS resolution failures",
        "IP address conflicts",
        "Network adapter not recognized"
    ]
}

# ────────────────────────────────
# COMMENT TEMPLATES
# ────────────────────────────────
LEAVE_COMMENT_TEMPLATES = {
    "Employee": {
        "Submitted": [
            "Please approve my leave request for {days} days.",
            "I need to take time off for {reason}.",
            "Requesting approval for my planned leave.",
            "Please review my leave application.",
            "I've submitted my leave request as discussed."
        ],
        "FollowUp": [
            "Just following up on my leave request.",
            "Any updates on my leave approval?",
            "Please let me know if you need any additional information.",
            "I'm available for any questions about my leave request.",
            "Checking the status of my leave application."
        ],
        "Clarification": [
            "I can provide additional details if needed.",
            "Let me know if you need any clarification.",
            "I'm flexible with the dates if there are any conflicts.",
            "I'll ensure my work is covered during my absence.",
            "Please let me know if you need any documentation."
        ]
    },
    "Manager": {
        "Approval": [
            "Approved. Please ensure your work is covered.",
            "Leave approved. Have a great time!",
            "Approved. Make sure to hand over any pending tasks.",
            "Your leave request has been approved.",
            "Approved. Please update your out-of-office message."
        ],
        "Rejection": [
            "Unable to approve due to project deadlines.",
            "Please reschedule - team has important deliverables.",
            "Rejected due to insufficient coverage.",
            "Cannot approve at this time due to workload.",
            "Please discuss with me before resubmitting."
        ],
        "Questions": [
            "Who will cover your responsibilities?",
            "Can you provide more details about the reason?",
            "Is this leave urgent or can it be rescheduled?",
            "Have you discussed this with your team?",
            "What's the impact on current projects?"
        ]
    },
    "HR": {
        "Policy": [
            "Your leave request complies with company policy.",
            "Please note the leave policy requirements.",
            "Your leave balance has been verified.",
            "Approved per HR guidelines.",
            "Leave processed according to company policy."
        ],
        "Final": [
            "Final approval granted by HR.",
            "Leave request fully approved.",
            "HR approval completed.",
            "Your leave has been officially approved.",
            "Leave processed and confirmed."
        ]
    }
}

TICKET_COMMENT_TEMPLATES = {
    "Employee": {
        "Initial": [
            "I'm experiencing {issue} with my {device}.",
            "Having trouble with {issue}. Can you help?",
            "Need assistance with {issue}.",
            "Please help me resolve this {issue}.",
            "I've been having problems with {issue}."
        ],
        "FollowUp": [
            "Any updates on this ticket?",
            "Following up on my support request.",
            "Is there any progress on this issue?",
            "Please let me know when this will be resolved.",
            "Checking the status of my ticket."
        ],
        "Additional": [
            "I can provide more details if needed.",
            "Let me know if you need additional information.",
            "I'm available for remote assistance.",
            "Please contact me if you need to access my system.",
            "I can provide screenshots if that would help."
        ]
    },
    "IT Support": {
        "Initial": [
            "I've received your ticket and will investigate.",
            "Looking into this issue now.",
            "I'll start working on this right away.",
            "Received your request. Investigating the problem.",
            "I'm on it. Let me check the system."
        ],
        "Update": [
            "I've identified the issue and working on a fix.",
            "Found the problem. Implementing solution now.",
            "Update: I'm currently troubleshooting this.",
            "Making progress on this issue.",
            "I've found the root cause and fixing it."
        ],
        "Resolution": [
            "This should now be resolved. Please test.",
            "Issue fixed. Let me know if you need anything else.",
            "Problem resolved. Please confirm it's working.",
            "Fixed the issue. You should be good to go.",
            "Resolution complete. Please verify the fix."
        ],
        "Escalation": [
            "This requires escalation to senior support.",
            "Escalating to the appropriate team.",
            "This issue needs specialist attention.",
            "I'm escalating this to our senior technician.",
            "This requires escalation due to complexity."
        ]
    },
    "Manager": {
        "Escalation": [
            "This has been escalated for priority handling.",
            "Escalating due to business impact.",
            "This requires immediate attention.",
            "Escalated for urgent resolution.",
            "This issue has been prioritized."
        ]
    }
}

# Ticket templates for realistic content generation
TICKET_TEMPLATES = {
    "Laptop Issues": {
        "subjects": [
            "Laptop {device} won't {action} after {event}",
            "Unable to {action} on {device} - {symptom}",
            "{device} {symptom} when {action}",
            "{device} {symptom} - urgent assistance needed",
            "Hardware issue with {device}: {symptom}"
        ],
        "descriptions": [
            "My {device} (Model: {model}) started {symptom} after {event}. "
            "I've tried {troubleshooting_step} but the issue persists. "
            "This is affecting my ability to {business_impact}.",
            
            "Device: {device}\nModel: {model}\nIssue: {symptom}\n"
            "When it happens: {trigger}\nImpact: {business_impact}\n"
            "Steps taken: {troubleshooting_steps}",
            
            "I'm experiencing {symptom} with my {device}. "
            "The problem started {time_frame} and I've attempted {troubleshooting_steps}. "
            "This is preventing me from {business_impact}."
        ],
        "faker_fields": {
            "device": ["laptop", "Dell laptop", "MacBook", "ThinkPad"],
            "action": ["boot up", "start", "turn on", "connect to WiFi", "charge"],
            "event": ["Windows update", "power outage", "system restart", "software installation"],
            "symptom": ["freezing", "blue screen", "slow performance", "overheating", "battery not charging"],
            "model": TECHNICAL_CONTENT["hardware_models"],
            "troubleshooting_step": TECHNICAL_CONTENT["troubleshooting_steps"][:6],
            "business_impact": ["complete my reports", "attend client meetings", "access critical files", "work remotely"],
            "trigger": ["opening multiple applications", "connecting to external monitor", "running intensive software"],
            "time_frame": ["yesterday", "this morning", "last week", "a few days ago"],
            "troubleshooting_steps": ["restarting the device", "checking power connections", "updating drivers"]
        }
    },
    "Software Issues": {
        "subjects": [
            "{application} keeps {symptom} when {action}",
            "Unable to {action} in {application} - {error}",
            "{application} {symptom} after {event}",
            "Software issue: {application} not working properly",
            "Need help with {application} - {symptom}"
        ],
        "descriptions": [
            "I'm having trouble with {application} (Version: {version}). "
            "The application {symptom} when I try to {action}. "
            "I've tried {troubleshooting_steps} but the problem continues.",
            
            "Application: {application}\nVersion: {version}\nIssue: {symptom}\n"
            "Error message: {error}\nSteps taken: {troubleshooting_steps}\n"
            "Impact: {business_impact}",
            
            "Since {event}, {application} has been {symptom}. "
            "I need this resolved quickly as it affects {business_impact}."
        ],
        "faker_fields": {
            "application": ["Outlook", "Teams", "Chrome", "Excel", "Word", "PowerPoint", "Adobe Photoshop", "Zoom"],
            "symptom": ["crashing", "freezing", "not responding", "showing error messages", "running slowly"],
            "action": ["opening attachments", "sending emails", "joining meetings", "saving files", "printing documents"],
            "error": TECHNICAL_CONTENT["error_messages"][:5],
            "event": ["the latest update", "yesterday's system restart", "installing new software"],
            "version": TECHNICAL_CONTENT["software_versions"][:8],
            "troubleshooting_steps": ["restarting the application", "clearing cache", "checking for updates"],
            "business_impact": ["my daily communication", "project deadlines", "client presentations", "team collaboration"]
        }
    },
    "Network & Connectivity": {
        "subjects": [
            "Cannot connect to {network_type} in {location}",
            "{network_issue} - need immediate assistance",
            "Network connectivity problem: {symptom}",
            "Unable to access {service} due to network issues",
            "WiFi connection {symptom} in {location}"
        ],
        "descriptions": [
            "I'm experiencing {network_issue} in {location}. "
            "This started {time_frame} and I've tried {troubleshooting_steps}. "
            "This is preventing me from {business_impact}.",
            
            "Location: {location}\nIssue: {network_issue}\n"
            "Symptoms: {symptom}\nSteps taken: {troubleshooting_steps}\n"
            "Impact: {business_impact}",
            
            "Network connectivity is {symptom} in {location}. "
            "I need this resolved urgently as it affects {business_impact}."
        ],
        "faker_fields": {
            "network_type": ["WiFi", "VPN", "Ethernet", "corporate network"],
            "location": ["conference room", "office", "meeting room", "cafeteria", "lobby"],
            "network_issue": TECHNICAL_CONTENT["network_issues"],
            "symptom": ["dropping frequently", "very slow", "not connecting", "intermittent"],
            "service": ["email", "shared drives", "intranet", "cloud applications"],
            "time_frame": ["this morning", "yesterday", "last week"],
            "troubleshooting_steps": ["restarting router", "checking network settings", "trying different locations"],
            "business_impact": ["attending important meetings", "accessing critical files", "communicating with clients"]
        }
    },
    "Access & Permissions": {
        "subjects": [
            "Need {access_type} for {system}",
            "Cannot access {system} - {issue}",
            "Account {issue} - urgent assistance needed",
            "Permission denied for {resource}",
            "Need help with {access_type} in {system}"
        ],
        "descriptions": [
            "I'm trying to access {system} but getting {issue}. "
            "I need this resolved as it's preventing me from {business_impact}. "
            "I've tried {troubleshooting_steps}.",
            
            "System: {system}\nIssue: {issue}\n"
            "User: {user_info}\nImpact: {business_impact}\n"
            "Steps taken: {troubleshooting_steps}",
            
            "Since {time_frame}, I've been unable to {access_type} in {system}. "
            "This is affecting {business_impact}."
        ],
        "faker_fields": {
            "access_type": ["password reset", "account creation", "permission changes", "access rights"],
            "system": ["Active Directory", "email system", "shared drives", "CRM system", "ERP system"],
            "issue": ["password expired", "account locked", "access denied", "permission error"],
            "resource": ["shared folders", "databases", "applications", "reports"],
            "user_info": ["new employee", "existing user", "contractor"],
            "time_frame": ["yesterday", "this morning", "last week"],
            "troubleshooting_steps": ["trying different passwords", "contacting my manager", "checking email for reset links"],
            "business_impact": ["completing my work", "accessing project files", "submitting reports"]
        }
    }
}

# ────────────────────────────────
# Date Validation Helpers
# ────────────────────────────────
def generate_chronological_dates(base_date: dt.date, num_dates: int, min_days_between: int = 1) -> list[dt.datetime]:
    """
    Generate a list of chronologically ordered datetime objects starting from base_date.
    Each date is at least min_days_between days after the previous one.
    """
    dates = []
    current_date = dt.datetime.combine(base_date, dt.time(9, 0))  # Start at 9 AM
    
    for i in range(num_dates):
        # Add some random hours and minutes for realistic timestamps
        hours_offset = random.randint(0, 8)  # 9 AM to 5 PM
        minutes_offset = random.randint(0, 59)
        current_date += dt.timedelta(days=min_days_between, hours=hours_offset, minutes=minutes_offset)
        dates.append(current_date)
    
    return dates

def generate_employee_dates() -> dict:
    """
    Generate realistic employee dates ensuring proper chronological order.
    Returns a dict with hire_date, termination_date, created_at, updated_at
    """
    # Hire date: 1-10 years ago, not in future
    years_back = random.randint(1, 10)
    hire_date = dt.date.today() - relativedelta(years=years_back)
    
    # 5% chance of termination
    is_terminated = random.random() < 0.05
    termination_date = None
    
    if is_terminated:
        # Termination date: between hire date and today
        days_employed = random.randint(30, (dt.date.today() - hire_date).days)
        termination_date = hire_date + dt.timedelta(days=days_employed)
    
    # Created at: same as hire date or slightly before
    created_at = dt.datetime.combine(hire_date, dt.time(9, 0)) - dt.timedelta(days=random.randint(0, 7))
    
    # Updated at: after created_at, before today
    max_update_days = (dt.date.today() - hire_date).days
    update_days = random.randint(1, max_update_days)
    updated_at = created_at + dt.timedelta(days=update_days)
    
    return {
        "hire_date": hire_date,
        "termination_date": termination_date,
        "created_at": created_at,
        "updated_at": updated_at
    }

def generate_leave_application_dates(hire_date: dt.date, termination_date: dt.date = None) -> dict:
    """
    Generate leave application dates that are between hire_date and termination_date (if exists).
    Returns a dict with start_date, end_date, and all approval timestamps in proper order.
    """
    if termination_date is None:
        termination_date = dt.date.today()
    
    # Ensure we have at least 30 days between hire and termination
    min_start_days = 30
    max_start_days = (termination_date - hire_date).days - 30
    
    if max_start_days < min_start_days:
        # Employee hasn't been here long enough for leave
        return None
    
    # Start date: between hire_date + 30 days and termination_date - 30 days
    start_days = random.randint(min_start_days, max_start_days)
    start_date = hire_date + dt.timedelta(days=start_days)
    
    # Leave duration: 1-14 days
    leave_days = random.randint(1, 14)
    end_date = start_date + dt.timedelta(days=leave_days - 1)  # -1 because start_date counts as day 1
    
    # Ensure end_date doesn't exceed termination_date
    if end_date > termination_date:
        end_date = termination_date
        start_date = end_date - dt.timedelta(days=leave_days - 1)
    
    # Generate chronological timestamps
    base_date = start_date - dt.timedelta(days=random.randint(1, 7))  # Application submitted before start date
    dates = generate_chronological_dates(base_date, 5, 1)  # 5 timestamps: created, submitted, manager_approved, hr_approved, updated
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "created_at": dates[0],
        "submitted_at": dates[1],
        "manager_approval_at": dates[2],
        "hr_approval_at": dates[3],
        "updated_at": dates[4]
    }

def safe_date_range(start_date: dt.datetime, end_date: dt.datetime = None) -> int:
    """
    Safely calculate the number of days between two dates, ensuring positive range.
    """
    if end_date is None:
        end_date = dt.datetime.now()
    days_diff = (end_date - start_date).days
    return max(1, days_diff)

def generate_timesheet_dates(hire_date: dt.date, termination_date: dt.date = None) -> dict:
    """
    Generate timesheet dates that are between hire_date and termination_date (if exists).
    Returns a dict with week_start, week_end, created_at, submitted_at, approved_at, updated_at
    """
    if termination_date is None:
        termination_date = dt.date.today()
    
    # Find a valid week start date (Monday) between hire_date and termination_date
    # Start from hire_date + 1 week to allow for onboarding
    min_start = hire_date + dt.timedelta(days=7)
    max_start = termination_date - dt.timedelta(days=7)
    
    if min_start > max_start:
        return None
    
    # Find a Monday within the valid range
    days_to_add = random.randint(0, (max_start - min_start).days)
    week_start = min_start + dt.timedelta(days=days_to_add)
    
    # Adjust to Monday
    while week_start.weekday() != 0:  # 0 = Monday
        week_start += dt.timedelta(days=1)
    
    week_end = week_start + dt.timedelta(days=6)  # Sunday
    
    # Generate chronological timestamps
    base_date = week_start
    dates = generate_chronological_dates(base_date, 4, 1)  # 4 timestamps: created, submitted, approved, updated
    
    return {
        "week_start": week_start,
        "week_end": week_end,
        "created_at": dates[0],
        "submitted_at": dates[1],
        "approved_at": dates[2],
        "updated_at": dates[3]
    }

# ────────────────────────────────
# Helpers
# ────────────────────────────────
def weighted_choice(weight_map: dict[str, float]) -> str:
    r, acc = random.random(), 0.0
    for key, w in weight_map.items():
        acc += w
        if r < acc:
            return key
    return next(reversed(weight_map))

def wr(csv_name: str, rows: list[dict]) -> None:
    if not rows:
        return
    pd.DataFrame(rows).to_csv(
        CFG["csv_out"] / f"{csv_name}.csv",
        index=False,
        quoting=csv.QUOTE_MINIMAL,
    )
    print(f"  · {csv_name}.csv  ({len(rows):,} rows)")

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def today() -> dt.date:            # convenience
    return dt.date.today()

# ────────────────────────────────
# Ticket Generation Helpers
# ────────────────────────────────

def generate_ticket_number(ticket_id: int, year: int) -> str:
    """Generate ticket number in format TKT-YYYY-XXXX"""
    return f"TKT-{year}-{ticket_id:04d}"

def get_ticket_subject(category_name: str) -> str:
    """Generate realistic subject based on category"""
    if category_name in TICKET_TEMPLATES:
        template = random.choice(TICKET_TEMPLATES[category_name]["subjects"])
        fields = TICKET_TEMPLATES[category_name]["faker_fields"]
        
        # Replace placeholders with realistic values
        for field, values in fields.items():
            if f"{{{field}}}" in template:
                template = template.replace(f"{{{field}}}", random.choice(values))
        
        return template
    else:
        # Fallback for categories not in templates
        return fake.sentence(nb_words=6, variable_nb_words=True)

def get_ticket_description(category_name: str, priority: str) -> str:
    """Generate detailed description based on category and priority"""
    if category_name in TICKET_TEMPLATES:
        template = random.choice(TICKET_TEMPLATES[category_name]["descriptions"])
        fields = TICKET_TEMPLATES[category_name]["faker_fields"]
        
        # Replace placeholders with realistic values
        for field, values in fields.items():
            if f"{{{field}}}" in template:
                template = template.replace(f"{{{field}}}", random.choice(values))
        
        # Add urgency based on priority
        if priority in ["HIGH", "CRIT", "URG"]:
            template += "\n\nURGENT: This is affecting critical business operations and needs immediate attention."
        
        return template
    else:
        # Fallback description
        return fake.paragraph(nb_sentences=3)

def calculate_due_date(priority_code: str, opened_at: dt.datetime) -> dt.datetime:
    """Calculate due date based on priority SLA"""
    sla_hours = {
        "LOW": 72,    # 3 business days
        "MED": 24,    # 1 business day
        "HIGH": 4,    # 4 hours
        "CRIT": 1,    # 1 hour
        "URG": 2      # 2 hours
    }
    
    hours = sla_hours.get(priority_code, 24)
    due_date = opened_at + dt.timedelta(hours=hours)
    
    # Adjust for business hours (9 AM - 5 PM)
    if due_date.hour < 9:
        due_date = due_date.replace(hour=9, minute=0)
    elif due_date.hour >= 17:
        due_date = due_date + dt.timedelta(days=1)
        due_date = due_date.replace(hour=9, minute=0)
    
    return due_date

def determine_escalation_needed(priority: str, time_open: int) -> bool:
    """Determine if ticket should be escalated based on business rules"""
    if priority in ["CRIT", "URG"]:
        return time_open > 2  # Escalate after 2 hours for critical tickets
    elif priority == "HIGH":
        return time_open > 6  # Escalate after 6 hours for high priority
    elif priority == "MED":
        return time_open > 48  # Escalate after 2 days for medium priority
    else:
        return time_open > 168  # Escalate after 1 week for low priority

def get_it_staff(employees: list) -> list:
    """Get list of IT staff who can be assigned to tickets"""
    # For simplicity, use employees with ManagerID (managers) as IT staff
    # In a real scenario, you'd have specific IT roles/designations
    it_staff = [emp for emp in employees if emp.get("ManagerID") is not None]
    
    # If no managers found, use a subset of employees
    if not it_staff:
        it_staff = employees[:len(employees)//4]  # Use first 25% of employees
    
    return it_staff

def generate_business_hours_timestamp(start_date: dt.date, end_date: dt.date) -> dt.datetime:
    """Generate timestamp during business hours (9 AM - 5 PM)"""
    # Random date between start and end
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    random_date = start_date + dt.timedelta(days=random_days)
    
    # Random time during business hours (9 AM - 5 PM)
    hour = random.randint(9, 16)  # 9 AM to 4 PM (5 PM is 17:00)
    minute = random.randint(0, 59)
    
    return dt.datetime.combine(random_date, dt.time(hour, minute))

def generate_ticket_status_progression(opened_at: dt.datetime, priority: str) -> list:
    """Generate realistic status progression for a ticket"""
    statuses = []
    current_time = opened_at
    
    # Initial status: Open
    statuses.append({
        "status": "Open",
        "timestamp": current_time,
        "activity_type": "Status_Change",
        "details": "Ticket opened"
    })
    
    # Assignment (usually within 1-4 hours for business hours)
    if current_time.hour >= 9 and current_time.hour < 17:
        assignment_delay = random.randint(1, 4)
    else:
        # If opened outside business hours, assignment next business day
        assignment_delay = random.randint(9, 24)
    
    current_time += dt.timedelta(hours=assignment_delay)
    statuses.append({
        "status": "Assigned",
        "timestamp": current_time,
        "activity_type": "Assignment",
        "details": "Ticket assigned to IT staff"
    })
    
    # In-Progress (usually within 1-2 hours of assignment)
    current_time += dt.timedelta(hours=random.randint(1, 2))
    statuses.append({
        "status": "In-Progress",
        "timestamp": current_time,
        "activity_type": "Status_Change",
        "details": "Work started on ticket"
    })
    
    # Resolution time based on priority
    resolution_hours = {
        "LOW": random.randint(4, 24),
        "MED": random.randint(2, 8),
        "HIGH": random.randint(1, 4),
        "CRIT": random.randint(1, 2),
        "URG": random.randint(1, 3)
    }
    
    current_time += dt.timedelta(hours=resolution_hours.get(priority, 8))
    statuses.append({
        "status": "Resolved",
        "timestamp": current_time,
        "activity_type": "Status_Change",
        "details": "Issue resolved"
    })
    
    # Closed (usually within 1-2 hours of resolution)
    current_time += dt.timedelta(hours=random.randint(1, 2))
    statuses.append({
        "status": "Closed",
        "timestamp": current_time,
        "activity_type": "Status_Change",
        "details": "Ticket closed"
    })
    
    return statuses

NOW_ISO = dt.datetime.now().isoformat(sep=" ")

# ────────────────────────────────
# 1. Lookup helpers (IDs fixed by DDL seeds)
# ────────────────────────────────
GENDER_CODES  = ["M", "F", "O", "NB"]
EMP_TYPES     = ["Full-Time", "Part-Time", "Contract", "Intern"]
WORK_MODES    = ["Remote", "Hybrid", "In-Person"]

APPROVAL_STAT = ["Pending", "Approved", "Rejected"]
LA_STATUSES   = ["Draft", "Submitted", "Manager-Approved",
                 "HR-Approved", "Rejected", "Cancelled"]
TS_STATUSES   = ["Draft", "Submitted", "Approved", "Rejected"]

ASSET_STATUS_CODES = [
    "In-Stock", "Available", "Assigned",
    "Maintenance", "Decommissioning", "Retired",
]

# quick sanity to catch future DDL changes
assert set(CFG["emp_type_mix"]) == set(EMP_TYPES)
assert set(CFG["work_mode_mix"]) == set(WORK_MODES)
assert set(CFG["asset_status_mix"]) == set(ASSET_STATUS_CODES)

# ────────────────────────────────
# 2. Core structure
# ────────────────────────────────
def gen_locations(n: int):
    rows = []
    for lid in range(1, n + 1):
        city = fake.city()
        # Generate chronological dates for location
        created_at = dt.datetime.now() - dt.timedelta(days=random.randint(365, 1825))  # 1-5 years ago
        update_days = random.randint(1, safe_date_range(created_at))
        updated_at = created_at + dt.timedelta(days=update_days)
        
        rows.append({
            "LocationID":   lid,
            "LocationName": f"Office – {city}",
            "Address1":     fake.street_address(),
            "Address2":     "",
            "City":         city,
            "State":        fake.state(),
            "Country":      "USA",
            "PostalCode":   fake.postcode(),
            "Phone":        fake.phone_number(),
            "TimeZone":     "America/Los_Angeles",
            "IsActive":     1,
            "CreatedAt":    created_at.isoformat(sep=" "),
            "UpdatedAt":    updated_at.isoformat(sep=" "),
        })
    return rows

def gen_departments(structure, locations):
    rows, did = [], 1
    for root, children in structure:
        parent_id = did
        # Generate chronological dates for parent department
        created_at = dt.datetime.now() - dt.timedelta(days=random.randint(365, 1825))  # 1-5 years ago
        update_days = random.randint(1, safe_date_range(created_at))
        updated_at = created_at + dt.timedelta(days=update_days)
        
        rows.append({
            "DepartmentID":       parent_id,
            "DepartmentName":     root,
            "DepartmentCode":     f"{root[:3].upper()}{parent_id:02d}",
            "ParentDepartmentID": None,
            "LocationID":         random.choice(locations)["LocationID"],
            "IsActive":           1,
            "CreatedAt":          created_at.isoformat(sep=" "),
            "UpdatedAt":          updated_at.isoformat(sep=" "),
        })
        did += 1
        for ch in children:
            # Child departments created after parent
            child_created_at = created_at + dt.timedelta(days=random.randint(30, 180))
            update_days = random.randint(1, safe_date_range(child_created_at))
            child_updated_at = child_created_at + dt.timedelta(days=update_days)
            
            rows.append({
                "DepartmentID":   did,
                "DepartmentName": ch,
                "DepartmentCode": f"{ch[:3].upper()}{did:02d}",
                "ParentDepartmentID": parent_id,
                "LocationID":     random.choice(locations)["LocationID"],
                "IsActive":       1,
                "CreatedAt":      child_created_at.isoformat(sep=" "),
                "UpdatedAt":      child_updated_at.isoformat(sep=" "),
            })
            did += 1
    return rows

def gen_teams(departments, rng):
    rows, tid = [], 1
    for d in departments:
        for _ in range(random.randint(*rng)):
            code = f"T{tid:04d}"
            # Teams created after their departments
            dept_created = dt.datetime.fromisoformat(d["CreatedAt"])
            team_created_at = dept_created + dt.timedelta(days=random.randint(30, 180))
            update_days = random.randint(1, safe_date_range(team_created_at))
            team_updated_at = team_created_at + dt.timedelta(days=update_days)
            
            rows.append({
                "TeamID":             tid,
                "TeamName":           f"{d['DepartmentName']} Team {fake.bothify('??').upper()}",
                "TeamCode":           code,
                "DepartmentID":       d["DepartmentID"],
                "TeamLeadEmployeeID": None,   # filled later
                "IsActive":           1,
                "CreatedAt":          team_created_at.isoformat(sep=" "),
                "UpdatedAt":          team_updated_at.isoformat(sep=" "),
            })
            tid += 1
    return rows

# ────────────────────────────────
# 3. Employees & security
# ────────────────────────────────
def gen_users(employees):
    """Generate Users table data based on employee information"""
    rows = []
    password_data = []
    
    for emp in employees:
        # Create username from first and last name (max 100 chars)
        username = f"{emp['FirstName'].lower()}.{emp['LastName'].lower()}"
        if len(username) > 100:
            # Truncate to fit NVARCHAR(100)
            username = username[:100]
        
        # Ensure unique username by adding number if needed
        base_username = username
        counter = 1
        while any(u.get('Username') == username for u in rows):
            # Ensure counter doesn't make it exceed 100 chars
            suffix = str(counter)
            max_base_len = 100 - len(suffix)
            username = f"{base_username[:max_base_len]}{suffix}"
            counter += 1
        
        # Create email (should match CompanyEmail from employee, max 100 chars)
        email = emp['CompanyEmail']
        if len(email) > 100:
            # Truncate email to fit NVARCHAR(100)
            email = email[:100]
        
        # Generate a real password
        real_password = fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
        
        # Hash the password for database storage
        hashed_password = hash_password(real_password)
        
        # Store password data for Excel file
        password_data.append({
            "Email": email,
            "RealPassword": real_password,
            "HashedPassword": hashed_password,
            "EmployeeID": emp['EmployeeID'],
            "EmployeeName": f"{emp['FirstName']} {emp['LastName']}",
            "Username": username
        })
        
        # Generate chronological dates for user
        emp_created = dt.datetime.fromisoformat(emp["CreatedAt"])
        user_created_at = emp_created + dt.timedelta(days=random.randint(0, 7))  # User created same day or within a week
        update_days = random.randint(1, safe_date_range(user_created_at))
        user_updated_at = user_created_at + dt.timedelta(days=update_days)
        password_days = random.randint(1, safe_date_range(user_created_at))
        password_changed_at = user_created_at + dt.timedelta(days=password_days)
        
        # Set last login based on activity
        last_login = None
        if emp['IsActive'] and random.random() < 0.8:  # 80% of active users have logged in
            login_days = random.randint(1, safe_date_range(user_created_at))
            last_login = user_created_at + dt.timedelta(days=login_days)
            last_login = last_login.isoformat(sep=" ")
        
        rows.append({
            "UserID":           emp['UserID'],  # Use the same UserID from employee
            "Username":         username,
            "Email":            email,
            "HashedPassword":   hashed_password,
            "IsActive":         emp['IsActive'],
            "LastLoginAt":      last_login,
            "PasswordChangedAt": password_changed_at.isoformat(sep=" "),
            "CreatedAt":        user_created_at.isoformat(sep=" "),
            "UpdatedAt":        user_updated_at.isoformat(sep=" "),
        })
    
    return rows, password_data

def gen_designations():
    # designation rows already seeded in DDL; grab their IDs dynamically 1..10
    return list(range(1, 11))

def gen_employees(teams, locations, n):
    start_time = time.time()
    print(f"Generating {n} employees...")
    rows, eid = [], 1
    managers = {}
    hr_representatives = []
    active_pct = CFG["employment_active_pct"]

    # always one active manager per team
    for tm in teams:
        first, last = fake.first_name(), fake.last_name()
        etype  = weighted_choice(CFG["emp_type_mix"])
        wmode  = weighted_choice(CFG["work_mode_mix"])
        
        # Create unique UserID (max 50 chars)
        user_id = f"{first.lower()}.{last.lower()}"
        if len(user_id) > 50:
            # Truncate to fit NVARCHAR(50)
            user_id = user_id[:50]

        # Generate proper employee dates
        emp_dates = generate_employee_dates()
        
        rows.append({
            "EmployeeID":         eid,
            "EmployeeCode":       f"EMP{eid:05d}",
            "UserID":             user_id,
            "CompanyEmail":       f"{user_id}@echobyte.com",
            "FirstName":          first,
            "MiddleName": fake.first_name() if random.random() < 0.7 else None,
            "LastName":           last,
            "DateOfBirth":        (today() - relativedelta(years=random.randint(28, 58))).isoformat(),
            "GenderCode":         random.choice(GENDER_CODES),
            "MaritalStatus":      random.choice(["Single", "Married", ""]),
            "PersonalEmail":      fake.email(),
            "PersonalPhone":      fake.phone_number(),
            "WorkPhone":          fake.phone_number(),
            # inline address
            "Address1":           fake.street_address(),
            "Address2":           "",
            "City":               fake.city(),
            "State":              fake.state(),
            "Country":            "USA",
            "PostalCode":         fake.postcode(),

            "TeamID":             tm["TeamID"],
            "LocationID":         random.choice(locations)["LocationID"],
            "ManagerID":          None,
            "DesignationID":      random.choice(gen_designations()),
            "EmploymentTypeCode": etype,
            "WorkModeCode":       wmode,
            "HireDate":           emp_dates["hire_date"].isoformat(),
            "TerminationDate":    emp_dates["termination_date"].isoformat() if emp_dates["termination_date"] else None,
            "IsActive":           1 if emp_dates["termination_date"] is None else 0,
            "CreatedAt":          emp_dates["created_at"].isoformat(sep=" "),
            "UpdatedAt":          emp_dates["updated_at"].isoformat(sep=" "),
        })
        managers[tm["TeamID"]] = eid
        tm["TeamLeadEmployeeID"] = eid
        eid += 1

    remaining = n - len(rows)
    while remaining > 0:
        tm        = random.choice(teams)
        first, last = fake.first_name(), fake.last_name()
        active    = random.random() < active_pct
        etype     = weighted_choice(CFG["emp_type_mix"])
        wmode     = weighted_choice(CFG["work_mode_mix"])
        
        # Create unique UserID with number suffix to avoid conflicts (max 50 chars)
        base_user_id = f"{first.lower()}.{last.lower()}"
        if len(base_user_id) > 50:
            # Truncate to fit NVARCHAR(50)
            base_user_id = base_user_id[:50]
        
        user_id = base_user_id
        counter = 1
        while any(emp.get('UserID') == user_id for emp in rows):
            # Ensure counter doesn't make it exceed 50 chars
            suffix = str(counter)
            max_base_len = 50 - len(suffix)
            user_id = f"{base_user_id[:max_base_len]}{suffix}"
            counter += 1
        
        # Generate proper employee dates
        emp_dates = generate_employee_dates()
        
        rows.append({
            "EmployeeID":         eid,
            "EmployeeCode":       f"EMP{eid:05d}",
            "UserID":             user_id,
            "CompanyEmail":       f"{user_id}@echobyte.com",
            "FirstName":          first,
            "MiddleName":         "",
            "LastName":           last,
            "DateOfBirth":        (today() - relativedelta(years=random.randint(21, 58))).isoformat(),
            "GenderCode":         random.choice(GENDER_CODES),
            "MaritalStatus":      random.choice(["Single", "Married", ""]),
            "PersonalEmail":      fake.email(),
            "PersonalPhone":      fake.phone_number() if random.random() < 0.9 else None,
            "WorkPhone":          fake.phone_number() if active else None,

            "Address1":           fake.street_address(),
            "Address2":           "" if random.random() < 0.8 else fake.secondary_address(),
            "City":               fake.city(),
            "State":              fake.state(),
            "Country":            "USA",
            "PostalCode":         fake.postcode(),

            "TeamID":             tm["TeamID"],
            "LocationID":         random.choice(locations)["LocationID"],
            "ManagerID":          managers[tm["TeamID"]],
            "DesignationID":      random.choice(gen_designations()),
            "EmploymentTypeCode": etype,
            "WorkModeCode":       wmode,
            "HireDate":           emp_dates["hire_date"].isoformat(),
            "TerminationDate":    emp_dates["termination_date"].isoformat() if emp_dates["termination_date"] else None,
            "IsActive":           1 if emp_dates["termination_date"] is None else 0,
            "CreatedAt":          emp_dates["created_at"].isoformat(sep=" "),
            "UpdatedAt":          emp_dates["updated_at"].isoformat(sep=" "),
        })
        eid += 1
        remaining -= 1
    
    # Assign HR representatives to employees (for role assignment later)
    active_employees = [emp for emp in rows if emp["IsActive"] == 1]
    hr_emp_count = max(1, int(len(active_employees) * CFG["hr_role_pct"]))
    
    # Select HR representatives from active employees
    hr_representatives = random.sample(active_employees, min(hr_emp_count, len(active_employees)))
    
    log_performance("Employee generation", start_time)
    print(f"Generated {len(rows)} employees")
    return rows, managers, hr_representatives

def gen_emergency_contacts(employees):
    rows, cid = [], 1
    for emp in employees:
        if random.random() < 0.9:
            # Generate chronological dates for emergency contact
            emp_created = dt.datetime.fromisoformat(emp["CreatedAt"])
            contact_created_at = emp_created + dt.timedelta(days=random.randint(1, 30))
            update_days = random.randint(1, safe_date_range(contact_created_at))
            contact_updated_at = contact_created_at + dt.timedelta(days=update_days)
            
            rows.append({
                "ContactID":    cid,
                "EmployeeID":   emp["EmployeeID"],
                "ContactName":  fake.name(),
                "Relationship": random.choice(["Spouse", "Parent", "Sibling", "Friend"]),
                "Phone1":       fake.phone_number(),
                "Phone2":       fake.phone_number() if random.random() < 0.3 else None,
                "Email":        fake.email(),
                "Address":      fake.address().replace("\n", ", "),
                "IsPrimary":    1,
                "IsActive":     1,
                "CreatedAt":    contact_created_at.isoformat(sep=" "),
                "UpdatedAt":    contact_updated_at.isoformat(sep=" "),
            })
            cid += 1
    return rows

def gen_roles_and_emp_roles(employees, managers, hr_representatives):
    # Role IDs seeded in DDL: 1..11   (Employee, Manager, HR, Admin, CEO, ...)
    rows_roles = []        # not needed – already seeded
    rows_emp_roles, erid = [], 1
    
    # Create sets for quick lookup
    manager_ids = set(managers.values())
    hr_rep_ids = {emp["EmployeeID"] for emp in hr_representatives}
    
    for emp in employees:
        # Determine base role
        if emp["EmployeeID"] in manager_ids:
            base_role = 2  # Manager
        elif emp["EmployeeID"] in hr_rep_ids:
            base_role = 3  # HR (RoleID 3 from DDL)
        else:
            base_role = 1  # Employee
        
        # Generate chronological dates for employee role
        emp_created = dt.datetime.fromisoformat(emp["CreatedAt"])
        role_assigned_at = emp_created + dt.timedelta(days=random.randint(0, 7))  # Assigned same day or within a week
        
        rows_emp_roles.append({
            "EmployeeRoleID": erid,
            "EmployeeID":     emp["EmployeeID"],
            "RoleID":         base_role,
            "AssignedAt":     role_assigned_at.isoformat(sep=" "),
            "AssignedByID":   emp["ManagerID"] or emp["EmployeeID"],
            "IsActive":       1,
        })
        erid += 1
    return rows_roles, rows_emp_roles

# ────────────────────────────────
# 4. Leave management
# ────────────────────────────────
def gen_leave_types():
    # Use those seeded, but map code → ID (Identity starts at 1)
    return [
        (1, "VAC", 20),
        (2, "SICK", 10),
        (3, "PARENT", 90),
        (4, "BEREAVE", 5),
        (5, "UNPAID", 0),
    ]

def gen_leave_balances(employees):
    rows, bid = [], 1
    types = gen_leave_types()
    years_back = CFG["leave_type_years_back"]
    current_year = today().year
    for emp in employees:
        # Parse employee hire date
        hire_date = dt.datetime.fromisoformat(emp["HireDate"]).date()
        hire_year = hire_date.year
        
        for leave_id, code, days in types:
            for y in range(max(hire_year, current_year - years_back + 1), current_year + 1):
                used = round(random.uniform(0, min(days, days*0.6)), 1) if days else 0
                
                # Generate chronological dates for leave balance
                # Balance created at the start of the year or when employee was hired
                balance_date = dt.date(y, 1, 1)
                if balance_date < hire_date:
                    balance_date = hire_date
                
                created_at = dt.datetime.combine(balance_date, dt.time(9, 0))
                update_days = random.randint(1, safe_date_range(created_at))
                updated_at = created_at + dt.timedelta(days=update_days)
                
                rows.append({
                    "BalanceID":     bid,
                    "EmployeeID":    emp["EmployeeID"],
                    "LeaveTypeID":   leave_id,
                    "Year":          y,
                    "EntitledDays":  days,
                    "UsedDays":      used,
                    "CreatedAt":     created_at.isoformat(sep=" "),
                    "UpdatedAt":     updated_at.isoformat(sep=" "),
                })
                bid += 1
    return rows

def gen_leave_applications(employees, managers):
    start_time = time.time()
    print(f"Generating leave applications for {len(employees)} employees...")
    rows, lid = [], 1
    status_mix = CFG["leave_app_status_mix"]
    leave_types = gen_leave_types()
    
    # OPTIMIZATION: Pre-filter active employees
    active_employees = [emp for emp in employees if emp["IsActive"]]
    employees_with_leave = [emp for emp in active_employees if random.random() <= 0.3]
    print(f"  {len(employees_with_leave)} employees will have leave applications")
    
    for i, emp in enumerate(employees_with_leave):
        if i % 10 == 0:  # Progress indicator every 10 employees
            log_progress(i, len(employees_with_leave), "Leave applications")
            
        # Parse employee dates
        hire_date = dt.datetime.fromisoformat(emp["HireDate"]).date()
        termination_date = None
        if emp["TerminationDate"]:
            termination_date = dt.datetime.fromisoformat(emp["TerminationDate"]).date()
        
        for _ in range(random.randint(0, 3)):
            ltype = random.choice(leave_types)
            days = random.choice([1, 2, 3, 4, 5, 0.5])
            
            # Generate proper leave application dates
            leave_dates = generate_leave_application_dates(hire_date, termination_date)
            if leave_dates is None:
                continue  # Skip if employee hasn't been here long enough
                
            stat = weighted_choice(status_mix)
            
            # Set approval statuses and timestamps based on status
            manager_approval_status = None
            manager_approval_at = None
            hr_approver_id = None
            hr_approval_status = None
            hr_approval_at = None
            
            if stat in ("Manager-Approved", "HR-Approved"):
                manager_approval_status = "Approved"
                manager_approval_at = leave_dates["manager_approval_at"]
            elif stat == "Rejected":
                manager_approval_status = "Rejected"
                manager_approval_at = leave_dates["manager_approval_at"]
            
            if stat == "HR-Approved":
                hr_approver_id = emp["ManagerID"]  # Use manager as HR approver for simplicity
                hr_approval_status = "Approved"
                hr_approval_at = leave_dates["hr_approval_at"]
            
            rows.append({
                "LeaveApplicationID": lid,
                "EmployeeID":         emp["EmployeeID"],
                "LeaveTypeID":        ltype[0],
                "StartDate":          leave_dates["start_date"].isoformat(),
                "EndDate":            leave_dates["end_date"].isoformat(),
                "NumberOfDays":       days,
                "Reason":             random.choice(["Family trip", "Medical", "Personal", ""]),
                "StatusCode":         stat,
                "SubmittedAt":        leave_dates["submitted_at"].isoformat(sep=" "),
                "ManagerID":          emp["ManagerID"],
                "ManagerApprovalStatus": manager_approval_status,
                "ManagerApprovalAt":  manager_approval_at.isoformat(sep=" ") if manager_approval_at else None,
                "HRApproverID":       hr_approver_id,
                "HRApprovalStatus":   hr_approval_status,
                "HRApprovalAt":       hr_approval_at.isoformat(sep=" ") if hr_approval_at else None,
                "CreatedAt":          leave_dates["created_at"].isoformat(sep=" "),
                "UpdatedAt":          leave_dates["updated_at"].isoformat(sep=" "),
            })
            lid += 1
    
    log_performance("Leave application generation", start_time)
    print(f"Generated {len(rows)} leave applications")
    return rows

# ────────────────────────────────
# 5. Timesheets
# ────────────────────────────────
def gen_timesheets_and_details(employees):
    start_time = time.time()
    print(f"Generating timesheets for {len(employees)} employees...")
    ts_rows, det_rows = [], []
    tsid = detid = 1
    status_mix = CFG["timesheet_status_mix"]

    active_employees = [emp for emp in employees if emp["IsActive"]]
    print(f"  {len(active_employees)} active employees will have timesheets")
    
    for i, emp in enumerate(active_employees):
        if i % 10 == 0:  # Progress indicator every 10 employees
            log_progress(i, len(active_employees), "Employee timesheets")
            
        # Parse employee dates
        hire_date = dt.datetime.fromisoformat(emp["HireDate"]).date()
        termination_date = None
        if emp["TerminationDate"]:
            termination_date = dt.datetime.fromisoformat(emp["TerminationDate"]).date()
        
        # Generate timesheets for the employee's employment period
        current_date = hire_date + dt.timedelta(days=7)  # Start 1 week after hire
        weeks_generated = 0
        generated_weeks = set()  # Track generated weeks to avoid duplicates
        
        while current_date < (termination_date or dt.date.today()) and weeks_generated < CFG["weeks_of_timesheets"]:
            # Find next Monday
            while current_date.weekday() != 0:  # 0 = Monday
                current_date += dt.timedelta(days=1)
            
            # Check if we've already generated a timesheet for this week
            week_key = (emp["EmployeeID"], current_date.isoformat())
            if week_key in generated_weeks:
                current_date += dt.timedelta(days=7)
                continue
            
            # Generate proper timesheet dates
            timesheet_dates = generate_timesheet_dates(hire_date, termination_date)
            if timesheet_dates is None:
                break  # Skip if no valid timesheet period
                
            period_start = timesheet_dates["week_start"]
            period_end = timesheet_dates["week_end"]
            
            # Ensure we don't have duplicate weeks
            if (emp["EmployeeID"], period_start.isoformat()) in generated_weeks:
                current_date = period_end + dt.timedelta(days=1)
                continue
            
            status = weighted_choice(status_mix)
            weekly_hours = 0.0
            
            # Generate daily details
            for d in range(5):  # Monday to Friday
                work_date = period_start + dt.timedelta(days=d)
                start_hr  = random.randint(8, 10)
                worked    = random.uniform(*CFG["daily_hours_range"])
                break_m   = random.randint(CFG["break_range_min"], CFG["break_range_max"])
                net       = round(worked - break_m/60.0, 2)
                
                det_rows.append({
                    "DetailID":       detid,
                    "TimesheetID":    tsid,
                    "WorkDate":       work_date.isoformat(),
                    "ProjectCode":    None,
                    "TaskDescription": "Feature work" if random.random()<0.7 else "Bug fix",
                    "HoursWorked":    net,
                    "IsOvertime":     1 if net > 8 else 0,
                    "CreatedAt":      timesheet_dates["created_at"].isoformat(sep=" "),
                })
                detid          += 1
                weekly_hours   += net
            
            # Set approval details based on status
            approved_by_id = emp["ManagerID"] if status == "Approved" else None
            approved_at = timesheet_dates["approved_at"] if status == "Approved" else None
            
            ts_rows.append({
                "TimesheetID":   tsid,
                "EmployeeID":    emp["EmployeeID"],
                "WeekStartDate": period_start.isoformat(),
                "WeekEndDate":   period_end.isoformat(),
                "TotalHours":    round(weekly_hours, 2),
                "StatusCode":    status,
                "SubmittedAt":   timesheet_dates["submitted_at"].isoformat(sep=" "),
                "ApprovedByID":  approved_by_id,
                "ApprovedAt":    approved_at.isoformat(sep=" ") if approved_at else None,
                "Comments":      "",
                "CreatedAt":     timesheet_dates["created_at"].isoformat(sep=" "),
                "UpdatedAt":     timesheet_dates["updated_at"].isoformat(sep=" "),
            })
            
            # Mark this week as generated
            generated_weeks.add((emp["EmployeeID"], period_start.isoformat()))
            tsid += 1
            weeks_generated += 1
            
            # Move to next week
            current_date = period_end + dt.timedelta(days=1)
    
    log_performance("Timesheet generation", start_time)
    print(f"Generated {len(ts_rows)} timesheets and {len(det_rows)} timesheet details")
    return ts_rows, det_rows

# ────────────────────────────────
# 6. Assets
# ────────────────────────────────
LAPTOP_MODELS = ["Dell Latitude 7440", "MacBook Pro 14", "M3", "Lenovo ThinkPad X1"]
def gen_assets(asset_types, locations):
    rows, aid = [], 1
    for _ in range(CFG["n_assets"]):
        status = weighted_choice(CFG["asset_status_mix"])
        atype  = random.choice(asset_types)
        contract = random.random() < 0.25
        purchase = today() - relativedelta(months=random.randint(0, 60))
        
        # Generate chronological dates for asset
        created_at = dt.datetime.combine(purchase, dt.time(9, 0)) + dt.timedelta(days=random.randint(0, 30))
        # Ensure updated_at is after created_at and before now
        update_days = random.randint(1, safe_date_range(created_at))
        updated_at = created_at + dt.timedelta(days=update_days)
        
        rows.append({
            "AssetID":            aid,
            "AssetTag":           f"AS{aid:06d}",
            "SerialNumber":       fake.uuid4() if random.random()<0.9 else None,
            "MACAddress":         fake.mac_address() if atype["AssetTypeName"] in
                                                   ("Laptop", "Docking Station", "Monitor") else None,
            "AssetTypeID":        atype["AssetTypeID"],
            "AssetStatusCode":    status,
            "Model":              random.choice(LAPTOP_MODELS) if atype["AssetTypeName"]=="Laptop" else None,
            "Vendor":             random.choice(["Dell", "Apple", "Lenovo", "HP", ""]) ,
            "PurchaseDate":       purchase.isoformat(),
            "WarrantyEndDate":    (purchase + relativedelta(years=3)).isoformat(),
            "IsUnderContract":    1 if contract else 0,
            "ContractStartDate":  purchase.isoformat() if contract else None,
            "ContractExpiryDate": (purchase + relativedelta(years=3)).isoformat() if contract else None,
            "LocationID":         random.choice(locations)["LocationID"],
            "Notes":              "",
            "IsActive":           1,
            "CreatedAt":          created_at.isoformat(sep=" "),
            "UpdatedAt":          updated_at.isoformat(sep=" "),
        })
        aid += 1
    return rows
def gen_asset_assignments(assets, employees):
    start_time = time.time()
    print(f"Generating asset assignments...")
    rows, asid = [], 1

    # OPTIMIZATION: Use sets for O(1) lookups
    active_emp = [e for e in employees if e["IsActive"]]
    assignable_codes_set = CFG["assignable_codes"]  # Already a set

    # OPTIMIZATION: Pre-filter assignable assets
    assignable_assets = [
        a for a in assets
        if a["AssetStatusCode"] in assignable_codes_set
    ]
    print(f"  {len(assignable_assets)} assets eligible for assignment")

    # Optional defensive check
    valid_asset_ids = {a["AssetID"] for a in assets}

    for asset in assignable_assets:
        if random.random() > 0.5:
            continue  # skip some randomly

        emp = random.choice(active_emp)
        due = asset["ContractExpiryDate"]

        # ✅ Safely handle None
        if isinstance(due, str):
            due_dt = dt.datetime.fromisoformat(due).date()
            if due_dt < dt.date.today():
                continue  # skip expired assets

        # Extra safety: skip if asset ID doesn't exist
        if asset["AssetID"] not in valid_asset_ids:
            continue

        # Generate chronological dates for asset assignment
        asset_created = dt.datetime.fromisoformat(asset["CreatedAt"])
        emp_created = dt.datetime.fromisoformat(emp["CreatedAt"])
        
        # Assignment should be after both asset and employee were created
        assignment_start = max(asset_created, emp_created) + dt.timedelta(days=random.randint(30, 180))
        assignment_created_at = assignment_start
        update_days = random.randint(1, safe_date_range(assignment_start))
        assignment_updated_at = assignment_start + dt.timedelta(days=update_days)

        rows.append({
            "AssignmentID":      asid,
            "AssetID":           asset["AssetID"],
            "EmployeeID":        emp["EmployeeID"],
            "AssignedAt":        assignment_start.isoformat(sep=" "),
            "DueReturnDate":     due,
            "ReturnedAt":        None,
            "ConditionAtAssign": "Working",
            "ConditionAtReturn": None,
            "AssignedByID":      emp["ManagerID"] or emp["EmployeeID"],
            "ReceivedByID":      None,
            "Notes":             "",
            "CreatedAt":         assignment_created_at.isoformat(sep=" "),
            "UpdatedAt":         assignment_updated_at.isoformat(sep=" "),
        })

        asset["AssetStatusCode"] = "Assigned"
        asid += 1

    log_performance("Asset assignment generation", start_time)
    print(f"Generated {len(rows)} asset assignments")
    return rows




# ────────────────────────────────
# 7. Feedback
# ────────────────────────────────
def gen_feedbacks(employees, teams):
    rows, fid = [], 1

    # Build TeamID → DepartmentID map
    team_to_dept = {t["TeamID"]: t["DepartmentID"] for t in teams}

    for _ in range(random.randint(100, 200)):
        emp = random.choice(employees)
        team_id = emp["TeamID"]
        dept_id = team_to_dept.get(team_id)

        # Generate chronological dates for feedback
        emp_created = dt.datetime.fromisoformat(emp["CreatedAt"])
        feedback_days = random.randint(30, safe_date_range(emp_created))
        feedback_at = emp_created + dt.timedelta(days=feedback_days)

        rows.append({
            "FeedbackID":         fid,
            "FeedbackAt":         feedback_at.isoformat(sep=" "),
            "FeedbackTypeCode":   random.choice(["General", "Manager", "Department", "Other"]),
            "Category":           random.choice(["Process", "Culture", "Workload", ""]),
            "Subject":            random.choice(["Suggestion", "Issue", "Praise", ""]),
            "FeedbackText":       fake.paragraph(nb_sentences=5),
            "TargetManagerID":    emp["ManagerID"],
            "TargetDepartmentID": dept_id,
            "FeedbackHash":       fake.sha256(raw_output=False),
            "IsRead":             0,
            "ReadByID":           None,
            "ReadAt":             None,
        })
        fid += 1
    return rows


# ────────────────────────────────
# 8. Tickets
# ────────────────────────────────

def gen_tickets(employees, assets, categories):
    """Generate realistic tickets with proper relationships"""
    start_time = time.time()
    print(f"Generating {CFG['n_tickets']} tickets...")
    rows, tid = [], 1
    
    # OPTIMIZATION: Use sets for O(1) lookups
    it_staff = get_it_staff(employees)
    if not it_staff:
        it_staff = employees  # Fallback to all employees
    
    # OPTIMIZATION: Pre-filter managers and create sets for faster lookups
    managers = [emp for emp in employees if emp.get("ManagerID") is not None]
    manager_ids = {emp["EmployeeID"] for emp in managers}
    it_staff_ids = {emp["EmployeeID"] for emp in it_staff}
    
    # OPTIMIZATION: Pre-build asset assignment mapping for O(1) lookups
    employee_assets = {}
    for asset in assets:
        if asset.get("AssignedToID"):
            emp_id = asset["AssignedToID"]
            if emp_id not in employee_assets:
                employee_assets[emp_id] = []
            employee_assets[emp_id].append(asset["AssetID"])
    
    # Create category mapping (name to ID)
    category_map = {cat["CategoryName"]: cat["CategoryID"] for cat in categories}
    
    # Generate tickets over the past year
    start_date = dt.date.today() - dt.timedelta(days=365)
    end_date = dt.date.today()
    
    for i in range(CFG["n_tickets"]):
        if i % 50 == 0:  # Progress indicator every 50 tickets
            log_progress(i, CFG["n_tickets"], "Ticket generation")
            
        # Generate ticket timestamp during business hours
        opened_at = generate_business_hours_timestamp(start_date, end_date)
        
        # Select random employee to open ticket
        opened_by = random.choice(employees)
        
        # Select category and priority
        category_name = random.choice(list(TICKET_TEMPLATES.keys()))
        # Map template category names to actual category IDs
        if category_name == "Laptop Issues":
            category_id = 10  # Laptop Issues category ID
        elif category_name == "Software Issues":
            category_id = 2   # Software Issues category ID
        elif category_name == "Network & Connectivity":
            category_id = 3   # Network & Connectivity category ID
        elif category_name == "Access & Permissions":
            category_id = 4   # Access & Permissions category ID
        else:
            category_id = 1   # Default to Hardware Issues
        priority = weighted_choice(CFG["ticket_priority_mix"])
        
        # Generate subject and description
        subject = get_ticket_subject(category_name)
        description = get_ticket_description(category_name, priority)
        
        # OPTIMIZATION: Use pre-built asset mapping for O(1) lookup
        asset_id = None
        if random.random() < CFG["asset_related_ticket_pct"] and assets:
            # Select asset assigned to the employee using pre-built mapping
            emp_assets = employee_assets.get(opened_by["EmployeeID"], [])
            if emp_assets:
                asset_id = random.choice(emp_assets)
            else:
                # If no assets assigned to employee, randomly select any asset
                asset_id = random.choice(assets)["AssetID"]
        
        # Generate status progression
        status_progression = generate_ticket_status_progression(opened_at, priority)
        current_status = status_progression[-1]["status"]  # Use final status
        
        # Calculate timestamps
        assigned_at = None
        escalated_at = None
        resolved_at = None
        closed_at = None
        
        for status in status_progression:
            if status["status"] == "Assigned":
                assigned_at = status["timestamp"]
            elif status["status"] == "Escalated":
                escalated_at = status["timestamp"]
            elif status["status"] == "Resolved":
                resolved_at = status["timestamp"]
            elif status["status"] == "Closed":
                closed_at = status["timestamp"]
        
        # Determine assignment and escalation
        assigned_to_id = None
        escalated_to_id = None
        
        # Ensure all tickets are assigned within 48 hours
        if assigned_at:
            assigned_to_id = random.choice(it_staff)["EmployeeID"]
        else:
            # If not assigned in status progression, assign within 48 hours
            assigned_at = opened_at + dt.timedelta(hours=random.randint(1, CFG["ticket_assignment_hours"]))
            assigned_to_id = random.choice(it_staff)["EmployeeID"]
        
        if escalated_at and random.random() < CFG["escalation_pct"]:
            escalated_to_id = random.choice(managers)["EmployeeID"]
        
        # Calculate due date
        due_date = calculate_due_date(priority, opened_at)
        
        rows.append({
            "TicketID": tid,
            "TicketNumber": generate_ticket_number(tid, opened_at.year),
            "Subject": subject,
            "Description": description,
            "CategoryID": category_id,
            "PriorityCode": priority,
            "StatusCode": current_status,
            "OpenedByID": opened_by["EmployeeID"],
            "AssignedToID": assigned_to_id,
            "EscalatedToID": escalated_to_id,
            "AssetID": asset_id,
            "OpenedAt": opened_at.isoformat(sep=" "),
            "AssignedAt": assigned_at.isoformat(sep=" "),
            "EscalatedAt": escalated_at.isoformat(sep=" ") if escalated_at else None,
            "ResolvedAt": resolved_at.isoformat(sep=" ") if resolved_at else None,
            "ClosedAt": closed_at.isoformat(sep=" ") if closed_at else None,
            "DueDate": due_date.isoformat(sep=" "),
            "CreatedAt": opened_at.isoformat(sep=" "),
            "UpdatedAt": (closed_at or resolved_at or assigned_at or opened_at).isoformat(sep=" "),
        })
        
        tid += 1
    
    log_performance("Ticket generation", start_time)
    return rows

def gen_ticket_activities(tickets, employees):
    """Generate ticket activities with realistic timeline"""
    rows, aid = [], 1
    
    for ticket in tickets:
        # Generate status progression for this ticket
        opened_at = dt.datetime.fromisoformat(ticket["OpenedAt"])
        priority = ticket["PriorityCode"]
        status_progression = generate_ticket_status_progression(opened_at, priority)
        
        # Create activities for each status change
        for status in status_progression:
            # Determine who performed the action
            if status["activity_type"] == "Assignment":
                performed_by = ticket.get("AssignedToID") or random.choice(employees)["EmployeeID"]
            elif status["activity_type"] == "Escalation":
                performed_by = ticket.get("EscalatedToID") or random.choice(employees)["EmployeeID"]
            else:
                performed_by = random.choice(employees)["EmployeeID"]
            
            rows.append({
                "ActivityID": aid,
                "TicketID": ticket["TicketID"],
                "ActivityType": status["activity_type"],
                "PerformedByID": performed_by,
                "OldValue": None,  # Could be enhanced to track previous status
                "NewValue": status["status"],
                "ActivityDetails": status["details"],
                "PerformedAt": status["timestamp"].isoformat(sep=" "),
            })
            aid += 1
        
        # Add some additional activities (comments, updates)
        num_additional = random.randint(1, 3)
        for _ in range(num_additional):
            # Random time between opened and closed
            if ticket["ClosedAt"]:
                closed_at = dt.datetime.fromisoformat(ticket["ClosedAt"])
                activity_time = opened_at + (closed_at - opened_at) * random.random()
            else:
                activity_time = opened_at + dt.timedelta(hours=random.randint(1, 24))
            
            activity_types = ["Comment", "Update", "Note"]
            activity_details = [
                "User provided additional information",
                "Requested status update",
                "Added troubleshooting notes",
                "Contacted user for clarification",
                "Scheduled follow-up call"
            ]
            
            rows.append({
                "ActivityID": aid,
                "TicketID": ticket["TicketID"],
                "ActivityType": random.choice(activity_types),
                "PerformedByID": random.choice(employees)["EmployeeID"],
                "OldValue": None,
                "NewValue": None,
                "ActivityDetails": random.choice(activity_details),
                "PerformedAt": activity_time.isoformat(sep=" "),
            })
            aid += 1
    
    return rows

def gen_ticket_attachments(tickets, employees):
    """Generate ticket attachments with realistic file information"""
    rows, attid = [], 1
    
    attachment_types = [
        ("screenshot", "image/png", ".png"),
        ("error_log", "text/plain", ".txt"),
        ("system_info", "text/plain", ".txt"),
        ("document", "application/pdf", ".pdf"),
        ("spreadsheet", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"),
        ("presentation", "application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx")
    ]
    
    for ticket in tickets:
        # 25% chance of having attachments
        if random.random() < CFG["attachment_pct"]:
            num_attachments = random.randint(1, 3)
            
            for _ in range(num_attachments):
                att_type, mime_type, extension = random.choice(attachment_types)
                
                # Generate realistic file name
                if att_type == "screenshot":
                    file_name = f"screenshot_{fake.date_time().strftime('%Y%m%d_%H%M%S')}{extension}"
                elif att_type == "error_log":
                    file_name = f"error_log_{fake.date_time().strftime('%Y%m%d')}{extension}"
                elif att_type == "system_info":
                    file_name = f"system_info_{fake.date_time().strftime('%Y%m%d')}{extension}"
                else:
                    file_name = f"{att_type}_{fake.word()}{extension}"
                
                # Generate file path
                file_path = f"/attachments/tickets/{ticket['TicketID']}/{file_name}"
                
                # Generate realistic file size
                if mime_type.startswith("image/"):
                    file_size = random.randint(50000, 500000)  # 50KB - 500KB
                elif mime_type.startswith("text/"):
                    file_size = random.randint(1000, 50000)    # 1KB - 50KB
                else:
                    file_size = random.randint(100000, 2000000)  # 100KB - 2MB
                
                # Upload time (after ticket opened, before closed)
                opened_at = dt.datetime.fromisoformat(ticket["OpenedAt"])
                if ticket["ClosedAt"]:
                    closed_at = dt.datetime.fromisoformat(ticket["ClosedAt"])
                    upload_time = opened_at + (closed_at - opened_at) * random.random()
                else:
                    upload_time = opened_at + dt.timedelta(hours=random.randint(1, 24))
                
                rows.append({
                    "AttachmentID": attid,
                    "TicketID": ticket["TicketID"],
                    "FileName": file_name,
                    "FilePath": file_path,
                    "FileSize": file_size,
                    "MimeType": mime_type,
                    "UploadedByID": random.choice(employees)["EmployeeID"],
                    "UploadedAt": upload_time.isoformat(sep=" "),
                })
                attid += 1
    
    return rows

# Note: TicketCategories are already populated in the DDL, so no need to generate them here
# The DDL contains all the ticket categories and subcategories that would be generated by this function


# ────────────────────────────────
# COMMENT GENERATION
# ────────────────────────────────
def gen_comments(leave_applications, tickets, employees, managers, hr_reps, it_staff):
    """Generate realistic comments for LeaveApplications and Tickets"""
    start_time = time.time()
    print(f"Generating comments for {len(leave_applications)} leave applications and {len(tickets)} tickets...")
    rows, cid = [], 1
    
    # OPTIMIZATION: Use sets for O(1) lookups instead of O(n) list searches
    hr_ids = {hr["EmployeeID"] for hr in hr_reps}
    it_ids = {it["EmployeeID"] for it in it_staff}
    manager_ids = {emp["EmployeeID"] for emp in employees if emp.get("ManagerID") is not None}
    
    # OPTIMIZATION: Pre-build employee role mapping for O(1) lookups
    employee_roles = {}
    for emp in employees:
        emp_id = emp["EmployeeID"]
        if emp_id in manager_ids:
            employee_roles[emp_id] = "Manager"
        elif emp_id in hr_ids:
            employee_roles[emp_id] = "HR"
        elif emp_id in it_ids:
            employee_roles[emp_id] = "IT Support"
        else:
            employee_roles[emp_id] = "Employee"
    
    # Generate comments for Leave Applications (20% of applications)
    print("Processing leave applications...")
    leave_apps_with_comments = [app for app in leave_applications if random.random() < CFG["leave_comments_pct"]]
    print(f"  {len(leave_apps_with_comments)} leave applications will have comments")
    
    for i, leave_app in enumerate(leave_apps_with_comments):
        if i % 20 == 0:  # Progress indicator every 20 applications
            log_progress(i, len(leave_apps_with_comments), "Leave application comments")
            num_comments = random.randint(*CFG["leave_comments_per_app"])
            
            # Create chronological comment timeline
            comment_timeline = []
            
            # Employee initial comment (always first)
            employee_id = leave_app["EmployeeID"]
            submitted_at = dt.datetime.fromisoformat(leave_app["SubmittedAt"])
            
            # Employee comment at submission
            comment_timeline.append({
                "timestamp": submitted_at + dt.timedelta(minutes=random.randint(1, 30)),
                "commenter_id": employee_id,
                "commenter_role": "Employee",
                "comment_type": "Submitted",
                "template_key": "Submitted"
            })
            
            # Manager comment (if manager exists and status allows)
            if leave_app["ManagerID"] and leave_app["ManagerApprovalAt"]:
                manager_approval_at = dt.datetime.fromisoformat(leave_app["ManagerApprovalAt"])
                if leave_app["ManagerApprovalStatus"] == "Approved":
                    comment_timeline.append({
                        "timestamp": manager_approval_at + dt.timedelta(minutes=random.randint(1, 60)),
                        "commenter_id": leave_app["ManagerID"],
                        "commenter_role": "Manager",
                        "comment_type": "Approval",
                        "template_key": "Approval"
                    })
                else:
                    comment_timeline.append({
                        "timestamp": manager_approval_at + dt.timedelta(minutes=random.randint(1, 60)),
                        "commenter_id": leave_app["ManagerID"],
                        "commenter_role": "Manager",
                        "comment_type": "Rejection",
                        "template_key": "Rejection"
                    })
            
            # HR comment (if HR approval exists)
            if leave_app["HRApproverID"] and leave_app["HRApprovalAt"]:
                hr_approval_at = dt.datetime.fromisoformat(leave_app["HRApprovalAt"])
                comment_timeline.append({
                    "timestamp": hr_approval_at + dt.timedelta(minutes=random.randint(1, 60)),
                    "commenter_id": leave_app["HRApproverID"],
                    "commenter_role": "HR",
                    "comment_type": "Final",
                    "template_key": "Final"
                })
            
            # Add follow-up comments if needed (with safety limit)
            max_attempts = 10  # Prevent infinite loops
            attempts = 0
            while len(comment_timeline) < num_comments and attempts < max_attempts:
                attempts += 1
                # Add employee follow-up or manager questions
                last_comment = comment_timeline[-1]
                if last_comment["commenter_role"] == "Employee":
                    # Manager can ask questions
                    if leave_app["ManagerID"]:
                        comment_timeline.append({
                            "timestamp": last_comment["timestamp"] + dt.timedelta(hours=random.randint(2, 24)),
                            "commenter_id": leave_app["ManagerID"],
                            "commenter_role": "Manager",
                            "comment_type": "Questions",
                            "template_key": "Questions"
                        })
                elif last_comment["commenter_role"] == "Manager":
                    # Employee can provide clarification
                    comment_timeline.append({
                        "timestamp": last_comment["timestamp"] + dt.timedelta(hours=random.randint(1, 12)),
                        "commenter_id": employee_id,
                        "commenter_role": "Employee",
                        "comment_type": "Clarification",
                        "template_key": "Clarification"
                    })
                else:
                    # Employee follow-up
                    comment_timeline.append({
                        "timestamp": last_comment["timestamp"] + dt.timedelta(hours=random.randint(4, 48)),
                        "commenter_id": employee_id,
                        "commenter_role": "Employee",
                        "comment_type": "FollowUp",
                        "template_key": "FollowUp"
                    })
            
            # Generate actual comments from timeline
            for comment in comment_timeline[:num_comments]:
                template = random.choice(LEAVE_COMMENT_TEMPLATES[comment["commenter_role"]][comment["template_key"]])
                
                # Fill template variables
                comment_text = template.format(
                    days=leave_app["NumberOfDays"],
                    reason=leave_app["Reason"] or "personal reasons"
                )
                
                rows.append({
                    "CommentID": cid,
                    "EntityType": "LeaveApplication",
                    "EntityID": leave_app["LeaveApplicationID"],
                    "CommenterID": comment["commenter_id"],
                    "CommenterRole": comment["commenter_role"],
                    "CommentText": comment_text,
                    "CreatedAt": comment["timestamp"].isoformat(sep=" "),
                    "UpdatedAt": None,
                    "IsEdited": False,
                    "IsActive": True,
                })
                cid += 1
    
    # Generate comments for Tickets (100% of tickets)
    print("Processing tickets...")
    for i, ticket in enumerate(tickets):
        if i % 25 == 0:  # Progress indicator every 25 tickets (more frequent for tickets)
            log_progress(i, len(tickets), "Ticket comments")
        num_comments = random.randint(*CFG["ticket_comments_per_ticket"])
        
        # Create chronological comment timeline
        comment_timeline = []
        opened_at = dt.datetime.fromisoformat(ticket["OpenedAt"])
        
        # Employee initial comment (always first)
        comment_timeline.append({
            "timestamp": opened_at + dt.timedelta(minutes=random.randint(1, 30)),
            "commenter_id": ticket["OpenedByID"],
            "commenter_role": "Employee",
            "comment_type": "Initial",
            "template_key": "Initial"
        })
        
        # IT Support initial response (within 48 hours)
        if ticket["AssignedToID"]:
            assigned_at = dt.datetime.fromisoformat(ticket["AssignedAt"]) if ticket["AssignedAt"] else opened_at + dt.timedelta(hours=random.randint(1, CFG["ticket_assignment_hours"]))
            comment_timeline.append({
                "timestamp": assigned_at + dt.timedelta(minutes=random.randint(5, 60)),
                "commenter_id": ticket["AssignedToID"],
                "commenter_role": "IT Support",
                "comment_type": "Initial",
                "template_key": "Initial"
            })
        
        # Add progress updates and follow-ups (with safety limit)
        max_attempts = 10  # Prevent infinite loops
        attempts = 0
        while len(comment_timeline) < num_comments and attempts < max_attempts:
            attempts += 1
            last_comment = comment_timeline[-1]
            
            if last_comment["commenter_role"] == "IT Support":
                # Employee follow-up or IT update
                if random.random() < 0.6:  # 60% chance of employee follow-up
                    comment_timeline.append({
                        "timestamp": last_comment["timestamp"] + dt.timedelta(hours=random.randint(2, 24)),
                        "commenter_id": ticket["OpenedByID"],
                        "commenter_role": "Employee",
                        "comment_type": "FollowUp",
                        "template_key": "FollowUp"
                    })
                else:  # IT update
                    comment_timeline.append({
                        "timestamp": last_comment["timestamp"] + dt.timedelta(hours=random.randint(1, 8)),
                        "commenter_id": ticket["AssignedToID"] or random.choice(it_staff)["EmployeeID"],
                        "commenter_role": "IT Support",
                        "comment_type": "Update",
                        "template_key": "Update"
                    })
            elif last_comment["commenter_role"] == "Employee":
                # IT response or employee additional info
                if random.random() < 0.7:  # 70% chance of IT response
                    comment_timeline.append({
                        "timestamp": last_comment["timestamp"] + dt.timedelta(hours=random.randint(1, 12)),
                        "commenter_id": ticket["AssignedToID"] or random.choice(it_staff)["EmployeeID"],
                        "commenter_role": "IT Support",
                        "comment_type": "Update",
                        "template_key": "Update"
                    })
                else:  # Employee additional info
                    comment_timeline.append({
                        "timestamp": last_comment["timestamp"] + dt.timedelta(hours=random.randint(1, 6)),
                        "commenter_id": ticket["OpenedByID"],
                        "commenter_role": "Employee",
                        "comment_type": "Additional",
                        "template_key": "Additional"
                    })
            else:
                # Manager escalation comment
                if ticket["EscalatedToID"]:
                    comment_timeline.append({
                        "timestamp": last_comment["timestamp"] + dt.timedelta(hours=random.randint(1, 4)),
                        "commenter_id": ticket["EscalatedToID"],
                        "commenter_role": "Manager",
                        "comment_type": "Escalation",
                        "template_key": "Escalation"
                    })
                else:
                    # Fallback to employee follow-up if no escalation
                    comment_timeline.append({
                        "timestamp": last_comment["timestamp"] + dt.timedelta(hours=random.randint(2, 24)),
                        "commenter_id": ticket["OpenedByID"],
                        "commenter_role": "Employee",
                        "comment_type": "FollowUp",
                        "template_key": "FollowUp"
                    })
        
        # Add resolution comment if ticket is resolved
        if ticket["ResolvedAt"] and len(comment_timeline) < num_comments:
            resolved_at = dt.datetime.fromisoformat(ticket["ResolvedAt"])
            comment_timeline.append({
                "timestamp": resolved_at + dt.timedelta(minutes=random.randint(1, 30)),
                "commenter_id": ticket["AssignedToID"] or random.choice(it_staff)["EmployeeID"],
                "commenter_role": "IT Support",
                "comment_type": "Resolution",
                "template_key": "Resolution"
            })
        
        # Generate actual comments from timeline
        for comment in comment_timeline[:num_comments]:
            template = random.choice(TICKET_COMMENT_TEMPLATES[comment["commenter_role"]][comment["template_key"]])
            
            # Fill template variables for ticket comments
            comment_text = template.format(
                issue=random.choice(["connectivity problems", "software issues", "hardware problems", "access issues"]),
                device=random.choice(["laptop", "computer", "system", "device"])
            )
            
            rows.append({
                "CommentID": cid,
                "EntityType": "Ticket",
                "EntityID": ticket["TicketID"],
                "CommenterID": comment["commenter_id"],
                "CommenterRole": comment["commenter_role"],
                "CommentText": comment_text,
                "CreatedAt": comment["timestamp"].isoformat(sep=" "),
                "UpdatedAt": None,
                "IsEdited": False,
                "IsActive": True,
            })
            cid += 1
    
    log_performance("Comment generation", start_time)
    print(f"Generated {len(rows)} comments total")
    return rows


# ────────────────────────────────
# MAIN
# ────────────────────────────────
def main():
    total_start_time = time.time()
    print("Generating fake echobyte data …")

    # build hierarchy
    print("\n🏗️  Building organizational hierarchy...")
    locations     = gen_locations(CFG["n_locations"])
    departments   = gen_departments(CFG["dept_structure"], locations)
    teams         = gen_teams(departments, CFG["teams_per_dept"])
    employees, mgrs, hr_reps = gen_employees(teams, locations, CFG["n_employees"])
    
    print("\n👥 Generating employee data...")
    e_contacts    = gen_emergency_contacts(employees)
    users, password_data = gen_users(employees)
    _, emp_roles  = gen_roles_and_emp_roles(employees, mgrs, hr_reps)
    
    print("\n📅 Generating time-based data...")
    leave_bal     = gen_leave_balances(employees)
    leave_apps    = gen_leave_applications(employees, mgrs)
    ts_periods, ts_details = gen_timesheets_and_details(employees)

    # assets / assignments
    print("\n💻 Generating asset data...")
    # Use DDL constants for AssetTypes to ensure proper foreign key relationships
    assets      = gen_assets(ASSET_TYPES, locations)
    assignments = gen_asset_assignments(assets, employees)

    print("\n📝 Generating feedback data...")
    feedbacks   = gen_feedbacks(employees, teams)

    # tickets
    print("\n🎫 Generating ticket data...")
    # Use DDL constants for TicketCategories to ensure proper foreign key relationships
    tickets = gen_tickets(employees, assets, TICKET_CATEGORIES)
    ticket_activities = gen_ticket_activities(tickets, employees)
    ticket_attachments = gen_ticket_attachments(tickets, employees)

    # comments
    print("\n💬 Generating comment data...")
    it_staff = get_it_staff(employees)
    comments = gen_comments(leave_apps, tickets, employees, mgrs, hr_reps, it_staff)


    # write csvs (parents first)
    wr("Locations",    locations)
    wr("Departments",  departments)
    wr("Teams",        teams)
    wr("Users",        users)  # Users must be written before Employees due to FK constraint
    wr("Employees",    employees)
    wr("EmergencyContacts", e_contacts)
    wr("EmployeeRoles", emp_roles)
    
    # write password data to CSV file
    wr("UserPasswords", password_data)

    wr("LeaveBalances",       leave_bal)
    wr("LeaveApplications",   leave_apps)

    wr("Timesheets",          ts_periods)
    wr("TimesheetDetails",    ts_details)

    wr("Assets",              assets)
    wr("AssetAssignments",    assignments)

    wr("EmployeeFeedbacks",   feedbacks)

    # tickets
    # Note: TicketCategories are already populated in the DDL, so no CSV needed
    wr("Tickets",             tickets)
    wr("TicketActivities",    ticket_activities)
    wr("TicketAttachments",   ticket_attachments)

    # comments
    print("\n💾 Writing CSV files...")
    wr("Comments",            comments)

    total_time = time.time() - total_start_time
    print(f"\n✅ All done! Total time: {total_time:.2f}s")
    print("📁 CSVs live under:", CFG["csv_out"].resolve())

if __name__ == "__main__":
    main()
