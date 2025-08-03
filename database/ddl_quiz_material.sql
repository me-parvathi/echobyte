-- =====================================================================
--  FULL INSERT SCRIPT  –  GENERATED 2025-08-03 FROM  AI Chatbot Quizzes.xlsx
--  CourseID = 6
--  5 quizzes, 10 questions each  → 50 questions total
-- =====================================================================

-- ---------------------------------------------------------------
-- Quiz: Azure Infrastructure
-- ---------------------------------------------------------------
DECLARE @QuizID_1 INT;
SELECT @QuizID_1 = QuizID
FROM   dbo.Quizzes
WHERE  CourseID = 6
  AND  Title     = N'Azure Infrastructure';

IF @QuizID_1 IS NULL
BEGIN
    INSERT INTO dbo.Quizzes (CourseID, Title, QuestionCount, TimeLimitMin, PassingPct, IsActive)
    VALUES (6, N'Azure Infrastructure', 10, 30, 70.00, 1);
    SET @QuizID_1 = SCOPE_IDENTITY();
END

-- Q1
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_1, 1,
N'What is the purpose of Azure Resource Manager (ARM)?',
N'Explanation: ARM enables infrastructure deployment and management. Others are subsets of its role.');
DECLARE @Q1_1 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_1, 1, N'A. Manage storage', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_1, 2, N'B. Deploy apps', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_1, 3, N'C. Deploy  and manage resources', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_1, 4, N'D. Monitor logs', 0);

-- Q2
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_1, 2,
N'Which service provides scalable cloud computing in Azure?',
N'Explanation: VMs provide compute power; others serve storage/networking purposes.');
DECLARE @Q1_2 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_2, 1, N'A. Azure SQL', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_2, 2, N'B. Virtual Machines', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_2, 3, N'C. Blob Storage', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_2, 4, N'D. CDN', 0);

-- Q3
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_1, 3,
N'Azure Virtual Network is most similar to:',
N'Explanation: Virtual Networks act like traditional networks to connect resources.');
DECLARE @Q1_3 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_3, 1, N'A. Hard drive', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_3, 2, N'B. Router and Switch', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_3, 3, N'C. RAM', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_3, 4, N'D. Keyboard', 0);

-- Q4
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_1, 4,
N'Which Azure storage type is best for unstructured data?',
N'Explanation: Blob Storage is ideal for images, videos, and other unstructured data.');
DECLARE @Q1_4 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_4, 1, N'A. Queue Storage', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_4, 2, N'B. Blob Storage', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_4, 3, N'C. File Storage', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_4, 4, N'D. Table Storage', 0);

-- Q5
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_1, 5,
N'What is an Azure Availability Zone?',
N'Explanation: Zones offer fault tolerance and high availability across data centers.');
DECLARE @Q1_5 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_5, 1, N'A. Monitoring tool', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_5, 2, N'B. Developer environment', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_5, 3, N'C. Physical location for redundancy', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_5, 4, N'D. VM Size', 0);

-- Q6
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_1, 6,
N'Which tool allows monitoring performance and health of Azure resources?',
N'Explanation: Azure Monitor collects logs and metrics for resource health.');
DECLARE @Q1_6 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_6, 1, N'A. DevOps', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_6, 2, N'B. Azure Monitor', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_6, 3, N'C. App Insights', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_6, 4, N'D. Azure Pipelines', 0);

-- Q7
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_1, 7,
N'What is the main advantage of Azure Load Balancer?',
N'Explanation: Azure Load Balancer spreads traffic across resources for better performance.');
DECLARE @Q1_7 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_7, 1, N'A. Storing logs', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_7, 2, N'B. Distributing traffic', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_7, 3, N'C. Encrypting data', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_7, 4, N'D. Creating containers', 0);

-- Q8
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_1, 8,
N'A Resource Group in Azure is:',
N'Explanation: Resource groups allow logical grouping and unified management of resources.');
DECLARE @Q1_8 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_8, 1, N'A. A billing method', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_8, 2, N'B. A container for related resources', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_8, 3, N'C. A VM type', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_8, 4, N'D. A database', 0);

