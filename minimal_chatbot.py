"""
Minimal Gemini Chatbot - Just the essentials
Demonstrates the basic Gemini LLM multi-turn chat call in ~25 lines.
"""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv("backend/.env")
load_dotenv()

# 1. Initialize client (reads GEMINI_API_KEY from environment or .env)
api_key = os.getenv("GEMINI_API_KEY") or input("Enter your Gemini API Key: ")
client = genai.Client(api_key=api_key)

# 2. Start a multi-turn chat session with Gemini
chat = client.chats.create(model="gemini-2.5-flash")

print("Gemini Chatbot ready! (Type 'quit' to exit)\n")

while True:
    user_prompt = input("You: ")
    if user_prompt.lower() in ["quit", "exit"]:
        break

    # 3. Send message and receive response
    response = chat.send_message(user_prompt)
    print(f"Gemini: {response.text}\n")
