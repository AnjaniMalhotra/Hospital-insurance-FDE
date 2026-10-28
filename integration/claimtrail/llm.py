"""The AI model ClaimTrail's agents use, built with Pydantic AI.
Gemini -> a second Gemini model -> OpenAI (backup) as ONE model: Pydantic AI's FallbackModel tries the next one
if a model fails or is overloaded. There is no offline mode: set GEMINI_API_KEY to use ClaimTrail.
Models can be changed with env vars GEMINI_MODEL / GEMINI_BACKUP_MODEL / OPENAI_MODEL. Calls are sent at once; when
Google answers "too many requests" (429), "busy" (503) or "timed out" (504), the call waits a little and retries. GEMINI_RPM=n paces the
calls to n a minute instead (0 = off, the default).
"""
import asyncio
import os
import threading
import time
from functools import cache

from pydantic_ai.exceptions import ModelRateLimitError, ModelServerError, ModelUnavailableError
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.settings import ModelSettings

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")              # fastest here: ~3 s a letter
GEMINI_BACKUP_MODEL = os.getenv("GEMINI_BACKUP_MODEL", "gemini-3.5-flash-lite")
GEMINI_RPM = int(os.getenv("GEMINI_RPM", "0"))
RETRY_WAITS = [5, 10, 20, 30]  # seconds to wait before each retry of an overloaded or rate-limited call
RETRYABLE = (ModelRateLimitError, ModelUnavailableError, ModelServerError)  # 429, 503, other 5xx
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
GEMINI_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
HAS_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
READY = bool(GEMINI_KEY) or HAS_OPENAI
GEMINI_MODELS = list(dict.fromkeys([GEMINI_MODEL, GEMINI_BACKUP_MODEL] if GEMINI_BACKUP_MODEL else [GEMINI_MODEL]))
MODE = " -> ".join([f"Gemini {m}" for m in GEMINI_MODELS] * bool(GEMINI_KEY) + [f"OpenAI {OPENAI_MODEL}"] * HAS_OPENAI) or "not set up"
NO_KEY = "No AI key set. Set GEMINI_API_KEY (and optionally OPENAI_API_KEY as a backup), then restart: python start_integration.py"
SETTINGS = ModelSettings(timeout=30)  # give up on a call after 30 s (then the backup model), so a run never hangs


@cache  # build the model once
def model():
    """Gemini first (main, then backup model), OpenAI last: only the ones that have a key."""
    if not READY:
        raise RuntimeError(NO_KEY)
    chain = []
    if GEMINI_KEY:
        from pydantic_ai.models.google import GoogleModel
        from pydantic_ai.providers.google import GoogleProvider
        provider = GoogleProvider(api_key=GEMINI_KEY)
        chain += [GoogleModel(m, provider=provider) for m in GEMINI_MODELS]
    if HAS_OPENAI:
        from pydantic_ai.models.openai import OpenAIChatModel
        chain.append(OpenAIChatModel(OPENAI_MODEL))
    return chain[0] if len(chain) == 1 else FallbackModel(*chain)


_next_call, _pace_lock = [0.0], threading.Lock()
_loop = asyncio.new_event_loop()                                    # ONE event loop for every agent call: the model's
threading.Thread(target=_loop.run_forever, daemon=True).start()     # connection belongs to it, whichever thread asks


def run(agent, prompt):
    """Run an agent on `prompt` and return its result. Safe from the pipeline's parallel threads. If every model is
    rate-limited or busy, waits and retries (RETRY_WAITS); paced to GEMINI_RPM calls a minute if that is set."""
    for wait in RETRY_WAITS + [None]:
        if GEMINI_RPM:
            with _pace_lock:                                        # wait for our turn
                time.sleep(max(0.0, _next_call[0] - time.monotonic()))
                _next_call[0] = time.monotonic() + 60 / GEMINI_RPM
        try:
            return asyncio.run_coroutine_threadsafe(agent.run(prompt), _loop).result()
        except (*RETRYABLE, ExceptionGroup) as e:
            if wait is None or not _retryable(e):
                raise
            time.sleep(wait)


def _retryable(e):
    """True for 'too many requests' / 'busy' / 'timed out' errors. FallbackModel wraps the errors of all its models
    in a group: retry only if every model failed that way."""
    if isinstance(e, ExceptionGroup):
        return all(_retryable(x) for x in e.exceptions)
    return isinstance(e, RETRYABLE)
