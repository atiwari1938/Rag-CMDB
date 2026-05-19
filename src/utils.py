import os
import sqlite3
import hashlib
import pandas as pd

def init_hash_db():
    """
    Initialize SQLite database for storing document hashes.
    """
    db_path = os.path.join(os.path.dirname(__file__), "..", "data", "processed_hashes.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Create table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS processed (
            hash TEXT PRIMARY KEY,
            filename TEXT,
            processed_date TEXT
        )
    """)
    conn.commit()
    return conn

def load_existing():
    """
    Load existing processed documents from the database.
    Returns:
        set: A set of document hashes that have been processed
    """
    conn = init_hash_db()
    cur = conn.cursor()
    
    cur.execute("SELECT hash FROM processed")
    existing = set(row[0] for row in cur.fetchall())
    
    conn.close()
    return existing
    conn = init_hash_db()
    cur = conn.cursor()
    
    cur.execute("SELECT hash FROM processed_docs")
    existing = set(row[0] for row in cur.fetchall())
    
    conn.close()
    return existing

def get_text_hash(text):
    """
    Generate SHA-256 hash of text content.
    """
    return hashlib.sha256(str(text).encode()).hexdigest()
