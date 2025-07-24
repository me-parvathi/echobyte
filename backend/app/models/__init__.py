# Import all models here for easy access
from .lookup_models import (
    Genders,
    EmploymentTypes,
    WorkModes,
    LeaveApplicationStatuses,
    ApprovalStatuses,
    TimesheetStatuses,
    FeedbackTypes,
    Designations
)

from .core_models import (
    Locations,
    Departments,
    Teams
)

from .employee_models import (
    Employees,
    EmergencyContacts,
    Roles,
    EmployeeRoles
)

from .leave_models import (
    LeaveTypes,
    LeaveBalances,
    LeaveApplications
)

from .timesheet_models import (
    Timesheets,
    TimesheetDetails
)

from .feedback_models import (
    EmployeeFeedbacks,
    AuditLogs
)

from .asset_models import (
    AssetStatuses,
    AssetTypes,
    Assets,
    AssetAssignments
)

# Export all models
__all__ = [
    # Lookup models
    'Genders', 'EmploymentTypes', 'WorkModes', 'LeaveApplicationStatuses',
    'ApprovalStatuses', 'TimesheetStatuses', 'FeedbackTypes', 'Designations',
    
    # Core models
    'Locations', 'Departments', 'Teams',
    
    # Employee models
    'Employees', 'EmergencyContacts', 'Roles', 'EmployeeRoles',
    
    # Leave models
    'LeaveTypes', 'LeaveBalances', 'LeaveApplications',
    
    # Timesheet models
    'Timesheets', 'TimesheetDetails',
    
    # Feedback models
    'EmployeeFeedbacks', 'AuditLogs',
    
    # Asset models
    'AssetStatuses', 'AssetTypes', 'Assets', 'AssetAssignments'
] 