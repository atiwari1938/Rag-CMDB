# import argparse
# from retriever import retrieve
# from generator import generate_response

# def main():
#     p = argparse.ArgumentParser(description="SupportAssist AI CLI")
#     sub = p.add_subparsers(dest="cmd", required=True)
#     q = sub.add_parser("retrieve")
#     q.add_argument("--query", required=True)
#     g = sub.add_parser("generate")
#     g.add_argument("--query", required=True)

#     args = p.parse_args()
#     if args.cmd == "retrieve":
#         print(retrieve(args.query))
#     elif args.cmd == "generate":
#         print(generate_response(args.query, retrieve(args.query)))

# if __name__ == "__main__":
#     main()
# src/main.py

import argparse
from ingestion import process as ingest
from embeddings import embed_documents
from retriever import retrieve
from generator import generate_response

def main():
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

    # Step 1: Ingestion
    print("\n1️⃣  Data Ingestion")
    ingest()

    # Step 2: Embeddings & Indexing
    print("\n2️⃣  Embedding Documents")
    embed_documents()

    # Step 3: Retrieval
    print(f"\n3️⃣  Retrieving top {args.top_k} tickets for query:\n   \"{args.query}\"")
    tickets = retrieve(args.query, top_k=args.top_k)
    for i, t in enumerate(tickets, 1):
        print(f"   {i}. {t['short_description']}")

    # Step 4: Generation
    print("\n4️⃣  Generating AI Response")
    response = generate_response(args.query, tickets)
    print("\n💬 Final Response:\n")
    print(response)

if __name__ == "__main__":
    main()
