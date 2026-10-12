"""
========================================================
SUPABASE DATABASE SERVICE (backend/db.py)
Manages connection, conversation history, and message storage.
========================================================
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load from backend/.env or root .env
BACKEND_DIR = Path(__file__).resolve().parent
BASE_DIR = BACKEND_DIR.parent

if (BACKEND_DIR / ".env").exists():
    load_dotenv(BACKEND_DIR / ".env")
elif (BASE_DIR / ".env").exists():
    load_dotenv(BASE_DIR / ".env")
else:
    load_dotenv()

# Global client cache
_supabase_client = None


def get_supabase_client():
    """Initializes and returns the Supabase client if configured."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")

    if supabase_url and supabase_key:
        try:
            from supabase import create_client
            _supabase_client = create_client(supabase_url, supabase_key)
            print("[Database] Successfully connected to Supabase!")
        except Exception as e:
            print(f"[Database] Warning: Failed to connect to Supabase: {e}")
            _supabase_client = None
    else:
        _supabase_client = None

    return _supabase_client


def is_supabase_enabled() -> bool:
    """Checks if Supabase credentials are configured."""
    return get_supabase_client() is not None


def create_conversation(title: str = "New Conversation") -> Optional[str]:
    """Creates a new conversation record in Supabase."""
    client = get_supabase_client()
    if not client:
        return None

    try:
        response = client.table("conversations").insert({"title": title[:50]}).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["id"]
    except Exception as e:
        print(f"[Database Error] create_conversation failed: {e}")
    return None


def save_message(conversation_id: str, role: str, content: str) -> bool:
    """Saves a message to Supabase."""
    client = get_supabase_client()
    if not client or not conversation_id:
        return False

    try:
        client.table("messages").insert({
            "conversation_id": conversation_id,
            "role": role,
            "content": content
        }).execute()
        return True
    except Exception as e:
        print(f"[Database Error] save_message failed: {e}")
        return False


def get_conversations() -> List[Dict[str, Any]]:
    """Retrieves all conversations ordered by creation date."""
    client = get_supabase_client()
    if not client:
        return []

    try:
        response = (
            client.table("conversations")
            .select("id, title, created_at")
            .order("created_at", desc=True)
            .limit(30)
            .execute()
        )
        return response.data or []
    except Exception as e:
        print(f"[Database Error] get_conversations failed: {e}")
        return []


def get_conversation_messages(conversation_id: str) -> List[Dict[str, Any]]:
    """Retrieves all messages for a specific conversation."""
    client = get_supabase_client()
    if not client or not conversation_id:
        return []

    try:
        response = (
            client.table("messages")
            .select("id, role, content, created_at")
            .eq("conversation_id", conversation_id)
            .order("created_at", desc=False)
            .execute()
        )
        return response.data or []
    except Exception as e:
        print(f"[Database Error] get_conversation_messages failed: {e}")
        return []
