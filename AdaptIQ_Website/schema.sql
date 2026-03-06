-- Database Schema for AdaptIQ Content Caching

-- 1. Create the content_cache table
CREATE TABLE IF NOT EXISTS public.content_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL, -- "anonymous" or actual user ID
    content_hash TEXT NOT NULL, -- MD5 hash of the original content
    tab_type TEXT NOT NULL, -- summary, read_easy, focus_mode, step_mode, mind_map, quiz
    result_json JSONB NOT NULL, -- The AI generated response
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Add an index for faster lookups (optional but recommended)
CREATE INDEX IF NOT EXISTS idx_content_cache_lookup 
ON public.content_cache (user_id, content_hash, tab_type);

-- 3. Enable RLS (Row Level Security) if using in production
ALTER TABLE public.content_cache ENABLE ROW LEVEL SECURITY;

-- 4. Create simple policy for testing (Allow all access for now)
-- WARNING: In production, restrict this to authenticated users or specific logic.
CREATE POLICY "Enable all access for testing" ON public.content_cache
FOR ALL USING (true);
