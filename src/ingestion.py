import os
import glob
import hashlib
import sqlite3
import pandas as pd
from datetime import datetime

# Paths
BASE      = os.path.dirname(__file__)
INCOMING  = os.path.join(BASE, "..", "data", "incoming")
PARQUET   = os.path.join(BASE, "..", "data", "tickets.parquet")
HASH_DB   = os.path.join(BASE, "..", "data", "processed_hashes.db")

def get_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def init_hash_db():
    conn = sqlite3.connect(HASH_DB)
    conn.execute("CREATE TABLE IF NOT EXISTS processed (hash TEXT PRIMARY KEY)")
    conn.commit()
    return conn

def load_existing() -> pd.DataFrame:
    return pd.read_parquet(PARQUET) if os.path.exists(PARQUET) else pd.DataFrame()

def save(df: pd.DataFrame):
    df.to_parquet(PARQUET, index=False)

def process():
    conn     = init_hash_db()
    cur      = conn.cursor()
    existing = load_existing()
    new_rows = []

    for fx in glob.glob(os.path.join(INCOMING, "*.xlsx")):
        xlsx = pd.ExcelFile(fx)
        for sheet in xlsx.sheet_names:
            df = xlsx.parse(sheet)
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
            for _, row in df.iterrows():
                text = f"{row.get('short_description','')}\n{row.get('description','')}"
                h    = get_text_hash(text)
                if cur.execute("SELECT 1 FROM processed WHERE hash=?", (h,)).fetchone():
                    continue

                record = row.to_dict()
                record["ingested_at"] = datetime.utcnow()
                new_rows.append(record)
                cur.execute("INSERT INTO processed (hash) VALUES (?)", (h,))

    conn.commit()
    conn.close()

    if new_rows:
        df_new   = pd.DataFrame(new_rows)
        combined = pd.concat([existing, df_new], ignore_index=True)
        save(combined)
        print(f"Ingested {len(new_rows)} new records.")
    else:
        print("No new records to ingest.")

if __name__ == "__main__":
    process()
