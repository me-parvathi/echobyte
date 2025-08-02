# init_db.py
import sqlite3
conn = sqlite3.connect("chatbot_auth.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")
conn.commit()
conn.close()
print("✅ DB initialized")
