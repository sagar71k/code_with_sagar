import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("API key kaha hai bhai")

client=Groq(api_key=my_api_key)

model="llama-3.3-70b-versatile"
role="user"
prompt=" i love you baby"

massage_system = {
    "role": "system",
    "content": " You are my strict office colleague who is also my manager."
}
# message me role and content
message=[message_system, message]

response=client.chat.completions.create(model=model, messages=message)

print("############################")

answer = response.choices[0].message.content
print(answer)