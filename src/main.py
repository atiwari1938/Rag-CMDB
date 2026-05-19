print("Starting script...")
try:
    import sys
    import os
    # Add the src directory to the Python path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    import argparse
    print("Imported argparse")
    from src.ingestion import process as ingest
    print("Imported ingestion")
    from src.embeddings import embed_documents
    print("Imported embeddings")
    from src.retriever import retrieve, generate_response
    print("Imported retriever")
except Exception as e:
    import traceback
    print(f"Import error: {e}")
    traceback.print_exc()

def main():
    """
    Run the full SupportAssist AI pipeline: ingest → embed → retrieve → generate.
    """
    parser = argparse.ArgumentParser(
        description="Run the full SupportAssist AI pipeline: ingest → embed → retrieve → generate"
    )
    parser.add_argument(
        "-q", "--query",
        type=str,
        required=True,
        help="User query to test the RAG pipeline"
    )
    parser.add_argument(
        "--top_k",
        type=int,
        default=3,
        help="Number of similar tickets to retrieve"
    )
    args = parser.parse_args()

    if not args.query.strip():
        print("❌ Error: Query cannot be empty.")
        return

    try:
        print("\n1️⃣  Data Ingestion")
        print("Starting ingestion process...")
        ingest()
        print("Ingestion completed successfully")
    except Exception as e:
        print(f"❌ Data ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return

    try:
        print("\n2️⃣  Embedding Documents")
        embed_documents()
    except Exception as e:
        print(f"❌ Embedding documents failed: {e}")
        return

    try:
        print(f"\n3️⃣  Retrieving top {args.top_k} tickets for query:\n   \"{args.query}\"")
        tickets = retrieve(args.query, [], args.top_k)
        if tickets:
            for i, t in enumerate(tickets, 1):
                print(f"   {i}. {t['short_description']}")
        else:
            print("   No relevant tickets found.")
    except Exception as e:
        print(f"❌ Retrieval failed: {e}")
        return

    try:
        print("\n4️⃣  Generating AI Response")
        response = generate_response(args.query, tickets)
        print("\n💬 Final Response:\n")
        print(response)
    except Exception as e:
        print(f"❌ Generation failed: {e}")

if __name__ == "__main__":
    main()