import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Supabase Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-anon-role-key")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "your-service-role-key")

    # AI API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key")

    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "adaptiq_modular_refactor_secret_2026")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
