import pandas as pd
import os

parquet_path = os.path.join(os.path.dirname(__file__), "..", "data", "tickets.parquet")

if os.path.exists(parquet_path):
    df = pd.read_parquet(parquet_path)
    print(f"✅ Total rows: {len(df)}")
    print(f"📋 Columns: {df.columns.tolist()}")
    
    if 'document_type' in df.columns:
        print(f"\n📊 Document types:")
        print(df['document_type'].value_counts())
        
        # Check for support documents
        support_docs = df[df['document_type'] == 'support_document']
        print(f"\n📄 Support documents: {len(support_docs)}")
        if len(support_docs) > 0:
            print("\nSupport document filenames:")
            for idx, row in support_docs.iterrows():
                print(f"  - {row.get('filename', 'N/A')}")
    else:
        print("\n⚠️ No 'document_type' column found!")
        print(f"Available columns: {df.columns.tolist()}")
else:
    print(f"❌ File not found: {parquet_path}")
