import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

completion = client.chat.completions.create(
  model="moonshotai/kimi-k2-0905",
  messages=[
    {
      "role": "user",
      "content": "Advice on vibe coding"
    }
  ]
)

print(completion.choices[0].message.content)
