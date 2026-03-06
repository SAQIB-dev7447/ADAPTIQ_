-- Database Schema for AdaptIQ Content Caching with Users

-- 1. Create the content_cache table
-- Relies on Supabase Auth (auth.users) for user management
CREATE TABLE IF NOT EXISTS public.content_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    content_hash TEXT NOT NULL,
    tab_type TEXT NOT NULL,
    result_json JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Add an index for faster lookups
CREATE INDEX IF NOT EXISTS idx_content_cache_lookup 
ON public.content_cache (user_id, content_hash, tab_type);

-- 3. Enable RLS (Row Level Security)
ALTER TABLE public.content_cache ENABLE ROW LEVEL SECURITY;

-- 4. Create policies for Row Level Security
-- Allow authenticated users to insert their own cache entries
CREATE POLICY "Users can insert their own cache" ON public.content_cache
FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Allow authenticated users to select their own cache entries
CREATE POLICY "Users can view their own cache" ON public.content_cache
FOR SELECT USING (auth.uid() = user_id);
