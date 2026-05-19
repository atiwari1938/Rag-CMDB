import os
from dotenv import load_dotenv
from openai import AzureOpenAI

print("Debug: Starting client initialization")
load_dotenv()

# Initialize the Azure OpenAI client using environment variables
try:
    # The client will automatically use environment variables:
    # AZURE_OPENAI_ENDPOINT
    # AZURE_OPENAI_API_KEY
    # OPENAI_API_VERSION
    client = AzureOpenAI()
    print("\nDebug: Azure OpenAI client initialized successfully")
except Exception as e:
    print(f"\nError initializing Azure OpenAI client: {str(e)}")
    import traceback
    traceback.print_exc()
    raise

# Model deployments
CHAT_DEPLOYMENT = "gpt-4o-mini"  # Chat model
EMBED_DEPLOYMENT = "text-embedding-ada-002"  # Embedding model

def get_chat_response(messages, context=None, max_retries=3):
    """
    Get a response from the Azure OpenAI chat model with support context and RAG integration
    Args:
        messages: List of message dictionaries
        context: Optional dictionary containing relevant ticket data and retrieved knowledge
        max_retries: Maximum number of retries in case of transient errors
    """
    try:
        print("\nPreparing chat request...")
        
        # Add system message with support context and RAG integration
        system_message = {
            "role": "system",
            "content": """You are an experienced IT Support Assistant with access to a knowledge base of support tickets and documentation. Analyze the provided context, retrieved knowledge, and user query to give accurate, relevant responses.
            
Guidelines:
1. Always analyze and reference the retrieved context/knowledge when available
2. Prioritize official procedures from documented solutions
3. Give clear step-by-step solutions with detailed instructions
4. If similar tickets exist in context, adapt their solutions appropriately
5. For critical issues, include escalation paths and SLA information
6. Reference relevant ticket numbers, documentation, or knowledge base articles
7. If the retrieved context is insufficient, indicate what additional information is needed
8. Maintain security and compliance requirements in all solutions

Knowledge Integration:
- Use retrieved ticket history to identify common patterns
- Apply successful solutions from similar past tickets
- Consider department-specific policies and procedures
- Reference relevant documentation and guidelines
- Factor in user roles and access levels from context"""
        }
        
        # Insert context if provided
        if context:
            # Format context for better readability
            if isinstance(context, dict):
                formatted_context = "\n".join([f"{k}: {v}" for k, v in context.items()])
            else:
                formatted_context = str(context)
                
            system_message["content"] += f"\n\nRetrieved Knowledge and Context:\n{formatted_context}"
            print("Added retrieved knowledge and context to system message")
            
        # Ensure system message is first
        if not messages or messages[0]["role"] != "system":
            messages = [system_message] + messages
            print("Inserted system message at start of conversation")
        
        print(f"\nPreparing GPT request...")
        print(f"Total messages: {len(messages)}")
        print(f"Latest user query: {messages[-1]['content'][:100]}...")
        
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # Using the correct deployment name
                    messages=messages
                )
                print("Received GPT response successfully")
                return response.choices[0].message.content
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise  # Re-raise the last error if all retries failed
                print(f"Attempt {attempt + 1} failed, retrying...")
                import time
                time.sleep(1)  # Wait 1 second before retrying
        
    except Exception as e:
        print(f"\nError in get_chat_response: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def get_embeddings(texts, max_retries=3):
    """
    Get embeddings for one or more texts using Azure OpenAI
    Args:
        texts: Single string or list of strings to embed
        max_retries: Maximum number of retries in case of transient errors
    Returns:
        Single embedding vector or list of embedding vectors
    """
    try:
        print("\nPreparing embedding request...")
        if isinstance(texts, str):
            texts = [texts]
            
        # Clean and prepare texts
        cleaned_texts = [
            text.replace('\n', ' ').replace('\r', ' ').strip()
            for text in texts if text and text.strip()  # Skip empty texts
        ]
        
        if not cleaned_texts:
            raise ValueError("No valid texts to embed after cleaning")
            
        print(f"Generating embeddings for {len(cleaned_texts)} texts")
        
        for attempt in range(max_retries):
            try:
                response = client.embeddings.create(
                    model=EMBED_DEPLOYMENT,
                    input=cleaned_texts,
                    encoding_format="float"
                )
                print(f"✅ Successfully received embeddings for {len(cleaned_texts)} texts")
                embeddings = [data.embedding for data in response.data]
                return embeddings[0] if len(embeddings) == 1 else embeddings
                
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    print(f"\n❌ All {max_retries} attempts failed.")
                    raise  # Re-raise the last error
                print(f"⚠️ Attempt {attempt + 1} failed, retrying in 1 second...")
                print(f"Error details: {str(e)}")
                import time
                time.sleep(1)
        
    except Exception as e:
        print(f"\nError getting embeddings: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

# Example usage
if __name__ == "__main__":
    import sys
    sys.stdout = sys.__stdout__  # Force output to real stdout
    sys.stderr = sys.__stderr__  # Force output to real stderr
    
    try:
        print("\n=== Starting Test Cases ===", flush=True)
        
        # Test Case 1: Password Reset with Context
        print("\nTest Case 1: Password Reset Request")
        context = {
            "ticket_id": "INC001",
            "user_department": "Finance",
            "previous_incidents": "2 failed login attempts",
            "security_level": "High",
            "relevant_policies": ["MFA Required", "90-day password rotation"]
        }
        
        messages = [
            {"role": "user", "content": "I need to reset my password urgently for the financial system"}
        ]
        
        response = get_chat_response(messages, str(context))
        print("\nContext-Aware Response:", response)

        # Test Case 2: Software Installation with Policy Check
        print("\nTest Case 2: Software Installation Request")
        context = {
            "ticket_id": "REQ002",
            "software_name": "Adobe Creative Suite",
            "user_role": "Marketing Designer",
            "license_status": "Available",
            "approval_status": "Pending manager approval"
        }
        
        messages = [
            {"role": "user", "content": "I need to install Adobe Creative Suite on my workstation"}
        ]
        
        response = get_chat_response(messages, str(context))
        print("\nPolicy-Aware Response:", response)

        # Test Case 3: Network Issue with Technical Context
        print("\nTest Case 3: Network Connectivity Issue")
        context = {
            "ticket_id": "INC003",
            "system_status": "VPN Service: Active, Network Load: 85%",
            "user_location": "Remote",
            "recent_changes": "VPN client update deployed yesterday",
            "affected_services": ["Email", "SharePoint"]
        }
        
        messages = [
            {"role": "user", "content": "Cannot access company resources while working from home"}
        ]
        
        response = get_chat_response(messages, str(context))
        print("\nTechnical Context Response:", response)

        # Test embeddings
        print("\nTesting Embedding Generation:")
        texts = [
            "High priority password reset request for financial system access",
            "VPN connectivity issues after recent system update",
            "Software installation request pending approval"
        ]
        embeddings = get_embeddings(texts)
        print(f"Generated {len(embeddings)} embeddings")
        print(f"Embedding dimension: {len(embeddings[0])}")
        
        print("\n=== All Tests Completed Successfully ===")
        
    except Exception as e:
        print(f"\nTest run failed: {str(e)}")
        import traceback
        traceback.print_exc()
