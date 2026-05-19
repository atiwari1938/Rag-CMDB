import pickle
import os

# Load metadata
meta_path = os.path.join('..', 'data', 'tickets_meta.pkl')
with open(meta_path, 'rb') as f:
    meta = pickle.load(f)

# Find documents
docs = [m for m in meta if m.get('document_type') == 'support_document']

print(f"Found {len(docs)} documents\n")

for doc in docs:
    print("=" * 80)
    print(f"Filename: {doc.get('filename')}")
    print(f"Short description: {doc.get('short_description', 'N/A')}")
    
    content = doc.get('content', '').lower()
    print(f"\nContent length: {len(content)} characters")
    
    # Check for search terms
    search_terms = ['secure', 'form', 'liveperson']
    print("\nSearch term analysis:")
    for term in search_terms:
        count = content.count(term)
        print(f"  '{term}': appears {count} times")
        if count > 0:
            # Find first occurrence context
            idx = content.find(term)
            context_start = max(0, idx - 50)
            context_end = min(len(content), idx + 50)
            print(f"    First occurrence context: ...{content[context_start:context_end]}...")
    
    print("\nFirst 500 characters of content:")
    print(content[:500])
    print("=" * 80)
