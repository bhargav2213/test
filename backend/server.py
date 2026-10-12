"""
========================================================
BACKEND PYTHON SERVER (backend/server.py)
Executes securely on the Host Server / Machine.

Features:
- Serving static frontend assets (HTML, CSS, JS)
- Protecting environment secrets (GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY)
- Validating API requests from clients
- Storing conversation history in Supabase PostgreSQL
- Interfacing with Google Gemini LLM SDK
========================================================
"""

import os
import sys
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Resolve paths and import paths
BACKEND_DIR = Path(__file__).resolve().parent
BASE_DIR = BACKEND_DIR.parent
FRONTEND_DIR = BASE_DIR / "frontend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Load environment variables (Check backend/.env first, then root .env)
if (BACKEND_DIR / ".env").exists():
    load_dotenv(BACKEND_DIR / ".env")
elif (BASE_DIR / ".env").exists():
    load_dotenv(BASE_DIR / ".env")
else:
    load_dotenv()

# Import Supabase database service
try:
    import db
except ImportError:
    from backend import db

PORT = int(os.environ.get("PORT", 5000))


class BackendHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path.strip("/")
        params = urllib.parse.parse_qs(url.query)

        # 1. API: System Status
        if path == "api/status":
            has_gemini = bool(os.environ.get("GEMINI_API_KEY"))
            has_supabase = db.is_supabase_enabled()
            self.send_json({
                "has_key": has_gemini,
                "has_supabase": has_supabase,
                "default_model": os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
            })
            return

        # 2. API: Fetch conversations or conversation messages
        if path == "api/conversations":
            conv_id = params.get("id", [None])[0]
            if conv_id:
                messages = db.get_conversation_messages(conv_id)
                self.send_json({"messages": messages})
            else:
                conversations = db.get_conversations()
                self.send_json({"conversations": conversations})
            return

        # 3. Static File Serving (Frontend files)
        if not path or path == "index.html":
            file_to_serve = FRONTEND_DIR / "index.html"
            content_type = "text/html; charset=utf-8"
        elif path == "style.css":
            file_to_serve = FRONTEND_DIR / "style.css"
            content_type = "text/css; charset=utf-8"
        elif path == "app.js":
            file_to_serve = FRONTEND_DIR / "app.js"
            content_type = "application/javascript; charset=utf-8"
        else:
            self.send_response(404)
            self.end_headers()
            return

        if file_to_serve.exists():
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            with open(file_to_serve, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)

        # API: /api/chat
        if url.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)

            try:
                data = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                self.send_error_json("Invalid JSON payload from frontend.", 400)
                return

            # API Key resolution
            api_key = data.get("api_key") or os.environ.get("GEMINI_API_KEY")
            if not api_key:
                self.send_error_json(
                    "Missing Gemini API Key. Provide it in the UI or set GEMINI_API_KEY in backend/.env.",
                    400,
                )
                return

            default_model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
            model_name = data.get("model") or default_model
            system_instruction = data.get("system_instruction")
            messages = data.get("messages", [])
            conversation_id = data.get("conversation_id")

            if not messages:
                self.send_error_json("No messages received.", 400)
                return

            latest_user_message = messages[-1].get("content", "")

            # If Supabase is enabled and no conversation_id exists, create one
            if db.is_supabase_enabled() and not conversation_id:
                title = latest_user_message[:35] + ("..." if len(latest_user_message) > 35 else "")
                conversation_id = db.create_conversation(title=title)

            # Persist user message in Supabase
            if db.is_supabase_enabled() and conversation_id:
                db.save_message(conversation_id, "user", latest_user_message)

            try:
                # Contact Google Gemini API via official SDK
                client = genai.Client(api_key=api_key)

                # Format conversation history
                formatted_contents = []
                for msg in messages:
                    role = "user" if msg.get("role") == "user" else "model"
                    formatted_contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=msg.get("content", ""))],
                        )
                    )

                config = types.GenerateContentConfig(
                    system_instruction=system_instruction if system_instruction else None,
                    temperature=0.7,
                )

                response = client.models.generate_content(
                    model=model_name,
                    contents=formatted_contents,
                    config=config,
                )

                reply_text = response.text if response.text else "(Empty response)"

                # Persist model reply in Supabase
                if db.is_supabase_enabled() and conversation_id:
                    db.save_message(conversation_id, "model", reply_text)

                self.send_json({
                    "reply": reply_text,
                    "conversation_id": conversation_id
                })

            except Exception as e:
                self.send_error_json(f"Gemini API Error: {str(e)}", 500)
        else:
            self.send_response(404)
            self.end_headers()

    def send_json(self, payload, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def send_error_json(self, message, code=400):
        self.send_json({"error": message}, code=code)

    def log_message(self, format, *args):
        sys.stderr.write(f"[Backend Server] {format % args}\n")


def start_server():
    server_address = ("127.0.0.1", PORT)
    httpd = HTTPServer(server_address, BackendHandler)
    print("=" * 65)
    print(f"🚀 Backend Server running on http://127.0.0.1:{PORT}")
    print(f"📁 Serving Frontend from: {FRONTEND_DIR}")
    print(f"🗄️  Supabase Database: {'Connected ✅' if db.is_supabase_enabled() else 'Not configured (optional) ⚠️'}")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down backend server.")
        httpd.server_close()


if __name__ == "__main__":
    start_server()
