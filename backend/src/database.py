# src/database.py

import os
import duckdb
from contextlib import contextmanager
from .config import get_settings

settings = get_settings()

# Ensure the directory for the DuckDB file exists
db_dir = os.path.dirname(settings.DB_FILE) or "."
os.makedirs(db_dir, exist_ok=True)

@contextmanager
def get_db():
    """Yield a DuckDB connection, closing it when done."""
    conn = duckdb.connect(settings.DB_FILE)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize the database: sequence + tables."""
    with get_db() as conn:
        conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS file_id_seq
            START WITH 1
            INCREMENT BY 1;
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY 
                    DEFAULT nextval('file_id_seq'),
                file_path VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY,
                email VARCHAR UNIQUE NOT NULL,
                hashed_password VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id UUID PRIMARY KEY,
                name VARCHAR NOT NULL,
                file_id INTEGER NOT NULL,
                user_id UUID NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

# Auto-initialize when this module is imported
init_db()
