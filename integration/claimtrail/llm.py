"""The AI model ClaimTrail's agents use, built with Pydantic AI.
Gemini (main) -> OpenAI (backup) as ONE model: Pydantic AI's FallbackModel tries OpenAI if Gemini fails.
There is no offline mode: set GEMINI_API_KEY to use ClaimTrail.
Models can be changed with env vars GEMINI_MODEL / OPENAI_MODEL. GEMINI_RPM paces the calls to stay under the
per-minute quota (the free tier allows about 15 a minute); set GEMINI_RPM=0 on a paid key for no pacing.
"""
import asyncio
import os
import threading
import time
from functools import cache

from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.settings import ModelSettings

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
GEMINI_RPM = int(os.getenv("GEMINI_RPM", "12"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
GEMINI_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
HAS_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
READY = bool(GEMINI_KEY) or HAS_OPENAI
MODE = " -> ".join([f"Gemini {GEMINI_MODEL}"] * bool(GEMINI_KEY) + [f"OpenAI {OPENAI_MODEL}"] * HAS_OPENAI) or "not set up"
NO_KEY = "No AI key set. Set GEMINI_API_KEY (and optionally OPENAI_API_KEY as a backup), then restart: python start_integration.py"
SETTINGS = ModelSettings(timeout=60)  # give up on a call after 60 s, so a run never hangs


@cache  # build the model once
def model():
    """Gemini first, OpenAI as the backup: only the ones that have a key."""
    if not READY:
        raise RuntimeError(NO_KEY)
    chain = []
    if GEMINI_KEY:
        from pydantic_ai.models.google import GoogleModel
        from pydantic_ai.providers.google import GoogleProvider
        chain.append(GoogleModel(GEMINI_MODEL, provider=GoogleProvider(api_key=GEMINI_KEY)))
    if HAS_OPENAI:
        from pydantic_ai.models.openai import OpenAIChatModel
        chain.append(OpenAIChatModel(OPENAI_MODEL))
    return chain[0] if len(chain) == 1 else FallbackModel(*chain)


_next_call, _pace_lock = [0.0], threading.Lock()
_loop = asyncio.new_event_loop()                                    # ONE event loop for every agent call: the model's
threading.Thread(target=_loop.run_forever, daemon=True).start()     # connection belongs to it, whichever thread asks


def run(agent, prompt):
    """Run an agent on `prompt` and return its result. Safe from the pipeline's parallel threads; calls are paced
    (GEMINI_RPM) so the free tier's per-minute quota is never hit."""
    if GEMINI_RPM:
        with _pace_lock:                                            # wait for our turn
            time.sleep(max(0.0, _next_call[0] - time.monotonic()))
            _next_call[0] = time.monotonic() + 60 / GEMINI_RPM
    return asyncio.run_coroutine_threadsafe(agent.run(prompt), _loop).result()
