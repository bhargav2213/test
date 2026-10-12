/**
 * ========================================================
 * FRONTEND JAVASCRIPT (app.js)
 * Executes strictly in the client's Web Browser.
 * 
 * Features:
 * - Real-time chat interactivity
 * - Supabase conversation history loading and switching
 * - Markdown & syntax highlighted responses
 * - Connection status monitors
 * ========================================================
 */

// Local chat state
let chatHistory = [];
let currentConversationId = null;
let isGenerating = false;

// DOM Elements
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
const supabaseStatusBadge = document.getElementById('supabaseStatusBadge');
const supabaseStatusText = document.getElementById('supabaseStatusText');
const conversationsList = document.getElementById('conversationsList');

// Setup suggestion chips
document.querySelectorAll('.suggestion-card').forEach(card => {
  card.addEventListener('click', () => {
    const text = card.getAttribute('data-prompt');
    userInput.value = text;
    userInput.dispatchEvent(new Event('input'));
    sendMessage();
  });
});

// Auto-expand textarea height as user types
userInput.addEventListener('input', () => {
  userInput.style.height = 'auto';
  userInput.style.height = Math.min(userInput.scrollHeight, 160) + 'px';
});

// Update active model badge
modelSelect.addEventListener('change', () => {
  activeModelLabel.textContent = modelSelect.value;
});

// Check Backend & Database Status
async function checkBackendStatus() {
  try {
    const response = await fetch('/api/status');
    const data = await response.json();
    
    // 1. Gemini Key Check
    if (data.has_key) {
      apiStatusBadge.className = 'api-status-badge';
      apiStatusText.textContent = 'Gemini .env Active';
    } else {
      const storedKey = localStorage.getItem('gemini_api_key');
      if (storedKey) {
        apiKeyInput.value = storedKey;
        apiStatusBadge.className = 'api-status-badge';
        apiStatusText.textContent = 'Browser Key Saved';
      } else {
        apiStatusBadge.className = 'api-status-badge missing';
        apiStatusText.textContent = 'Gemini Key Needed';
      }
    }

    // 2. Supabase Check
    if (data.has_supabase) {
      supabaseStatusBadge.className = 'api-status-badge';
      supabaseStatusText.textContent = 'Supabase Connected';
      loadConversations();
    } else {
      supabaseStatusBadge.className = 'api-status-badge neutral';
      supabaseStatusText.textContent = 'Supabase Not Configured';
      conversationsList.innerHTML = '<div class="history-empty">Add SUPABASE_URL to .env to enable chat saving</div>';
    }
  } catch (err) {
    apiStatusBadge.className = 'api-status-badge missing';
    apiStatusText.textContent = 'Backend Offline';
    supabaseStatusBadge.className = 'api-status-badge missing';
    supabaseStatusText.textContent = 'Offline';
  }
}
checkBackendStatus();

apiKeyInput.addEventListener('change', () => {
  if (apiKeyInput.value.trim()) {
    localStorage.setItem('gemini_api_key', apiKeyInput.value.trim());
    apiStatusBadge.className = 'api-status-badge';
    apiStatusText.textContent = 'Browser Key Saved';
  }
});

// Load Past Conversations from Supabase
async function loadConversations() {
  try {
    const res = await fetch('/api/conversations');
    const data = await res.json();
    const items = data.conversations || [];

    if (items.length === 0) {
      conversationsList.innerHTML = '<div class="history-empty">No conversations saved yet.</div>';
      return;
    }

    conversationsList.innerHTML = '';
    items.forEach(conv => {
      const itemEl = document.createElement('div');
      itemEl.className = `conversation-item ${conv.id === currentConversationId ? 'active' : ''}`;
      itemEl.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink:0;"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        <span style="overflow:hidden; text-overflow:ellipsis;">${escapeHtml(conv.title)}</span>
      `;
      itemEl.addEventListener('click', () => switchConversation(conv.id));
      conversationsList.appendChild(itemEl);
    });
  } catch (err) {
    console.error('Failed to load conversations:', err);
  }
}

// Switch and load an existing conversation
async function switchConversation(convId) {
  currentConversationId = convId;
  messagesArea.innerHTML = '';
  chatHistory = [];

  try {
    const res = await fetch(`/api/conversations?id=${convId}`);
    const data = await res.json();
    const messages = data.messages || [];

    messages.forEach(msg => {
      renderMessage(msg.role, msg.content);
      chatHistory.push({ role: msg.role, content: msg.content });
    });

    loadConversations();
  } catch (err) {
    console.error('Failed to switch conversation:', err);
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text || '';
  return div.innerHTML;
}

// Helper: Render message bubble
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

// Main function: Send message to Backend
async function sendMessage() {
  const text = userInput.value.trim();
  if (!text || isGenerating) return;

  userInput.value = '';
  userInput.style.height = 'auto';

  // 1. Render user message
  renderMessage('user', text);
  chatHistory.push({ role: 'user', content: text });

  isGenerating = true;
  sendBtn.disabled = true;

  // 2. Render assistant placeholder
  const botBubble = renderMessage('gemini', '');
  botBubble.classList.add('typing-cursor');

  try {
    const customKey = apiKeyInput.value.trim() || localStorage.getItem('gemini_api_key') || '';
    
    // 3. Request to Backend
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: chatHistory,
        model: modelSelect.value,
        system_instruction: systemPrompt.value.trim(),
        api_key: customKey,
        conversation_id: currentConversationId
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Server error occurred');
    }

    const data = await response.json();
    const replyText = data.reply;

    if (data.conversation_id && !currentConversationId) {
      currentConversationId = data.conversation_id;
      loadConversations();
    }

    botBubble.innerHTML = marked.parse(replyText);
    botBubble.querySelectorAll('pre code').forEach((block) => {
      hljs.highlightElement(block);
    });
    chatHistory.push({ role: 'model', content: replyText });

  } catch (err) {
    botBubble.innerHTML = `<span style="color: #f87171;">⚠️ <strong>Error:</strong> ${err.message}</span>`;
  } finally {
    botBubble.classList.remove('typing-cursor');
    isGenerating = false;
    sendBtn.disabled = false;
    userInput.focus();
  }
}

// Keydown handler
userInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

sendBtn.addEventListener('click', sendMessage);

// Clear / New chat
function startNewChat() {
  currentConversationId = null;
  chatHistory = [];
  messagesArea.innerHTML = '';
  if (welcomeHero) {
    welcomeHero.style.display = 'block';
    messagesArea.appendChild(welcomeHero);
  }
  loadConversations();
  userInput.focus();
}

btnNewChat.addEventListener('click', startNewChat);
btnClear.addEventListener('click', startNewChat);
