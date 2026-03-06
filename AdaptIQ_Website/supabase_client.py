# supabase_client.py
# Supabase SDK removed (incompatible with Python 3.14).
# Auth operations (sign_up, sign_in, sign_out) use the Supabase Auth REST API directly.
# See AdaptIQ_ErrorFix_Instructions.md Error 1.

import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Ensure .env is loaded even if this module is imported first


def _auth_headers():
    return {
        "apikey": os.environ.get("SUPABASE_KEY", ""),
        "Content-Type": "application/json",
    }

def _auth_url(path):
    return f"{os.environ.get('SUPABASE_URL', '')}/auth/v1/{path}"


def sign_up(email: str, password: str) -> dict:
    """Register a new user. Returns user dict or raises on error."""
    r = requests.post(
        _auth_url("signup"),
        headers=_auth_headers(),
        json={"email": email, "password": password}
    )
    data = r.json()
    if r.status_code not in (200, 201) or data.get("error"):
        error_msg = data.get("error_description") or data.get("msg") or data.get("error") or "Sign up failed"
        raise Exception(error_msg)
    return data


def sign_in(email: str, password: str) -> dict:
    """
    Sign in with email + password.
    Returns dict with keys: access_token, user { id, email }
    """
    r = requests.post(
        _auth_url("token?grant_type=password"),
        headers=_auth_headers(),
        json={"email": email, "password": password}
    )
    data = r.json()
    if r.status_code != 200 or data.get("error"):
        error_msg = data.get("error_description") or data.get("msg") or data.get("error") or "Login failed"
        raise Exception(error_msg)
    return data


def sign_out(access_token: str) -> None:
    """Sign out (invalidates the token on Supabase side)."""
    requests.post(
        _auth_url("logout"),
        headers={**_auth_headers(), "Authorization": f"Bearer {access_token}"},
    )


# Legacy compatibility shim — kept so existing app.py import doesn't break.
def get_supabase_client():
    """
    Returns a simple namespace with auth methods backed by REST calls.
    Drop-in for code that calls supabase_client.get_supabase_client().auth.sign_up etc.
    """
    class _Auth:
        def sign_up(self, creds):
            return _UserResponse(sign_up(creds["email"], creds["password"]))

        def sign_in_with_password(self, creds):
            data = sign_in(creds["email"], creds["password"])
            return _SessionResponse(data)

        def sign_out(self):
            pass  # token handled in flask session

    class _Client:
        auth = _Auth()

    return _Client()


class _UserResponse:
    """Mimics supabase response.user"""
    def __init__(self, data):
        user_data = data.get("user") or data
        self.user = _User(user_data) if user_data else None

class _User:
    def __init__(self, data):
        self.id = data.get("id", "")
        self.email = data.get("email", "")

class _Session:
    def __init__(self, data):
        self.access_token = data.get("access_token", "")

class _SessionResponse:
    """Mimics supabase response.user + response.session"""
    def __init__(self, data):
        user_obj = data.get("user") or {}
        self.user = _User(user_obj) if user_obj else None
        self.session = _Session(data)
