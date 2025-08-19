import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Deployment/model name for chat
CHAT_MODEL = os.getenv("GROQ_CHAT_MODEL", "llama3-8b-8192")