-- Q9
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_1, 9,
N'Which component helps in automating Azure deployments?',
N'Explanation: ARM templates define infrastructure as code for reproducible deployments.');
DECLARE @Q1_9 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_9, 1, N'A. SQL', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_9, 2, N'B. ARM Templates', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_9, 3, N'C. Azure Monitor', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_9, 4, N'D. VNet', 0);

-- Q10
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_1, 10,
N'Azure Regions are:',
N'Explanation: Azure Regions represent geographic areas where data centers are located.');
DECLARE @Q1_10 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_10, 1, N'A. Data centers on-prem', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_10, 2, N'B. Geo locations for Azure services', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_10, 3, N'C. Code libraries', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q1_10, 4, N'D. Network types', 0);

PRINT '✓ Loaded 10 questions for quiz "Azure Infrastructure" (QuizID=' + CAST(@QuizID_1 AS NVARCHAR(20)) + ')';

-- ---------------------------------------------------------------
-- Quiz: Azure for Developers
-- ---------------------------------------------------------------
DECLARE @QuizID_2 INT;
SELECT @QuizID_2 = QuizID
FROM   dbo.Quizzes
WHERE  CourseID = 6
  AND  Title     = N'Azure for Developers';

IF @QuizID_2 IS NULL
BEGIN
    INSERT INTO dbo.Quizzes (CourseID, Title, QuestionCount, TimeLimitMin, PassingPct, IsActive)
    VALUES (6, N'Azure for Developers', 10, 30, 70.00, 1);
    SET @QuizID_2 = SCOPE_IDENTITY();
END

-- Q1
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_2, 1,
N'What does Azure App Service primarily allow you to do?',
N'Explanation: Azure App Service is a PaaS offering designed to host web apps.');
DECLARE @Q2_1 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_1, 1, N'A. Host static websites only', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_1, 2, N'B. Create machine learning models', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_1, 3, N'C. Deploy and scale web applications', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_1, 4, N'D. Send emails', 0);

-- Q2
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_2, 2,
N'Which tool helps automate developer workflows and provisioning in Azure?',
N'Explanation: azd automates setup and deployment for developers.');
DECLARE @Q2_2 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_2, 1, N'A. Azure Boards', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_2, 2, N'B. Azure Developer CLI (azd)', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_2, 3, N'C. GitHub Pages', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_2, 4, N'D. Azure Logic Apps', 0);

-- Q3
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_2, 3,
N'What is a common use case for Azure Functions?',
N'Explanation: Functions run lightweight code in response to events - serverless computing.');
DECLARE @Q2_3 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_3, 1, N'B. Running event-driven serverless code', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_3, 2, N'B. Router and Switch', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_3, 3, N'C. Building static sites', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_3, 4, N'D. Managing identity', 0);

-- Q4
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_2, 4,
N'Which Azure service is best for managing application secrets and keys?',
N'Explanation: Key Vault securely stores secrets, keys, and certificates.');
DECLARE @Q2_4 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_4, 1, N'A. Azure Blob Storage', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_4, 2, N'B. Azure Identity', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_4, 3, N'C. Azure Key Vault', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_4, 4, N'D. Azure DevOps', 0);

-- Q5
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_2, 5,
N'What programming languages are supported by Azure Functions?',
N'Explanation: Azure Functions supports multiple languages, making it flexible.');
DECLARE @Q2_5 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_5, 1, N'A. Only C#', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_5, 2, N'B. C#, JavaScript, Python, and more', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_5, 3, N'C. Only Python', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_5, 4, N'D. Only Java', 0);

-- Q6
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_2, 6,
N'Which of the following best describes Azure SDKs?',
N'Explanation: Azure SDKs provide language-specific libraries for developers to interact with Azure.');
DECLARE @Q2_6 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_6, 1, N'A. Frontend frameworks', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_6, 2, N'B. Developer libraries for integrating Azure services', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_6, 3, N'C. Microsoft 365 APIs', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_6, 4, N'D. GitHub integrations', 0);

