# # import os
# # import pickle
# # import numpy as np
# # import pandas as pd
# # import faiss

# # from dotenv import load_dotenv
# # from openai_client import client, EMBED_ENGINE

# # # Load .env (in case it hasn’t been)
# # load_dotenv()

# # # Paths
# # BASE_DIR     = os.path.dirname(__file__)
# # DATA_DIR     = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))
# # TICKETS_PATH = os.path.join(DATA_DIR, "tickets.parquet")
# # INDEX_PATH   = os.path.join(DATA_DIR, "faiss_index.idx")
# # META_PATH    = os.path.join(DATA_DIR, "tickets_meta.pkl")

# # def load_tickets() -> pd.DataFrame:
# #     if not os.path.exists(TICKETS_PATH):
# #         raise FileNotFoundError(f"{TICKETS_PATH} not found. Run ingestion first.")
# #     return pd.read_parquet(TICKETS_PATH)

# # def embed_documents(batch_size: int = 20):
# #     df = load_tickets()

# #     # Prepare text blobs
# #     texts = (
# #         df["short_description"].fillna("").astype(str) +
# #         "\n" +
# #         df["description"].fillna("").astype(str)
# #     ).tolist()

# #     embeddings = []
# #     # Use the client.embeddings.create(...) with deployment_id
# #     for i in range(0, len(texts), batch_size):
# #         batch = texts[i : i + batch_size]
# #         resp  = client.embeddings.create(
# #             deployment_id=EMBED_ENGINE,
# #             input=batch
# #         )
# #         embeddings.extend([record.embedding for record in resp.data])

# #     # Build FAISS index
# #     dim   = len(embeddings[0])
# #     index = faiss.IndexFlatL2(dim)
# #     index.add(np.array(embeddings, dtype="float32"))
# #     faiss.write_index(index, INDEX_PATH)
# #     print(f"[✓] FAISS index saved to {INDEX_PATH} ({len(embeddings)} vectors)")

# #     # Save metadata
# #     meta_df = df[[
# #         "short_description",
# #         "description",
# #         "priority",
# #         "assignment_group",
# #         "task_type",
# #         "root_cause_code"
# #     ]].copy()
# #     with open(META_PATH, "wb") as f:
# #         pickle.dump(meta_df, f)
# #     print(f"[✓] Metadata saved to {META_PATH}")

# # if __name__ == "__main__":
# #     embed_documents()


# import os
# import pickle
# import faiss
# import numpy as np
# import pandas as pd
# from sentence_transformers import SentenceTransformer
# from dotenv import load_dotenv

# # Load .env vars
# load_dotenv()

# # Paths
# BASE_DIR     = os.path.dirname(__file__)
# DATA_DIR     = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))
# TICKETS_PATH = os.path.join(DATA_DIR, "tickets.parquet")
# INDEX_PATH   = os.path.join(DATA_DIR, "faiss_index.idx")
# META_PATH    = os.path.join(DATA_DIR, "tickets_meta.pkl")

# # Embedding model name (HuggingFace/Jina) :contentReference[oaicite:1]{index=1}
# HF_MODEL = os.getenv("HF_EMBEDDING_MODEL", "jinaai/jina-embeddings-v2-base-en")

# def load_tickets() -> pd.DataFrame:
#     if not os.path.exists(TICKETS_PATH):
#         raise FileNotFoundError(f"{TICKETS_PATH} not found. Run ingestion first.")
#     return pd.read_parquet(TICKETS_PATH)

# def embed_documents(batch_size: int = 32):
#     # Load data
#     df = load_tickets()

#     # Combine key fields into one text blob per ticket
#     texts = (
#         df["short_description"].fillna("").astype(str) +
#         "\n" +
#         df["description"].fillna("").astype(str)
#     ).tolist()

#     # Initialize HuggingFace SentenceTransformer
#     embedder = SentenceTransformer(HF_MODEL)

#     # Compute embeddings in batches
#     embeddings = []
#     for i in range(0, len(texts), batch_size):
#         batch = texts[i : i + batch_size]
#         emb = embedder.encode(batch, convert_to_numpy=True, show_progress_bar=True)
#         embeddings.append(emb)
#     embeddings = np.vstack(embeddings)

#     # Build FAISS index
#     dim   = embeddings.shape[1]
#     index = faiss.IndexFlatL2(dim)
#     index.add(embeddings.astype("float32"))
#     faiss.write_index(index, INDEX_PATH)
#     print(f"[✓] FAISS index saved to {INDEX_PATH} ({len(texts)} vectors)")

#     # Save metadata for lookup
#     meta_df = df[[
#         "short_description",
#         "description",
#         "priority",
#         "assignment_group",
#         "task_type",
#         "root_cause_code"
#     ]].copy()
#     with open(META_PATH, "wb") as f:
#         pickle.dump(meta_df, f)
#     print(f"[✓] Metadata saved to {META_PATH}")

# if __name__ == "__main__":
#     embed_documents()

import os
import pickle
import numpy as np
import pandas as pd
import faiss
from dotenv import load_dotenv
from openai_client import client, EMBED_DEPLOYMENT

# Load .env only if necessary
load_dotenv()

# Paths
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))
TICKETS_PATH = os.path.join(DATA_DIR, "tickets.parquet")
INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.idx")
META_PATH = os.path.join(DATA_DIR, "tickets_meta.pkl")

def load_tickets() -> pd.DataFrame:
    if not os.path.exists(TICKETS_PATH):
        raise FileNotFoundError(f"{TICKETS_PATH} not found. Run ingestion first.")
    return pd.read_parquet(TICKETS_PATH)

def embed_documents(batch_size: int = 20):
    df = load_tickets()
    texts = (
        df["short_description"].fillna("").astype(str) +
        "\n" +
        df["description"].fillna("").astype(str)
    ).tolist()

    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.embeddings.create(
            model="text-embedding-ada-002",
            input=batch,
            encoding_format="float"
        )
        # Adjust response parsing based on actual API response
        try:
            embeddings.extend([d['embedding'] for d in resp['data']])
        except (TypeError, KeyError, AttributeError):
            # Try dot notation if using OpenAI SDK >=1.0
            embeddings.extend([d.embedding for d in resp.data])

    if not embeddings:
        raise ValueError("No embeddings were generated.")

    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings, dtype="float32"))
    faiss.write_index(index, INDEX_PATH)
    print(f"[✔] FAISS index saved to {INDEX_PATH} ({len(embeddings)} vectors)")

    meta_df = df[[
        "short_description",
        "description",
        "priority",
        "assignment_group",
        "task_type",
        "root_cause_code"
    ]].copy()
    with open(META_PATH, "wb") as f:
        pickle.dump(meta_df, f)
    print(f"[✔] Metadata saved to {META_PATH}")

if __name__ == "__main__":
    embed_documents()