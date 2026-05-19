import os
from dotenv import load_dotenv
import requests
import sys

print("Loading environment...", flush=True)
load_dotenv()

api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

print(f"Endpoint: {endpoint}", flush=True)
print(f"API Key: {api_key[:4]}...{api_key[-4:]}", flush=True)

# Use the exact endpoint from .env
endpoint = "https://hexavarsity-secureapi.azurewebsites.net/api/azureai/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-02-01"
print(f"Using exact endpoint: {endpoint}", flush=True)

headers = {
    "Content-Type": "application/json",
    "api-key": api_key,
    "Accept": "application/json"
}

data = {
    "messages": [
        {"role": "system", "content": "You are a helpful IT support assistant."},
        {"role": "user", "content": "How do I reset my password?"}
    ]
}

try:
    print("\nSending request...", flush=True)
    response = requests.post(endpoint, headers=headers, json=data, timeout=30)
    print(f"\nStatus code: {response.status_code}", flush=True)
    print(f"Response headers: {dict(response.headers)}", flush=True)
    print(f"\nResponse text: {response.text}", flush=True)
except requests.exceptions.Timeout:
    print("\nRequest timed out after 30 seconds", flush=True)
except requests.exceptions.RequestException as e:
    print(f"\nRequest failed: {str(e)}", flush=True)
except Exception as e:
    print(f"\nUnexpected error: {str(e)}", flush=True)
    import traceback
    traceback.print_exc()
