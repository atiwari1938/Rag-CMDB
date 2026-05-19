import os
import faiss
import pickle
import numpy as np
from openai_client import client, CHAT_DEPLOYMENT, EMBED_DEPLOYMENT

# Constants
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))
INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.idx")
META_PATH = os.path.join(DATA_DIR, "tickets_meta.pkl")

def retrieve(query: str, tickets: list = None, top_k: int = 5) -> list:
    """
    Retrieves relevant tickets based on the query using semantic search.
    Args:
        query: The search query
        tickets: List of tickets (unused, kept for backward compatibility)
        top_k: Number of most relevant tickets to return (default: 5)
    Returns:
        List of most relevant tickets
    """
    try:
        # Load FAISS index and metadata
        index = faiss.read_index(INDEX_PATH)
        with open(META_PATH, 'rb') as f:
            tickets_meta = pickle.load(f)
        
        # Debug: Log document types in metadata
        doc_types = {}
        for item in tickets_meta:
            dt = item.get('document_type', 'unknown')
            doc_types[dt] = doc_types.get(dt, 0) + 1
        print(f"🔍 Index contains: {doc_types}")
        
        # Prepare query
        query = query.lower()  # Convert to lowercase to match ingested data
        
        # Get query embedding
        resp = client.embeddings.create(
            model=EMBED_DEPLOYMENT,
            input=[query]
        )
        query_embedding = np.array(resp.data[0].embedding).reshape(1, -1).astype('float32')
        
        # Search index with increased k to allow for filtering
        # Search ALL items to ensure documents are always considered
        search_k = len(tickets_meta)  # Search everything to ensure documents are found
        D, I = index.search(query_embedding, search_k)
        print(f"🔎 Searching {search_k} candidates from {len(tickets_meta)} total items")
        
        # Filter and rank results
        results = []
        seen_items = set()  # To avoid duplicates
        docs_found = 0
        
        for idx in I[0]:
            if idx != -1:  # -1 indicates no match found
                item = tickets_meta[idx]
                
                # Create unique identifier for deduplication
                item_type = item.get('document_type', 'ticket')
                
                # Debug: Count documents
                if item_type == 'support_document':
                    docs_found += 1
                    print(f"📄 Found document #{docs_found}: {item.get('filename', 'N/A')}")
                
                if item_type == 'support_document':
                    # For documents, use filename as unique identifier
                    unique_id = f"doc_{item.get('filename', '')}"
                else:
                    # For tickets, use description as before
                    unique_id = f"ticket_{item.get('short_description', '')}"
                
                if unique_id in seen_items:
                    continue
                seen_items.add(unique_id)
                
                # Calculate relevance score
                relevance = 0
                query_terms = set(query.split())
                
                # Handle both tickets and documents
                if item_type == 'support_document':
                    # For documents: check filename and content
                    filename = item.get('filename', '').lower()
                    content = item.get('content', '').lower()
                    desc = item.get('description', '').lower()
                    
                    # Debug log for ALL documents
                    print(f"🔍 Document: {filename}")
                    print(f"  Query: '{query}'")
                    print(f"  Query terms: {query_terms}")
                    print(f"  Content length: {len(content)}")
                    print(f"  First 200 chars of content: {content[:200]}")
                    
                    # MUCH higher weights for documents to prioritize them
                    term_matches = {}
                    for term in query_terms:
                        matches = 0
                        if term in filename:
                            relevance += 100  # Very high weight for filename matches
                            matches += 100
                        if term in desc:
                            relevance += 50  # High weight for description
                            matches += 50
                        if term in content:
                            relevance += 30  # Strong weight for content matches
                            matches += 30
                        if matches > 0:
                            term_matches[term] = matches
                    
                    print(f"  Term matches: {term_matches}")
                    print(f"  Total relevance: {relevance}")
                else:
                    # For tickets: check title, description, category
                    title = item.get('short_description', '').lower()
                    desc = item.get('description', '').lower()
                    category = item.get('category', '').lower()
                    subcategory = item.get('subcategory', '').lower()
                    
                    for term in query_terms:
                        if term in title:
                            relevance += 3  # Higher weight for title matches
                        if term in desc:
                            relevance += 2  # Medium weight for description matches
                        if term in category or term in subcategory:
                            relevance += 1  # Lower weight for category matches
                
                results.append((relevance, item))
                
                # Don't limit results anymore - process all candidates
                # if len(results) >= top_k * 2:  # Get double the requested amount for sorting
                #     break
        
        # Sort by relevance and return top_k results
        results.sort(key=lambda x: (-x[0], x[1].get('short_description', '')))  # Sort by relevance desc, then title
        
        # Debug: Log top 10 results with scores
        print(f"\n📊 Top 10 results by relevance:")
        for i, (score, item) in enumerate(results[:10], 1):
            item_type = item.get('document_type', 'ticket')
            if item_type == 'support_document':
                name = item.get('filename', 'N/A')
            else:
                name = item.get('short_description', 'N/A')[:60]
            print(f"  {i}. [{item_type}] Score: {score} - {name}")
        
        top_results = [ticket for _, ticket in results[:top_k]]
        
        # Debug: Log what we're returning
        result_types = {}
        for item in top_results:
            dt = item.get('document_type', 'unknown')
            result_types[dt] = result_types.get(dt, 0) + 1
        print(f"📤 Returning {len(top_results)} results: {result_types}")
        
        return top_results
        
    except Exception as e:
        print(f"❌ Error during retrieval: {e}")
        # Fallback to simple filtering if semantic search fails
        return tickets[:top_k] if tickets else []

def generate_response(user_query: str, context_tickets: list) -> str:
    """
    Generates a response to user_query based on context from tickets and documents.
    Args:
        user_query: The user's question
        context_tickets: List of relevant support tickets and documents for context
    Returns:
        str: AI-generated response based on the context
    """
    if not user_query or not context_tickets:
        return "Missing query or context tickets."

    try:
        # Format the context from tickets and documents
        snippets = []
        for i, item in enumerate(context_tickets):
            if isinstance(item, dict):
                item_type = item.get('document_type', 'ticket')
                
                if item_type == 'support_document':
                    # Format document content
                    filename = item.get('filename', 'Unknown Document')
                    content = item.get('content', '')
                    # Limit content to first 1000 characters to avoid token limits
                    content_preview = content[:1000] + "..." if len(content) > 1000 else content
                    snippets.append(f"{i+1}. [Document: {filename}]\n{content_preview}")
                else:
                    # Format ticket content
                    short_desc = item.get('short_description', 'No title')
                    desc = item.get('description', 'No description')
                    snippets.append(f"{i+1}. [Ticket: {short_desc}]\n{desc}")
        
        if not snippets:
            return "No relevant context found to answer the question."
        
        context = "\n\n".join(snippets)
        
        # Make the API call
        try:
            completion = client.chat.completions.create(
                model=CHAT_DEPLOYMENT,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful support assistant. Use the provided support tickets and documents to answer the user's question."
                    },
                    {
                        "role": "user",
                        "content": f"Based on these support tickets and documents:\n\n{context}\n\nQuestion: {user_query}"
                    }
                ],
                temperature=0.7,
                max_tokens=256
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"❌ Error in chat completion: {str(e)}")
            return f"Error generating response: {str(e)}"
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return "Sorry, an error occurred while generating the response."

if __name__ == "__main__":
    # Sample usage
    sample_tickets = [
        {"short_description": "Password reset", "description": "User forgot password."},
        {"short_description": "Account locked", "description": "User entered wrong password 5 times."}
    ]
    response = generate_response("How do I reset my password?", sample_tickets)
    print(response)