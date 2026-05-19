import sys
from openai_client import get_chat_response

# Test cases with different contexts
def test_basic_query():
    print("\nTest 1: Basic Query without Context")
    response = get_chat_response([
        {"role": "user", "content": "How do I reset my password?"}
    ])
    print("Response:", response)

def test_with_similar_tickets():
    print("\nTest 2: Query with Similar Tickets")
    context = {
        "ticket_id": "INC123",
        "similar_tickets": [
            "INC120: User password expired, guided through reset process",
            "INC121: User account locked after multiple attempts"
        ],
        "user_info": {
            "department": "Finance",
            "role": "Senior Analyst"
        }
    }
    response = get_chat_response([
        {"role": "user", "content": "I need to reset my password urgently"}
    ], context)
    print("Response:", response)

def test_with_department_policy():
    print("\nTest 3: Query with Department Policy")
    context = {
        "ticket_id": "REQ456",
        "department_policies": [
            "Finance users require manager approval for software installs",
            "All software must be from approved catalog"
        ],
        "user_info": {
            "department": "Finance",
            "role": "Analyst"
        }
    }
    response = get_chat_response([
        {"role": "user", "content": "I need to install Python on my machine"}
    ], context)
    print("Response:", response)

if __name__ == "__main__":
    try:
        print("Starting RAG-enhanced GPT Tests...")
        
        test_basic_query()
        test_with_similar_tickets()
        test_with_department_policy()
        
        print("\nAll tests completed successfully")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
