# routes/api.py
# Uses plain requests + Supabase REST API instead of the supabase SDK
# (SDK is incompatible with Python 3.14 — see AdaptIQ_ErrorFix_Instructions.md Error 1)

from flask import Blueprint, request, jsonify, session as flask_session
from services.ingestion import extract_text
from services.ai import generate_tab
import requests as http
import os
import jwt

api = Blueprint("api", __name__)

VALID_TABS = ["summary", "read_easy", "focus_mode", "step_by_step", "mind_map", "quiz", "ai_detection"]

# ── Supabase REST Helpers ─────────────────────────────────────────────────────

def _headers():
    """Service-role headers for all server-side DB calls (bypasses RLS)."""
    key = os.environ["SUPABASE_SERVICE_KEY"]
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

def _url(path):
    return f"{os.environ['SUPABASE_URL']}/rest/v1/{path}"


def db_insert(table, data):
    r = http.post(_url(table), headers=_headers(), json=data)
    r.raise_for_status()
    return r.json()[0]


def db_select_one(table, filters):
    params = {k: f"eq.{v}" for k, v in filters.items()}
    params["limit"] = 1
    r = http.get(_url(table), headers=_headers(), params=params)
    r.raise_for_status()
    result = r.json()
    return result[0] if result else None


def db_update(table, filters, data):
    params = {k: f"eq.{v}" for k, v in filters.items()}
    r = http.patch(_url(table), headers=_headers(), params=params, json=data)
    r.raise_for_status()
    # Check if content exists before parsing JSON (Supabase PATCH can return 204)
    return r.json() if r.content else {}


def db_rpc(fn, params):
    r = http.post(f"{os.environ['SUPABASE_URL']}/rest/v1/rpc/{fn}", headers=_headers(), json=params)
    r.raise_for_status()
    # Check if content exists before parsing JSON (VOID RPCs return 204 No Content)
    return r.json() if r.content else {}


def db_delete(table, filters):
    params = {k: f"eq.{v}" for k, v in filters.items()}
    r = http.delete(_url(table), headers=_headers(), params=params)
    r.raise_for_status()
    return True


# ── JWT Auth Helper ───────────────────────────────────────────────────────────

