from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
import os
import json

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("API key not found")

client = Groq(api_key=api_key)


class Ticket(BaseModel):
    name: str
    email: str
    issue: str


text = """
Hello My name is Pratyush.
I have an iPhone which is not working at all.
My address is Delhi.
My email is abc@gmail.com.
My contact number is 82134.
"""

schema = Ticket.model_json_schema()

system_prompt = f"""
You are an information extraction assistant.

Extract only the required information.

Return ONLY valid JSON matching this schema.

{json.dumps(schema)}
"""

user_prompt = f"""
Extract personal information from this ticket.

{text}
"""

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ],
    temperature=0,
)

data = json.loads(response.choices[0].message.content)

ticket = Ticket(**data)

print(ticket.name)
print(ticket.email)
print(ticket.issue)