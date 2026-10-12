-- ========================================================
-- Supabase SQL Schema for Gemini Chatbot
-- Run this in your Supabase Dashboard: SQL Editor -> New Query -> Run
-- ========================================================

-- 1. Create table for Chat Conversations
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Create table for Chat Messages
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'model')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Enable Row Level Security (RLS) - Recommended by Supabase
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- 4. Create public access policies (allows anon/authenticated users to read and write)
CREATE POLICY "Allow public read on conversations" 
ON conversations FOR SELECT USING (true);

CREATE POLICY "Allow public insert on conversations" 
ON conversations FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read on messages" 
ON messages FOR SELECT USING (true);

CREATE POLICY "Allow public insert on messages" 
ON messages FOR INSERT WITH CHECK (true);
