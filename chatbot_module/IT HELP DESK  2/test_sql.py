import pyodbc
import bcrypt
import jwt
from datetime import datetime, timedelta

# === CONFIG ===
AZURE_SQL_SERVER= "echobyte-dev.database.windows.net"
AZURE_SQL_DATABASE= "echobyte-prod"
AZURE_SQL_USERNAME= "CloudSAed8256da"
AZURE_SQL_PASSWORD= "EchobyteDev123"
SECRET_KEY = "myverysecurekey123"
Driver= '{ODBC Driver 17 for SQL Server}' # Same as used in your Flask app

# Connect to Azure SQL
conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
)
cursor = conn.cursor()

# Step 1: Fetch employees with unhashed passwords
cursor.execute("SELECT email, password FROM employees WHERE password NOT LIKE '$2b$%'")
rows = cursor.fetchall()

print(f"🔍 Found {len(rows)} employees with unhashed passwords.\n")

# Step 2: Hash and update
for email, plain_password in rows:
    try:
        hashed_password = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()
        cursor.execute("UPDATE employees SET password = ? WHERE email = ?", hashed_password, email)
        print(f"✅ Updated password for {email}")
    except Exception as e:
        print(f"❌ Failed to hash password for {email}: {e}")

# Step 3: Commit changes
conn.commit()
cursor.close()
conn.close()

print("\n✅ Finished hashing all plaintext passwords.")