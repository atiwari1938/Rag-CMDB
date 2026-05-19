import pandas as pd
import pickle

print("="*80)
print("CHECKING TICKET NUMBER FIELDS")
print("="*80)

# Load parquet data
df = pd.read_parquet('data/tickets.parquet')
tickets = df[df['document_type'].isna()]

print(f"\nTotal tickets: {len(tickets)}")
print(f"\nAll columns ({len(df.columns)}):")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. {col}")

# Check for number-related columns
number_cols = [col for col in df.columns if 'number' in col.lower() or 'id' in col.lower()]
print(f"\n\nNumber/ID related columns ({len(number_cols)}):")
for col in number_cols:
    non_null = tickets[col].notna().sum()
    print(f"  - {col}: {non_null}/{len(tickets)} tickets have values")
    if non_null > 0:
        sample_val = tickets[tickets[col].notna()][col].iloc[0]
        print(f"    Example: {sample_val}")

# Check a sample ticket
print("\n" + "="*80)
print("SAMPLE TICKET DATA")
print("="*80)
if len(tickets) > 0:
    sample = tickets.iloc[0]
    print("\nFirst ticket - Non-empty fields:")
    for col in df.columns:
        val = sample[col]
        if pd.notna(val) and str(val).strip() != '':
            val_str = str(val)[:100]
            print(f"  {col}: {val_str}")

# Check what's in the metadata pickle
print("\n" + "="*80)
print("CHECKING FAISS METADATA")
print("="*80)
with open('data/tickets_meta.pkl', 'rb') as f:
    meta = pickle.load(f)

# Find first ticket in metadata
ticket_meta = [m for m in meta if m.get('document_type') != 'support_document']
if ticket_meta:
    print(f"\nFirst ticket in metadata has these fields:")
    first_ticket = ticket_meta[0]
    for key, val in first_ticket.items():
        if val is not None and str(val).strip() != '':
            val_str = str(val)[:100]
            print(f"  {key}: {val_str}")
