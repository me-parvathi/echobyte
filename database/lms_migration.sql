-- =====================================================================
-- LMS Database Migration Script
-- Adds TimeSpentMinutes to EmployeeModuleProgress and creates QuizAttemptLimits table
-- =====================================================================

-- Add TimeSpentMinutes column to EmployeeModuleProgress table
IF NOT EXISTS (
    SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'EmployeeModuleProgress' 
    AND COLUMN_NAME = 'TimeSpentMinutes'
)
BEGIN
    ALTER TABLE dbo.EmployeeModuleProgress 
    ADD TimeSpentMinutes INT NULL;
    
    PRINT '✓ Added TimeSpentMinutes column to EmployeeModuleProgress table';
END
ELSE
BEGIN
    PRINT 'ℹ TimeSpentMinutes column already exists in EmployeeModuleProgress table';
END

-- Create QuizAttemptLimits table
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'QuizAttemptLimits')
BEGIN
    CREATE TABLE dbo.QuizAttemptLimits (
        LimitID         INT           IDENTITY(1,1) PRIMARY KEY,
        EmployeeID      INT           NOT NULL,
        QuizID          INT           NOT NULL,
        AttemptCount    INT           NOT NULL DEFAULT(0),
        LastAttemptDate DATETIME2     NULL,
        CooldownUntil   DATETIME2     NULL,  -- When cooldown period ends
        CreatedAt       DATETIME2(3)  NOT NULL DEFAULT SYSUTCDATETIME(),
        UpdatedAt       DATETIME2(3)  NOT NULL DEFAULT SYSUTCDATETIME(),
        
        CONSTRAINT FK_QuizAttemptLimits_Emp FOREIGN KEY(EmployeeID)
            REFERENCES dbo.Employees(EmployeeID),
        CONSTRAINT FK_QuizAttemptLimits_Quiz FOREIGN KEY(QuizID)
            REFERENCES dbo.Quizzes(QuizID),
        CONSTRAINT CHK_QuizAttemptLimits_AttemptCount CHECK (AttemptCount >= 0)
    );
    
    -- Create unique index to prevent duplicate records
    CREATE UNIQUE INDEX UX_QuizAttemptLimits_EmployeeQuiz
        ON dbo.QuizAttemptLimits(EmployeeID, QuizID);
    
    PRINT '✓ Created QuizAttemptLimits table';
END
ELSE
BEGIN
    PRINT 'ℹ QuizAttemptLimits table already exists';
END

-- Create trigger to update UpdatedAt timestamp
IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_QuizAttemptLimits_UpdatedAt')
BEGIN
    EXEC('
    CREATE TRIGGER TR_QuizAttemptLimits_UpdatedAt
    ON dbo.QuizAttemptLimits
    AFTER UPDATE
    AS
    BEGIN
        UPDATE dbo.QuizAttemptLimits
        SET UpdatedAt = SYSUTCDATETIME()
        FROM dbo.QuizAttemptLimits qal
        INNER JOIN inserted i ON qal.LimitID = i.LimitID;
    END
    ');
    
    PRINT '✓ Created trigger for QuizAttemptLimits UpdatedAt';
END
ELSE
BEGIN
    PRINT 'ℹ Trigger for QuizAttemptLimits UpdatedAt already exists';
END

-- Create some sample badge definitions for course completion
IF NOT EXISTS (SELECT * FROM dbo.BadgeDefinitions WHERE BadgeCode = 'COURSE_6_COMPLETE')
BEGIN
    INSERT INTO dbo.BadgeDefinitions (BadgeCode, Name, Description, IconURL, IsActive)
    VALUES 
    ('COURSE_6_COMPLETE', 'Azure Fundamentals Master', 'Completed the Azure Fundamentals course', '/badges/azure-master.png', 1),
    ('QUIZ_1_MASTERY', 'Azure Infrastructure Expert', 'Mastered Azure Infrastructure quiz', '/badges/infrastructure-expert.png', 1),
    ('QUIZ_2_MASTERY', 'Azure Developer Expert', 'Mastered Azure for Developers quiz', '/badges/developer-expert.png', 1),
    ('QUIZ_3_MASTERY', 'Machine Learning Beginner', 'Mastered Machine Learning for Beginners quiz', '/badges/ml-beginner.png', 1),
    ('QUIZ_4_MASTERY', 'AI Fundamentals Expert', 'Mastered Azure AI Fundamentals quiz', '/badges/ai-expert.png', 1),
    ('QUIZ_5_MASTERY', 'Data Scientist Associate', 'Mastered Azure Data Scientist Associate quiz', '/badges/data-scientist.png', 1);
    
    PRINT '✓ Created sample badge definitions';
END
ELSE
BEGIN
    PRINT 'ℹ Sample badge definitions already exist';
END

PRINT '================================================================';
PRINT '✓ LMS Database Migration Completed Successfully';
PRINT '================================================================'; 