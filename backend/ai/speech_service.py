from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

import aiohttp

logger = logging.getLogger(__name__)

try:
    import whisper  # type: ignore
except Exception:  # pragma: no cover
    whisper = None  # type: ignore


class SpeechService:
    """Optional speech-to-text helper with graceful fallback when Whisper is unavailable."""

    def __init__(self, model_name: str = "base") -> None:
        self.model_name = model_name
        self.model: Any = None
        self.model_loaded = False

    async def load_model(self) -> bool:
        if self.model_loaded:
            return True
        if whisper is None:
            logger.warning("Whisper is not installed; speech transcription is disabled")
            return False
        try:
            loop = asyncio.get_running_loop()
            self.model = await loop.run_in_executor(None, whisper.load_model, self.model_name)
            self.model_loaded = True
            logger.info("Speech model loaded: %s", self.model_name)
            return True
        except Exception as exc:
            logger.error("Failed to load speech model: %s", exc)
            return False

    async def transcribe(self, audio_source: str, language: Optional[str] = None) -> Dict[str, Any]:
        if not await self.load_model():
            return {
                "text": "",
                "language": language or "unknown",
                "segments": [],
                "error": "speech_model_unavailable",
            }

        temp_path: Optional[Path] = None
        try:
            if audio_source.startswith(("http://", "https://")):
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
                    async with session.get(audio_source) as response:
                        response.raise_for_status()
                        audio_data = await response.read()
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                    tmp.write(audio_data)
                    temp_path = Path(tmp.name)
                    source_path = str(temp_path)
            else:
                source_path = audio_source

            loop = asyncio.get_running_loop()
            options: Dict[str, Any] = {}
            if language:
                options["language"] = language
            result = await loop.run_in_executor(
                None,
                lambda: self.model.transcribe(source_path, **options),
            )
            return {
                "text": result.get("text", "").strip(),
                "language": result.get("language", language or "unknown"),
                "segments": result.get("segments", []),
            }
        except Exception as exc:
            logger.error("Speech transcription failed: %s", exc)
            return {
                "text": "",
                "language": language or "unknown",
                "segments": [],
                "error": str(exc),
            }
        finally:
            if temp_path and temp_path.exists():
                try:
                    os.unlink(temp_path)
                except OSError:
                    logger.debug("Failed to remove temp audio file %s", temp_path)

    async def detect_language(self, audio_source: str) -> str:
        result = await self.transcribe(audio_source)
        return str(result.get("language") or "unknown")


speech_service = SpeechService()