-- Q7
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_2, 7,
N'Which service simplifies CI/CD for Azure-based apps?',
N'Explanation: Azure DevOps provides pipelines, repos, and boards for software delivery.');
DECLARE @Q2_7 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_7, 1, N'A. Azure Monitor', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_7, 2, N'B. Azure DevTest Labs', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_7, 3, N'C. Azure DevOps', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_7, 4, N'D. Azure Advisor', 0);

-- Q8
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_2, 8,
N'How do Azure Resource Manager (ARM) templates help developers?',
N'Explanation: ARM templates define resources as JSON for repeatable deployments.');
DECLARE @Q2_8 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_8, 1, N'A. Store user data', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_8, 2, N'B. Create mobile apps', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_8, 3, N'C. Automate infrastructure provisioning', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_8, 4, N'D. Write backend logic', 0);

-- Q9
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_2, 9,
N'What is the benefit of using the Azure Developer CLI over traditional CLI tools?',
N'Explanation: azd provides developer-specific scaffolding and auto-provisions cloud resources.');
DECLARE @Q2_9 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_9, 1, N'A. Better font rendering', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_9, 2, N'B. Faster project scaffolding and environment setup', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_9, 3, N'C. No learning curve', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_9, 4, N'D. It doesn''t need authentication', 0);

-- Q10
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_2, 10,
N'Which service would you use to trigger an Azure Function based on blob uploads?',
N'Explanation: Event Grid can trigger functions in response to blob storage events.');
DECLARE @Q2_10 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_10, 1, N'A. Azure Monitor', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_10, 2, N'B. Azure Kubernetes Service', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_10, 3, N'C. Azure Event Grid', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q2_10, 4, N'D. Azure Firewall', 0);

PRINT '✓ Loaded 10 questions for quiz "Azure for Developers" (QuizID=' + CAST(@QuizID_2 AS NVARCHAR(20)) + ')';

-- ---------------------------------------------------------------
-- Quiz: Machine Learning for Beginners
-- ---------------------------------------------------------------
DECLARE @QuizID_3 INT;
SELECT @QuizID_3 = QuizID
FROM   dbo.Quizzes
WHERE  CourseID = 6
  AND  Title     = N'Machine Learning for Beginners';

IF @QuizID_3 IS NULL
BEGIN
    INSERT INTO dbo.Quizzes (CourseID, Title, QuestionCount, TimeLimitMin, PassingPct, IsActive)
    VALUES (6, N'Machine Learning for Beginners', 10, 30, 70.00, 1);
    SET @QuizID_3 = SCOPE_IDENTITY();
END

-- Q1
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_3, 1,
N'What is the goal of machine learning?',
N'Explanation: ML focuses on learning from data and making predictions.');
DECLARE @Q3_1 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_1, 1, N'A. Send emails automatically', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_1, 2, N'B. Enable systems to learn from data without being explicitly programmed', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_1, 3, N'C. Compress files', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_1, 4, N'D. Create websites', 0);

-- Q2
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_3, 2,
N'Which of the following is an example of supervised learning?',
N'Explanation: Supervised learning uses labeled data for prediction tasks.');
DECLARE @Q3_2 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_2, 1, N'A. Clustering similar news articles', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_2, 2, N'B. Predicting house prices based on historical data', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_2, 3, N'C. Grouping customer types', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_2, 4, N'D. Dimensionality reduction', 0);

-- Q3
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_3, 3,
N'What are features in a dataset?',
N'Explanation: Features are the inputs to an ML model.');
DECLARE @Q3_3 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_3, 1, N'A. Colors', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_3, 2, N'B. Input variables used to make predictions', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_3, 3, N'C. Hidden files', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_3, 4, N'D. Predictions', 0);

-- Q4
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_3, 4,
N'Which language is most commonly used for beginner ML projects?',
N'Explanation: Python is widely used due to its simplicity and available libraries like scikit-learn.');
DECLARE @Q3_4 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_4, 1, N'A. Java', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_4, 2, N'B. R', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_4, 3, N'C. Python', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_4, 4, N'D. Ruby', 0);

-- Q5
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_3, 5,
N'Which of the following is a real-world application of machine learning?',
N'Explanation: ML helps in classifying spam vs. non-spam emails.');
DECLARE @Q3_5 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_5, 1, N'A. Generating electricity', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_5, 2, N'B. Email spam filtering', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_5, 3, N'C. Copying files', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_5, 4, N'D. Playing music', 0);

