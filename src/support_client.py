from openai import AzureOpenAI

# Initialize client with exact endpoint that works in test.py
client = AzureOpenAI(
    azure_endpoint="https://hexavarsity-secureapi.azurewebsites.net/api/azureai/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-02-01",
    api_key="a1f72ca8e12abf00",
    api_version="2024-02-01"
)

def get_chat_response(messages, context=None):
    """
    Get a response from the Azure OpenAI chat model with support context
    Args:
        messages: List of message dictionaries
        context: Optional dictionary containing relevant ticket data
    """
    try:
        print("\nPreparing chat request...")
        
        # Add system message with support context
        system_message = {
            "role": "system",
            "content": """You are an experienced IT Support Assistant. Analyze the provided context and user query to give accurate, relevant responses.
            
Guidelines:
1. Always consider the specific context provided in tickets/documentation
2. Prioritize official procedures and security protocols
3. Give step-by-step solutions when applicable
4. If information is missing, clearly state what additional details are needed
5. For critical issues, include escalation paths
6. Reference relevant ticket numbers or documentation when available

Current Support Knowledge Base Includes:
- Password reset procedures
- Access management protocols
- Software installation guidelines
- Network troubleshooting steps
- Security compliance requirements"""
        }
        
        # Insert context if provided
        if context:
            system_message["content"] += f"\n\nRelevant Context:\n{context}"
            print("Added context to system message")
            
        # Ensure system message is first
        if not messages or messages[0]["role"] != "system":
            messages = [system_message] + messages
        
        print(f"Sending request with {len(messages)} messages")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Deployment name
            messages=messages
        )
        
        print("Received response from API")
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error in chat request: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    try:
        # Test with a simple query first
        print("\nTest 1: Simple Query")
        response = get_chat_response([
            {"role": "user", "content": "How can you help me with IT support?"}
        ])
        print("\nResponse:", response)
        
        # Test with context
        print("\nTest 2: Query with Context")
        context = {
            "ticket_id": "INC001",
            "user_department": "Finance",
            "previous_incidents": "2 failed login attempts",
            "security_level": "High"
        }
        
        response = get_chat_response([
            {"role": "user", "content": "I need to reset my password"}
        ], str(context))
        
        print("\nResponse:", response)
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
