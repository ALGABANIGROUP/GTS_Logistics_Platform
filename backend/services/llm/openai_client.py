from __future__ import annotations

import os
from importlib import import_module
from importlib.util import find_spec
from typing import Any, Mapping, Optional

from fastapi.concurrency import run_in_threadpool

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "0").lower() in ("1", "true", "yes", "on")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "30"))
OPENAI_MAX_RETRIES = max(int(os.getenv("OPENAI_MAX_RETRIES", "2")), 1)


class OpenAIClient:
    def __init__(self) -> None:
        self._enabled = OPENAI_ENABLED and bool(OPENAI_API_KEY)
        self._client: Optional[Any] = None
        if self._enabled and find_spec("openai"):
            module = import_module("openai")
            OpenAI = getattr(module, "OpenAI", None)
            if OpenAI is not None:
                self._client = OpenAI(api_key=OPENAI_API_KEY, request_timeout=OPENAI_TIMEOUT)

    @property
    def is_available(self) -> bool:
        return self._client is not None

    async def chat_async(
        self,
        *,
        messages: list[Mapping[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> Any:
        if not self.is_available:
            raise RuntimeError("OpenAI client is not available.")
        attempt = 0

        def _call() -> Any:
            return self._client.chat.completions.create(
                model=model or OPENAI_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

        while True:
            try:
                return await run_in_threadpool(_call)
            except Exception:
                attempt += 1
                if attempt >= OPENAI_MAX_RETRIES:
                    raise

    async def health_check(self) -> bool:
        if not self.is_available:
            return False

        def _call() -> bool:
            if not hasattr(self._client, "models"):
                return False
            models = self._client.models.list(limit=1)
            return bool(getattr(models, "data", None))

        try:
            return await run_in_threadpool(_call)
        except Exception:
            return False


_client_instance: Optional[OpenAIClient] = None


def get_openai_client() -> OpenAIClient:
    global _client_instance
    if _client_instance is None:
        _client_instance = OpenAIClient()
    return _client_instance
