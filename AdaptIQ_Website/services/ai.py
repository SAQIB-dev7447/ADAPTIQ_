# services/ai.py
# AI generation service — google.genai for 5 tabs, Groq Llama for Quiz.
# RULE: Every response is validated with Pydantic before being saved to Supabase.
# RULE: No raw string parsing. No regex. No unvalidated AI output ever reaches the DB.

import os
import json
import time
from google import genai
from google.genai import types
from groq import Groq
from models.schemas import (
    SummaryOutput, ReadEasyOutput, FocusModeOutput,
    StepByStepOutput, MindMapOutput, QuizOutput,
    AIDetectionOutput
)

# Clients are lazily initialized inside functions after dotenv has loaded env vars
_gemini_client = None
_groq_client = None

def _get_gemini():
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _gemini_client

def _get_groq():
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _groq_client

# Tab → (schema, model, prompt_template)
TAB_CONFIG = {
    "summary": {
        "schema": SummaryOutput,
        "model": "gemini",
        "prompt": (
            "You are an expert educational summariser. "
            "Summarise the following educational content into clear bullet points and key terms.\n\n"
            "CONTENT:\n{text}"
        ),
    },
    "read_easy": {
        "schema": ReadEasyOutput,
        "model": "gemini",
        "prompt": (
            "You are a plain-language education specialist. "
            "Rewrite the following content using simple vocabulary and short sentences "
            "suitable for a struggling reader or someone with dyslexia.\n\n"
            "CONTENT:\n{text}"
        ),
    },
    "focus_mode": {
        "schema": FocusModeOutput,
        "model": "gemini",
        "prompt": (
            "You are a focus and attention specialist. "
            "Break the following content into clearly labelled sections of maximum 80 words each. "
            "Each section must have a recap line.\n\n"
            "CONTENT:\n{text}"
        ),
    },
    "step_by_step": {
        "schema": StepByStepOutput,
        "model": "gemini",
        "prompt": (
            "You are a logical breakdown expert. "
            "Convert the following content into clear, ordered steps. "
            "Each step should be self-contained and under 60 words.\n\n"
            "CONTENT:\n{text}"
        ),
    },
    "mind_map": {
        "schema": MindMapOutput,
        "model": "gemini",
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
        "model": "groq",       # Groq for quiz — faster and free
        "prompt": (
            "You are an expert quiz writer. "
            "Generate exactly 3 multiple choice questions from the following content. "
            "Each question must have exactly 4 options. Mark exactly one as correct.\n\n"
            "CONTENT:\n{text}"
        ),
    },
    "ai_detection": {
        "schema": AIDetectionOutput,
        "model": "gemini",
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


def _call_gemini(prompt: str, schema, retries: int = 2) -> dict:
    client = _get_gemini()
    for attempt in range(retries + 1):
        try:
            response = client.models.generate_content(
                model="models/gemini-2.5-flash-lite-preview-09-2025",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema.model_json_schema(),
                ),
            )
            raw = response.text.strip()
            # Error 2 fix: strip markdown fences if Gemini wraps response in them
            if raw.startswith("```"):
                lines = raw.split("\n")
                raw = "\n".join(lines[1:-1])
            data = json.loads(raw)
            validated = schema(**data)
            return validated.model_dump()
        except Exception as e:
            # Error 7 fix: retry on quota exceeded (429)
            if "429" in str(e) and attempt < retries:
                time.sleep(10)
                continue
            if attempt == retries:
                raise RuntimeError(f"Gemini generation failed after {retries+1} attempts: {e}")
            continue


def _call_groq(prompt: str, schema, retries: int = 2) -> dict:
    client = _get_groq()
    for attempt in range(retries + 1):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"You must respond ONLY with a valid JSON object matching this schema: "
                            f"{json.dumps(schema.model_json_schema())}. "
                            "Respond ONLY with a valid JSON object. No explanation. No markdown. No preamble."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            raw = response.choices[0].message.content.strip()
            # Error 3 fix: strip markdown fences from Groq response
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:].strip()
            data = json.loads(raw)
            validated = schema(**data)
            return validated.model_dump()
        except Exception as e:
            if attempt == retries:
                raise RuntimeError(f"Groq generation failed after {retries+1} attempts: {e}")
            continue


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
