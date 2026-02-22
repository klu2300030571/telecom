import sqlite3

DB_NAME = "complaints.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # optional: rows behave like dict
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT NOT NULL,
        text TEXT NOT NULL,
        category TEXT,
        account_id TEXT,
        amount TEXT,
        team TEXT,
        status TEXT DEFAULT 'Open',
        created_at TEXT
    )
    """)

    # ✅ index for faster customer history search
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_complaints_customer
    ON complaints(customer_id)
    """)

    conn.commit()
    conn.close()