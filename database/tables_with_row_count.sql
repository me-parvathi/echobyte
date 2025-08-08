SELECT 
    s.name AS SchemaName,
    t.name AS TableName,
    SUM(p.rows) AS TotalRows
FROM 
    sys.tables t
INNER JOIN 
    sys.schemas s ON t.schema_id = s.schema_id
INNER JOIN 
    sys.partitions p ON t.object_id = p.object_id
WHERE 
    p.index_id IN (0,1)  -- 0 = heap, 1 = clustered index
GROUP BY 
    s.name, t.name
HAVING 
    SUM(p.rows) > 0
ORDER BY 
    TotalRows DESC;
