"""
Modern Gemini Web Chatbot Server
A complete, lightweight, dependency-free web server (uses Python's built-in http.server)
with the official google-genai SDK.
"""

import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

PORT = 5000

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gemini AI Chatbot</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

  <style>
    :root {
      --bg-primary: #0a0c10;
      --bg-secondary: #12161f;
      --bg-tertiary: #1b212f;
      --surface: #1e2638;
      --surface-hover: #263148;
      --border-color: #2b354c;
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --accent-grad: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #06b6d4 100%);
      --accent-glow: rgba(99, 102, 241, 0.25);
      --accent-primary: #6366f1;
      --user-bubble: #2563eb;
      --bot-bubble: #161c28;
      --radius-sm: 8px;
      --radius-md: 14px;
      --radius-lg: 20px;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-main);
      height: 100vh;
      display: flex;
      overflow: hidden;
    }

    /* Sidebar */
    .sidebar {
      width: 290px;
      background: var(--bg-secondary);
      border-right: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      padding: 20px 16px;
      transition: all 0.3s ease;
      z-index: 20;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border-color);
      margin-bottom: 16px;
    }

    .brand-logo {
      width: 38px;
      height: 38px;
      border-radius: 10px;
      background: var(--accent-grad);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 20px var(--accent-glow);
    }

    .brand-logo svg {
      width: 22px;
      height: 22px;
      fill: white;
    }

    .brand-name {
      font-size: 1.15rem;
      font-weight: 700;
      background: linear-gradient(to right, #ffffff, #cbd5e1);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .brand-tag {
      font-size: 0.65rem;
      background: rgba(99, 102, 241, 0.2);
      color: #a5b4fc;
      padding: 2px 6px;
      border-radius: 4px;
      margin-left: 6px;
      text-transform: uppercase;
      font-weight: 600;
      letter-spacing: 0.5px;
    }

    .btn-new-chat {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      width: 100%;
      padding: 12px;
      background: var(--accent-grad);
      color: white;
      border: none;
      border-radius: var(--radius-md);
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      box-shadow: 0 4px 14px var(--accent-glow);
    }

    .btn-new-chat:hover {
      opacity: 0.95;
      transform: translateY(-1px);
    }

    .sidebar-section {
      margin-top: 20px;
      flex: 1;
      overflow-y: auto;
    }

    .section-title {
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: var(--text-muted);
      margin-bottom: 12px;
    }

    .config-card {
      background: var(--surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }

    .field-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .field-label {
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-muted);
    }

    select, input[type="text"], input[type="password"], textarea {
      width: 100%;
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      color: var(--text-main);
      padding: 8px 10px;
      border-radius: var(--radius-sm);
      font-size: 0.85rem;
      outline: none;
      font-family: inherit;
      transition: border-color 0.2s;
    }

    select:focus, input:focus, textarea:focus {
      border-color: var(--accent-primary);
    }

    .api-status-badge {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.78rem;
      padding: 8px 10px;
      border-radius: var(--radius-sm);
      background: rgba(16, 185, 129, 0.1);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.2);
    }

    .api-status-badge.missing {
      background: rgba(239, 68, 68, 0.1);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.2);
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: currentColor;
    }

    /* Main Chat Layout */
    .chat-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      height: 100vh;
      position: relative;
    }

    .chat-header {
      padding: 16px 24px;
      background: var(--bg-secondary);
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .model-indicator {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.9rem;
      font-weight: 600;
    }

    .model-pill {
      background: var(--surface);
      border: 1px solid var(--border-color);
      padding: 4px 10px;
      border-radius: 20px;
      color: #38bdf8;
      font-size: 0.8rem;
    }

    .header-actions {
      display: flex;
      gap: 8px;
    }

    .btn-icon {
      background: var(--surface);
      border: 1px solid var(--border-color);
      color: var(--text-muted);
      width: 36px;
      height: 36px;
      border-radius: var(--radius-sm);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.2s;
    }

    .btn-icon:hover {
      background: var(--surface-hover);
      color: var(--text-main);
    }

    /* Messages Stream */
    .messages-area {
      flex: 1;
      overflow-y: auto;
      padding: 24px 20%;
      display: flex;
      flex-direction: column;
      gap: 20px;
      scroll-behavior: smooth;
    }

    @media (max-width: 1200px) {
      .messages-area {
        padding: 20px 10%;
      }
    }

    @media (max-width: 768px) {
      .sidebar {
        display: none;
      }
      .messages-area {
        padding: 16px;
      }
    }

    /* Welcome Hero */
    .welcome-hero {
      margin: auto;
      text-align: center;
      max-width: 600px;
      padding: 40px 20px;
    }

    .hero-icon {
      width: 64px;
      height: 64px;
      border-radius: 18px;
      background: var(--accent-grad);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 20px;
      box-shadow: 0 0 30px var(--accent-glow);
    }

    .hero-title {
      font-size: 1.8rem;
      font-weight: 700;
      margin-bottom: 10px;
    }

    .hero-subtitle {
      font-size: 0.95rem;
      color: var(--text-muted);
      line-height: 1.6;
      margin-bottom: 24px;
    }

    .prompt-suggestions {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
      text-align: left;
    }

    .suggestion-card {
      background: var(--surface);
      border: 1px solid var(--border-color);
      padding: 12px 14px;
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .suggestion-card:hover {
      background: var(--surface-hover);
      border-color: var(--accent-primary);
      transform: translateY(-2px);
    }

    .suggestion-title {
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-main);
      margin-bottom: 4px;
    }

    .suggestion-desc {
      font-size: 0.75rem;
      color: var(--text-muted);
    }

    /* Message Bubbles */
    .message-row {
      display: flex;
      gap: 14px;
      animation: fadeIn 0.3s ease-out;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .message-row.user {
      flex-direction: row-reverse;
    }

    .avatar {
      width: 36px;
      height: 36px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      font-weight: 700;
      font-size: 0.85rem;
    }

    .avatar.user {
      background: #2563eb;
      color: white;
    }

    .avatar.gemini {
      background: var(--accent-grad);
      color: white;
      box-shadow: 0 0 14px var(--accent-glow);
    }

    .message-content {
      max-width: 80%;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .message-bubble {
      padding: 14px 18px;
      border-radius: var(--radius-lg);
      font-size: 0.95rem;
      line-height: 1.6;
      word-break: break-word;
    }

    .message-row.user .message-bubble {
      background: #2563eb;
      color: white;
      border-bottom-right-radius: 4px;
    }

    .message-row.gemini .message-bubble {
      background: var(--bot-bubble);
      border: 1px solid var(--border-color);
      color: var(--text-main);
      border-bottom-left-radius: 4px;
    }

    /* Markdown Styling in Bot Bubble */
    .message-bubble pre {
      background: #0d1117;
      border: 1px solid #30363d;
      border-radius: var(--radius-sm);
      padding: 12px;
      margin: 12px 0;
      overflow-x: auto;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
      position: relative;
    }

    .message-bubble code:not(pre code) {
      background: rgba(255, 255, 255, 0.1);
      padding: 2px 6px;
      border-radius: 4px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
    }

    .message-bubble p {
      margin-bottom: 10px;
    }
    .message-bubble p:last-child {
      margin-bottom: 0;
    }
    .message-bubble ul, .message-bubble ol {
      margin-left: 20px;
      margin-bottom: 10px;
    }

    .typing-cursor::after {
      content: '▋';
      animation: blink 1s infinite;
      color: var(--accent-primary);
      margin-left: 4px;
    }

    @keyframes blink {
      0%, 50% { opacity: 1; }
      51%, 100% { opacity: 0; }
    }

    /* Input Dock */
    .input-dock {
      padding: 16px 20%;
      background: linear-gradient(to top, var(--bg-primary) 80%, transparent);
      position: relative;
    }

    @media (max-width: 1200px) {
      .input-dock {
        padding: 16px 10%;
      }
    }

    @media (max-width: 768px) {
      .input-dock {
        padding: 12px 16px;
      }
    }

    .input-box {
      background: var(--surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 8px 12px 8px 16px;
      display: flex;
      align-items: flex-end;
      gap: 10px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
      transition: border-color 0.2s, box-shadow 0.2s;
    }

    .input-box:focus-within {
      border-color: var(--accent-primary);
      box-shadow: 0 8px 30px var(--accent-glow);
    }

    .chat-textarea {
      flex: 1;
      background: transparent;
      border: none;
      color: var(--text-main);
      font-size: 0.95rem;
      padding: 6px 0;
      resize: none;
      max-height: 160px;
      min-height: 24px;
      line-height: 1.5;
      outline: none;
      font-family: inherit;
    }

    .send-btn {
      width: 38px;
      height: 38px;
      border-radius: 12px;
      background: var(--accent-grad);
      border: none;
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: transform 0.15s ease, opacity 0.2s;
      flex-shrink: 0;
    }

    .send-btn:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }

    .send-btn:not(:disabled):hover {
      transform: scale(1.05);
    }

    .input-footnote {
      text-align: center;
      font-size: 0.72rem;
      color: var(--text-muted);
      margin-top: 8px;
    }
  </style>
</head>
<body>

  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-logo">
        <svg viewBox="0 0 24 24"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>
      </div>
      <div>
        <div class="brand-name">Gemini Chat <span class="brand-tag">v2.5</span></div>
      </div>
    </div>

    <button id="btnNewChat" class="btn-new-chat">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
      New Conversation
    </button>

    <div class="sidebar-section">
      <div class="section-title">Model Configuration</div>
      <div class="config-card">
        <div id="apiStatusBadge" class="api-status-badge">
          <span class="status-dot"></span>
          <span id="apiStatusText">Checking API Key...</span>
        </div>

        <div class="field-group">
          <label class="field-label" for="apiKeyInput">Gemini API Key</label>
          <input type="password" id="apiKeyInput" placeholder="Optional if set in .env" autocomplete="off">
        </div>

        <div class="field-group">
          <label class="field-label" for="modelSelect">Select Model</label>
          <select id="modelSelect">
            <option value="gemini-2.5-flash" selected>gemini-2.5-flash (Fast & Capable)</option>
            <option value="gemini-2.0-flash">gemini-2.0-flash</option>
            <option value="gemini-1.5-flash">gemini-1.5-flash</option>
            <option value="gemini-1.5-pro">gemini-1.5-pro (Reasoning)</option>
          </select>
        </div>

        <div class="field-group">
          <label class="field-label" for="systemPrompt">System Persona</label>
          <textarea id="systemPrompt" rows="3" placeholder="Default: Helpful & polite AI assistant">You are a helpful, knowledgeable, and polite AI assistant.</textarea>
        </div>
      </div>
    </div>
  </aside>

  <!-- Main Chat Container -->
  <main class="chat-container">
    <header class="chat-header">
      <div class="model-indicator">
        <span>Active Model:</span>
        <span class="model-pill" id="activeModelLabel">gemini-2.5-flash</span>
      </div>
      <div class="header-actions">
        <button id="btnClear" class="btn-icon" title="Clear Chat History">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
        </button>
      </div>
    </header>

    <!-- Messages Container -->
    <div class="messages-area" id="messagesArea">
      <div class="welcome-hero" id="welcomeHero">
        <div class="hero-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="white"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>
        </div>
        <h1 class="hero-title">How can Gemini help you today?</h1>
        <p class="hero-subtitle">Chat with Google's state-of-the-art multimodal AI model. Ask questions, draft code, or brainstorm ideas.</p>

        <div class="prompt-suggestions">
          <div class="suggestion-card" onclick="usePrompt('Explain how Large Language Models work in simple terms.')">
            <div class="suggestion-title">Explain LLMs</div>
            <div class="suggestion-desc">Simple breakdown of language models</div>
          </div>
          <div class="suggestion-card" onclick="usePrompt('Write a Python function to fetch and parse JSON from a REST API.')">
            <div class="suggestion-title">Python Code</div>
            <div class="suggestion-desc">Fetch and parse JSON with requests</div>
          </div>
          <div class="suggestion-card" onclick="usePrompt('Suggest 5 creative ideas for a weekend coding project.')">
            <div class="suggestion-title">Project Ideas</div>
            <div class="suggestion-desc">Fun hacks to build over a weekend</div>
          </div>
          <div class="suggestion-card" onclick="usePrompt('Write a professional email following up on a job interview.')">
            <div class="suggestion-title">Draft Email</div>
            <div class="suggestion-desc">Follow-up note for hiring manager</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Box -->
    <div class="input-dock">
      <div class="input-box">
        <textarea
          id="userInput"
          class="chat-textarea"
          rows="1"
          placeholder="Ask Gemini anything... (Shift+Enter for new line)"
        ></textarea>
        <button id="sendBtn" class="send-btn" title="Send Message">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
        </button>
      </div>
      <div class="input-footnote">
        Powered by Google GenAI SDK &bull; Gemini may produce inaccurate info. Verify important facts.
      </div>
    </div>
  </main>

  <script>
    // State
    const chatHistory = [];
    let isGenerating = false;

    // Elements
    const messagesArea = document.getElementById('messagesArea');
    const welcomeHero = document.getElementById('welcomeHero');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const btnNewChat = document.getElementById('btnNewChat');
    const btnClear = document.getElementById('btnClear');
    const modelSelect = document.getElementById('modelSelect');
    const activeModelLabel = document.getElementById('activeModelLabel');
    const apiKeyInput = document.getElementById('apiKeyInput');
    const systemPrompt = document.getElementById('systemPrompt');
    const apiStatusBadge = document.getElementById('apiStatusBadge');
    const apiStatusText = document.getElementById('apiStatusText');

    // Auto-resize textarea
    userInput.addEventListener('input', () => {
      userInput.style.height = 'auto';
      userInput.style.height = Math.min(userInput.scrollHeight, 160) + 'px';
    });

    // Check API Status on load
    async function checkServerStatus() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();
        if (data.has_key) {
          apiStatusBadge.className = 'api-status-badge';
          apiStatusText.textContent = 'Server .env Key Active';
        } else {
          const storedKey = localStorage.getItem('gemini_api_key');
          if (storedKey) {
            apiKeyInput.value = storedKey;
            apiStatusBadge.className = 'api-status-badge';
            apiStatusText.textContent = 'Local Key Saved';
          } else {
            apiStatusBadge.className = 'api-status-badge missing';
            apiStatusText.textContent = 'API Key Required';
          }
        }
      } catch (e) {
        apiStatusBadge.className = 'api-status-badge missing';
        apiStatusText.textContent = 'Server Offline';
      }
    }
    checkServerStatus();

    // Persist API key input
    apiKeyInput.addEventListener('change', () => {
      if (apiKeyInput.value.trim()) {
        localStorage.setItem('gemini_api_key', apiKeyInput.value.trim());
        apiStatusBadge.className = 'api-status-badge';
        apiStatusText.textContent = 'Local Key Saved';
      }
    });

    modelSelect.addEventListener('change', () => {
      activeModelLabel.textContent = modelSelect.value;
    });

    function usePrompt(text) {
      userInput.value = text;
      userInput.dispatchEvent(new Event('input'));
      sendMessage();
    }

    function renderMessage(role, text) {
      if (welcomeHero) welcomeHero.style.display = 'none';

      const row = document.createElement('div');
      row.className = `message-row ${role}`;

      const avatar = document.createElement('div');
      avatar.className = `avatar ${role}`;
      avatar.textContent = role === 'user' ? 'U' : '✦';

      const content = document.createElement('div');
      content.className = 'message-content';

      const bubble = document.createElement('div');
      bubble.className = 'message-bubble';

      if (role === 'user') {
        bubble.textContent = text;
      } else {
        bubble.innerHTML = marked.parse(text);
        bubble.querySelectorAll('pre code').forEach((block) => {
          hljs.highlightElement(block);
        });
      }

      content.appendChild(bubble);
      row.appendChild(avatar);
      row.appendChild(content);

      messagesArea.appendChild(row);
      messagesArea.scrollTop = messagesArea.scrollHeight;
      return bubble;
    }

    async function sendMessage() {
      const text = userInput.value.trim();
      if (!text || isGenerating) return;

      userInput.value = '';
      userInput.style.height = 'auto';

      renderMessage('user', text);
      chatHistory.push({ role: 'user', content: text });

      isGenerating = true;
      sendBtn.disabled = true;

      // Create streaming placeholder for Gemini
      const botBubble = renderMessage('gemini', '');
      botBubble.classList.add('typing-cursor');

      let fullResponse = '';

      try {
        const customKey = apiKeyInput.value.trim() || localStorage.getItem('gemini_api_key') || '';
        const payload = {
          messages: chatHistory,
          model: modelSelect.value,
          system_instruction: systemPrompt.value.trim(),
          api_key: customKey
        };

        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.error || 'Server error occurred');
        }

        const data = await res.json();
        fullResponse = data.reply;
        botBubble.innerHTML = marked.parse(fullResponse);
        botBubble.querySelectorAll('pre code').forEach((block) => {
          hljs.highlightElement(block);
        });
        chatHistory.push({ role: 'model', content: fullResponse });

      } catch (err) {
        botBubble.innerHTML = `<span style="color: #f87171;">⚠️ <strong>Error:</strong> ${err.message}</span>`;
      } finally {
        botBubble.classList.remove('typing-cursor');
        isGenerating = false;
        sendBtn.disabled = false;
        userInput.focus();
      }
    }

    // Keyboard enter trigger
    userInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    sendBtn.addEventListener('click', sendMessage);

    function clearChat() {
      chatHistory.length = 0;
      messagesArea.innerHTML = '';
      if (welcomeHero) {
        welcomeHero.style.display = 'block';
        messagesArea.appendChild(welcomeHero);
      }
      userInput.focus();
    }

    btnNewChat.addEventListener('click', clearChat);
    btnClear.addEventListener('click', clearChat);
  </script>
