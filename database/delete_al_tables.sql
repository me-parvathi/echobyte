-- Step 1: Drop all foreign key constraints
DECLARE @sql NVARCHAR(MAX) = N'';

SELECT @sql += N'
ALTER TABLE [' + s.name + '].[' + t.name + '] DROP CONSTRAINT [' + fk.name + '];'
FROM sys.foreign_keys fk
JOIN sys.tables t      ON fk.parent_object_id = t.object_id
JOIN sys.schemas s     ON t.schema_id = s.schema_id;

EXEC sp_executesql @sql;

-- Step 2: Drop all tables
SET @sql = N'';

SELECT @sql += N'
DROP TABLE [' + s.name + '].[' + t.name + '];'
FROM sys.tables t
JOIN sys.schemas s ON t.schema_id = s.schema_id;

EXEC sp_executesql @sql;
