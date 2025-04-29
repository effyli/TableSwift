import os
import duckdb
from contextlib import contextmanager
from .config import get_settings

settings = get_settings()

# Ensure the db directory exists
os.makedirs(os.path.dirname(settings.DB_FILE), exist_ok=True)

def init_db():
    """Initialize the database and create necessary tables."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR PRIMARY KEY,
                email VARCHAR UNIQUE NOT NULL,
                hashed_password VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

@contextmanager
def get_db():
    """Get a database connection."""
    conn = duckdb.connect(settings.DB_FILE)
    try:
        yield conn
    finally:
        conn.close()

# Initialize the database when the module is imported
init_db()
