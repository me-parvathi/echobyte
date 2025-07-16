from sqlalchemy import create_engine

engine = create_engine(
    "mssql+pyodbc://sa:YourStrong!Passw0rd@localhost:1433/echobyte"
    "?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes",
    fast_executemany=True
)

with engine.connect() as conn:
    conn.execute("SELECT 1")
    print("Connection successful")
