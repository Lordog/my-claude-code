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
    model = "moonshotai/kimi-k2-0905",
    messages = [
        {"role": "system", "content": "You are Kimi, an AI assistant provided by Moonshot AI, who is more proficient in Chinese and English conversations. You will provide users with safe, helpful, and accurate answers. At the same time, you will reject any questions involving terrorism, racism, pornography, and violence. Moonshot AI is a proper noun and should not be translated into other languages."},
        {"role": "user", "content": "Determine whether 3214567 is a prime number through programming."}
    ],
    tools = [{
        "type": "function",
        "function": {
            "name": "CodeRunner",
            "description": "A code executor that supports running Python and JavaScript code",
            "parameters": {
                "properties": {
                    "language": {
                        "type": "string",
                        "enum": ["python", "javascript"]
                    },
                    "code": {
                        "type": "string",
                        "description": "The code is written here"
                    }
                },
            "type": "object"
            }
        }
    }],
    temperature = 0.6,
)
 
print(completion.choices[0].message)
