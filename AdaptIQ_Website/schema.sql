-- ============================================================
-- AdaptIQ Database Schema v2
-- Run this ENTIRE file in the Supabase SQL editor.
-- ============================================================

-- ── STEP 1: Drop old content_cache table if it exists ─────────────────────────
-- (Only needed if you previously ran the old schema)
-- DROP TABLE IF EXISTS public.content_cache CASCADE;


-- ── STEP 2: Sessions table — one row per user upload ──────────────────────────
CREATE TABLE IF NOT EXISTS public.sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES auth.users ON DELETE CASCADE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),

    -- Input source
    source_text     TEXT NOT NULL,
    source_type     TEXT NOT NULL CHECK (source_type IN ('paste', 'pdf', 'url', 'docx')),
    source_name     TEXT,

    -- Tab outputs — NULL = not yet generated
    summary         JSONB DEFAULT NULL,
    read_easy       JSONB DEFAULT NULL,
    focus_mode      JSONB DEFAULT NULL,
    step_by_step    JSONB DEFAULT NULL,
    mind_map        JSONB DEFAULT NULL,
    quiz            JSONB DEFAULT NULL,

    -- Track which tabs are done
    generated_tabs  TEXT[] DEFAULT '{}'
);

-- Index for fast user session lookups
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON public.sessions (user_id);


-- ── STEP 3: Quiz attempts table ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.quiz_attempts (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID REFERENCES auth.users ON DELETE CASCADE,
    session_id    UUID REFERENCES public.sessions ON DELETE CASCADE,
    score         INTEGER NOT NULL,
    total         INTEGER NOT NULL,
    answers       JSONB NOT NULL,
    attempted_at  TIMESTAMPTZ DEFAULT NOW()
);


-- ── STEP 4: Row Level Security ─────────────────────────────────────────────────
ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_attempts ENABLE ROW LEVEL SECURITY;

-- Users see only their own sessions
CREATE POLICY "Users see own sessions"
    ON public.sessions FOR ALL
    USING (auth.uid() = user_id);

-- Users see only their own quiz attempts
CREATE POLICY "Users see own quiz attempts"
    ON public.quiz_attempts FOR ALL
    USING (auth.uid() = user_id);


-- ── STEP 5: Helper function for appending tab names ───────────────────────────
-- Called from Python via supabase.rpc("append_generated_tab", {...})
CREATE OR REPLACE FUNCTION append_generated_tab(session_id UUID, tab TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE public.sessions
    SET generated_tabs = array_append(generated_tabs, tab)
    WHERE id = session_id
      AND NOT (tab = ANY(generated_tabs));
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

