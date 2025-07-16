#!/bin/bash

# Start SQL Server in the background
/opt/mssql/bin/sqlservr &

# Wait for SQL Server to be fully up and ready to accept connections
echo "⏳ Waiting for SQL Server to start and become ready..."
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'YourStrong!Passw0rd' -C -Q "SELECT 1"
while [ $? -ne 0 ]
do
    echo "SQL Server is unavailable, sleeping..."
    sleep 5
    /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'YourStrong!Passw0rd' -C -Q "SELECT 1"
done

# Run setup script to initialize DB and schema
echo "⚙️ Running setup.sql..."
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'YourStrong!Passw0rd' -C -i /setup/setup.sql

# Check if setup was successful
if [ $? -eq 0 ]; then
    echo "✅ Database setup completed successfully!"
else
    echo "❌ Database setup failed!"
fi

# Keep container running (don't exit after init)
echo "🚀 SQL Server is ready for connections"
wait