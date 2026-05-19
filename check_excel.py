import pandas as pd

# Read Excel directly
print("READING EXCEL FILE DIRECTLY:")
df = pd.read_excel('data/incoming/incident (3).xlsx')

print(f"\nOriginal columns from Excel ({len(df.columns)}):")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:2d}. '{col}'")

# Check if Number column exists
has_number = any('number' in str(col).lower() for col in df.columns)
print(f"\nHas 'Number' column?: {has_number}")

if has_number:
    number_col = [col for col in df.columns if 'number' in str(col).lower()][0]
    print(f"Number column name: '{number_col}'")
    print(f"Sample values: {df[number_col].head(3).tolist()}")

# Show what happens after cleaning
print("\nAfter column name cleaning:")
cleaned = [c.strip().lower().replace(" ", "_") for c in df.columns]
for orig, clean in list(zip(df.columns, cleaned))[:10]:
    print(f"  '{orig}' → '{clean}'")
