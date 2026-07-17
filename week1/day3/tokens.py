import os
from dotenv import load_dotenv
from groq import Groq

# Load API Key
load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API key kaha hai bhai")

client = Groq(api_key=my_api_key)

model = "llama-3.3-70b-versatile"
role = "user"

# 3 prompts
prompt1 = "Hi"
prompt2 = "Explain time travel in detail"
prompt3 = "Write a 1000 word essay on Machine Learning"

prompts = [prompt1, prompt2, prompt3]

for prompt in prompts:
    message = {
        "role": role,
        "content": prompt
    }

    messages = [message]

    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    usage = response.usage

    print(
        f"Prompt: {prompt} --> "
        f"your tokens: {usage.prompt_tokens} "
        f"completion_tokens: {usage.completion_tokens} "
        f"total tokens: {usage.total_tokens}"
    )