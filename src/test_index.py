import pickle
import os

meta_path = os.path.join(os.path.dirname(__file__), "..", "data", "tickets_meta.pkl")

if os.path.exists(meta_path):
    with open(meta_path, 'rb') as f:
        tickets_meta = pickle.load(f)
    
    print(f"✅ Total items in index: {len(tickets_meta)}")
    
    # Count document types
    doc_types = {}
    support_docs = []
    
    for item in tickets_meta:
        doc_type = item.get('document_type', 'unknown')
        doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        if doc_type == 'support_document':
            support_docs.append(item)
    
    print(f"\n📊 Document type distribution:")
    for dtype, count in doc_types.items():
        print(f"  - {dtype}: {count}")
    
    print(f"\n📄 Support documents ({len(support_docs)}):")
    for doc in support_docs:
        print(f"\n  Filename: {doc.get('filename', 'N/A')}")
        print(f"  File type: {doc.get('file_type', 'N/A')}")
        print(f"  Short desc: {doc.get('short_description', 'N/A')[:80]}")
        print(f"  Has content: {bool(doc.get('content'))}")
        if doc.get('content'):
            print(f"  Content length: {len(doc.get('content', ''))}")
            print(f"  Content preview: {doc.get('content', '')[:200]}...")
else:
    print(f"❌ File not found: {meta_path}")