-- Q6
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_3, 6,
N'What is a training set?',
N'Explanation: Training sets are the labeled examples the model learns from.');
DECLARE @Q3_6 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_6, 1, N'A. A finished model', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_6, 2, N'B. A test question', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_6, 3, N'C. Data used to teach the model', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_6, 4, N'D. A function in Python', 0);

-- Q7
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_3, 7,
N'Which library is commonly used in Python for machine learning?',
N'Explanation: Scikit-learn provides simple tools for building ML models.');
DECLARE @Q3_7 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_7, 1, N'A. React', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_7, 2, N'B. Scikit-learn', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_7, 3, N'C. Express.js', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_7, 4, N'D. NumPy only', 0);

-- Q8
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_3, 8,
N'Which evaluation metric would you most likely use for a classification model?',
N'Explanation: Accuracy is a basic metric for classification (true predictions / total).');
DECLARE @Q3_8 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_8, 1, N'A. Mean squared error', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_8, 2, N'B. Accuracy', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_8, 3, N'C. Range', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_8, 4, N'D. Median', 0);

-- Q9
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_3, 9,
N'What is overfitting in machine learning?',
N'Explanation: Overfitting means the model "memorizes" training data and doesn''t generalize.');
DECLARE @Q3_9 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_9, 1, N'A. Too much RAM usage', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_9, 2, N'B. Model performs well on training data but poorly on new data', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_9, 3, N'C. Model runs too fast', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_9, 4, N'D. Model has no features', 0);

-- Q10
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_3, 10,
N'What is the purpose of using a validation set in ML?',
N'Explanation: Validation sets help adjust model settings without touching the test set.');
DECLARE @Q3_10 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_10, 1, N'A. Speed up training', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_10, 2, N'B. Tune hyperparameters and prevent overfitting', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_10, 3, N'C. Delete duplicates', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q3_10, 4, N'D. Secure the model', 0);

PRINT '✓ Loaded 10 questions for quiz "Machine Learning for Beginners" (QuizID=' + CAST(@QuizID_3 AS NVARCHAR(20)) + ')';

-- ---------------------------------------------------------------
-- Quiz: Azure AI Fundamentals (AI-900)
-- ---------------------------------------------------------------
DECLARE @QuizID_4 INT;
SELECT @QuizID_4 = QuizID
FROM   dbo.Quizzes
WHERE  CourseID = 6
  AND  Title     = N'Azure AI Fundamentals (AI-900)';

IF @QuizID_4 IS NULL
BEGIN
    INSERT INTO dbo.Quizzes (CourseID, Title, QuestionCount, TimeLimitMin, PassingPct, IsActive)
    VALUES (6, N'Azure AI Fundamentals (AI-900)', 10, 30, 70.00, 1);
    SET @QuizID_4 = SCOPE_IDENTITY();
END

-- Q1
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_4, 1,
N'What does AI stand for?',
N'Explanation: AI stands for Artificial Intelligence – systems that simulate human intelligence.');
DECLARE @Q4_1 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_1, 1, N'A. Application Interface', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_1, 2, N'B. Artificial Intelligence', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_1, 3, N'C. Automated Integration', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_1, 4, N'D. Azure Integration', 0);

-- Q2
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_4, 2,
N'Which Azure service lets you analyze images and recognize faces?',
N'Explanation: Computer Vision extracts information from images and videos.');
DECLARE @Q4_2 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_2, 1, N'A. Azure Bot Service', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_2, 2, N'B. Azure Computer Vision', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_2, 3, N'C. Azure Machine Learning', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_2, 4, N'D. Azure Data Factory', 0);

-- Q3
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_4, 3,
N'Which Azure service is used to build and deploy chatbots?',
N'Explanation: Bot Service allows developers to build conversational bots.');
DECLARE @Q4_3 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_3, 1, N'A. Azure OpenAI', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_3, 2, N'B. Azure Bot Service', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_3, 3, N'C. Azure Functions', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_3, 4, N'D. Azure SignalR', 0);

