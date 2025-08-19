# import os
# from openai import AzureOpenAI

# client = AzureOpenAI(
#   azure_endpoint ='https://hexavarsity-secureapi.azurewebsites.net/api/azureai/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-02-01' , 
#   api_key='a1f72ca8e12abf00',  
#   api_version="2024-02-01"
# )

# response = client.chat.completions.create(
#     model="gpt-4o-mini", # model = "deployment_name"
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
#         {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
#         {"role": "user", "content": "Do other Azure services support this too?"}
#     ]
# )

# print(response.choices[0].message.content)

from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="https://hexavarsity-secureapi.azurewebsites.net/api/azureai/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-02-01",
    api_key="a1f72ca8e12abf00",
    api_version="2024-02-01"
)

response = client.chat.completions.create(
    model="gpt-4o-mini",  # Deployment name
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
)

print(response.choices[0].message.content)
