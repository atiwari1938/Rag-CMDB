import pandas as pd
import os

# Load the parquet file
data_path = os.path.join('data', 'tickets.parquet')
df = pd.read_parquet(data_path)

print("="*80)
print("TICKET DATA ANALYSIS")
print("="*80)

print(f"\nTotal records: {len(df)}")
print(f"\nAll columns ({len(df.columns)}):")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. {col}")

print("\n" + "="*80)
print("SAMPLE TICKET DATA")
print("="*80)

if len(df) > 0:
    # Find first non-document record
    tickets = df[df['document_type'].isna()]
    if len(tickets) > 0:
        sample = tickets.iloc[0].to_dict()
        print("\nFirst ticket record:")
        for key, value in sample.items():
            if pd.notna(value):
                value_str = str(value)[:100] if len(str(value)) > 100 else str(value)
                print(f"  {key}: {value_str}")
    
    # Check for number-related columns
    print("\n" + "="*80)
    print("NUMBER/ID COLUMNS")
    print("="*80)
    number_cols = [col for col in df.columns if 'number' in col.lower() or 'id' in col.lower() or 'sys' in col.lower()]
    print(f"\nFound {len(number_cols)} number/ID related columns:")
    for col in number_cols:
        non_null = df[col].notna().sum()
        print(f"  - {col}: {non_null}/{len(df)} non-null values")
        if non_null > 0:
            print(f"    Sample: {df[df[col].notna()][col].iloc[0]}")