-- Q4
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_4, 4,
N'Which of the following is NOT part of Azure Cognitive Services?',
N'Explanation: DevOps is for software lifecycle management, not AI services.');
DECLARE @Q4_4 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_4, 1, N'A. Vision', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_4, 2, N'B. Speech', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_4, 3, N'C. Azure DevOps', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_4, 4, N'D. Language', 0);

-- Q5
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_4, 5,
N'Which Azure service provides pre-built machine learning models?',
N'Explanation: Cognitive Services offer ready-to-use AI capabilities.');
DECLARE @Q4_5 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_5, 1, N'A. Azure Monitor', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_5, 2, N'B. Azure Cognitive Services', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_5, 3, N'C. Azure Kubernetes', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_5, 4, N'D. Azure SQL', 0);

-- Q6
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_4, 6,
N'What does natural language processing (NLP) enable?',
N'Explanation: NLP helps computers process and analyze human language.');
DECLARE @Q4_6 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_6, 1, N'A. Image captioning', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_6, 2, N'B. Face detection', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_6, 3, N'C. Understanding and responding to text or speech', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_6, 4, N'D. Video editing', 0);

-- Q7
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_4, 7,
N'Which Azure service allows you to train custom ML models?',
N'Explanation: Azure ML enables custom model training and deployment.');
DECLARE @Q4_7 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_7, 1, N'A. Azure AI Studio', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_7, 2, N'B. Azure Machine Learning', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_7, 3, N'C. Azure Logic Apps', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_7, 4, N'D. Azure CDN', 0);

-- Q8
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_4, 8,
N'What’s the difference between structured and unstructured data?',
N'Explanation: Structured data fits in rows and columns; unstructured is free-form like media and text.');
DECLARE @Q4_8 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_8, 1, N'A. There is none', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_8, 2, N'B. Structured is visual data', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_8, 3, N'C. Structured is tabular; unstructured is text, image, audio', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_8, 4, N'D. Unstructured data can''t be used in ML', 0);

-- Q9
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_4, 9,
N'Which Azure service allows real-time speech translation?',
N'Explanation: Azure Speech Service supports speech-to-text, text-to-speech, and real-time translation.');
DECLARE @Q4_9 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_9, 1, N'A. Azure Translator Text', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_9, 2, N'B. Azure Bot Service', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_9, 3, N'C. Azure Speech Service', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_9, 4, N'D. Azure QnA Maker', 0);

-- Q10
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_4, 10,
N'In responsible AI, what does fairness refer to?',
N'Explanation: Fairness ensures AI systems don’t make biased or discriminatory decisions.');
DECLARE @Q4_10 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_10, 1, N'A. Legal compliance', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_10, 2, N'B. Preventing bias in predictions', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_10, 3, N'C. Faster performance', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q4_10, 4, N'D. Open-source software', 0);

PRINT '✓ Loaded 10 questions for quiz "Azure AI Fundamentals (AI-900)" (QuizID=' + CAST(@QuizID_4 AS NVARCHAR(20)) + ')';

-- ---------------------------------------------------------------
-- Quiz: Azure Data Scientist Associate
-- ---------------------------------------------------------------
DECLARE @QuizID_5 INT;
SELECT @QuizID_5 = QuizID
FROM   dbo.Quizzes
WHERE  CourseID = 6
  AND  Title     = N'Azure Data Scientist Associate';

IF @QuizID_5 IS NULL
BEGIN
    INSERT INTO dbo.Quizzes (CourseID, Title, QuestionCount, TimeLimitMin, PassingPct, IsActive)
    VALUES (6, N'Azure Data Scientist Associate', 10, 30, 70.00, 1);
    SET @QuizID_5 = SCOPE_IDENTITY();
END

-- Q1
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_5, 1,
N'What is the primary use of Azure Machine Learning?',
N'Explanation: Azure ML is built for end-to-end machine learning workflows.');
DECLARE @Q5_1 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_1, 1, N'A. Email filtering', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_1, 2, N'B. Build, train, and deploy ML models', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_1, 3, N'C. Host websites', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_1, 4, N'D. Manage Azure billing', 0);

