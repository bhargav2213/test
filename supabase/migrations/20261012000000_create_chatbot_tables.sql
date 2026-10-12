-- ==============================================================================
-- Supabase Migration: 20261012000000_create_chatbot_tables.sql
-- Description: Sets up conversations and messages tables with RLS and indexes.
-- ==============================================================================

-- 1. Create table for Conversations
CREATE TABLE IF NOT EXISTS public.conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Create table for Messages
CREATE TABLE IF NOT EXISTS public.messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES public.conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'model')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Create indexes for fast lookup and sorting
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
    ON public.messages(conversation_id);

CREATE INDEX IF NOT EXISTS idx_conversations_created_at 
    ON public.conversations(created_at DESC);

-- 4. Enable Row Level Security (RLS)
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

-- 5. Drop existing policies if any to ensure clean re-runs
DROP POLICY IF EXISTS "Allow all operations on conversations" ON public.conversations;
DROP POLICY IF EXISTS "Allow all operations on messages" ON public.messages;

-- 6. Create permissive policies for application access
CREATE POLICY "Allow all operations on conversations" 
    ON public.conversations 
    FOR ALL 
    USING (true) 
    WITH CHECK (true);

CREATE POLICY "Allow all operations on messages" 
    ON public.messages 
    FOR ALL 
    USING (true) 
    WITH CHECK (true);
