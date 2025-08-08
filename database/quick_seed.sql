-- =====================================================================
-- Quick LMS Seed Script
-- Run this in SQL Server Management Studio to quickly populate data
-- =====================================================================

-- Clear existing data (optional)
-- DELETE FROM dbo.EmployeeModuleProgress;
-- DELETE FROM dbo.EmployeeCourses;
-- DELETE FROM dbo.QuizAttempts;
-- DELETE FROM dbo.EmployeeBadges;
-- DELETE FROM dbo.QuizOptions;
-- DELETE FROM dbo.QuizQuestions;
-- DELETE FROM dbo.Quizzes;
-- DELETE FROM dbo.CourseModules;
-- DELETE FROM dbo.Courses;
-- DELETE FROM dbo.BadgeDefinitions;

-- Seed Courses
INSERT INTO dbo.Courses (CourseCode, Title, Difficulty, EstimatedHours, IsActive)
VALUES
  ('SQL101', 'SQL Fundamentals', 'Beginner', 5.00, 1),
  ('DOCK201', 'Docker & Containers', 'Intermediate', 6.00, 1),
  ('FAST301', 'FastAPI Web Development', 'Intermediate', 5.50, 1),
  ('REACT101', 'React.js Basics', 'Beginner', 6.00, 1),
  ('AZURE100', 'Azure Fundamentals (AZ-900)', 'Beginner', 7.00, 1);

-- Seed Course Modules
INSERT INTO dbo.CourseModules (CourseID, ModuleSeq, Title, VideoURL, VideoType)
VALUES
  -- SQL Fundamentals (CourseID = 1)
  (1, 1, 'Introduction to SQL', 'https://www.youtube.com/watch?v=9Pzj7Aj25lw', 'I'),
  (1, 2, 'Basic SELECT Queries', 'https://www.youtube.com/watch?v=7S_tz1z_5bA', 'I'),
  (1, 3, 'Joins and Relationships', 'https://www.youtube.com/watch?v=0OQJDd3QqQM', 'I'),
  (1, 4, 'Aggregations and Grouping', 'https://www.youtube.com/watch?v=4pKrqZ2HS_4', 'I'),
  
  -- Docker & Containers (CourseID = 2)
  (2, 1, 'Introduction to Docker', 'https://www.youtube.com/watch?v=3c-iBn73dDE', 'I'),
  (2, 2, 'Running Containers', 'https://www.youtube.com/watch?v=pg19Z8LL06w', 'I'),
  (2, 3, 'Building Images with Dockerfile', 'https://www.youtube.com/watch?v=VpxBq3QumQU', 'I'),
  (2, 4, 'Orchestrating with Docker Compose', 'https://www.youtube.com/watch?v=HG6yIjZapSA', 'I'),
  
  -- FastAPI Web Development (CourseID = 3)
  (3, 1, 'Setup & Hello World', 'https://www.youtube.com/watch?v=7t2alSnE2-I', 'I'),
  (3, 2, 'Path and Query Parameters', 'https://www.youtube.com/watch?v=AdAjccWYJIQ', 'I'),
  (3, 3, 'Data Validation with Pydantic', 'https://www.youtube.com/watch?v=iWS9ogMPOI0', 'I'),
  (3, 4, 'Dependency Injection', 'https://www.youtube.com/watch?v=Tyhtp1Ou_Pk', 'I'),
  
  -- React.js Basics (CourseID = 4)
  (4, 1, 'JSX and Components', 'https://www.youtube.com/watch?v=w7ejDZ8SWv8', 'I'),
  (4, 2, 'State and Props', 'https://www.youtube.com/watch?v=0e2IQDzZbEg', 'I'),
  (4, 3, 'React Hooks', 'https://www.youtube.com/watch?v=f687hBjwFcM', 'I'),
  (4, 4, 'React Router', 'https://www.youtube.com/watch?v=Law7wfdg_ls', 'I'),
  
  -- Azure Fundamentals (CourseID = 5)
  (5, 1, 'Introduction to Cloud Concepts', 'https://www.youtube.com/watch?v=YfZ0zk5Zzcw', 'I'),
  (5, 2, 'Core Azure Services Overview', 'https://www.youtube.com/watch?v=-pX5PjIYTJs', 'I'),
  (5, 3, 'Azure Storage Services', 'https://www.youtube.com/watch?v=BZivZUzqtTs', 'I'),
  (5, 4, 'Azure Networking Basics', 'https://www.youtube.com/watch?v=JsWOCZKUCEM', 'I');

-- Seed Badge Definitions
INSERT INTO dbo.BadgeDefinitions (BadgeCode, Name, Description, IconURL, IsActive)
VALUES 
  ('SQL_EXPERT', 'SQL Expert', 'Completed SQL Fundamentals course', '/badges/sql-expert.png', 1),
  ('DOCKER_EXPERT', 'Docker Expert', 'Completed Docker & Containers course', '/badges/docker-expert.png', 1),
  ('FASTAPI_EXPERT', 'FastAPI Expert', 'Completed FastAPI Web Development course', '/badges/fastapi-expert.png', 1),
  ('REACT_EXPERT', 'React Expert', 'Completed React.js Basics course', '/badges/react-expert.png', 1),
  ('AZURE_EXPERT', 'Azure Expert', 'Completed Azure Fundamentals course', '/badges/azure-expert.png', 1);

-- Seed Quizzes
INSERT INTO dbo.Quizzes (CourseID, Title, QuestionCount, TimeLimitMin, PassingPct, IsActive)
VALUES 
  (1, 'SQL Fundamentals Quiz', 10, 30, 70.00, 1),
  (2, 'Docker Basics Quiz', 15, 45, 75.00, 1),
  (3, 'FastAPI Development Quiz', 12, 40, 80.00, 1),
  (4, 'React.js Fundamentals Quiz', 15, 45, 75.00, 1),
  (5, 'Azure Fundamentals Quiz', 20, 60, 70.00, 1);

PRINT '================================================================';
PRINT '✓ Quick LMS Seed Completed Successfully!';
PRINT '✓ 5 courses with modules created';
PRINT '✓ 5 badge definitions created';
PRINT '✓ 5 quizzes created';
PRINT '================================================================';
PRINT '';
PRINT '🎉 Your Learning & Development page should now show:';
PRINT '   • 5 Learning Tracks (courses)';
PRINT '   • 5 Azure Certification Quizzes';
PRINT '   • All courses available for enrollment';
PRINT '';
PRINT '📝 Next: Start your backend server and refresh the page!'; 