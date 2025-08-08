/* =====================================================================
   Load five quizzes (50 questions total) into course "Azure Fundamentals"
   FIXED VERSION - Includes existence checks to prevent unique constraint violations
   ===================================================================== */
SET XACT_ABORT, NOCOUNT ON;   -- fail fast on any error

BEGIN TRY
    BEGIN TRAN;

    /* ─────────────────────────────────────────
       0. Ensure the parent course row exists
       ───────────────────────────────────────── */
    DECLARE @CourseID INT;

    SELECT @CourseID = CourseID
    FROM   dbo.Courses
    WHERE  CourseCode = N'AZURE100';

    IF @CourseID IS NULL
    BEGIN
        INSERT dbo.Courses ( CourseCode, Title, Difficulty, EstimatedHours, IsActive)
        VALUES (N'AZURE100',N'Azure Fundamentals', N'Beginner',	7.00, 1);

        SET @CourseID = SCOPE_IDENTITY();
    END

/* =====================================================================
   1. Quiz : Azure Infrastructure
   ===================================================================== */
    DECLARE @QuizID INT;

    SELECT @QuizID = QuizID
    FROM   dbo.Quizzes
    WHERE  CourseID = @CourseID
      AND  Title     = N'Azure Infrastructure';

    IF @QuizID IS NULL
    BEGIN
        INSERT dbo.Quizzes (CourseID, Title, QuestionCount, TimeLimitMin, PassingPct, IsActive)
        VALUES (@CourseID, N'Azure Infrastructure', 10, 30, 70.00, 1);
        SET @QuizID = SCOPE_IDENTITY();
    END

    /* Q1 ---------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 1)
    BEGIN
        DECLARE @Q1 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 1,
                N'What is the purpose of Azure Resource Manager (ARM)?',
                N'ARM enables infrastructure deployment and management. Others are subsets of its role.');
        SET @Q1 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@Q1, 1, N'A. Manage storage', 0),
            (@Q1, 2, N'B. Deploy apps', 0),
            (@Q1, 3, N'C. Deploy and manage resources', 1),
            (@Q1, 4, N'D. Monitor logs', 0);
    END

    /* Q2 ---------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 2)
    BEGIN
        DECLARE @Q2 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 2,
                N'Which service provides scalable cloud computing in Azure?',
                N'VMs provide compute power; others serve storage/networking purposes.');
        SET @Q2 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@Q2, 1, N'A. Azure SQL', 0),
            (@Q2, 2, N'B. Virtual Machines', 1),
            (@Q2, 3, N'C. Blob Storage', 0),
            (@Q2, 4, N'D. CDN', 0);
    END

    /* Q3 ---------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 3)
    BEGIN
        DECLARE @Q3 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 3,
                N'Azure Virtual Network is most similar to:',
                N'Virtual Networks act like traditional networks to connect resources.');
        SET @Q3 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@Q3, 1, N'A. Hard drive', 0),
            (@Q3, 2, N'B. Router and Switch', 1),
            (@Q3, 3, N'C. RAM', 0),
            (@Q3, 4, N'D. Keyboard', 0);
    END

    /* Q4 ---------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 4)
    BEGIN
        DECLARE @Q4 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 4,
                N'Which Azure storage type is best for unstructured data?',
                N'Blob Storage is ideal for images, videos, and other unstructured data.');
        SET @Q4 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@Q4, 1, N'A. Queue Storage', 0),
            (@Q4, 2, N'B. Blob Storage', 1),
            (@Q4, 3, N'C. File Storage', 0),
            (@Q4, 4, N'D. Table Storage', 0);
    END

    /* Q5 ---------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 5)
    BEGIN
        DECLARE @Q5 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 5,
                N'What is an Azure Availability Zone?',
                N'Zones offer fault tolerance and high availability across data centers.');
        SET @Q5 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@Q5, 1, N'A. Monitoring tool', 0),
            (@Q5, 2, N'B. Developer environment', 0),
            (@Q5, 3, N'C. Physical location for redundancy', 1),
            (@Q5, 4, N'D. VM Size', 0);
    END

    /* Q6 ---------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 6)
    BEGIN
        DECLARE @Q6 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 6,
                N'Which tool allows monitoring performance and health of Azure resources?',
                N'Azure Monitor collects logs and metrics for resource health.');
        SET @Q6 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@Q6, 1, N'A. DevOps', 0),
            (@Q6, 2, N'B. Azure Monitor', 1),
            (@Q6, 3, N'C. App Insights', 0),
            (@Q6, 4, N'D. Azure Pipelines', 0);
    END

    /* Q7 ---------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 7)
    BEGIN
        DECLARE @Q7 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 7,
                N'What is the main advantage of Azure Load Balancer?',
                N'Azure Load Balancer spreads traffic across resources for better performance.');
        SET @Q7 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@Q7, 1, N'A. Storing logs', 0),
            (@Q7, 2, N'B. Distributing traffic', 1),
            (@Q7, 3, N'C. Encrypting data', 0),
            (@Q7, 4, N'D. Creating containers', 0);
    END

    /* Q8 ---------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 8)
    BEGIN
        DECLARE @Q8 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 8,
                N'A Resource Group in Azure is:',
                N'Resource groups allow logical grouping and unified management of resources.');
        SET @Q8 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@Q8, 1, N'A. A billing method', 0),
            (@Q8, 2, N'B. A container for related resources', 1),
            (@Q8, 3, N'C. A VM type', 0),
            (@Q8, 4, N'D. A database', 0);
    END

    /* Q9 ---------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 9)
    BEGIN
        DECLARE @Q9 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 9,
                N'Which component helps in automating Azure deployments?',
                N'ARM templates define infrastructure as code for reproducible deployments.');
        SET @Q9 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@Q9, 1, N'A. SQL', 0),
            (@Q9, 2, N'B. ARM Templates', 1),
            (@Q9, 3, N'C. Azure Monitor', 0),
            (@Q9, 4, N'D. VNet', 0);
    END

    /* Q10 --------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 10)
    BEGIN
        DECLARE @Q10 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 10,
                N'Azure Regions are:',
                N'Azure Regions represent geographic areas where data centers are located.');
        SET @Q10 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@Q10, 1, N'A. Data centers on-prem', 0),
            (@Q10, 2, N'B. Geo locations for Azure services', 1),
            (@Q10, 3, N'C. Code libraries', 0),
            (@Q10, 4, N'D. Network types', 0);
    END

    PRINT N'✓ Loaded 10 questions for quiz "Azure Infrastructure" (QuizID=' + CAST(@QuizID AS nvarchar(20)) + N')';

/* =====================================================================
   2. Quiz : Azure for Developers
   ===================================================================== */
    SELECT @QuizID = QuizID
    FROM   dbo.Quizzes
    WHERE  CourseID = @CourseID
      AND  Title     = N'Azure for Developers';

    IF @QuizID IS NULL
    BEGIN
        INSERT dbo.Quizzes (CourseID, Title, QuestionCount, TimeLimitMin, PassingPct, IsActive)
        VALUES (@CourseID, N'Azure for Developers', 10, 30, 70.00, 1);
        SET @QuizID = SCOPE_IDENTITY();
    END

    /* Q1 ---------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 1)
    BEGIN
        DECLARE @D_Q1 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 1,
                N'What does Azure App Service primarily allow you to do?',
                N'Azure App Service is a PaaS offering designed to host web apps.');
        SET @D_Q1 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@D_Q1, 1, N'A. Host static websites only', 0),
            (@D_Q1, 2, N'B. Create machine learning models', 0),
            (@D_Q1, 3, N'C. Deploy and scale web applications', 1),
            (@D_Q1, 4, N'D. Send emails', 0);
    END

    /* Q2 ---------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 2)
    BEGIN
        DECLARE @D_Q2 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 2,
                N'Which tool helps automate developer workflows and provisioning in Azure?',
                N'azd automates setup and deployment for developers.');
        SET @D_Q2 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@D_Q2, 1, N'A. Azure Boards', 0),
            (@D_Q2, 2, N'B. Azure Developer CLI (azd)', 1),
            (@D_Q2, 3, N'C. GitHub Pages', 0),
            (@D_Q2, 4, N'D. Azure Logic Apps', 0);
    END

    /* Q3 ---------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 3)
    BEGIN
        DECLARE @D_Q3 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 3,
                N'What is a common use case for Azure Functions?',
                N'Functions run lightweight code in response to events - serverless computing.');
        SET @D_Q3 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@D_Q3, 1, N'A. Running event-driven serverless code', 1),
            (@D_Q3, 2, N'B. Hosting databases', 0),
            (@D_Q3, 3, N'C. Building static sites', 0),
            (@D_Q3, 4, N'D. Managing identity', 0);
    END

    /* Q4 ---------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 4)
    BEGIN
        DECLARE @D_Q4 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 4,
                N'Which Azure service is best for managing application secrets and keys?',
                N'Key Vault securely stores secrets, keys, and certificates.');
        SET @D_Q4 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@D_Q4, 1, N'A. Azure Blob Storage', 0),
            (@D_Q4, 2, N'B. Azure Identity', 0),
            (@D_Q4, 3, N'C. Azure Key Vault', 1),
            (@D_Q4, 4, N'D. Azure DevOps', 0);
    END

    /* Q5 ---------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 5)
    BEGIN
        DECLARE @D_Q5 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 5,
                N'What programming languages are supported by Azure Functions?',
                N'Azure Functions supports multiple languages, making it flexible.');
        SET @D_Q5 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@D_Q5, 1, N'A. Only C#', 0),
            (@D_Q5, 2, N'B. C#, JavaScript, Python, and more', 1),
            (@D_Q5, 3, N'C. Only Python', 0),
            (@D_Q5, 4, N'D. Only Java', 0);
    END

    /* Q6 ---------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 6)
    BEGIN
        DECLARE @D_Q6 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 6,
                N'Which of the following best describes Azure SDKs?',
                N'Azure SDKs provide language-specific libraries for developers to interact with Azure.');
        SET @D_Q6 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@D_Q6, 1, N'A. Frontend frameworks', 0),
            (@D_Q6, 2, N'B. Developer libraries for integrating Azure services', 1),
            (@D_Q6, 3, N'C. Microsoft 365 APIs', 0),
            (@D_Q6, 4, N'D. GitHub integrations', 0);
    END

    /* Q7 ---------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 7)
    BEGIN
        DECLARE @D_Q7 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 7,
                N'Which service simplifies CI/CD for Azure-based apps?',
                N'Azure DevOps provides pipelines, repos, and boards for software delivery.');
        SET @D_Q7 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@D_Q7, 1, N'A. Azure Monitor', 0),
            (@D_Q7, 2, N'B. Azure DevTest Labs', 0),
            (@D_Q7, 3, N'C. Azure DevOps', 1),
            (@D_Q7, 4, N'D. Azure Advisor', 0);
    END

    /* Q8 ---------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 8)
    BEGIN
        DECLARE @D_Q8 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 8,
                N'How do Azure Resource Manager (ARM) templates help developers?',
                N'ARM templates define resources as JSON for repeatable deployments.');
        SET @D_Q8 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@D_Q8, 1, N'A. Store user data', 0),
            (@D_Q8, 2, N'B. Create mobile apps', 0),
            (@D_Q8, 3, N'C. Automate infrastructure provisioning', 1),
            (@D_Q8, 4, N'D. Write backend logic', 0);
    END

    /* Q9 ---------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 9)
    BEGIN
        DECLARE @D_Q9 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 9,
                N'What is the benefit of using the Azure Developer CLI over traditional CLI tools?',
                N'azd provides developer-specific scaffolding and auto-provisions cloud resources.');
        SET @D_Q9 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@D_Q9, 1, N'A. Better font rendering', 0),
            (@D_Q9, 2, N'B. Faster project scaffolding and environment setup', 1),
            (@D_Q9, 3, N'C. No learning curve', 0),
            (@D_Q9, 4, N'D. It doesn''t need authentication', 0);
    END

    /* Q10 --------------------------------------------------------------- */
    IF NOT EXISTS (SELECT 1 FROM dbo.QuizQuestions WHERE QuizID = @QuizID AND QuestionSeq = 10)
    BEGIN
        DECLARE @D_Q10 INT;
        INSERT dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
        VALUES (@QuizID, 10,
                N'Which service would you use to trigger an Azure Function based on blob uploads?',
                N'Event Grid can trigger functions in response to blob storage events.');
        SET @D_Q10 = SCOPE_IDENTITY();

        INSERT dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
            (@D_Q10, 1, N'A. Azure Monitor', 0),
            (@D_Q10, 2, N'B. Azure Kubernetes Service', 0),
            (@D_Q10, 3, N'C. Azure Event Grid', 1),
            (@D_Q10, 4, N'D. Azure Firewall', 0);
    END

    PRINT N'✓ Loaded 10 questions for quiz "Azure for Developers" (QuizID=' + CAST(@QuizID AS nvarchar(20)) + N')';

    /* ================================================================== */
    PRINT N'================================================================';
    PRINT N'✓ ALL QUIZZES HAVE BEEN LOADED INTO COURSE "' 
          + N'Azure Fundamentals" (CourseID=' + CAST(@CourseID AS nvarchar(20)) + N')';
    PRINT N'================================================================';

    COMMIT;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK;
    THROW;  -- re-raise the original error with line number
END CATCH;
