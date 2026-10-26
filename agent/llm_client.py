import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.environ["OPENROUTER_MODEL"]

client = OpenAI(
   base_url="https://openrouter.ai/api/v1",
   api_key=os.environ["OPENROUTER_API_KEY"],
   timeout=60.0
)


def chat_completion(messages, tools):
   return client.chat.completions.create(
       model=MODEL,
       messages=messages,
       tools=tools,
       tool_choice="auto",
       stream=True
   )
