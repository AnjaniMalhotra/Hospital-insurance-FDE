"""One function, ask(), that talks to an AI model.
Provider chain: Gemini (main) -> OpenAI (fallback). There is no offline mode: set GEMINI_API_KEY to use ClaimTrail.
Models can be changed with env vars GEMINI_MODEL / OPENAI_MODEL. GEMINI_RPM paces the calls to stay under the
per-minute quota (the free tier allows about 15 a minute); set GEMINI_RPM=0 on a paid key for no pacing.
"""
import os
import threading
import time
from functools import cache

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
GEMINI_RPM = int(os.getenv("GEMINI_RPM", "12"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
HAS_GEMINI = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
HAS_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
READY = HAS_GEMINI or HAS_OPENAI
MODE = " -> ".join([f"Gemini {GEMINI_MODEL}"] * HAS_GEMINI + [f"OpenAI {OPENAI_MODEL}"] * HAS_OPENAI) or "not set up"
NO_KEY = "No AI key set. Set GEMINI_API_KEY (and optionally OPENAI_API_KEY as a backup), then restart: python start_integration.py"


@cache  # create each client once and keep it alive (a garbage-collected client closes itself)
def client(provider):
    if provider == "gemini":  # give up after 60 s and 2 tries (e.g. "model overloaded"), so a run never hangs
        from google import genai
        from google.genai import types
        return genai.Client(http_options=types.HttpOptions(timeout=60_000, retry_options=types.HttpRetryOptions(attempts=2)))
    from openai import OpenAI
    return OpenAI(timeout=60, max_retries=1)


_next_call, _pace_lock = [0.0], threading.Lock()


def pace():
    """Wait for our turn so Gemini calls are spaced out (parallel threads queue up here)."""
    if GEMINI_RPM:
        with _pace_lock:
            time.sleep(max(0.0, _next_call[0] - time.monotonic()))
            _next_call[0] = time.monotonic() + 60 / GEMINI_RPM


def ask_gemini(prompt, schema):
    pace()
    config = {"response_mime_type": "application/json", "response_schema": schema} if schema else None
    resp = client("gemini").models.generate_content(model=GEMINI_MODEL, contents=prompt, config=config)
    return resp.parsed if schema else resp.text


def ask_openai(prompt, schema):
    if schema:
        return client("openai").responses.parse(model=OPENAI_MODEL, input=prompt,
                                                text_format=schema).output_parsed
    return client("openai").responses.create(model=OPENAI_MODEL, input=prompt).output_text


def ask(prompt, schema=None):
    """Try Gemini first; on any failure (outage, quota, bad output) fall back to OpenAI.
    Returns a `schema` object (pydantic), or plain text when no schema is given."""
    if not READY:
        raise RuntimeError(NO_KEY)
    if HAS_GEMINI:
        try:
            result = ask_gemini(prompt, schema)
            if result:
                return result
            print("  Gemini returned nothing, trying OpenAI")
        except Exception as e:
            print(f"  Gemini failed ({type(e).__name__}: {str(e)[:80]}), trying OpenAI")
    if HAS_OPENAI:
        return ask_openai(prompt, schema)
    raise RuntimeError("Gemini failed and no OPENAI_API_KEY is set for the fallback")
