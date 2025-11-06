#!/usr/bin/env python3
"""
communication_module.py
Unified comms layer for CALI:
- Text in → event bus
- Text out → Coqui TTS via CaliToneOut
- Async hooks so FastAPI /ws can broadcast state

Design notes:
• Thread-safe TTS with an asyncio lock (Coqui is not fully thread-safe).
• Pluggable notifier callback to push events (e.g., to your WebSocket manager).
• Minimal dependencies: relies on comms.cali_tone_out.CaliToneOut only.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Awaitable, Callable, Deque, Dict, List, Optional, Union
from collections import deque
import asyncio
import time
import re
import json

try:
    # Local TTS wrapper (created earlier)
    from .cali_tone_out import CaliToneOut
except Exception:  # pragma: no cover
    # Fallback for flat layout (if not using a 'comms/' package)
    from cali_tone_out import CaliToneOut  # type: ignore


# ---------- Data Models ----------

@dataclass
class Utterance:
    role: str                # "user" | "cali" | "system"
    text: str
    ts: float                # epoch seconds
    audio_path: Optional[str] = None
    meta: Optional[Dict] = None


# ---------- Utility ----------

def _safe_id(text: str, prefix: str = "utt") -> str:
    base = re.sub(r"[^\w\-]+", "-", text.strip().lower())[:48]
    base = re.sub(r"-{2,}", "-", base).strip("-") or "msg"
    return f"{prefix}-{int(time.time()*1000)}-{base}"


# ---------- Core Comms ----------

class CommunicationModule:
    """
    Orchestrates CALI comms:
      - stores a small rolling history (default 200 entries)
      - synthesizes speech for CALI messages
      - notifies external listeners (e.g., /ws broadcaster)
    """

    def __init__(
        self,
        history_size: int = 200,
        tts_model: str = "tts_models/en/ljspeech/tacotron2-DDC",
        tts_out_dir: Union[str, Path] = "tts_out",
        tts_gpu: bool = False,
        notifier: Optional[Callable[[Dict], Awaitable[None]]] = None,
    ) -> None:
        self.history: Deque[Utterance] = deque(maxlen=history_size)
        self._tts = CaliToneOut(model_name=tts_model, output_dir=tts_out_dir, gpu=tts_gpu, progress_bar=False)
        self._notifier = notifier
        self._tts_lock = asyncio.Lock()

    # ----- Public API -----

    async def attach_notifier(self, notifier: Callable[[Dict], Awaitable[None]]) -> None:
        """Set/replace the async notifier (e.g., FastAPI WebSocket broadcaster)."""
        self._notifier = notifier

    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Return recent conversation as list[dict]."""
        items = list(self.history)[-limit:] if limit else list(self.history)
        return [asdict(x) for x in items]

    async def add_user_text(self, text: str, meta: Optional[Dict] = None) -> Utterance:
        """Record a user message and notify listeners."""
        utt = Utterance(role="user", text=text, ts=time.time(), meta=meta or {})
        self.history.append(utt)
        await self._emit("user_message", utt)
        return utt

    async def add_system_text(self, text: str, meta: Optional[Dict] = None) -> Utterance:
        """Record a system message and notify listeners."""
        utt = Utterance(role="system", text=text, ts=time.time(), meta=meta or {})
        self.history.append(utt)
        await self._emit("system_message", utt)
        return utt

    async def speak(self, text: str, speaker: Optional[str] = None, language: Optional[str] = None, meta: Optional[Dict] = None) -> Utterance:
        """
        Generate CALI speech from `text`, return the utterance with audio path set.
        Serialized by lock to avoid TTS concurrency issues.
        """
        if not text or not text.strip():
            raise ValueError("speak(): text cannot be empty")

        # Create record first (audio added later)
        utt = Utterance(role="cali", text=text, ts=time.time(), meta=meta or {})
        await self._emit("cali_thinking", utt)

        # TTS (serialized)
        async with self._tts_lock:
            # Use stable base name derived from text
            base = _safe_id(text, prefix="cali")
            out_path = self._tts.synthesize(text=text, file_name=base, speaker=speaker, language=language)

        utt.audio_path = str(out_path)
        self.history.append(utt)

        # Final event for clients (UI can play audio)
        await self._emit("cali_spoke", utt)
        return utt

    async def summarize(self, max_chars: int = 1500) -> str:
        """
        Lightweight text-only summary for UI panes; no LLM call here.
        Concatenates last messages up to `max_chars`.
        """
        buf: List[str] = []
        total = 0
        for u in reversed(self.history):
            line = f"[{u.role}] {u.text}"
            if total + len(line) > max_chars:
                break
            buf.append(line)
            total += len(line)
        text = "\n".join(reversed(buf))
        await self._emit("summary_ready", {"text": text})
        return text

    # ----- Internals -----

    async def _emit(self, event: str, payload: Union[Utterance, Dict]) -> None:
        """Send event to notifier if attached."""
        if not self._notifier:
            return
        data = asdict(payload) if isinstance(payload, Utterance) else payload
        try:
            await self._notifier({"event": event, "data": data, "ts": time.time()})
        except Exception:
            # Non-fatal: comms should never crash due to UI notifier issues
            pass


# ---------- Optional: simple in-process notifier for testing ----------

class InMemoryNotifier:
    """Collects emitted events for tests or headless runs."""
    def __init__(self) -> None:
        self.events: List[Dict] = []

    async def __call__(self, msg: Dict) -> None:
        self.events.append(msg)

    def drain(self) -> List[Dict]:
        ev, self.events = self.events, []
        return ev


# ---------- CLI smoke test ----------

if __name__ == "__main__":
    """
    Example:
      python comms/communication_module.py
    Produces a cali TTS wav and prints emitted events.
    """
    async def _demo():
        notifier = InMemoryNotifier()
        comms = CommunicationModule(notifier=notifier)
        await comms.add_user_text("Hello CALI, test the speaker.")
        utt = await comms.speak("I am online and my voice is working.")
        print("Audio:", utt.audio_path)
        print(json.dumps(notifier.drain(), indent=2))

    asyncio.run(_demo())
