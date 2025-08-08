"""
Database migration script for AI Agent system
Adds agent fields to existing tables and creates new agent-specific tables
"""

import logging
from sqlalchemy import text
from core.database import get_db, engine

logger = logging.getLogger(__name__)


def migrate_agent_tables():
    """Migrate database to add agent fields and tables"""
    
    try:
        with engine.connect() as connection:
            # Add agent fields to LeaveApplications table
            logger.info("Adding agent fields to LeaveApplications table...")
            
            # Check if columns already exist
            result = connection.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'LeaveApplications' 
                AND COLUMN_NAME IN ('AgentDecision', 'AgentConfidence', 'AgentReason', 'AgentProcessedAt', 'AgentVersion')
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            
            if 'AgentDecision' not in existing_columns:
                connection.execute(text("""
                    ALTER TABLE LeaveApplications 
                    ADD AgentDecision VARCHAR(20)
                """))
                logger.info("Added AgentDecision column to LeaveApplications")
            
            if 'AgentConfidence' not in existing_columns:
                connection.execute(text("""
                    ALTER TABLE LeaveApplications 
                    ADD AgentConfidence DECIMAL(3,2)
                """))
                logger.info("Added AgentConfidence column to LeaveApplications")
            
            if 'AgentReason' not in existing_columns:
                connection.execute(text("""
                    ALTER TABLE LeaveApplications 
                    ADD AgentReason TEXT
                """))
                logger.info("Added AgentReason column to LeaveApplications")
            
            if 'AgentProcessedAt' not in existing_columns:
                connection.execute(text("""
                    ALTER TABLE LeaveApplications 
                    ADD AgentProcessedAt DATETIME
                """))
                logger.info("Added AgentProcessedAt column to LeaveApplications")
            
            if 'AgentVersion' not in existing_columns:
                connection.execute(text("""
                    ALTER TABLE LeaveApplications 
                    ADD AgentVersion VARCHAR(20)
                """))
                logger.info("Added AgentVersion column to LeaveApplications")
            
            # Add agent fields to Timesheets table
            logger.info("Adding agent fields to Timesheets table...")
            
            result = connection.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'Timesheets' 
                AND COLUMN_NAME IN ('AgentDecision', 'AgentConfidence', 'AgentReason', 'AgentProcessedAt', 'AgentVersion')
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            
            if 'AgentDecision' not in existing_columns:
                connection.execute(text("""
                    ALTER TABLE Timesheets 
                    ADD AgentDecision VARCHAR(20)
                """))
                logger.info("Added AgentDecision column to Timesheets")
            
            if 'AgentConfidence' not in existing_columns:
                connection.execute(text("""
                    ALTER TABLE Timesheets 
                    ADD AgentConfidence DECIMAL(3,2)
                """))
                logger.info("Added AgentConfidence column to Timesheets")
            
            if 'AgentReason' not in existing_columns:
                connection.execute(text("""
                    ALTER TABLE Timesheets 
                    ADD AgentReason TEXT
                """))
                logger.info("Added AgentReason column to Timesheets")
            
            if 'AgentProcessedAt' not in existing_columns:
                connection.execute(text("""
                    ALTER TABLE Timesheets 
                    ADD AgentProcessedAt DATETIME
                """))
                logger.info("Added AgentProcessedAt column to Timesheets")
            
            if 'AgentVersion' not in existing_columns:
                connection.execute(text("""
                    ALTER TABLE Timesheets 
                    ADD AgentVersion VARCHAR(20)
                """))
                logger.info("Added AgentVersion column to Timesheets")
            
            # Create AgentAuditLogs table
            logger.info("Creating AgentAuditLogs table...")
            
            connection.execute(text("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='AgentAuditLogs' AND xtype='U')
                CREATE TABLE AgentAuditLogs (
                    AuditID INT IDENTITY(1,1) PRIMARY KEY,
                    DecisionID VARCHAR(50) NOT NULL,
                    AgentName VARCHAR(50) NOT NULL,
                    AgentVersion VARCHAR(20) NOT NULL,
                    EntityType VARCHAR(20) NOT NULL,
                    EntityID INT NOT NULL,
                    Action VARCHAR(50) NOT NULL,
                    Decision VARCHAR(20),
                    ConfidenceScore DECIMAL(3,2),
                    Reason TEXT,
                    BusinessRulesApplied NVARCHAR(MAX),
                    RiskFactors NVARCHAR(MAX),
                    Recommendations NVARCHAR(MAX),
                    Details NVARCHAR(MAX),
                    CreatedAt DATETIME NOT NULL DEFAULT GETUTCDATE()
                )
            """))
            logger.info("Created AgentAuditLogs table")
            
            # Create AgentLearningData table
            logger.info("Creating AgentLearningData table...")
            
            connection.execute(text("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='AgentLearningData' AND xtype='U')
                CREATE TABLE AgentLearningData (
                    LearningID INT IDENTITY(1,1) PRIMARY KEY,
                    DecisionID VARCHAR(50) NOT NULL,
                    AgentName VARCHAR(50) NOT NULL,
                    EntityType VARCHAR(20) NOT NULL,
                    EntityID INT NOT NULL,
                    OriginalDecision VARCHAR(20) NOT NULL,
                    OriginalConfidence DECIMAL(3,2) NOT NULL,
                    OriginalReason TEXT,
                    OriginalBusinessRules NVARCHAR(MAX),
                    OriginalRiskFactors NVARCHAR(MAX),
                    OverrideDecision VARCHAR(20),
                    OverrideConfidence DECIMAL(3,2),
                    OverrideReason TEXT,
                    OverrideBy VARCHAR(100),
                    OverrideAt DATETIME,
                    LearningApplied BIT DEFAULT 0,
                    PatternExtracted NVARCHAR(MAX),
                    LearningImpact DECIMAL(3,2),
                    CreatedAt DATETIME NOT NULL DEFAULT GETUTCDATE(),
                    UpdatedAt DATETIME NOT NULL DEFAULT GETUTCDATE()
                )
            """))
            logger.info("Created AgentLearningData table")
            
            # Create AgentPerformanceMetrics table
            logger.info("Creating AgentPerformanceMetrics table...")
            
            connection.execute(text("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='AgentPerformanceMetrics' AND xtype='U')
                CREATE TABLE AgentPerformanceMetrics (
                    MetricID INT IDENTITY(1,1) PRIMARY KEY,
                    AgentName VARCHAR(50) NOT NULL,
                    EntityType VARCHAR(20) NOT NULL,
                    TimePeriod VARCHAR(20) NOT NULL,
                    PeriodStart DATE NOT NULL,
                    PeriodEnd DATE NOT NULL,
                    TotalDecisions INT DEFAULT 0,
                    ApprovedDecisions INT DEFAULT 0,
                    RejectedDecisions INT DEFAULT 0,
                    EscalatedDecisions INT DEFAULT 0,
                    FlaggedDecisions INT DEFAULT 0,
                    CorrectDecisions INT DEFAULT 0,
                    OverrideCount INT DEFAULT 0,
                    AccuracyRate DECIMAL(5,4),
                    OverrideRate DECIMAL(5,4),
                    AverageConfidence DECIMAL(3,2),
                    AverageProcessingTime DECIMAL(8,3),
                    AnomalyDetectionRate DECIMAL(5,4),
                    ConfidenceCorrelation DECIMAL(3,2),
                    CreatedAt DATETIME NOT NULL DEFAULT GETUTCDATE(),
                    UpdatedAt DATETIME NOT NULL DEFAULT GETUTCDATE()
                )
            """))
            logger.info("Created AgentPerformanceMetrics table")
            
            # Create AgentNotifications table
            logger.info("Creating AgentNotifications table...")
            
            connection.execute(text("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='AgentNotifications' AND xtype='U')
                CREATE TABLE AgentNotifications (
                    NotificationID INT IDENTITY(1,1) PRIMARY KEY,
                    UserID VARCHAR(50) NOT NULL,
                    NotificationType VARCHAR(50) NOT NULL,
                    Title VARCHAR(200) NOT NULL,
                    Message TEXT NOT NULL,
                    Data NVARCHAR(MAX),
                    Priority VARCHAR(20) DEFAULT 'normal',
                    IsRead BIT DEFAULT 0,
                    ReadAt DATETIME,
                    CreatedAt DATETIME NOT NULL DEFAULT GETUTCDATE()
                )
            """))
            logger.info("Created AgentNotifications table")
            
            # Create AgentPatterns table
            logger.info("Creating AgentPatterns table...")
            
            connection.execute(text("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='AgentPatterns' AND xtype='U')
                CREATE TABLE AgentPatterns (
                    PatternID INT IDENTITY(1,1) PRIMARY KEY,
                    AgentName VARCHAR(50) NOT NULL,
                    PatternType VARCHAR(50) NOT NULL,
                    PatternKey VARCHAR(100) NOT NULL,
                    PatternData NVARCHAR(MAX) NOT NULL,
                    ConfidenceScore DECIMAL(3,2) NOT NULL,
                    UsageCount INT DEFAULT 0,
                    SuccessRate DECIMAL(5,4),
                    IsActive BIT DEFAULT 1,
                    CreatedAt DATETIME NOT NULL DEFAULT GETUTCDATE(),
                    UpdatedAt DATETIME NOT NULL DEFAULT GETUTCDATE()
                )
            """))
            logger.info("Created AgentPatterns table")
            
            # Create indexes for better performance
            logger.info("Creating indexes...")
            
            connection.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_AgentAuditLogs_DecisionID')
                CREATE INDEX IX_AgentAuditLogs_DecisionID ON AgentAuditLogs (DecisionID)
            """))
            
            connection.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_AgentAuditLogs_EntityType_EntityID')
                CREATE INDEX IX_AgentAuditLogs_EntityType_EntityID ON AgentAuditLogs (EntityType, EntityID)
            """))
            
            connection.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_AgentLearningData_DecisionID')
                CREATE INDEX IX_AgentLearningData_DecisionID ON AgentLearningData (DecisionID)
            """))
            
            connection.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_AgentNotifications_UserID')
                CREATE INDEX IX_AgentNotifications_UserID ON AgentNotifications (UserID)
            """))
            
            connection.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_AgentNotifications_IsRead')
                CREATE INDEX IX_AgentNotifications_IsRead ON AgentNotifications (IsRead)
            """))
            
            connection.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_AgentPerformanceMetrics_AgentName_TimePeriod')
                CREATE INDEX IX_AgentPerformanceMetrics_AgentName_TimePeriod ON AgentPerformanceMetrics (AgentName, TimePeriod)
            """))
            
            logger.info("Created indexes successfully")
            
            # Commit the transaction
            connection.commit()
            
            logger.info("Agent tables migration completed successfully!")
            
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    migrate_agent_tables()
