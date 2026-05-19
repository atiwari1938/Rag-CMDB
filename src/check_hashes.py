import sqlite3
import os

# Check the processed hashes database
db_path = os.path.join(os.path.dirname(__file__), "..", "data", "processed_hashes.db")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Count existing hashes
    cur.execute("SELECT COUNT(*) FROM processed")
    count = cur.fetchone()[0]
    print(f"Current hash entries in database: {count}")
    
    # Show first 5 entries
    cur.execute("SELECT hash, filename FROM processed LIMIT 5")
    rows = cur.fetchall()
    if rows:
        print("\nFirst 5 entries:")
        for row in rows:
            print(f"  - Hash: {row[0][:20]}..., Filename: {row[1] if row[1] else 'N/A'}")
    
    conn.close()
else:
    print("❌ Database file not found")
