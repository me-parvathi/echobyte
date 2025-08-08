/* ─────────────────────────────────────────────
   0.  Create / switch to the database
   ───────────────────────────────────────────── */
IF DB_ID(N'echobyte') IS NULL
    CREATE DATABASE echobyte;
GO
USE echobyte;
GO

/* Always roll back whole batch on any error */
SET XACT_ABORT ON;
GO

/* ============================================================
   1.  Lookup tables (enum‑replacements)
   ============================================================ */

CREATE TABLE dbo.Genders (
    GenderCode      NVARCHAR(10)  NOT NULL PRIMARY KEY,   -- e.g. M, F, O, NB…
    GenderName      NVARCHAR(50)  NOT NULL,
    IsActive        BIT           NOT NULL CONSTRAINT DF_Genders_IsActive DEFAULT (1),
    CreatedAt       DATETIME2(3)  NOT NULL CONSTRAINT DF_Genders_Created DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.EmploymentTypes (
    EmploymentTypeCode NVARCHAR(20)  NOT NULL PRIMARY KEY,  -- Full‑Time, Part‑Time …
    EmploymentTypeName NVARCHAR(50)  NOT NULL,
    IsActive           BIT           NOT NULL CONSTRAINT DF_EmpTypes_IsActive DEFAULT (1),
    CreatedAt          DATETIME2(3)  NOT NULL CONSTRAINT DF_EmpTypes_Created DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.WorkModes (
    WorkModeCode  NVARCHAR(20)  NOT NULL PRIMARY KEY,       -- Remote, Hybrid, …
    WorkModeName  NVARCHAR(50)  NOT NULL,
    IsActive      BIT           NOT NULL CONSTRAINT DF_WorkModes_IsActive DEFAULT (1),
    CreatedAt     DATETIME2(3)  NOT NULL CONSTRAINT DF_WorkModes_Created DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.LeaveApplicationStatuses (
    StatusCode    NVARCHAR(25)  NOT NULL PRIMARY KEY,       -- Draft, Submitted …
    StatusName    NVARCHAR(50)  NOT NULL,
    IsActive      BIT           NOT NULL CONSTRAINT DF_LAStatus_IsActive DEFAULT (1),
    CreatedAt     DATETIME2(3)  NOT NULL CONSTRAINT DF_LAStatus_Created DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.ApprovalStatuses (
    ApprovalStatusCode NVARCHAR(20) NOT NULL PRIMARY KEY,   -- Pending, Approved …
    ApprovalStatusName NVARCHAR(50) NOT NULL,
    IsActive           BIT          NOT NULL CONSTRAINT DF_ApprovalStatus_IsActive DEFAULT (1),
    CreatedAt          DATETIME2(3) NOT NULL CONSTRAINT DF_ApprovalStatus_Created DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.TimesheetStatuses (
    TimesheetStatusCode NVARCHAR(20) NOT NULL PRIMARY KEY,  -- Draft, Submitted …
    TimesheetStatusName NVARCHAR(50) NOT NULL,
    IsActive            BIT          NOT NULL CONSTRAINT DF_TimesheetStatus_IsActive DEFAULT (1),
    CreatedAt           DATETIME2(3) NOT NULL CONSTRAINT DF_TimesheetStatus_Created DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.FeedbackTypes (
    FeedbackTypeCode NVARCHAR(20) NOT NULL PRIMARY KEY,     -- General, Manager …
    FeedbackTypeName NVARCHAR(50) NOT NULL,
    IsActive         BIT          NOT NULL CONSTRAINT DF_FeedbackTypes_IsActive DEFAULT (1),
    CreatedAt        DATETIME2(3) NOT NULL CONSTRAINT DF_FeedbackTypes_Created DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.Designations (
    DesignationID   INT           IDENTITY(1,1) PRIMARY KEY,
    DesignationName NVARCHAR(100) NOT NULL UNIQUE,          -- e.g. Software Engineer II
    IsActive        BIT           NOT NULL CONSTRAINT DF_Designations_IsActive DEFAULT (1),
    CreatedAt       DATETIME2(3)  NOT NULL CONSTRAINT DF_Designations_Created DEFAULT SYSUTCDATETIME()
);

/* ============================================================
   2.  Core lookup tables (company structure)
   ============================================================ */

CREATE TABLE dbo.Locations (
    LocationID     INT            IDENTITY(1,1)  PRIMARY KEY,
    LocationName   NVARCHAR(100)  NOT NULL UNIQUE,
    Address1       NVARCHAR(200)  NOT NULL,
    Address2       NVARCHAR(200)  NULL,
    City           NVARCHAR(100)  NOT NULL,
    State          NVARCHAR(100)  NULL,
    Country        NVARCHAR(100)  NOT NULL,
    PostalCode     NVARCHAR(20)   NULL,
    Phone          NVARCHAR(50)   NULL,
    TimeZone       NVARCHAR(50)   NOT NULL,
    IsActive       BIT            NOT NULL CONSTRAINT DF_Locations_IsActive DEFAULT (1),
    CreatedAt      DATETIME2(3)   NOT NULL CONSTRAINT DF_Locations_Created DEFAULT SYSUTCDATETIME(),
    UpdatedAt      DATETIME2(3)   NOT NULL CONSTRAINT DF_Locations_Updated DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.Departments (
    DepartmentID       INT            IDENTITY(1,1) PRIMARY KEY,
    DepartmentName     NVARCHAR(100)  NOT NULL,
    DepartmentCode     NVARCHAR(20)   NOT NULL UNIQUE,
    ParentDepartmentID INT            NULL,
    LocationID         INT            NOT NULL,
    IsActive           BIT            NOT NULL CONSTRAINT DF_Departments_IsActive DEFAULT (1),
    CreatedAt          DATETIME2(3)   NOT NULL CONSTRAINT DF_Departments_Created DEFAULT SYSUTCDATETIME(),
    UpdatedAt          DATETIME2(3)   NOT NULL CONSTRAINT DF_Departments_Updated DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_Departments_Location
        FOREIGN KEY (LocationID) REFERENCES dbo.Locations(LocationID)
);
GO
/* Self‑reference added separately to avoid cyclic‑cascade issues */
ALTER TABLE dbo.Departments  WITH NOCHECK
ADD CONSTRAINT FK_Departments_Parent
    FOREIGN KEY (ParentDepartmentID)
    REFERENCES dbo.Departments(DepartmentID)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
GO

CREATE TABLE dbo.Teams (
    TeamID              INT            IDENTITY(1,1) PRIMARY KEY,
    TeamName            NVARCHAR(100)  NOT NULL,
    TeamCode            NVARCHAR(20)   NOT NULL UNIQUE,
    DepartmentID        INT            NOT NULL,
    TeamLeadEmployeeID  INT            NULL,
    IsActive            BIT            NOT NULL CONSTRAINT DF_Teams_IsActive DEFAULT (1),
    CreatedAt           DATETIME2(3)   NOT NULL CONSTRAINT DF_Teams_Created DEFAULT SYSUTCDATETIME(),
    UpdatedAt           DATETIME2(3)   NOT NULL CONSTRAINT DF_Teams_Updated DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_Teams_Departments
        FOREIGN KEY (DepartmentID) REFERENCES dbo.Departments(DepartmentID)
);
GO

/* ============================================================
   3.  Employees and related tables
   ============================================================ */

CREATE TABLE dbo.Employees (
    EmployeeID          INT            IDENTITY(1,1) PRIMARY KEY,
    EmployeeCode        NVARCHAR(20)   NOT NULL UNIQUE,
    UserID              NVARCHAR(50)   NOT NULL UNIQUE,
    CompanyEmail        NVARCHAR(100)  NOT NULL UNIQUE,
    FirstName           NVARCHAR(50)   NOT NULL,
    MiddleName          NVARCHAR(50)   NULL,
    LastName            NVARCHAR(50)   NOT NULL,
    DateOfBirth         DATE           NULL,
    GenderCode          NVARCHAR(10)   NOT NULL,
    MaritalStatus       NVARCHAR(20)   NULL,
    PersonalEmail       NVARCHAR(100)  NULL,
    PersonalPhone       NVARCHAR(50)   NULL,
    WorkPhone           NVARCHAR(50)   NULL,

    -- Address
    Address1            NVARCHAR(200)  NULL,
    Address2            NVARCHAR(200)  NULL,
    City                NVARCHAR(100)  NULL,
    State               NVARCHAR(100)  NULL,
    Country             NVARCHAR(100)  NULL,
    PostalCode          NVARCHAR(20)   NULL,

    -- Work details
    TeamID              INT            NOT NULL,
    LocationID          INT            NOT NULL,
    ManagerID           INT            NULL,
    DesignationID       INT            NOT NULL,
    EmploymentTypeCode  NVARCHAR(20)   NOT NULL,
    WorkModeCode        NVARCHAR(20)   NOT NULL,
    HireDate            DATE           NOT NULL,
    TerminationDate     DATE           NULL,

    -- System fields
    IsActive            BIT            NOT NULL CONSTRAINT DF_Employees_IsActive DEFAULT (1),
    CreatedAt           DATETIME2(3)   NOT NULL CONSTRAINT DF_Employees_Created DEFAULT SYSUTCDATETIME(),
    UpdatedAt           DATETIME2(3)   NOT NULL CONSTRAINT DF_Employees_Updated DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_Employees_Teams
        FOREIGN KEY (TeamID)       REFERENCES dbo.Teams(TeamID),

    CONSTRAINT FK_Employees_Locations
        FOREIGN KEY (LocationID)   REFERENCES dbo.Locations(LocationID),

    CONSTRAINT FK_Employees_Managers
        FOREIGN KEY (ManagerID)    REFERENCES dbo.Employees(EmployeeID)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION,

    CONSTRAINT FK_Employees_Genders
        FOREIGN KEY (GenderCode)   REFERENCES dbo.Genders(GenderCode),

    CONSTRAINT FK_Employees_EmpTypes
        FOREIGN KEY (EmploymentTypeCode) REFERENCES dbo.EmploymentTypes(EmploymentTypeCode),

    CONSTRAINT FK_Employees_WorkModes
        FOREIGN KEY (WorkModeCode) REFERENCES dbo.WorkModes(WorkModeCode),

    CONSTRAINT FK_Employees_Designations
        FOREIGN KEY (DesignationID) REFERENCES dbo.Designations(DesignationID)
);
GO

/* Now we can link TeamLeadEmployeeID */
ALTER TABLE dbo.Teams WITH NOCHECK
ADD CONSTRAINT FK_Teams_TeamLead
    FOREIGN KEY (TeamLeadEmployeeID)
    REFERENCES dbo.Employees(EmployeeID)
    ON DELETE SET NULL
    ON UPDATE NO ACTION;
GO

CREATE TABLE dbo.EmergencyContacts (
    ContactID      INT            IDENTITY(1,1) PRIMARY KEY,
    EmployeeID     INT            NOT NULL,
    ContactName    NVARCHAR(100)  NOT NULL,
    Relationship   NVARCHAR(50)   NOT NULL,
    Phone1         NVARCHAR(50)   NOT NULL,
    Phone2         NVARCHAR(50)   NULL,
    Email          NVARCHAR(100)  NULL,
    Address        NVARCHAR(200)  NULL,
    IsPrimary      BIT            NOT NULL CONSTRAINT DF_EmergencyContacts_IsPrimary DEFAULT (0),
    IsActive       BIT            NOT NULL CONSTRAINT DF_EmergencyContacts_IsActive  DEFAULT (1),
    CreatedAt      DATETIME2(3)   NOT NULL CONSTRAINT DF_EmergencyContacts_Created  DEFAULT SYSUTCDATETIME(),
    UpdatedAt      DATETIME2(3)   NOT NULL CONSTRAINT DF_EmergencyContacts_Updated  DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_EmergencyContacts_Employees
        FOREIGN KEY (EmployeeID) REFERENCES dbo.Employees(EmployeeID)
);

/* Guarantee exactly one active primary contact per employee */
CREATE UNIQUE INDEX UX_EmergencyContacts_Primary
ON dbo.EmergencyContacts(EmployeeID)
WHERE IsPrimary = 1 AND IsActive = 1;
GO

/* ============================================================
   4.  Roles & security
   ============================================================ */

CREATE TABLE dbo.Roles (
    RoleID      INT            IDENTITY(1,1)  PRIMARY KEY,
    RoleName    NVARCHAR(50)   NOT NULL UNIQUE,
    Description NVARCHAR(200)  NULL,
    IsActive    BIT            NOT NULL CONSTRAINT DF_Roles_IsActive DEFAULT (1),
    CreatedAt   DATETIME2(3)   NOT NULL CONSTRAINT DF_Roles_Created DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.EmployeeRoles (
    EmployeeRoleID INT           IDENTITY(1,1) PRIMARY KEY,
    EmployeeID     INT           NOT NULL,
    RoleID         INT           NOT NULL,
    AssignedAt     DATETIME2(3)  NOT NULL CONSTRAINT DF_EmpRoles_Assigned DEFAULT SYSUTCDATETIME(),
    AssignedByID   INT           NULL,
    IsActive       BIT           NOT NULL CONSTRAINT DF_EmpRoles_IsActive DEFAULT (1),

    CONSTRAINT FK_EmpRoles_Employees   FOREIGN KEY (EmployeeID)   REFERENCES dbo.Employees(EmployeeID),
    CONSTRAINT FK_EmpRoles_Roles       FOREIGN KEY (RoleID)       REFERENCES dbo.Roles(RoleID),
    CONSTRAINT FK_EmpRoles_AssignedBy  FOREIGN KEY (AssignedByID) REFERENCES dbo.Employees(EmployeeID)
);

/* Only one active row per (Employee,Role) */
CREATE UNIQUE INDEX UX_EmployeeRoles_Active
ON dbo.EmployeeRoles(EmployeeID, RoleID)
WHERE IsActive = 1;
GO

/* ============================================================
   5.  Leave management
   ============================================================ */

CREATE TABLE dbo.LeaveTypes (
    LeaveTypeID        INT            IDENTITY(1,1)  PRIMARY KEY,
    LeaveTypeName      NVARCHAR(50)   NOT NULL,
    LeaveCode          NVARCHAR(10)   NOT NULL UNIQUE,
    DefaultDaysPerYear DECIMAL(4,1)   NULL,
    IsActive           BIT            NOT NULL CONSTRAINT DF_LeaveTypes_IsActive DEFAULT (1),
    CreatedAt          DATETIME2(3)   NOT NULL CONSTRAINT DF_LeaveTypes_Created DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.LeaveBalances (
    BalanceID      INT            IDENTITY(1,1) PRIMARY KEY,
    EmployeeID     INT            NOT NULL,
    LeaveTypeID    INT            NOT NULL,
    Year           INT            NOT NULL,
    EntitledDays   DECIMAL(4,1)   NOT NULL,
    UsedDays       DECIMAL(4,1)   NOT NULL DEFAULT (0),
    RemainingDays  AS (EntitledDays - UsedDays),
    CreatedAt      DATETIME2(3)   NOT NULL CONSTRAINT DF_LeaveBalances_Created DEFAULT SYSUTCDATETIME(),
    UpdatedAt      DATETIME2(3)   NOT NULL CONSTRAINT DF_LeaveBalances_Updated DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_LeaveBalances_Employees FOREIGN KEY (EmployeeID)  REFERENCES dbo.Employees(EmployeeID),
    CONSTRAINT FK_LeaveBalances_Types     FOREIGN KEY (LeaveTypeID) REFERENCES dbo.LeaveTypes(LeaveTypeID),
    CONSTRAINT UQ_LeaveBalances_EmployeeYear UNIQUE (EmployeeID, LeaveTypeID, Year)
);

CREATE TABLE dbo.LeaveApplications (
    LeaveApplicationID     INT            IDENTITY(1,1) PRIMARY KEY,
    EmployeeID             INT            NOT NULL,
    LeaveTypeID            INT            NOT NULL,
    StartDate              DATE           NOT NULL,
    EndDate                DATE           NOT NULL,
    NumberOfDays           DECIMAL(4,1)   NOT NULL,
    Reason                 NVARCHAR(500)  NULL,

    StatusCode             NVARCHAR(25)   NOT NULL,
    SubmittedAt            DATETIME2(3)   NULL,

    ManagerID              INT            NULL,
    ManagerApprovalStatus  NVARCHAR(20)   NULL,
    ManagerApprovalAt      DATETIME2(3)   NULL,
    ManagerComments        NVARCHAR(500)  NULL,

    HRApproverID           INT            NULL,
    HRApprovalStatus       NVARCHAR(20)   NULL,
    HRApprovalAt           DATETIME2(3)   NULL,
    HRComments             NVARCHAR(500)  NULL,

    CreatedAt              DATETIME2(3)   NOT NULL CONSTRAINT DF_LeaveApplications_Created DEFAULT SYSUTCDATETIME(),
    UpdatedAt              DATETIME2(3)   NOT NULL CONSTRAINT DF_LeaveApplications_Updated DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_LeaveApplications_Employees     FOREIGN KEY (EmployeeID)    REFERENCES dbo.Employees(EmployeeID),
    CONSTRAINT FK_LeaveApplications_Types         FOREIGN KEY (LeaveTypeID)   REFERENCES dbo.LeaveTypes(LeaveTypeID),
    CONSTRAINT FK_LeaveApplications_Status        FOREIGN KEY (StatusCode)    REFERENCES dbo.LeaveApplicationStatuses(StatusCode),
    CONSTRAINT FK_LeaveApplications_Manager       FOREIGN KEY (ManagerID)     REFERENCES dbo.Employees(EmployeeID),
    CONSTRAINT FK_LeaveApplications_HRApprover    FOREIGN KEY (HRApproverID)  REFERENCES dbo.Employees(EmployeeID),

    CONSTRAINT CHK_LeaveApplications_Dates CHECK (EndDate >= StartDate)
);

/* ============================================================
   6.  Timesheets
   ============================================================ */

CREATE TABLE dbo.Timesheets (
    TimesheetID           INT            IDENTITY(1,1) PRIMARY KEY,
    EmployeeID            INT            NOT NULL,
    WeekStartDate         DATE           NOT NULL,
    WeekEndDate           DATE           NOT NULL,
    TotalHours            DECIMAL(5,2)   NOT NULL DEFAULT (0),
    StatusCode            NVARCHAR(20)   NOT NULL,
    SubmittedAt           DATETIME2(3)   NULL,
    ApprovedByID          INT            NULL,
    ApprovedAt            DATETIME2(3)   NULL,
    Comments              NVARCHAR(500)  NULL,
    CreatedAt             DATETIME2(3)   NOT NULL CONSTRAINT DF_Timesheets_Created DEFAULT SYSUTCDATETIME(),
    UpdatedAt             DATETIME2(3)   NOT NULL CONSTRAINT DF_Timesheets_Updated DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_Timesheets_Employees      FOREIGN KEY (EmployeeID)    REFERENCES dbo.Employees(EmployeeID),
    CONSTRAINT FK_Timesheets_Status         FOREIGN KEY (StatusCode)    REFERENCES dbo.TimesheetStatuses(TimesheetStatusCode),
    CONSTRAINT FK_Timesheets_ApprovedBy     FOREIGN KEY (ApprovedByID)  REFERENCES dbo.Employees(EmployeeID),
    CONSTRAINT CHK_Timesheets_Dates CHECK (WeekEndDate >= WeekStartDate),
    CONSTRAINT UQ_Timesheets_EmployeeWeek UNIQUE (EmployeeID, WeekStartDate)
);

CREATE TABLE dbo.TimesheetDetails (
    DetailID       INT            IDENTITY(1,1) PRIMARY KEY,
    TimesheetID    INT            NOT NULL,
    WorkDate       DATE           NOT NULL,
    ProjectCode    NVARCHAR(50)   NULL,
    TaskDescription NVARCHAR(200) NULL,
    HoursWorked    DECIMAL(4,2)   NOT NULL CHECK (HoursWorked BETWEEN 0 AND 24),
    IsOvertime     BIT            NOT NULL CONSTRAINT DF_TimesheetDetails_IsOvertime DEFAULT (0),
    CreatedAt      DATETIME2(3)   NOT NULL CONSTRAINT DF_TimesheetDetails_Created DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_TimesheetDetails_Timesheets
        FOREIGN KEY (TimesheetID) REFERENCES dbo.Timesheets(TimesheetID) ON DELETE CASCADE,

    CONSTRAINT UQ_TimesheetDetails_UniqueDate UNIQUE (TimesheetID, WorkDate)
);

/* ============================================================
   7.  Feedback
   ============================================================ */

CREATE TABLE dbo.EmployeeFeedbacks (
    FeedbackID        INT            IDENTITY(1,1) PRIMARY KEY,
    FeedbackAt        DATETIME2(3)   NOT NULL CONSTRAINT DF_Feedbacks_Date DEFAULT SYSUTCDATETIME(),
    FeedbackTypeCode  NVARCHAR(20)   NOT NULL,
    Category          NVARCHAR(50)   NULL,
    Subject           NVARCHAR(200)  NULL,
    FeedbackText      NVARCHAR(MAX)  NOT NULL,

    TargetManagerID       INT        NULL,
    TargetDepartmentID    INT        NULL,

    FeedbackHash      NVARCHAR(64)   NULL,
    IsRead            BIT            NOT NULL CONSTRAINT DF_Feedbacks_IsRead DEFAULT (0),
    ReadByID          INT            NULL,
    ReadAt            DATETIME2(3)   NULL,

    CONSTRAINT FK_Feedbacks_Type          FOREIGN KEY (FeedbackTypeCode)   REFERENCES dbo.FeedbackTypes(FeedbackTypeCode),
    CONSTRAINT FK_Feedbacks_TargetManager FOREIGN KEY (TargetManagerID)    REFERENCES dbo.Employees(EmployeeID),
    CONSTRAINT FK_Feedbacks_TargetDept    FOREIGN KEY (TargetDepartmentID) REFERENCES dbo.Departments(DepartmentID),
    CONSTRAINT FK_Feedbacks_ReadBy        FOREIGN KEY (ReadByID)           REFERENCES dbo.Employees(EmployeeID)
);

/* ============================================================
   8.  Audit
   ============================================================ */

CREATE TABLE dbo.AuditLogs (
    AuditID     INT            IDENTITY(1,1) PRIMARY KEY,
    TableName   NVARCHAR(128)  NOT NULL,
    Operation   NVARCHAR(10)   NOT NULL,
    RecordID    INT            NOT NULL,
    ChangedBy   NVARCHAR(100)  NOT NULL,
    ChangedAt   DATETIME2(3)   NOT NULL CONSTRAINT DF_AuditLogs_Date DEFAULT SYSUTCDATETIME(),
    OldValues   NVARCHAR(MAX)  NULL,
    NewValues   NVARCHAR(MAX)  NULL
);
GO

/* Sample trigger on Employees */
CREATE OR ALTER TRIGGER dbo.tr_Employees_Audit
ON dbo.Employees
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    /* Deleted rows audit */
    INSERT INTO dbo.AuditLogs (TableName, Operation, RecordID, ChangedBy, OldValues)
    SELECT 'Employees', 'DELETE', d.EmployeeID, SYSTEM_USER,
           (SELECT * FROM (SELECT d.*) z FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
    FROM deleted d;

    /* Updated rows audit */
    INSERT INTO dbo.AuditLogs (TableName, Operation, RecordID, ChangedBy, OldValues, NewValues)
    SELECT 'Employees', 'UPDATE', i.EmployeeID, SYSTEM_USER,
           (SELECT * FROM (SELECT d.*) z FOR JSON PATH, WITHOUT_ARRAY_WRAPPER),
           (SELECT * FROM (SELECT i.*) z FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
    FROM inserted i
    JOIN deleted  d ON d.EmployeeID = i.EmployeeID
    WHERE EXISTS (SELECT i.EmployeeID EXCEPT SELECT d.EmployeeID);  -- ensure update

    /* Inserted rows audit */
    INSERT INTO dbo.AuditLogs (TableName, Operation, RecordID, ChangedBy, NewValues)
    SELECT 'Employees', 'INSERT', i.EmployeeID, SYSTEM_USER,
           (SELECT * FROM (SELECT i.*) z FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
    FROM inserted i
    WHERE NOT EXISTS (SELECT 1 FROM deleted WHERE deleted.EmployeeID = i.EmployeeID);
END;
GO

/* ============================================================
   9.  Hierarchy views
   ============================================================ */

CREATE OR ALTER VIEW dbo.vw_DepartmentHierarchies
AS
WITH cte AS (
    SELECT  d.DepartmentID,
            d.DepartmentName,
            d.DepartmentCode,
            d.ParentDepartmentID,
            CAST(NULL AS NVARCHAR(100)) AS ParentDepartmentName,
            0  AS Level,
            CAST(d.DepartmentName AS NVARCHAR(MAX)) AS HierarchyPath
    FROM dbo.Departments d
    WHERE d.ParentDepartmentID IS NULL AND d.IsActive = 1

    UNION ALL

    SELECT  d.DepartmentID,
            d.DepartmentName,
            d.DepartmentCode,
            d.ParentDepartmentID,
            p.DepartmentName,
            c.Level + 1,
            c.HierarchyPath + N' > ' + d.DepartmentName
    FROM dbo.Departments d
    JOIN cte c          ON d.ParentDepartmentID = c.DepartmentID
    JOIN dbo.Departments p ON p.DepartmentID     = d.ParentDepartmentID
)
SELECT * FROM cte;
GO

CREATE OR ALTER VIEW dbo.vw_EmployeeHierarchies
AS
WITH cte AS (
    SELECT  e.EmployeeID,
            e.EmployeeCode,
            CONCAT(e.FirstName, ' ', e.LastName) AS EmployeeName,
            des.DesignationName                  AS Designation,
            e.ManagerID,
            CAST(NULL AS NVARCHAR(100)) AS ManagerName,
            0          AS Level,
            CAST(e.EmployeeID AS NVARCHAR(MAX)) AS HierarchyPath
    FROM dbo.Employees e
    JOIN dbo.Designations des ON des.DesignationID = e.DesignationID
    WHERE e.ManagerID IS NULL AND e.IsActive = 1

    UNION ALL

    SELECT  e.EmployeeID,
            e.EmployeeCode,
            CONCAT(e.FirstName, ' ', e.LastName),
            des.DesignationName,
            e.ManagerID,
            CONCAT(m.FirstName, ' ', m.LastName),
            c.Level + 1,
            c.HierarchyPath + N' > ' + CAST(e.EmployeeID AS NVARCHAR(MAX))
    FROM dbo.Employees  e
    JOIN dbo.Employees  m   ON m.EmployeeID = e.ManagerID
    JOIN dbo.Designations des ON des.DesignationID = e.DesignationID
    JOIN cte            c   ON e.ManagerID  = c.EmployeeID
    WHERE e.IsActive = 1
)
SELECT * FROM cte;
GO

/* ============================================================
   10.  Stored procedures (example: leave approval)
   ============================================================ */

CREATE OR ALTER PROCEDURE dbo.sp_ProcessLeaveApproval
    @LeaveApplicationID INT,
    @ApproverID         INT,
    @ApprovalStatusCode NVARCHAR(20),
    @Comments           NVARCHAR(500) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @CurrentStatusCode  NVARCHAR(25),
            @EmployeeManagerID  INT,
            @IsHR               BIT = 0;

    /* HR role? */
    IF EXISTS (SELECT 1
               FROM dbo.EmployeeRoles er
               JOIN dbo.Roles r ON r.RoleID = er.RoleID
               WHERE er.EmployeeID = @ApproverID
                 AND r.RoleName    = 'HR'
                 AND er.IsActive   = 1)
        SET @IsHR = 1;

    /* Current status + manager */
    SELECT  @CurrentStatusCode = la.StatusCode,
            @EmployeeManagerID = e.ManagerID
    FROM dbo.LeaveApplications la
    JOIN dbo.Employees e ON e.EmployeeID = la.EmployeeID
    WHERE la.LeaveApplicationID = @LeaveApplicationID;

    /* Manager approval */
    IF @ApproverID = @EmployeeManagerID
       AND @CurrentStatusCode = 'Submitted'
    BEGIN
        UPDATE dbo.LeaveApplications
        SET ManagerApprovalStatus = @ApprovalStatusCode,
            ManagerApprovalAt     = SYSUTCDATETIME(),
            ManagerComments       = @Comments,
            StatusCode            = CASE WHEN @ApprovalStatusCode = 'Approved'
                                          THEN 'Manager-Approved'
                                          ELSE 'Rejected' END,
            UpdatedAt             = SYSUTCDATETIME()
        WHERE LeaveApplicationID = @LeaveApplicationID;
    END
    /* HR approval */
    ELSE IF @IsHR = 1
         AND @CurrentStatusCode = 'Manager-Approved'
    BEGIN
        UPDATE dbo.LeaveApplications
        SET HRApproverID      = @ApproverID,
            HRApprovalStatus  = @ApprovalStatusCode,
            HRApprovalAt      = SYSUTCDATETIME(),
            HRComments        = @Comments,
            StatusCode        = CASE WHEN @ApprovalStatusCode = 'Approved'
                                      THEN 'HR-Approved'
                                      ELSE 'Rejected' END,
            UpdatedAt         = SYSUTCDATETIME()
        WHERE LeaveApplicationID = @LeaveApplicationID;

        /* adjust balance */
        IF @ApprovalStatusCode = 'Approved'
        BEGIN
            UPDATE lb
            SET UsedDays  = UsedDays + la.NumberOfDays,
                UpdatedAt = SYSUTCDATETIME()
            FROM dbo.LeaveBalances lb
            JOIN dbo.LeaveApplications la
                ON lb.EmployeeID  = la.EmployeeID
               AND lb.LeaveTypeID = la.LeaveTypeID
            WHERE la.LeaveApplicationID = @LeaveApplicationID
              AND lb.Year = YEAR(la.StartDate);
        END
    END
END;
GO

/* ============================================================
   11.  Seed data (minimal)
   ============================================================ */

/* Genders */
INSERT INTO dbo.Genders (GenderCode, GenderName) VALUES
 ('M','Male'), ('F','Female'), ('O','Other'), ('NB','Non‑Binary');

/* Employment types */
INSERT INTO dbo.EmploymentTypes (EmploymentTypeCode, EmploymentTypeName) VALUES
 ('Full-Time','Full‑Time'), ('Part-Time','Part‑Time'),
 ('Contract','Contract'),   ('Intern','Intern');

/* Work modes */
INSERT INTO dbo.WorkModes (WorkModeCode, WorkModeName) VALUES
 ('Remote','Remote'), ('In-Person','In‑Person'), ('Hybrid','Hybrid');

/* Approval statuses */
INSERT INTO dbo.ApprovalStatuses (ApprovalStatusCode, ApprovalStatusName) VALUES
 ('Pending','Pending'), ('Approved','Approved'), ('Rejected','Rejected');

/* Leave application statuses */
INSERT INTO dbo.LeaveApplicationStatuses (StatusCode, StatusName) VALUES
 ('Draft','Draft'), ('Submitted','Submitted'),
 ('Manager-Approved','Manager‑Approved'), ('HR-Approved','HR‑Approved'),
 ('Rejected','Rejected'), ('Cancelled','Cancelled');

/* Timesheet statuses */
INSERT INTO dbo.TimesheetStatuses (TimesheetStatusCode, TimesheetStatusName) VALUES
 ('Draft','Draft'), ('Submitted','Submitted'),
 ('Approved','Approved'), ('Rejected','Rejected');

/* Feedback types */
INSERT INTO dbo.FeedbackTypes (FeedbackTypeCode, FeedbackTypeName) VALUES
 ('General','General'), ('Manager','Manager'),
 ('Department','Department'), ('Company','Company'), ('Other','Other');

/* Roles – expanded for tech company */
INSERT INTO dbo.Roles (RoleName, Description) VALUES
 ('Employee','Regular employee'),
 ('Manager','Team manager with approval rights'),
 ('HR','Human Resources'),
 ('Admin','System administrator'),
 ('CEO','Chief Executive Officer'),
 ('Developer','Software Developer'),
 ('QA','Quality Assurance'),
 ('DevOps','DevOps Engineer'),
 ('Designer','UX/UI Designer'),
 ('Product Manager','Product Manager'),
 ('Scrum Master','Scrum Master');

/* Designations (sample) */
INSERT INTO dbo.Designations (DesignationName) VALUES
 ('Software Engineer I'), ('Software Engineer II'),
 ('Senior Software Engineer'), ('Staff Engineer'),
 ('Principal Engineer'), ('QA Engineer'),
 ('Senior QA Engineer'), ('DevOps Engineer'),
 ('UX Designer'), ('Product Manager');
GO

/* Helpful indexes */
CREATE INDEX IX_Employees_ManagerID   ON dbo.Employees(ManagerID);
CREATE INDEX IX_Employees_TeamID      ON dbo.Employees(TeamID);
CREATE INDEX IX_Employees_LocationID  ON dbo.Employees(LocationID);

CREATE INDEX IX_LeaveApplications_EmployeeID ON dbo.LeaveApplications(EmployeeID);
CREATE INDEX IX_LeaveApplications_StatusCode ON dbo.LeaveApplications(StatusCode);

CREATE INDEX IX_Timesheets_EmployeeID ON dbo.Timesheets(EmployeeID);
CREATE INDEX IX_Timesheets_WeekStart  ON dbo.Timesheets(WeekStartDate);

CREATE INDEX IX_Departments_ParentID  ON dbo.Departments(ParentDepartmentID);
GO


/* ============================================================
   12.  IT Asset Management
   ============================================================ */

/* ---------- status lookup (drives business rules) */
CREATE TABLE dbo.AssetStatuses (
    AssetStatusCode  NVARCHAR(20)  NOT NULL PRIMARY KEY,      -- Assigned, In-Stock, etc.
    AssetStatusName  NVARCHAR(50)  NOT NULL,
    IsAssignable     BIT           NOT NULL,                  -- 1 = can be given to an employee
    IsActive         BIT           NOT NULL CONSTRAINT DF_AssetStatuses_IsActive DEFAULT (1),
    CreatedAt        DATETIME2(3)  NOT NULL CONSTRAINT DF_AssetStatuses_Created DEFAULT SYSUTCDATETIME()
);

/* ---------- type lookup */
CREATE TABLE dbo.AssetTypes (
    AssetTypeID     INT            IDENTITY(1,1) PRIMARY KEY,
    AssetTypeName   NVARCHAR(100)  NOT NULL UNIQUE,
    IsActive        BIT            NOT NULL CONSTRAINT DF_AssetTypes_IsActive DEFAULT (1),
    CreatedAt       DATETIME2(3)   NOT NULL CONSTRAINT DF_AssetTypes_Created DEFAULT SYSUTCDATETIME()
);

/* ---------- master record */
CREATE TABLE dbo.Assets (
    AssetID            INT            IDENTITY(1,1) PRIMARY KEY,
    AssetTag           NVARCHAR(50)   NOT NULL UNIQUE,           -- company barcode / tag
    SerialNumber       NVARCHAR(100)  NULL UNIQUE,
    MACAddress         NVARCHAR(100)  NULL UNIQUE,
    AssetTypeID        INT            NOT NULL,
    AssetStatusCode    NVARCHAR(20)   NOT NULL,
    Model              NVARCHAR(100)  NULL,
    Vendor             NVARCHAR(100)  NULL,
    PurchaseDate       DATE           NULL,
    WarrantyEndDate    DATE           NULL,
    IsUnderContract    BIT            NOT NULL CONSTRAINT DF_Asst_IsUnderContract DEFAULT (0),
    ContractStartDate  DATE           NULL,
    ContractExpiryDate DATE           NULL,
    LocationID         INT            NULL,                      -- where it physically sits
    Notes              NVARCHAR(500)  NULL,
    IsActive           BIT            NOT NULL CONSTRAINT DF_Asst_IsActive DEFAULT (1),
    CreatedAt          DATETIME2(3)   NOT NULL CONSTRAINT DF_Asst_Created DEFAULT SYSUTCDATETIME(),
    UpdatedAt          DATETIME2(3)   NOT NULL CONSTRAINT DF_Asst_Updated DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_Asst_Type      FOREIGN KEY (AssetTypeID)     REFERENCES dbo.AssetTypes(AssetTypeID),
    CONSTRAINT FK_Asst_Status    FOREIGN KEY (AssetStatusCode) REFERENCES dbo.AssetStatuses(AssetStatusCode),
    CONSTRAINT FK_Asst_Location  FOREIGN KEY (LocationID)      REFERENCES dbo.Locations(LocationID),

    /* Contract sanity: either no dates, or both dates present & ordered */
    CONSTRAINT CHK_Asst_ContractDates CHECK (
        (IsUnderContract = 0 AND ContractStartDate IS NULL AND ContractExpiryDate IS NULL) OR
        (IsUnderContract = 1 AND ContractStartDate IS NOT NULL
                           AND ContractExpiryDate IS NOT NULL
                           AND ContractExpiryDate >= ContractStartDate)
    )
);

/* ---------- assignments (one open row per asset) */
CREATE TABLE dbo.AssetAssignments (
    AssignmentID        INT           IDENTITY(1,1) PRIMARY KEY,
    AssetID             INT           NOT NULL,
    EmployeeID          INT           NOT NULL,
    AssignedAt          DATETIME2(3)  NOT NULL CONSTRAINT DF_Asg_AssignedAt DEFAULT SYSUTCDATETIME(),
    DueReturnDate       DATE          NULL,                     -- typically ≤ contract expiry
    ReturnedAt          DATETIME2(3)  NULL,
    ConditionAtAssign   NVARCHAR(200) NULL,
    ConditionAtReturn   NVARCHAR(200) NULL,
    AssignedByID        INT           NOT NULL,                 -- IT staff
    ReceivedByID        INT           NULL,                     -- IT staff on return
    Notes               NVARCHAR(500) NULL,
    CreatedAt           DATETIME2(3)  NOT NULL CONSTRAINT DF_Asg_Created DEFAULT SYSUTCDATETIME(),
    UpdatedAt           DATETIME2(3)  NOT NULL CONSTRAINT DF_Asg_Updated DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_Asg_Asset        FOREIGN KEY (AssetID)      REFERENCES dbo.Assets(AssetID),
    CONSTRAINT FK_Asg_Employee     FOREIGN KEY (EmployeeID)   REFERENCES dbo.Employees(EmployeeID),
    CONSTRAINT FK_Asg_AssignedBy   FOREIGN KEY (AssignedByID) REFERENCES dbo.Employees(EmployeeID),
    CONSTRAINT FK_Asg_ReceivedBy   FOREIGN KEY (ReceivedByID) REFERENCES dbo.Employees(EmployeeID),
    CONSTRAINT CHK_Asg_DueDate CHECK (DueReturnDate IS NULL OR DueReturnDate >= CAST(AssignedAt AS DATE))
);

/* guarantee ONE active assignment per asset */
CREATE UNIQUE INDEX UX_Asg_Active
ON dbo.AssetAssignments(AssetID)
WHERE ReturnedAt IS NULL;

/* ============================================================
   12-A.  Business-rule triggers
   ============================================================ */

GO
/* 1) Validate contract-due rule + 2) sync status */
CREATE OR ALTER TRIGGER dbo.tr_AssetAssignments_BusinessRules
ON dbo.AssetAssignments
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    /* ——— VALIDATION: due date must respect contract expiry ——— */
    IF EXISTS (
        SELECT 1
        FROM inserted i
        JOIN dbo.Assets a ON a.AssetID = i.AssetID
        WHERE a.IsUnderContract = 1
          AND a.ContractExpiryDate IS NOT NULL
          AND (i.DueReturnDate IS NULL OR i.DueReturnDate > a.ContractExpiryDate)
    )
    BEGIN
        RAISERROR('DueReturnDate may not exceed the asset''s ContractExpiryDate.',16,1);
        ROLLBACK TRANSACTION;
        RETURN;
    END

    /* ——— STATUS SYNC: open assignment ⇒ Assigned ——— */
    UPDATE a
    SET    a.AssetStatusCode = 'Assigned',
           a.UpdatedAt       = SYSUTCDATETIME()
    FROM   dbo.Assets a
    JOIN   inserted i ON i.AssetID = a.AssetID
    WHERE  i.ReturnedAt IS NULL;

    /* ——— STATUS SYNC: all assignments closed ⇒ In-Stock ——— */
    UPDATE a
    SET    a.AssetStatusCode = 'In-Stock',
           a.UpdatedAt       = SYSUTCDATETIME()
    FROM   dbo.Assets a
    JOIN   deleted d ON d.AssetID = a.AssetID
    WHERE  d.ReturnedAt IS NULL                           -- row that just closed
      AND  NOT EXISTS (SELECT 1
                       FROM dbo.AssetAssignments z
                       WHERE z.AssetID = a.AssetID
                         AND z.ReturnedAt IS NULL)       -- no other open rows
      AND  a.AssetStatusCode = 'Assigned';
END;
GO

/* ============================================================
   12-B.  Seed lookup data
   ============================================================ */

INSERT INTO dbo.AssetStatuses (AssetStatusCode, AssetStatusName, IsAssignable) VALUES
 ('In-Stock',        'In Stock (unboxed)',          1),
 ('Available',       'Ready for Issue',             1),
 ('Assigned',        'Issued to Employee',          0),
 ('Maintenance',     'Under Maintenance/Repair',    0),
 ('Decommissioning', 'Pending Secure Wipe',         0),
 ('Retired',         'Disposed / Recycled',         0);

INSERT INTO dbo.AssetTypes (AssetTypeName) VALUES
 ('Laptop'), ('Monitor'), ('Keyboard'), ('Mouse'),
 ('Docking Station'), ('Mobile Phone'), ('Headset');

-- Make sure an “IT Support” role exists for asset admins
IF NOT EXISTS (SELECT 1 FROM dbo.Roles WHERE RoleName = 'IT Support')
    INSERT INTO dbo.Roles (RoleName, Description)
    VALUES ('IT Support', 'IT Help-Desk / Asset Management');
GO
