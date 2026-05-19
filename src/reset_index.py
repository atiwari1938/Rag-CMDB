import os

data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

files_to_delete = [
    "faiss_index.idx",
    "tickets_meta.pkl", 
    "tickets.parquet",
    "processed_hashes.db"
]

for filename in files_to_delete:
    filepath = os.path.join(data_dir, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"✅ Deleted: {filename}")
    else:
        print(f"⚠️ Not found: {filename}")

print("\n✅ All files deleted. Restart the server or send a query to trigger reindexing.")
