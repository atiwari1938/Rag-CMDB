import pandas as pd
import pickle

print("="*80)
print("PARQUET FILE CHECK")
print("="*80)
df = pd.read_parquet('data/tickets.parquet')
print(f"Columns ({len(df.columns)}): {list(df.columns)}")
print(f"\nHas 'number'?: {'number' in df.columns}")

print("\n" + "="*80)
print("METADATA PICKLE CHECK")
print("="*80)
with open('data/tickets_meta.pkl', 'rb') as f:
    meta = pickle.load(f)

first_ticket = next((m for m in meta if m.get('document_type') != 'support_document'), None)
if first_ticket:
    print(f"First ticket keys: {list(first_ticket.keys())}")
    print(f"Has 'number'?: {'number' in first_ticket}")
