from supabase import create_client, Client
from config import Config

def get_supabase_client() -> Client:
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def get_cached_content(user_id, content_hash, tab_type):
    """
    Checks if the generated content for a specific tab already exists in Supabase.
    """
    supabase = get_supabase_client()
    result = supabase.table("content_cache").select("*") \
        .eq("user_id", user_id) \
        .eq("content_hash", content_hash) \
        .eq("tab_type", tab_type) \
        .execute()
    
    return result.data[0] if result.data else None

def save_content_cache(user_id, content_hash, tab_type, result_json):
    """
    Saves the generated content to Supabase cache.
    """
    supabase = get_supabase_client()
    data = {
        "user_id": user_id,
        "content_hash": content_hash,
        "tab_type": tab_type,
        "result_json": result_json
    }
    supabase.table("content_cache").insert(data).execute()
