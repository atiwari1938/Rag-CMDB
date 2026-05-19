import pandas as pd
import os

print("="*80)
print("CHECKING EXCEL FILE COLUMNS")
print("="*80)

# Check incident file
incident_file = 'data/incoming/incident (3).xlsx'
if os.path.exists(incident_file):
    print(f"\nFile: {incident_file}")
    df = pd.read_excel(incident_file)
    print(f"Total rows: {len(df)}")
    print(f"\nColumns ({len(df.columns)}):")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    
    print("\nFirst row sample:")
    if len(df) > 0:
        first_row = df.iloc[0]
        for col in df.columns[:15]:  # Show first 15 columns
            val = first_row[col]
            if pd.notna(val):
                print(f"  {col}: {str(val)[:80]}")

# Check request item file
req_file = 'data/incoming/sc_req_item (1) 1.xlsx'
if os.path.exists(req_file):
    print("\n" + "="*80)
    print(f"\nFile: {req_file}")
    df2 = pd.read_excel(req_file)
    print(f"Total rows: {len(df2)}")
    print(f"\nColumns ({len(df2.columns)}):")
    for i, col in enumerate(df2.columns, 1):
        print(f"  {i}. {col}")
