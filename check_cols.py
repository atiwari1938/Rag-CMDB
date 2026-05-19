import pandas as pd
import os

excel_path = 'data/incoming/incident (3).xlsx'
print(f"Reading: {excel_path}\n")

# Read Excel
df = pd.read_excel(excel_path)
print(f"✓ Total rows: {len(df)}")
print(f"✓ Total columns: {len(df.columns)}\n")

print("="*80)
print("ALL COLUMNS (Original names from Excel):")
print("="*80)
for i, col in enumerate(df.columns, 1):
    print(f"{i:3d}. '{col}'")

# Look for Number column
print("\n" + "="*80)
print("SEARCHING FOR 'NUMBER' COLUMN:")
print("="*80)
number_cols = [col for col in df.columns if 'number' in col.lower() or 'num' in col.lower()]
if number_cols:
    print(f"✓ Found {len(number_cols)} column(s) with 'number' in name:")
    for col in number_cols:
        print(f"  - '{col}'")
        print(f"    Sample values: {df[col].head(3).tolist()}")
else:
    print("✗ No columns containing 'number' found")

# Show first row
print("\n" + "="*80)
print("FIRST ROW DATA (first 10 columns):")
print("="*80)
if len(df) > 0:
    for col in df.columns[:10]:
        val = df.iloc[0][col]
        if pd.notna(val):
            print(f"  {col}: {val}")

# Check what happens after column name cleaning
print("\n" + "="*80)
print("AFTER CLEANING (lowercase, spaces to underscores):")
print("="*80)
cleaned_cols = [c.strip().lower().replace(" ", "_") for c in df.columns]
for i, (orig, clean) in enumerate(zip(df.columns[:10], cleaned_cols[:10]), 1):
    print(f"  {orig:30s} → {clean}")
