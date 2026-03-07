# services/ai.py
# AI generation service — Groq Llama for ALL tabs (Gemini quota exhausted).
# RULE: Every response is validated with Pydantic before being saved to Supabase.
# RULE: No raw string parsing. No regex. No unvalidated AI output ever reaches the DB.

import os
import json
import time
# from google import genai        # DISABLED — Gemini quota exhausted
# from google.genai import types  # DISABLED — Gemini quota exhausted
from groq import Groq
from models.schemas import (
    SummaryOutput, ReadEasyOutput, FocusModeOutput,
    StepByStepOutput, MindMapOutput, QuizOutput,
    AIDetectionOutput
)

# Groq client — lazily initialized after dotenv loads env vars
_groq_client = None

# _gemini_client = None  # DISABLED

# def _get_gemini():       # DISABLED
#     global _gemini_client
#     if _gemini_client is None:
#         _gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
#     return _gemini_client

def _get_groq():
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _groq_client

# Convenience alias used by the new _call_groq below
_groq = None
def _init_groq():
    global _groq
    if _groq is None:
        _groq = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _groq

# Tab → (schema, model, prompt_template)
TAB_CONFIG = {
    "summary": {
        "schema": SummaryOutput,
        "model": "groq",  # switched from gemini — quota exhausted
        "prompt": (
            "You are an expert educational summariser. "
            "Summarise the following educational content into clear bullet points and key terms.\n\n"
            "CONTENT:\n{text}"
        ),
    },
    "read_easy": {
        "schema": ReadEasyOutput,
        "model": "groq",  # switched from gemini — quota exhausted
        "prompt": (
            "You are a plain-language education specialist. "
            "Rewrite the following content using simple vocabulary and short sentences "
            "suitable for a struggling reader or someone with dyslexia.\n\n"
            "CONTENT:\n{text}"
        ),
    },
    "focus_mode": {
        "schema": FocusModeOutput,
        "model": "groq",  # switched from gemini — quota exhausted
        "prompt": (
            "You are a focus and attention specialist. "
            "Break the following content into clearly labelled sections of maximum 80 words each. "
            "Each section must have a recap line.\n\n"
            "CONTENT:\n{text}"
        ),
    },
    "step_by_step": {
        "schema": StepByStepOutput,
        "model": "groq",  # switched from gemini — quota exhausted
        "prompt": (
            "You are a logical breakdown expert. "
            "Convert the following content into clear, ordered steps. "
            "Each step should be self-contained and under 60 words.\n\n"
            "CONTENT:\n{text}"
        ),
    },
    "mind_map": {
        "schema": MindMapOutput,
        "model": "groq",  # switched from gemini — quota exhausted
        "prompt": (
            "You are a Mermaid.js diagram expert. "
            "Generate a valid Mermaid mindmap diagram for the following content. "
            "Rules: Start with 'mindmap'. Use only double quotes for labels. "
            "No markdown fences. No backticks. No special characters in labels.\n\n"
            "CONTENT:\n{text}"
        ),
    },
    "quiz": {
        "schema": QuizOutput,
        "model": "groq",
        "prompt": (
            "You are an expert quiz writer. "
            "Generate exactly 3 multiple choice questions from the following content. "
            "Each question must have exactly 4 options. Mark exactly one as correct.\n\n"
            "CONTENT:\n{text}"
        ),
    },
    "ai_detection": {
        "schema": AIDetectionOutput,
        "model": "groq",  # switched from gemini — quota exhausted
        "prompt": (
            "You are an expert forensic linguist and AI content detection specialist. "
            "Analyse the following text and determine what percentage is likely AI-generated. "
            "Look for these AI indicators: overly uniform sentence structure, "
            "lack of personal anecdotes, hedging language, perfect grammar throughout, "
            "generic transitions, absence of typos or colloquialisms, "
            "and repetitive phrasing patterns. "
            "Also identify human indicators such as personal voice, irregular rhythm, "
            "domain-specific slang, emotional language, and imperfect grammar. "
            "Be objective and evidence-based in your analysis.\n\n"
            "CONTENT:\n{text}"
        ),
    },
}


def generate_tab(tab_name: str, source_text: str) -> dict:
    """
    Calls the appropriate AI model for the given tab.
    Returns a dict (JSON-serialisable) ready to be saved to Supabase.
    Raises RuntimeError if generation fails after retries.
    """
    config = TAB_CONFIG[tab_name]
    prompt = config["prompt"].format(text=source_text)
    schema = config["schema"]

    if config["model"] == "gemini":
        return _call_gemini(prompt, schema)
    elif config["model"] == "groq":
        return _call_groq(prompt, schema)