def _get_user_id() -> str | None:
    """
    Try 1: Decode Bearer JWT token from Authorization header.
    Try 2: Fall back to Flask server-side session (set by app.py login route).
    Either source is acceptable — both require a real Supabase login.
    """
    import base64

    # ── Try Bearer token first ──
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            secret = os.environ["SUPABASE_JWT_SECRET"]
            secret_bytes = base64.b64decode(secret + "==")
            payload = jwt.decode(
                token,
                secret_bytes,
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
            uid = payload.get("sub")
            if uid:
                return uid
        except Exception:
            pass  # Fall through to session fallback

    # ── Fallback: Flask server-side session ──
    uid = flask_session.get("user_id")
    return uid if uid else None


# ── ROUTE 1: UPLOAD ───────────────────────────────────────────────────────────

@api.route("/api/upload", methods=["POST"])
def upload():
    """
    Accepts content upload. Extracts text. Saves session row to Supabase.
    Returns session_id. Makes ZERO AI calls.
    """
    user_id = _get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorised"}), 401

    source_type = request.form.get("source_type")
    source_name = request.form.get("source_name", "Untitled")

    try:
        if source_type == "paste":
            content = request.form.get("content", "")
        elif source_type in ("pdf", "docx"):
            content = request.files["file"].read()
        elif source_type == "url":
            content = request.form.get("url", "")
        else:
            return jsonify({"error": "Invalid source_type. Use: paste, pdf, url, docx"}), 400

        raw_text = extract_text(source_type, content)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Save to Supabase — all 6 tab columns default to NULL
    try:
        row = db_insert("sessions", {
            "user_id": user_id,
            "source_text": raw_text,
            "source_type": source_type,
            "source_name": source_name,
        })
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    return jsonify({"session_id": row["id"], "source_name": row["source_name"]}), 201


# ── ROUTE 2: GENERATE TAB ─────────────────────────────────────────────────────

@api.route("/api/generate/<tab_name>", methods=["POST"])
def generate(tab_name: str):
    """
    Cache check first — only calls AI if tab column is NULL.
    Saves result to Supabase before returning.
    """
    if tab_name not in VALID_TABS:
        return jsonify({"error": f"Unknown tab: {tab_name}"}), 400

    user_id = _get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorised"}), 401

    body = request.get_json()
    if not body:
        return jsonify({"error": "JSON body required"}), 400

    session_id = body.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id required"}), 400

    # Fetch session from Supabase
    row = db_select_one("sessions", {"id": session_id, "user_id": user_id})
    if not row:
        return jsonify({"error": "Session not found"}), 404

    # ── CACHE HIT: return immediately, no AI call ──
    if row.get(tab_name) is not None:
        return jsonify({"tab": tab_name, "data": row[tab_name], "cached": True}), 200

    # ── CACHE MISS: call AI exactly once ──
    source_text = row["source_text"]

    try:
        output = generate_tab(tab_name, source_text)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500

    # Save generated output to Supabase
    try:
        db_update("sessions", {"id": session_id}, {tab_name: output})
        db_rpc("append_generated_tab", {"session_id": session_id, "tab": tab_name})
    except Exception as e:
        return jsonify({"error": f"Failed to save to database: {str(e)}"}), 500

    return jsonify({"tab": tab_name, "data": output, "cached": False}), 200


# ── ROUTE 3: SESSION STATUS ───────────────────────────────────────────────────

@api.route("/api/session/<session_id>", methods=["GET", "DELETE"])
def handle_session(session_id: str):
    """Returns session metadata or deletes a session."""
    user_id = _get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorised"}), 401

    if request.method == "DELETE":
        try:
            db_delete("sessions", {"id": session_id, "user_id": user_id})
            return jsonify({"success": True}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to delete session: {str(e)}"}), 500

    # GET method
    params = {
        "id": f"eq.{session_id}",
        "user_id": f"eq.{user_id}",
        "select": "id,source_name,source_type,generated_tabs,created_at",
        "limit": 1,
    }
    r = http.get(_url("sessions"), headers=_headers(), params=params)
    r.raise_for_status()
    result = r.json()

    if not result:
        return jsonify({"error": "Session not found"}), 404

    return jsonify(result[0]), 200


# ── ROUTE 4: SESSION HISTORY ──────────────────────────────────────────────────

@api.route("/api/sessions", methods=["GET"])
def get_sessions():
    """Returns a list of all user sessions for the history sidebar."""
    user_id = _get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorised"}), 401

    params = {
        "user_id": f"eq.{user_id}",
        "select": "id,source_name,source_type,generated_tabs,created_at",
        "order": "created_at.desc",
        "limit": 10,
    }
    r = http.get(_url("sessions"), headers=_headers(), params=params)
    r.raise_for_status()
    
    return jsonify(r.json()), 200


# ── ROUTE 5: SUMMARY AUDIO ────────────────────────────────────────────────────

@api.route("/api/audio/summary", methods=["POST"])
def generate_audio_summary():
    user_id = _get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorised"}), 401

    body = request.get_json()
    session_id = body.get("session_id") if body else None
    if not session_id:
        return jsonify({"error": "session_id required"}), 400

    # Fetch session
    row = db_select_one("sessions", {"id": session_id, "user_id": user_id})
    if not row:
        return jsonify({"error": "Session not found"}), 404

    # Check summary exists — audio requires summary to be generated first
    if not row.get("summary"):
        return jsonify({"error": "Generate Summary first before creating audio"}), 400

    # Cache hit — audio already generated
    if row.get("summary_audio_url"):
        return jsonify({"audio_url": row["summary_audio_url"], "cached": True}), 200

    # Generate audio from cached summary data
    try:
        from services.ai import generate_summary_audio
        audio_bytes = generate_summary_audio(row["summary"])
    except Exception as e:
        return jsonify({"error": f"Audio generation failed: {str(e)}"}), 500

    # Upload to Supabase Storage
    try:
        import supabase_client
        filename = f"summary_{session_id}.mp3"
        audio_url = supabase_client.upload_audio(audio_bytes, filename)
    except Exception as e:
        return jsonify({"error": f"Audio upload failed: {str(e)}"}), 500

    # Save URL to session
    db_update("sessions", {"id": session_id}, {"summary_audio_url": audio_url})

    return jsonify({"audio_url": audio_url, "cached": False}), 200


# ── ROUTE 6: READ EASY AUDIO ──────────────────────────────────────────────────

@api.route("/api/audio/read-easy", methods=["POST"])
def generate_audio_read_easy():
    user_id = _get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorised"}), 401

    body = request.get_json()
    session_id = body.get("session_id") if body else None
    if not session_id:
        return jsonify({"error": "session_id required"}), 400

    row = db_select_one("sessions", {"id": session_id, "user_id": user_id})
    if not row:
        return jsonify({"error": "Session not found"}), 404

    if not row.get("read_easy"):
        return jsonify({"error": "Generate Read Easy first before creating audio"}), 400

    # Cache hit
    if row.get("read_easy_audio_url"):
        return jsonify({"audio_url": row["read_easy_audio_url"], "cached": True}), 200

    # Generate
    try:
        from services.ai import generate_read_easy_audio
        audio_bytes = generate_read_easy_audio(row["read_easy"])
    except Exception as e:
        return jsonify({"error": f"Audio generation failed: {str(e)}"}), 500

    # Upload to Supabase Storage
    try:
        import supabase_client
        filename = f"read_easy_{session_id}.mp3"
        audio_url = supabase_client.upload_audio(audio_bytes, filename)
    except Exception as e:
        return jsonify({"error": f"Audio upload failed: {str(e)}"}), 500

    # Save URL to session
    db_update("sessions", {"id": session_id}, {"read_easy_audio_url": audio_url})

    return jsonify({"audio_url": audio_url, "cached": False}), 200
