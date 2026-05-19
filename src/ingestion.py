import os
import glob
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Import helper functions from utils
from utils import init_hash_db, load_existing, get_text_hash

# Import document processor for PDF, DOCX, TXT files
try:
    from document_processor import process_all_documents
    DOCUMENT_PROCESSOR_AVAILABLE = True
except ImportError:
    print("⚠️ document_processor not available. Only Excel files will be processed.")
    DOCUMENT_PROCESSOR_AVAILABLE = False

load_dotenv()

INCOMING = os.getenv("INCOMING_DIR", os.path.join(os.path.dirname(__file__), "..", "data", "incoming"))

def process(force_reprocess=False):
    """
    Process incoming Excel files, deduplicate using hash, and store new rows.
    Args:
        force_reprocess: If True, reprocess all files regardless of hash database
    """
    conn = None
    new_rows = []
    try:
        print(f"Looking for Excel files in: {INCOMING}")
        if not os.path.exists(INCOMING):
            os.makedirs(INCOMING)
            print(f"Created directory: {INCOMING}")
            
        conn = init_hash_db()
        print("Database connection initialized")
        
        cur = conn.cursor()
        print("Database cursor created")
        
        # If force_reprocess is True, clear the hash database
        if force_reprocess:
            print("🔄 Force reprocess enabled - clearing hash database...")
            cur.execute("DELETE FROM processed")
            conn.commit()
            print("✅ Hash database cleared")
        
        existing = load_existing()
        print(f"Loaded {len(existing)} existing entries")
        
        # Get all Excel files and normalize paths
        xlsx_files = [os.path.abspath(f) for f in glob.glob(os.path.join(INCOMING, "*.xlsx"))]
        print(f"Found {len(xlsx_files)} Excel files:")
        for f in xlsx_files:
            print(f"  - {os.path.basename(f)}")
        
        if not xlsx_files:
            print("❌ No Excel files found in the incoming directory")
            return
            
        for fx in xlsx_files:
            try:
                print(f"\nProcessing file: {os.path.basename(fx)}")
                xlsx = pd.ExcelFile(fx)
                print(f"Sheets found: {xlsx.sheet_names}")
                
                for sheet in xlsx.sheet_names:
                    print(f"\nReading sheet: {sheet}")
                    df = pd.read_excel(fx, sheet_name=sheet)
                    print(f"Columns in {os.path.basename(fx)}, sheet {sheet}:")
                    print(df.columns.tolist())
                    
                    # Check if Number column exists BEFORE cleaning
                    if 'Number' in df.columns:
                        print(f"✓ 'Number' column found! Sample values: {df['Number'].head(3).tolist()}")
                    
                    # Clean column names
                    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
                    
                    # Check if number column exists AFTER cleaning
                    if 'number' in df.columns:
                        print(f"✓ 'number' column exists after cleaning! Sample values: {df['number'].head(3).tolist()}")
                    else:
                        print(f"✗ 'number' column NOT FOUND after cleaning!")
                        print(f"Available columns after cleaning: {df.columns.tolist()}")
                    
                    # Print first few rows for debugging
                    print("\nFirst few rows:")
                    print(df.head(2).to_string())
                    
                    # Convert to lowercase for better matching
                    if 'short_description' in df.columns:
                        df['short_description'] = df['short_description'].fillna('').astype(str).str.lower()
                    if 'description' in df.columns:
                        df['description'] = df['description'].fillna('').astype(str).str.lower()
                    if 'category' in df.columns:
                        df['category'] = df['category'].fillna('').astype(str).str.lower()
                    if 'subcategory' in df.columns:
                        df['subcategory'] = df['subcategory'].fillna('').astype(str).str.lower()
                    
                    for _, row in df.iterrows():
                        # Create a rich text representation for matching
                        text_parts = [
                            row.get('short_description', ''),
                            row.get('description', ''),
                            row.get('category', ''),
                            row.get('subcategory', '')
                        ]
                        text = ' '.join(filter(None, text_parts))
                        
                        h = get_text_hash(text)
                        if not force_reprocess and cur.execute("SELECT 1 FROM processed WHERE hash=?", (h,)).fetchone():
                            continue

                        record = row.to_dict()
                        record["ingested_at"] = datetime.utcnow()
                        new_rows.append(record)
                        cur.execute("INSERT INTO processed (hash) VALUES (?)", (h,))
                        
                conn.commit()
                print(f"✅ Successfully processed {fx}")
                
            except Exception as e:
                print(f"❌ Error processing {fx}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Process PDF, DOCX, TXT files if document processor is available
        if DOCUMENT_PROCESSOR_AVAILABLE:
            print("\n" + "="*60)
            print("📚 Processing support documents (PDF, DOCX, TXT)...")
            print("="*60)
            
            try:
                documents = process_all_documents(INCOMING)
                
                for doc in documents:
                    # Check if document was already processed using file hash (skip check if force_reprocess)
                    file_hash = doc.get('file_hash', '')
                    if not force_reprocess and cur.execute("SELECT 1 FROM processed WHERE hash=?", (file_hash,)).fetchone():
                        print(f"⏭️  Skipping {doc['filename']} (already processed)")
                        continue
                    
                    # Add document as a record
                    new_rows.append(doc)
                    cur.execute("INSERT INTO processed (hash) VALUES (?)", (file_hash,))
                    print(f"✅ Added {doc['filename']} to index")
                
                conn.commit()
                
            except Exception as e:
                print(f"⚠️ Error processing documents: {e}")
                import traceback
                traceback.print_exc()
                
        if new_rows:
            df_new = pd.DataFrame(new_rows)
            
            # Save to parquet file
            output_path = os.path.join(os.path.dirname(__file__), "..", "data", "tickets.parquet")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df_new.to_parquet(output_path, index=False)
            
            print(f"\n{'='*60}")
            print(f"✅ Total ingested: {len(df_new)} new records")
            print(f"   - Tickets: {len([r for r in new_rows if r.get('document_type') != 'support_document'])}")
            print(f"   - Documents: {len([r for r in new_rows if r.get('document_type') == 'support_document'])}")
            print(f"💾 Saved to: {output_path}")
            print(f"{'='*60}\n")
            return df_new
        else:
            print("ℹ️ No new rows ingested.")
            return None
            
    except Exception as e:
        print(f"❌ Error during ingestion process: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        if conn:
            try:
                conn.close()
                print("Database connection closed.")
            except Exception as e:
                print(f"⚠️ Error closing database connection: {e}")
    
    for fx in xlsx_files:
        try:
            print(f"\nProcessing file: {fx}")
            xlsx = pd.ExcelFile(fx)
            print(f"Sheets found: {xlsx.sheet_names}")
        except Exception as e:
            print(f"❌ Error reading {fx}: {e}")
            import traceback
            traceback.print_exc()
            continue

        for sheet in xlsx.sheet_names:
            df = xlsx.parse(sheet)
            print(f"\nColumns in {os.path.basename(fx)}, sheet {sheet}:")
            print(df.columns.tolist())
            
            # Clean column names
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
            
            # Print first few rows for debugging
            print("\nFirst few rows:")
            print(df.head(2).to_string())
            
            # Convert to lowercase for better matching
            if 'short_description' in df.columns:
                df['short_description'] = df['short_description'].fillna('').astype(str).str.lower()
            if 'description' in df.columns:
                df['description'] = df['description'].fillna('').astype(str).str.lower()
            if 'category' in df.columns:
                df['category'] = df['category'].fillna('').astype(str).str.lower()
            if 'subcategory' in df.columns:
                df['subcategory'] = df['subcategory'].fillna('').astype(str).str.lower()
            
            for _, row in df.iterrows():
                # Create a rich text representation for matching
                text_parts = [
                    row.get('short_description', ''),
                    row.get('description', ''),
                    row.get('category', ''),
                    row.get('subcategory', '')
                ]
                text = ' '.join(filter(None, text_parts))
                
                h = get_text_hash(text)
                if cur.execute("SELECT 1 FROM processed WHERE hash=?", (h,)).fetchone():
                    continue

                record = row.to_dict()
                record["ingested_at"] = datetime.utcnow()
                new_rows.append(record)
                cur.execute("INSERT INTO processed (hash) VALUES (?)", (h,))

    conn.commit()
    conn.close()

    if new_rows:
        df_new = pd.DataFrame(new_rows)
        print(f"✅ Ingested {len(df_new)} new rows.")
        # Save or process df_new as needed
    else:
        print("ℹ️ No new rows ingested.")    