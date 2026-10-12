# Gemini LLM Chatbot + Supabase Integration

This application features a full-stack AI chatbot with **Google Gemini 2.5** and persistent chat history powered by **Supabase PostgreSQL**.

---

## 🏛️ Architecture & Separation of Concerns

```text
test/
├── frontend/                  <-- Client-Side (Browser UI)
│   ├── index.html             # UI with Supabase Chat History & status badges
│   ├── style.css              # Dark theme, glassmorphic layout, chat styling
│   └── app.js                 # Event handling, chat switching, fetch API calls
│
├── backend/                   <-- Server-Side (Host Machine)
│   ├── db.py                  # Supabase database operations (CRUD for chats)
│   └── server.py              # HTTP server, API endpoints, Gemini SDK bridge
│
├── supabase_schema.sql        # Database migration script for Supabase
├── cli_chatbot.py             # Standalone terminal chatbot
├── minimal_chatbot.py         # 25-line Gemini call script
├── .env.example               # Configuration template
└── requirements.txt           # Dependencies (google-genai, supabase, python-dotenv)
```

---

## 🛠️ Step-by-Step: Connecting Supabase

### 1. Create a Free Supabase Project
1. Go to [supabase.com](https://supabase.com) and create an account.
2. Click **New Project** and choose a project name and database password.

### 2. Run the SQL Migration
1. In your Supabase Dashboard, click on **SQL Editor** in the left sidebar.
2. Click **New Query**.
3. Copy and paste the contents of [supabase_schema.sql](file:///c:/Users/BHARGAV/Desktop/test/supabase_schema.sql).
4. Click **Run**. This creates the `conversations` and `messages` tables with Row Level Security.

### 3. Get Your API Credentials
1. In Supabase, navigate to **Project Settings** (gear icon) $\rightarrow$ **API**.
2. Copy:
   - **Project URL** (e.g., `https://xyzabcdef.supabase.co`)
   - **anon / public key** (or `service_role` key)

### 4. Configure Your `.env` File
Create a `.env` file in the root folder with:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
```

---

## 🚀 Running the App

```powershell
python backend/server.py
```

Then open your browser at **[http://localhost:5000](http://localhost:5000)**.
- Both status pills will show **Active / Connected**.
- Conversations will be saved and displayed in the sidebar history.
