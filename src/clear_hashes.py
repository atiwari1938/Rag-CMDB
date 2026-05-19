import sqlite3
import os

# Clear the processed hashes database
db_path = os.path.join(os.path.dirname(__file__), "..", "data", "processed_hashes.db")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Count existing hashes
    cur.execute("SELECT COUNT(*) FROM processed")
    count = cur.fetchone()[0]
    print(f"Found {count} existing hash entries")
    
    # Clear all entries
    cur.execute("DELETE FROM processed")
    conn.commit()
    print(f"✅ Cleared all {count} hash entries from database")
    
    conn.close()
else:
    print("❌ Database file not found")
