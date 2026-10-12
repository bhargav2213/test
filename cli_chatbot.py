"""
Simple Gemini CLI Chatbot
Uses the official Google GenAI SDK (google-genai).
"""

import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load API key from backend/.env or root .env
load_dotenv("backend/.env")
load_dotenv()


def get_api_key():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\n=======================================================")
        print(" [!] GEMINI_API_KEY was not found in environment or .env")
        print("=======================================================")
        print("You can get a free Gemini API key from:")
        print("https://aistudio.google.com/app/apikey\n")
        try:
            api_key = input("Enter your Gemini API Key: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

        if not api_key:
            print("Error: API key is required to proceed.")
            sys.exit(1)
    return api_key


def main():
    print("=" * 60)
    print("🤖 Welcome to the Gemini Chatbot!")
    print("=" * 60)
    print("Type 'exit', 'quit', or 'q' to end the chat.")
    print("Type 'clear' to reset chat history.\n")

    api_key = get_api_key()

    # Initialize Gemini client
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Failed to initialize Gemini client: {e}")
        sys.exit(1)

    model_name = "gemini-2.5-flash"
    print(f"Using model: {model_name}")
    print("-" * 60)

    # Create a multi-turn chat session
    chat = client.chats.create(
        model=model_name,
        config=types.GenerateContentConfig(
            system_instruction="You are a helpful, knowledgeable, and polite AI assistant.",
            temperature=0.7,
        ),
    )

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break

        if user_input.lower() == "clear":
            chat = client.chats.create(
                model=model_name,
                config=types.GenerateContentConfig(
                    system_instruction="You are a helpful, knowledgeable, and polite AI assistant.",
                    temperature=0.7,
                ),
            )
            print("\n[Chat history cleared]")
            continue

        print("\nGemini: ", end="", flush=True)

        try:
            # Stream the response chunks in real-time
            response = chat.send_message_stream(user_input)
            for chunk in response:
                if chunk.text:
                    print(chunk.text, end="", flush=True)
            print()
        except Exception as e:
            print(f"\n[Error during generation]: {e}")


if __name__ == "__main__":
    main()
