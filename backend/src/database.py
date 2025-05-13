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
        # Create sequences for all tables
        conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS file_id_seq
            START WITH 1
            INCREMENT BY 1;
        """)
        
        conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS operation_id_seq
            START WITH 1
            INCREMENT BY 1;
        """)
        
        conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS action_id_seq
            START WITH 1
            INCREMENT BY 1;
        """)

        conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS description_id_seq
            START WITH 1
            INCREMENT BY 1;
        """)
        
        conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS label_id_seq
            START WITH 1
            INCREMENT BY 1;
        """)

        conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS code_id_seq
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

        conn.execute("""
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY 
                    DEFAULT nextval('operation_id_seq'),
                name VARCHAR NOT NULL
            );
        """)

        # Insert default operations if they don't exist
        operations = [
            "Transformation",
            "Error Detection",
            "Data Imputation",
            "Entity Matching"
        ]
        for operation in operations:
            conn.execute("""
                INSERT INTO operations (name)
                SELECT ? WHERE NOT EXISTS (
                    SELECT 1 FROM operations WHERE name = ?
                );
            """, [operation, operation])

        conn.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY
                    DEFAULT nextval('action_id_seq'),
                operation_id INTEGER,
                file_column VARCHAR,
                datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                project_id UUID,
                file_id INTEGER
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS description (
                id INTEGER PRIMARY KEY
                    DEFAULT nextval('description_id_seq'),
                description VARCHAR NOT NULL,
                version INTEGER NOT NULL,
                action_id INTEGER NOT NULL
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS labels (
                id INTEGER PRIMARY KEY
                    DEFAULT nextval('label_id_seq'),
                json VARCHAR NOT NULL,
                description_id INTEGER NOT NULL
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS codes (
                id INTEGER PRIMARY KEY
                    DEFAULT nextval('code_id_seq'),
                code VARCHAR NOT NULL,
                version INTEGER NOT NULL,
                label_id INTEGER NOT NULL
            );
        """)

# Auto-initialize when this module is imported
init_db()
