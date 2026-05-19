import pandas as pd
import pickle

# Check Excel file columns
print("="*80)
print("EXCEL FILE COLUMNS")
print("="*80)
df = pd.read_excel('../data/incoming/incident (3).xlsx')
print(f"\nColumns in incident (3).xlsx:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. '{col}'")

print(f"\nFirst row sample:")
first_row = df.iloc[0]
for col in df.columns[:10]:
    print(f"  {col}: {first_row[col]}")

# Check what's stored in parquet after ingestion
print("\n" + "="*80)
print("PARQUET FILE COLUMNS (after ingestion)")
print("="*80)
df_parquet = pd.read_parquet('../data/tickets.parquet')
print(f"\nColumns in tickets.parquet:")
for i, col in enumerate(df_parquet.columns, 1):
    print(f"  {i}. '{col}'")

# Check metadata
print("\n" + "="*80)
print("METADATA (what's sent to frontend)")
print("="*80)
with open('../data/tickets_meta.pkl', 'rb') as f:
    meta = pickle.load(f)

ticket_meta = [m for m in meta if m.get('document_type') != 'support_document']
if ticket_meta:
    first = ticket_meta[0]
    print(f"\nFirst ticket metadata keys:")
    for i, key in enumerate(first.keys(), 1):
        print(f"  {i}. '{key}'")
    
    # Show number-related fields
    print(f"\nNumber/ID related fields in metadata:")
    for key in first.keys():
        if 'number' in key.lower() or 'id' in key.lower():
            val = first.get(key)
            print(f"  {key}: {val}")