-- Q2
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_5, 2,
N'Which workspace component stores datasets and notebooks?',
N'Explanation: The workspace holds assets like datasets, environments, and notebooks.');
DECLARE @Q5_2 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_2, 1, N'A. Compute targets', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_2, 2, N'B. Azure ML Workspace', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_2, 3, N'C. Azure SQL', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_2, 4, N'D. Azure DevOps', 0);

-- Q3
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_5, 3,
N'Which Azure ML tool allows drag-and-drop model creation?',
N'Explanation: The Designer allows visual pipeline creation without code.');
DECLARE @Q5_3 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_3, 1, N'A. Azure DevTest Labs', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_3, 2, N'B. Designer (no-code) tool', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_3, 3, N'C. Visual Studio Code', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_3, 4, N'D. JupyterHub', 0);

-- Q4
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_5, 4,
N'Which compute type is used for scalable training of large models?',
N'Explanation: Compute Clusters support distributed training.');
DECLARE @Q5_4 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_4, 1, N'A. Inference Cluster', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_4, 2, N'B. Azure ML Compute Cluster', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_4, 3, N'C. Blob Storage', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_4, 4, N'D. App Service', 0);

-- Q5
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_5, 5,
N'What is the purpose of an experiment in Azure ML?',
N'Explanation: Experiments log metrics and track training attempts.');
DECLARE @Q5_5 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_5, 1, N'A. Write SQL queries', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_5, 2, N'B. Track model training runs', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_5, 3, N'C. Create user interfaces', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_5, 4, N'D. Manage Kubernetes', 0);

-- Q6
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_5, 6,
N'What is the role of an environment in Azure ML?',
N'Explanation: Environments define the execution environment for training jobs.');
DECLARE @Q5_6 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_6, 1, N'A. Manage billing', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_6, 2, N'B. Set Azure region', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_6, 3, N'C. Define Python packages and Docker settings', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_6, 4, N'D. Create web apps', 0);

-- Q7
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_5, 7,
N'Which file format is commonly used to define Azure ML pipelines?',
N'Explanation: YAML is used to structure pipeline configurations and runs.');
DECLARE @Q5_7 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_7, 1, N'A. JSON', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_7, 2, N'B. YAML', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_7, 3, N'C. CSV', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_7, 4, N'D. TXT', 0);

-- Q8
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_5, 8,
N'How does automated ML (AutoML) assist data scientists?',
N'Explanation: AutoML simplifies model selection and tuning via automation.');
DECLARE @Q5_8 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_8, 1, N'A. Improves graphics', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_8, 2, N'B. Automatically tests multiple algorithms and hyperparameters', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_8, 3, N'C. Stores passwords', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_8, 4, N'D. Runs Power BI reports', 0);

-- Q9
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_5, 9,
N'What is the benefit of model registration in Azure ML?',
N'Explanation: Registered models can be versioned and deployed repeatedly.');
DECLARE @Q5_9 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_9, 1, N'A. Increase bandwidth', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_9, 2, N'B. Track model versions and reuse across deployments', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_9, 3, N'C. Generate code', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_9, 4, N'D. Build charts', 0);

-- Q10
INSERT INTO dbo.QuizQuestions (QuizID, QuestionSeq, QuestionText, Explanation)
VALUES (@QuizID_5, 10,
N'Which of the following is true about data drift in ML?',
N'Explanation: Data drift causes model performance to degrade as new data shifts from the original.');
DECLARE @Q5_10 INT = SCOPE_IDENTITY();
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_10, 1, N'A. Improves accuracy', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_10, 2, N'B. Change in data distribution over time that can degrade model performance', 1);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_10, 3, N'C. Makes the model faster', 0);
INSERT INTO dbo.QuizOptions (QuestionID, OptionSeq, OptionText, IsCorrect) VALUES
(@Q5_10, 4, N'D. Affects only training data', 0);

PRINT '✓ Loaded 10 questions for quiz "Azure Data Scientist Associate" (QuizID=' + CAST(@QuizID_5 AS NVARCHAR(20)) + ')';

PRINT '================================================================';
PRINT '✓ ALL FIVE QUIZZES (50 questions) HAVE BEEN LOADED INTO COURSEID = 6';
PRINT '================================================================';
