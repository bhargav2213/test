"""
==============================================================================
MIGRATION RUNNER / VERIFIER (backend/migrate.py)
Single-command script to verify and run the Supabase database migration.
==============================================================================
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Set paths
BACKEND_DIR = Path(__file__).resolve().parent
BASE_DIR = BACKEND_DIR.parent
MIGRATION_FILE = BASE_DIR / "supabase" / "migrations" / "20261012000000_create_chatbot_tables.sql"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Load .env
if (BACKEND_DIR / ".env").exists():
    load_dotenv(BACKEND_DIR / ".env")
elif (BASE_DIR / ".env").exists():
    load_dotenv(BASE_DIR / ".env")
else:
    load_dotenv()

try:
    import db
except ImportError:
    from backend import db


def check_and_apply():
    print("=" * 70)
    print("🛠️  SUPABASE DATABASE MIGRATION CHECK")
    print("=" * 70)

    supabase_url = os.environ.get("SUPABASE_URL", "")
    project_id = supabase_url.replace("https://", "").split(".")[0] if supabase_url else ""

    print(f"Project URL : {supabase_url}")
    print(f"Project ID  : {project_id}")
    print(f"Migration   : {MIGRATION_FILE}")
    print("-" * 70)

    client = db.get_supabase_client()
    if not client:
        print("❌ Error: Unable to connect to Supabase. Please check your SUPABASE_URL and SUPABASE_KEY in backend/.env")
        return

    # Check if tables already exist
    try:
        client.table("conversations").select("id").limit(1).execute()
        client.table("messages").select("id").limit(1).execute()
        print("✅ SUCCESS: The 'conversations' and 'messages' tables are ALREADY CREATED and healthy in your Supabase database!")
        print("=" * 70)
        return
    except Exception:
        print("ℹ️  Tables 'conversations' and 'messages' need to be created.")

    # Read SQL migration content
    if not MIGRATION_FILE.exists():
        print(f"❌ Error: Migration file not found at {MIGRATION_FILE}")
        return

    sql_content = MIGRATION_FILE.read_text(encoding="utf-8")

    # Direct URL to the project's SQL editor
    sql_editor_url = f"https://supabase.com/dashboard/project/{project_id}/sql/new"

    print("\nTo apply the migration in 1 click:")
    print(f"👉 Open this link in your browser: {sql_editor_url}")
    print("\nThen paste and click 'RUN':\n")
    print("-" * 70)
    print(sql_content)
    print("-" * 70)


if __name__ == "__main__":
    check_and_apply()
