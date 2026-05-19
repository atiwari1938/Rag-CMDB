import sys
from openai import AzureOpenAI

sys.stderr.write("Starting client initialization...\n")

# Initialize client with exact endpoint that works in test.py
client = AzureOpenAI(
    azure_endpoint="https://hexavarsity-secureapi.azurewebsites.net/api/azureai/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-02-01",
    api_key="a1f72ca8e12abf00",
    api_version="2024-02-01"
)

sys.stderr.write("Client initialized\n")

def get_chat_response(messages, context=None):
    """
    Get a response from the Azure OpenAI chat model with support context
    Args:
        messages: List of message dictionaries
        context: Optional dictionary containing relevant ticket data
    """
    try:
        sys.stderr.write("\nPreparing chat request...\n")
        
        # Add system message with support context
        system_message = {
            "role": "system",
            "content": """You are an experienced IT Support Assistant. Analyze the provided context and user query to give accurate, relevant responses."""
        }
        
        # Insert context if provided
        if context:
            system_message["content"] += f"\n\nRelevant Context:\n{context}"
            sys.stderr.write("Added context to system message\n")
            
        # Ensure system message is first
        if not messages or messages[0]["role"] != "system":
            messages = [system_message] + messages
        
        sys.stderr.write(f"Sending request with {len(messages)} messages\n")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Deployment name
            messages=messages
        )
        
        sys.stderr.write("Received response from API\n")
        return response.choices[0].message.content
        
    except Exception as e:
        sys.stderr.write(f"Error in chat request: {str(e)}\n")
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise

if __name__ == "__main__":
    try:
        # Test with a simple query first
        sys.stderr.write("\nTest 1: Simple Query\n")
        response = get_chat_response([
            {"role": "user", "content": "Hello, how are you?"}
        ])
        sys.stderr.write(f"\nResponse: {response}\n")
        
    except Exception as e:
        sys.stderr.write(f"Test failed: {str(e)}\n")
        import traceback
        traceback.print_exc(file=sys.stderr)
