try:
    import flask
    import requests
    import google.generativeai
    import supabase
    from services import ai_service
    import supabase_client
    print("All imports successful!")
except Exception as e:
    print(f"Import Error: {e}")
