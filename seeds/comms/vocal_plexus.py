#!/usr/bin/env python3
"""
vocal_plexus.py
High-level voice orchestrator for CALI.

• Wraps comms.cali_tone_out.CaliToneOut (Coqui TTS).
• Provides async queue for non-blocking speech.
• Emits lifecycle events via an optional async notifier (e.g., WebSocket).
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Awaitable, Callable, Dict, Optional, Union
import asyncio
import time
import re
import json

try:
    from .cali_tone_out import CaliToneOut
except Exception:  # pragma: no cover
    from cali_tone_out import CaliToneOut  # flat layout fallback


# ---------- Models ----------

@dataclass
class TTSTask:
    text: str
    speaker: Optional[str] = None
    language: Optional[str] = None
    file_name: Optional[str] = None
    meta: Optional[Dict] = None
    ts: float = 0.0
    task_id: str = ""


# ---------- Utils ----------

def _safe_id(text: str, prefix: str = "vp") -> str:
    base = re.sub(r"[^\w\-]+", "-", text.strip().lower())[:48]
    base = re.sub(r"-{2,}", "-", base).strip("-") or "msg"
    return f"{prefix}-{int(time.time()*1000)}-{base}"


# ---------- Core ----------

class VocalPlexus:
    """
    Async TTS orchestrator:
      - start(): launch worker loop
      - stop():  cancel worker loop
      - say():   immediate TTS (await result)
      - enqueue(): queue TTS and return task_id
      - attach_notifier(): set an async callback to receive events
    """

    def __init__(
        self,
        model_name: str = "tts_models/en/ljspeech/tacotron2-DDC",
        out_dir: Union[str, Path] = "tts_out",
        gpu: bool = False,
        progress_bar: bool = False,
        queue_maxsize: int = 200,
        notifier: Optional[Callable[[Dict], Awaitable[None]]] = None,
    ) -> None:
        self.tts = CaliToneOut(model_name=model_name, output_dir=out_dir, gpu=gpu, progress_bar=progress_bar)
        self._lock = asyncio.Lock()                  # serialize Coqui calls
        self._queue: asyncio.Queue[TTSTask] = asyncio.Queue(maxsize=queue_maxsize)
        self._worker_task: Optional[asyncio.Task] = None
        self._notifier = notifier
        self._running = asyncio.Event()

    # ----- Notifier -----

    async def attach_notifier(self, notifier: Callable[[Dict], Awaitable[None]]) -> None:
        self._notifier = notifier

    async def _emit(self, event: str, data: Dict) -> None:
        if not self._notifier:
            return
        payload = {"event": event, "ts": time.time(), "data": data}
        try:
            await self._notifier(payload)
        except Exception:
            # Non-fatal; voice should never crash due to UI issues
            pass

    # ----- Lifecycle -----

    async def start(self) -> None:
        if self._worker_task and not self._worker_task.done():
            return
        self._running.set()
        self._worker_task = asyncio.create_task(self._worker_loop())
        await self._emit("vocal_plexus_started", {})

    async def stop(self) -> None:
        self._running.clear()
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        await self._emit("vocal_plexus_stopped", {})

    # ----- Public API -----

    async def say(
        self, text: str, *, speaker: Optional[str] = None, language: Optional[str] = None,
        file_name: Optional[str] = None, meta: Optional[Dict] = None
    ) -> Path:
        """Immediate, awaitable TTS."""
        if not text or not text.strip():
            raise ValueError("VocalPlexus.say: text cannot be empty")

        task = TTSTask(text=text, speaker=speaker, language=language, file_name=file_name, meta=meta or {})
        task.ts = time.time()
        task.task_id = _safe_id(text, prefix="say")
        await self._emit("tts_started", {"task": asdict(task)})

        async with self._lock:
            out = self.tts.synthesize(text=text, file_name=file_name or task.task_id, speaker=speaker, language=language)

        await self._emit("tts_done", {"task": asdict(task), "path": str(out)})
        return out

    async def enqueue(
        self, text: str, *, speaker: Optional[str] = None, language: Optional[str] = None,
        file_name: Optional[str] = None, meta: Optional[Dict] = None
    ) -> str:
        """Queue TTS and return task_id (non-blocking)."""
        if not text or not text.strip():
            raise ValueError("VocalPlexus.enqueue: text cannot be empty")

        task = TTSTask(text=text, speaker=speaker, language=language, file_name=file_name, meta=meta or {})
        task.ts = time.time()
        task.task_id = _safe_id(text, prefix="q")
        await self._queue.put(task)
        await self._emit("tts_queued", {"task": asdict(task)})
        return task.task_id

    def queue_size(self) -> int:
        return self._queue.qsize()

    # ----- Worker -----

    async def _worker_loop(self) -> None:
        while self._running.is_set():
            try:
                task = await self._queue.get()
                await self._emit("tts_started", {"task": asdict(task)})
                async with self._lock:
                    out = self.tts.synthesize(
                        text=task.text,
                        file_name=task.file_name or task.task_id,
                        speaker=task.speaker,
                        language=task.language,
                    )
                await self._emit("tts_done", {"task": asdict(task), "path": str(out)})
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self._emit("tts_error", {"error": str(e)})
            finally:
                # allow loop to breathe
                await asyncio.sleep(0.01)


# ---------- CLI smoke test ----------

if __name__ == "__main__":
    async def _demo():
        async def _print_evt(evt: Dict):
            print(json.dumps(evt, indent=2))

        vp = VocalPlexus(notifier=_print_evt)
        await vp.start()
        await vp.enqueue("Hello from CALI. My vocal plexus is online.")
        await vp.enqueue("This is a queued message, rendered after the first.")
        # also immediate:
        path = await vp.say("Immediate test synthesis.")
        print("Immediate path:", path)
        # give the queue a moment
        await asyncio.sleep(2.0)
        await vp.stop()

    asyncio.run(_demo())
