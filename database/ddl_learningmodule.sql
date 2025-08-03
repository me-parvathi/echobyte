-- ────────────────────────────────────────
-- 1. Courses
-- ────────────────────────────────────────
CREATE TABLE dbo.Courses (
    CourseID       INT            IDENTITY(1,1) PRIMARY KEY,
    CourseCode     NVARCHAR(50)   NOT NULL UNIQUE,    -- e.g. “AZ104-CLS”
    Title          NVARCHAR(200)  NOT NULL,
    Difficulty     NVARCHAR(20)   NOT NULL,           -- Beginner / Intermediate / Advanced
    EstimatedHours DECIMAL(5,2)   NOT NULL,           -- e.g. 12.5
    IsActive       BIT            NOT NULL DEFAULT(1),
    CreatedAt      DATETIME2(3)   NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt      DATETIME2(3)   NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ────────────────────────────────────────
-- 2. Course Modules (Lessons)
-- ────────────────────────────────────────
CREATE TABLE dbo.CourseModules (
    ModuleID    INT           IDENTITY(1,1) PRIMARY KEY,
    CourseID    INT           NOT NULL,
    ModuleSeq   INT           NOT NULL,              -- controls ordering
    Title       NVARCHAR(200) NOT NULL,
    VideoURL    NVARCHAR(500) NOT NULL,              -- embed URL or link
    VideoType   CHAR(1)       NOT NULL DEFAULT('I')  -- 'I'=iframe/embed, 'L'=link
        CONSTRAINT CHK_CourseModules_VideoType CHECK (VideoType IN ('I','L')),
    CONSTRAINT FK_CourseModules_Course FOREIGN KEY(CourseID)
        REFERENCES dbo.Courses(CourseID)
);
CREATE UNIQUE INDEX UX_CourseModules_Order
    ON dbo.CourseModules(CourseID, ModuleSeq);

-- ────────────────────────────────────────
-- 3. Employee’s Course Enrollments
-- ────────────────────────────────────────
CREATE TABLE dbo.EmployeeCourses (
    EmployeeCourseID INT          IDENTITY(1,1) PRIMARY KEY,
    EmployeeID       INT          NOT NULL,           -- FK to your Employees table
    CourseID         INT          NOT NULL,
    Status           NVARCHAR(20) NOT NULL DEFAULT('In-Progress'),
        -- In-Progress, Completed, Dropped
    EnrolledAt       DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
    CompletedAt      DATETIME2(3) NULL,
    CONSTRAINT FK_EmployeeCourses_Emp FOREIGN KEY(EmployeeID)
        REFERENCES dbo.Employees(EmployeeID),
    CONSTRAINT FK_EmployeeCourses_Crs FOREIGN KEY(CourseID)
        REFERENCES dbo.Courses(CourseID),
    CONSTRAINT UQ_EmployeeCourses UNIQUE(EmployeeID, CourseID)
);

-- ────────────────────────────────────────
-- 4. Per-Module Completion Tracker
-- ────────────────────────────────────────
CREATE TABLE dbo.EmployeeModuleProgress (
    EmpCourseID INT         NOT NULL,                  -- FK → EmployeeCourses
    ModuleID    INT         NOT NULL,                  -- FK → CourseModules
    CompletedAt DATETIME2   NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_EmployeeModuleProgress PRIMARY KEY(EmpCourseID, ModuleID),
    CONSTRAINT FK_EMPMP_EmpCourse FOREIGN KEY(EmpCourseID)
        REFERENCES dbo.EmployeeCourses(EmployeeCourseID),
    CONSTRAINT FK_EMPMP_Module FOREIGN KEY(ModuleID)
        REFERENCES dbo.CourseModules(ModuleID)
);

-- ────────────────────────────────────────
-- 5. Badge Definitions
-- ────────────────────────────────────────
CREATE TABLE dbo.BadgeDefinitions (
    BadgeID     INT           IDENTITY(1,1) PRIMARY KEY,
    BadgeCode   NVARCHAR(50)  NOT NULL UNIQUE,  -- e.g. “SEC_CHAMP”
    Name        NVARCHAR(200) NOT NULL,
    Description NVARCHAR(500) NULL,
    IconURL     NVARCHAR(500) NULL,
    IsActive    BIT           NOT NULL DEFAULT(1),
    CreatedAt   DATETIME2(3)  NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ────────────────────────────────────────
-- 6. Employee Badges
-- ────────────────────────────────────────
CREATE TABLE dbo.EmployeeBadges (
    EmployeeBadgeID INT        IDENTITY(1,1) PRIMARY KEY,
    EmployeeID      INT        NOT NULL,
    BadgeID         INT        NOT NULL,
    EarnedAt        DATETIME2  NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_EmployeeBadges_Emp FOREIGN KEY(EmployeeID)
        REFERENCES dbo.Employees(EmployeeID),
    CONSTRAINT FK_EmployeeBadges_Bdg FOREIGN KEY(BadgeID)
        REFERENCES dbo.BadgeDefinitions(BadgeID),
    CONSTRAINT UQ_EmployeeBadges UNIQUE(EmployeeID, BadgeID)
);

-- ────────────────────────────────────────
-- 7. Quiz Definitions
-- ────────────────────────────────────────
CREATE TABLE dbo.Quizzes (
    QuizID        INT           IDENTITY(1,1) PRIMARY KEY,
    CourseID      INT           NULL,                  -- optional link to course
    Title         NVARCHAR(200) NOT NULL,
    QuestionCount INT           NOT NULL,
    TimeLimitMin  INT           NOT NULL,              -- in minutes
    PassingPct    DECIMAL(5,2)  NOT NULL,              -- e.g. 70.00
    IsActive      BIT           NOT NULL DEFAULT(1),
    CONSTRAINT FK_Quizzes_Course FOREIGN KEY(CourseID)
        REFERENCES dbo.Courses(CourseID)
);

-- ────────────────────────────────────────
-- 8. Quiz Attempts
-- ────────────────────────────────────────
CREATE TABLE dbo.QuizAttempts (
    AttemptID     INT          IDENTITY(1,1) PRIMARY KEY,
    EmployeeID    INT          NOT NULL,
    QuizID        INT          NOT NULL,
    StartedAt     DATETIME2    NOT NULL DEFAULT SYSUTCDATETIME(),
    CompletedAt   DATETIME2    NULL,
    ScorePct      DECIMAL(5,2) NULL,
    IsPassed      BIT          NULL,
    CONSTRAINT FK_QuizAttempts_Emp FOREIGN KEY(EmployeeID)
        REFERENCES dbo.Employees(EmployeeID),
    CONSTRAINT FK_QuizAttempts_Quiz FOREIGN KEY(QuizID)
        REFERENCES dbo.Quizzes(QuizID)
);

/* ──────────────────────────────────────────────
   1. Question bank
   ────────────────────────────────────────────── */
CREATE TABLE dbo.QuizQuestions (
    QuestionID     INT            IDENTITY(1,1) PRIMARY KEY,
    QuizID         INT            NOT NULL,
    QuestionSeq    INT            NOT NULL,              -- display order within the quiz
    QuestionText   NVARCHAR(MAX)  NOT NULL,
    Explanation    NVARCHAR(MAX)  NULL,                  -- optional
    IsActive       BIT            NOT NULL DEFAULT (1),
    CreatedAt      DATETIME2(3)   NOT NULL DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_QQ_Quiz FOREIGN KEY (QuizID)
        REFERENCES dbo.Quizzes(QuizID),

    CONSTRAINT UX_QQ_Seq UNIQUE (QuizID, QuestionSeq)
);
GO

/* ──────────────────────────────────────────────
   2. Answer choices
   ────────────────────────────────────────────── */
CREATE TABLE dbo.QuizOptions (
    OptionID       INT            IDENTITY(1,1) PRIMARY KEY,
    QuestionID     INT            NOT NULL,
    OptionSeq      INT            NOT NULL,              -- A/B/C… or 1/2/3…
    OptionText     NVARCHAR(MAX)  NOT NULL,
    IsCorrect      BIT            NOT NULL,

    CONSTRAINT FK_QO_Question FOREIGN KEY (QuestionID)
        REFERENCES dbo.QuizQuestions(QuestionID),

    CONSTRAINT UX_QO_Seq UNIQUE (QuestionID, OptionSeq)
);

/* Needed for the composite FK used by QuizResponses */
CREATE UNIQUE INDEX UX_QO_QuestionOption
    ON dbo.QuizOptions (QuestionID, OptionID);
GO

/* ──────────────────────────────────────────────
   3. Learner selections
   ────────────────────────────────────────────── */
CREATE TABLE dbo.QuizResponses (
    AttemptID   INT NOT NULL,     -- FK → QuizAttempts
    QuestionID  INT NOT NULL,     -- FK part 1
    OptionID    INT NOT NULL,     -- FK part 2

    /* one row per selected option (supports multi-select questions) */
    CONSTRAINT PK_QuizResponses PRIMARY KEY (AttemptID, QuestionID, OptionID),

    CONSTRAINT FK_QR_Attempt FOREIGN KEY (AttemptID)
        REFERENCES dbo.QuizAttempts(AttemptID) ON DELETE CASCADE,

    /* Guarantees the (QuestionID, OptionID) pair is valid */
    CONSTRAINT FK_QR_QuestionOption FOREIGN KEY (QuestionID, OptionID)
        REFERENCES dbo.QuizOptions (QuestionID, OptionID)
);
GO

/* ──────────────────────────────────────────────
   4. Optional per-question scoring cache
   ────────────────────────────────────────────── */
CREATE TABLE dbo.QuizResponseScores (
    AttemptID  INT NOT NULL,
    QuestionID INT NOT NULL,
    IsCorrect  BIT NOT NULL,

    CONSTRAINT PK_QRS PRIMARY KEY (AttemptID, QuestionID),

    CONSTRAINT FK_QRS_Attempt FOREIGN KEY (AttemptID)
        REFERENCES dbo.QuizAttempts(AttemptID) ON DELETE CASCADE,

    CONSTRAINT FK_QRS_Question FOREIGN KEY (QuestionID)
        REFERENCES dbo.QuizQuestions(QuestionID)
);
GO