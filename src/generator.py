# from openai_client import get_chat_response

# def generate_response(user_query: str, context_snippets: str) -> str:
#     messages = [
#         {"role": "system", "content": "You are a helpful support assistant."},
#         {"role": "user", "content": f"Context:\n{context_snippets}\n\nQuestion: {user_query}"}
#     ]
#     return get_chat_response(messages)

# if __name__ == "__main__":
#     sample = generate_response(
#         user_query="How do I reset my password?",
#         context_snippets="To reset your password, go to Settings > Security. If you forget it, click 'Forgot Password'."
#     )
#     print(sample)


# # import os
# # import openai
# # from openai_client import CHAT_ENGINE

# # def generate_response(user_query: str, context_snippets: str) -> str:
# #     messages = [
# #         {"role": "system", "content": "You are a helpful support assistant."},
# #         {"role": "user",   "content": f"Context:\n{context_snippets}\n\nQuestion: {user_query}"}
# #     ]
# #     resp = openai.ChatCompletion.create(
# #         engine=CHAT_ENGINE,
# #         messages=messages,
# #         temperature=0.7,
# #         max_toens=256,
# #         top_p=0.6,
# #         frequency_penalty=0.7
# #     )   
# #     return resp.choices[0].message.content

# # if __name__ == "__main__":
# #     sample = generate_response(
# #         user_query="How do I reset my password?",
# #         context_snippets="To reset your password, go to Settings > Security. If you forget it, click 'Forgot Password'."
# #     )
# #     print(sample)


# # from openai_client import client, CHAT_MODEL
# # from groq import APIError

# # def generate_response(user_query: str, context_tickets: list[dict]) -> str:
# #     # Format context for the prompt
# #     snippets = "\n\n".join(
# #         f"{i+1}. {t['short_description']}: {t['description']}"
# #         for i, t in enumerate(context_tickets)
# #     )
# #     messages = [
# #         {"role": "system", "content": "You are a helpful support assistant."},
# #         {"role": "user",   "content":
# #             f"Based on these past tickets:\n{snippets}\n\n"
# #             f"Answer: {user_query}"
# #         }
# #     ]
# #     try:
# #         resp = client.chat.completions.create(
# #             model=CHAT_MODEL,   # :contentReference[oaicite:2]{index=2}
# #             messages=messages,
# #             temperature=0.7,
# #             max_tokens=256,
# #             top_p=0.6,
# #             frequency_penalty=0.7
# #         )
# #         return resp.choices[0].message.content
# #     except APIError as e:
# #         return f"Error from Groq API: {e}"

# # if __name__ == "__main__":
# #     # Quick test stub
# #     from retriever import retrieve
# #     tickets = retrieve("How do I reset my password?", top_k=3)
# #     print(generate_response("How do I reset my password?", tickets))


import os
from dotenv import load_dotenv
import openai
from openai_client import client, CHAT_DEPLOYMENT
 
# Load .env
load_dotenv()
 
def generate_response(user_query: str, context_tickets: list[dict]) -> str:
    # Format the retrieved tickets into prompt context
    snippets = "\n\n".join(
        f"{i+1}. {t['short_description']}\n{t['description']}"
        for i, t in enumerate(context_tickets)
    )
    messages = [
        {"role": "system", "content": "You are a helpful support assistant."},
        {"role": "user",   "content":
            f"Context:\n{snippets}\n\nQuestion:\n{user_query}"
        }
    ]
    resp = client.chat.completions.create(
        deployment_id=CHAT_DEPLOYMENT,
        messages=messages,
        temperature=0.7,
        max_tokens=256,
        top_p=0.6,
        frequency_penalty=0.7
    )
    return resp.choices[0].message.content
 
if __name__ == "__main__":
    # Quick smoke-test
    sample_context = [{"short_description":"Reset pw","description":"Navigate to Settings → Security → Reset Password"}]
    print(generate_response("How do I reset my password?", sample_context))