</body>
</html>
"""


class ChatServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)

        if url.path == "/" or url.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))

        elif url.path == "/api/status":
            has_key = bool(os.environ.get("GEMINI_API_KEY"))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"has_key": has_key}).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)

        if url.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)

            try:
                data = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                self.send_error_json("Invalid JSON payload in request.", 400)
                return

            # Determine API Key: request key takes priority, fallback to environment
            api_key = data.get("api_key") or os.environ.get("GEMINI_API_KEY")
            if not api_key:
                self.send_error_json(
                    "Missing Gemini API Key. Please provide it in the UI or set GEMINI_API_KEY in your .env file.",
                    400,
                )
                return

            model_name = data.get("model", "gemini-2.5-flash")
            system_instruction = data.get("system_instruction")
            messages = data.get("messages", [])

            if not messages:
                self.send_error_json("No messages provided.", 400)
                return

            # Call Gemini
            try:
                client = genai.Client(api_key=api_key)

                # Format multi-turn history for Google GenAI SDK
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

                reply_text = response.text if response.text else "(No response returned)"

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"reply": reply_text}).encode("utf-8"))

            except Exception as e:
                self.send_error_json(f"Gemini API Error: {str(e)}", 500)

        else:
            self.send_response(404)
            self.end_headers()

    def send_error_json(self, message, code=400):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode("utf-8"))

    def log_message(self, format, *args):
        # Clean terminal logging
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")


def run():
    server_address = ("127.0.0.1", PORT)
    httpd = HTTPServer(server_address, ChatServerHandler)
    print("=" * 65)
    print("🚀 Gemini AI Web Chatbot is running!")
    print(f"👉 Open in your browser: http://localhost:{PORT}")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()


if __name__ == "__main__":
    run()
