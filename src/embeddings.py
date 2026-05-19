import os
import pickle
import numpy as np
import pandas as pd
import faiss
from dotenv import load_dotenv

print("Debug: Importing OpenAI client...")
try:
    from openai_client import client, EMBED_DEPLOYMENT
    print("Debug: OpenAI client imported successfully")
except Exception as e:
    print(f"Debug: Error importing OpenAI client: {e}")
    import traceback
    traceback.print_exc()
    raise

load_dotenv()

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))
TICKETS_PATH = os.path.join(DATA_DIR, "tickets.parquet")
INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.idx")
META_PATH = os.path.join(DATA_DIR, "tickets_meta.pkl")

def load_tickets() -> pd.DataFrame:
    """
    Loads tickets data from parquet file.
    """
    if not os.path.exists(TICKETS_PATH):
        raise FileNotFoundError(f"{TICKETS_PATH} not found. Run ingestion first.")
    return pd.read_parquet(TICKETS_PATH)

def embed_documents(batch_size: int = 20):
    """
    Embeds tickets and builds FAISS index.
    """
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    try:
        df = load_tickets()
    except Exception as e:
        print(f"❌ Failed to load tickets: {e}")
        return

    # Prepare texts for embedding
    texts = []
    meta_data = []
    
    # Debug: Check if number column exists in dataframe
    if 'number' in df.columns:
        print(f"✓✓✓ DataFrame HAS 'number' column! Sample: {df['number'].head(3).tolist()}")
    else:
        print(f"✗✗✗ DataFrame DOES NOT have 'number' column!")
        print(f"Available columns: {df.columns.tolist()}")
    
    for _, row in df.iterrows():
        short_desc = str(row.get('short_description', '') or '')
        desc = str(row.get('description', '') or '')
        
        # For support documents, use content field
        if row.get('document_type') == 'support_document':
            content = str(row.get('content', '') or '')
            combined = f"{short_desc}\n{content}".strip()
        else:
            combined = f"{short_desc}\n{desc}".strip()
        
        # Truncate to ~6000 characters (~2000 tokens) to stay under 8192 token limit
        MAX_CHARS = 6000
        if len(combined) > MAX_CHARS:
            combined = combined[:MAX_CHARS] + "..."
            
        if combined:
            texts.append(combined)
            # Store ALL fields for later retrieval (including ticket number)
            meta_dict = row.to_dict()
            
            # Debug: Check if first non-document item has number field
            if len(meta_data) == 0 and row.get('document_type') != 'support_document':
                print(f"\n🔍 First ticket metadata check:")
                print(f"   Keys in meta_dict: {list(meta_dict.keys())}")
                print(f"   Has 'number'?: {'number' in meta_dict}")
                if 'number' in meta_dict:
                    print(f"   Number value: {meta_dict['number']}")
            
            # Ensure these fields exist for compatibility
            meta_dict.update({
                'short_description': short_desc,
                'description': desc,
            })
            meta_data.append(meta_dict)

    if not texts:
        print("❌ No valid texts to embed")
        return

    embeddings = []
    total_batches = (len(texts) + batch_size - 1) // batch_size
    print(f"🚀 Starting embedding process for {len(texts)} texts in {total_batches} batches...")

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        current_batch = i // batch_size + 1
        try:
            print(f"📦 Processing batch {current_batch}/{total_batches} ({len(batch)} texts)...")
            resp = client.embeddings.create(
                input=batch,
                model=EMBED_DEPLOYMENT
            )
            batch_embeddings = [item.embedding for item in resp.data]
            embeddings.extend(batch_embeddings)
            print(f"✅ Successfully embedded batch {current_batch}/{total_batches}")
        except Exception as e:
            print(f"❌ Error embedding batch {current_batch}: {e}")
            print(f"First text in failed batch: {batch[0][:100]}...")  # Show truncated first text
            continue

    print(f"📊 Completed embedding process: {len(embeddings)}/{len(texts)} texts successfully embedded")

    if not embeddings:
        print("❌ No embeddings generated.")
        return

    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings, dtype="float32"))
    faiss.write_index(index, INDEX_PATH)
    print(f"✅ FAISS index saved to {INDEX_PATH} ({len(embeddings)} vectors)")

    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(META_PATH), exist_ok=True)
    
    # Save filtered metadata from the embedding process
    with open(META_PATH, "wb") as f:
        pickle.dump(meta_data, f)
    print(f"✅ Metadata saved to {META_PATH} ({len(meta_data)} records)")

if __name__ == "__main__":
    embed_documents()