# ── _call_gemini — DISABLED (Gemini quota exhausted) ─────────────────────────
# def _call_gemini(prompt: str, schema, retries: int = 2) -> dict:
#     client = _get_gemini()
#     last_error = None
#     for attempt in range(retries + 1):
#         try:
#             response = client.models.generate_content(
#                 model="models/gemini-2.0-flash-lite",
#                 contents=prompt,
#                 config=types.GenerateContentConfig(
#                     response_mime_type="application/json",
#                     response_schema=schema.model_json_schema(),
#                 ),
#             )
#             raw = response.text.strip()
#             if raw.startswith("```"):
#                 lines = raw.split("\n")
#                 raw = "\n".join(lines[1:-1])
#             data = json.loads(raw)
#             validated = schema(**data)
#             return validated.model_dump()
#         except Exception as e:
#             last_error = e
#             if "429" in str(e):
#                 time.sleep(15)
#             continue
#     raise RuntimeError(f"Gemini generation failed after {retries + 1} attempts: {last_error}")
# ── END _call_gemini ──────────────────────────────────────────────────────────


def _call_groq(prompt: str, schema, retries: int = 3) -> dict:
    last_error = None
    for attempt in range(retries + 1):
        try:
            client = _get_groq()
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"You must respond ONLY with a valid JSON object "
                            f"matching this schema exactly: "
                            f"{json.dumps(schema.model_json_schema())}. "
                            "No explanation. No markdown. No preamble. "
                            "Return raw JSON only."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:].strip()
            data = json.loads(raw)
            validated = schema(**data)
            return validated.model_dump()
        except Exception as e:
            last_error = e
            if "rate_limit" in str(e).lower():
                time.sleep(10)
            continue
    raise RuntimeError(
        f"Groq generation failed after {retries + 1} attempts: {last_error}"
    )


# ── MERMAID SELF-HEALING ───────────────────────────────────────────────────────

MERMAID_HEAL_PROMPT = """
You are a Mermaid.js syntax expert. The following Mermaid diagram has a syntax error.
Fix it and return ONLY the corrected Mermaid syntax. No explanation. No backticks. No markdown.

BROKEN DIAGRAM:
{broken}

ERROR:
{error}
"""


def heal_mermaid(broken_code: str, error: str) -> str:
    """
    Attempts to fix a broken Mermaid diagram using Groq.
    Returns the fixed diagram string, or raises RuntimeError after 3 failures.
    """
    client = _get_groq()
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": MERMAID_HEAL_PROMPT.format(
                        broken=broken_code, error=error
                    )}
                ],
                temperature=0.1,
                max_tokens=500,
            )
            fixed = response.choices[0].message.content.strip()
            if fixed.startswith("mindmap") or fixed.startswith("graph") or fixed.startswith("flowchart"):
                return fixed
        except Exception:
            continue
    raise RuntimeError("Mermaid healing failed after 3 attempts")


import asyncio
import tempfile
import os

def generate_summary_audio(summary_data: dict) -> bytes:
    """
    Converts summary dict to a natural audio script
    and generates MP3 bytes using edge-tts.
    Returns raw MP3 bytes.
    """
    # Build the audio script from cached summary data
    title = summary_data.get("title", "Summary")
    bullets = summary_data.get("bullets", [])
    key_terms = summary_data.get("key_terms", [])

    # Format text naturally for speech
    lines = []
    lines.append(f"Here is your summary. {title}.")
    lines.append("The key points are as follows.")

    for i, bullet in enumerate(bullets, 1):
        lines.append(f"Point {i}. {bullet}.")

    if key_terms:
        terms = ", ".join(key_terms[:-1]) + f", and {key_terms[-1]}" \
                if len(key_terms) > 1 else key_terms[0]
        lines.append(f"Key terms to remember: {terms}.")

    script = " ".join(lines)

    # Generate audio using edge-tts
    async def _generate():
        import edge_tts
        # Use a deeper male voice and keep normal speed for better clarity
        voice = "en-US-ChristopherNeural"
        communicate = edge_tts.Communicate(script, voice, rate="+0%", pitch="-10Hz")
        # Write to temp file then read bytes
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tmp_path = f.name
        await communicate.save(tmp_path)
        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
        os.unlink(tmp_path)
        return audio_bytes

    import asyncio
    import concurrent.futures

    def _run_in_thread():
        return asyncio.run(_generate())

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(_run_in_thread)
        return future.result()


def generate_read_easy_audio(read_easy_data: dict) -> bytes:
    """
    Converts read_easy dict to a calm, flowing audio script
    and generates MP3 bytes using edge-tts.
    Returns raw MP3 bytes.
    """
    intro = read_easy_data.get("intro", "")
    paragraphs = read_easy_data.get("paragraphs", [])
    summary_line = read_easy_data.get("summary_line", "")

    lines = []
    lines.append("Here is your simplified reading.")

    if intro:
        lines.append(intro)

    for para in paragraphs:
        lines.append(para)

    if summary_line:
        lines.append(f"To summarise. {summary_line}")

    script = " ".join(lines)

    async def _generate():
        import edge_tts
        # Match summary audio voice for consistency
        voice = "en-US-ChristopherNeural"
        communicate = edge_tts.Communicate(script, voice, rate="+0%", pitch="-10Hz")
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tmp_path = f.name
        await communicate.save(tmp_path)
        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
        os.unlink(tmp_path)
        return audio_bytes

    import asyncio
    import concurrent.futures

    def _run_in_thread():
        return asyncio.run(_generate())

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(_run_in_thread)
        return future.result()
