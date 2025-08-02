import sqlite3
import pandas as pd

# Load the CSV file
df = pd.read_csv("It_help_desk_data.csv")

# Optional: print columns to verify
print("📄 Columns in CSV:", df.columns.tolist())

# Connect to the database
conn = sqlite3.connect("chatbot_auth.db")

# Save the DataFrame to a 'tickets' table (overwrite if already exists)
df.to_sql("tickets", conn, if_exists="replace", index=False)

# Print success
print("✅ Tickets imported successfully!")

# Confirm schema
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(tickets)")
print("📋 Schema:")
for row in cursor.fetchall():
    print(row)

conn.close()
