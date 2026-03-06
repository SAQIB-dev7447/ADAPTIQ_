import os

class Config:
    # Supabase Configuration
    # Replace these with your actual Supabase Project URL and API Key
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-anon-role-key")
    
    # AI API Keys
    # Replace these with your Gemini and Groq API keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key")
    
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "adaptiq_modular_refactor_secret_2026")
