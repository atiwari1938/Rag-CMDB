import os
from dotenv import load_dotenv
from openai import AzureOpenAI
 
# Load .env
load_dotenv()
 
# Instantiate AzureOpenAI client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION")
)
 
# Deployments (set these in .env)
CHAT_DEPLOYMENT  = os.getenv("AZURE_OPENAI_CHAT_MODEL")    
EMBED_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL") 

# import os
# from dotenv import load_dotenv
# from openai import AzureOpenAI

# # Load environment variables from .env file
# load_dotenv()

# # Set up Azure OpenAI client
# client = AzureOpenAI(
#     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#     api_version=os.getenv("OPENAI_API_VERSION")
# )

# # Function to get chat completions
# def get_chat_response(messages):
#     response = client.chat.completions.create(
#         model=os.getenv("AZURE_OPENAI_EMBEDDING_MODEL"),
#         messages=messages
#     )
#     return response.choices[0].message.content

# # Function to get embeddings
# def get_embeddings(input_text):
#     response = client.embeddings.create(
#         model=os.getenv("AZURE_OPENAI_EMBEDDING_MODEL"),
#         input=input_text,
#         encoding_format="float"
#     )
#     return response.data[0].embedding

# # Example usage
# if __name__ == "__main__":
#     # Chat example
#     chat_messages = [
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
#         {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
#         {"role": "user", "content": "Do other Azure services support this too?"}
#     ]
#     chat_response = get_chat_response(chat_messages)
#     print("Chat Response:", chat_response)

#     # Embedding example
#     input_text = "Hello AI"
#     embedding = get_embeddings(input_text)
#     print("Embedding:", embedding)



# import os
# from dotenv import load_dotenv
# from groq import Groq

# # Load environment variables
# load_dotenv()

# # Initialize Groq client for chat completions
# # :contentReference[oaicite:0]{index=0}
# client = Groq(
#     api_key=os.getenv("GROQ_API_KEY")
# )

# # Deployment/model name for chat
# CHAT_MODEL = os.getenv("GROQ_CHAT_MODEL", "llama3-8b-8192")
