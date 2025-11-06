#!/usr/bin/env python3
"""
whisper_interface.py
Unified Speech-to-Text for CALI.

Backends (auto-detected, in order):
  1) OpenAI API  (env OPENAI_API_KEY; model via OPENAI_TRANSCRIBE_MODEL, default "whisper-1")
  2) faster-whisper  (local)
  3) openai-whisper  (local)

Install notes (pick one local engine if not using API):
  pip install faster-whisper sounddevice soundfile
  # or
  pip install openai-whisper sounddevice soundfile
  # For OpenAI API:
  pip install openai>=1.0.0

API:
  wi = WhisperInterface()
  res = wi.transcribe_file("sample.wav")
  print(res.text)
"""

from __future__ import annotations

import io
import os
import time
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Tuple, Union

# Optional mic I/O (only if you use record_and_transcribe)
try:
    import sounddevice as sd
    import soundfile as sf
except Exception:
    sd = None
    sf = None

# ---------- Data Models ----------

@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str

@dataclass
class TranscriptResult:
    text: str
    language: Optional[str]
    duration_s: float
    backend: str
    model: str
    path: Optional[str]
    segments: List[TranscriptSegment]


# ---------- Backend detection ----------

def _has_openai() -> bool:
    try:
        import openai  # noqa: F401
        return bool(os.getenv("OPENAI_API_KEY"))
    except Exception:
        return False

def _has_faster_whisper() -> bool:
    try:
        import faster_whisper  # noqa: F401
        return True
    except Exception:
        return False

def _has_openai_whisper() -> bool:
    try:
        import whisper  # noqa: F401
        return True
    except Exception:
        return False


# ---------- Core Interface ----------

class WhisperInterface:
    """
    Unified STT wrapper. Chooses a backend unless explicitly specified.

    Args:
      backend: "auto" | "openai" | "faster-whisper" | "openai-whisper"
      model_size: local model size (base/small/medium/large-v3)
      openai_model: server model name (default: env OPENAI_TRANSCRIBE_MODEL or "whisper-1")
      device: "cpu" | "cuda" for local backends
      compute_type: faster-whisper compute type (e.g., "int8", "float16", "float32")
      verbose_json: try to return segments when supported
    """

    def __init__(
        self,
        backend: str = "auto",
        model_size: str = "base",
        openai_model: Optional[str] = None,
        device: str = "cpu",
        compute_type: str = "int8",
        verbose_json: bool = True,
    ) -> None:
        if backend == "auto":
            backend = self._auto_pick()
        self.backend = backend

        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.verbose_json = verbose_json
        self.openai_model = openai_model or os.getenv("OPENAI_TRANSCRIBE_MODEL", "whisper-1")

        # Lazy init members
        self._fw_model = None
        self._ow_model = None
        self._openai_client = None

        if self.backend == "openai":
            self._init_openai()
        elif self.backend == "faster-whisper":
            self._init_faster()
        elif self.backend == "openai-whisper":
            self._init_openai_whisper()
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    # ----- Backend initializers -----

    def _auto_pick(self) -> str:
        if _has_openai():
            return "openai"
        if _has_faster_whisper():
            return "faster-whisper"
        if _has_openai_whisper():
            return "openai-whisper"
        raise ImportError(
            "No STT backend available. Options:\n"
            "  • Set OPENAI_API_KEY for OpenAI API (pip install openai)\n"
            "  • pip install faster-whisper sounddevice soundfile\n"
            "  • or pip install openai-whisper sounddevice soundfile"
        )

    def _init_openai(self) -> None:
        try:
            from openai import OpenAI  # new SDK
            self._openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except Exception as e:
            raise ImportError("OpenAI SDK not installed or OPENAI_API_KEY not set.") from e

    def _init_faster(self) -> None:
        try:
            from faster_whisper import WhisperModel
            self._fw_model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        except Exception as e:
            raise ImportError("faster-whisper is not available.") from e

    def _init_openai_whisper(self) -> None:
        try:
            import whisper
            self._ow_model = whisper.load_model(self.model_size, device=self.device)
        except Exception as e:
            raise ImportError("openai-whisper is not available.") from e

    # ----- Public API -----

    def transcribe_file(
        self,
        path: Union[str, Path],
        language: Optional[str] = None,
        beam_size: int = 1,
        vad_filter: bool = False,
    ) -> TranscriptResult:
        path = str(Path(path).resolve())
        t0 = time.time()
        if self.backend == "openai":
            text, lang, segs = self._openai_transcribe_path(path, language)
        elif self.backend == "faster-whisper":
            text, lang, segs = self._faster_transcribe_path(path, language, beam_size, vad_filter)
        else:
            text, lang, segs = self._ow_transcribe_path(path, language)
        dt = time.time() - t0
        return TranscriptResult(
            text=text or "",
            language=lang,
            duration_s=dt,
            backend=self.backend,
            model=self.openai_model if self.backend == "openai" else self.model_size,
            path=path,
            segments=segs,
        )

    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: Optional[str] = None,
    ) -> TranscriptResult:
        t0 = time.time()
        if self.backend == "openai":
            text, lang, segs = self._openai_transcribe_bytes(audio_bytes, filename, language)
            dt = time.time() - t0
            return TranscriptResult(
                text=text or "",
                language=lang,
                duration_s=dt,
                backend=self.backend,
                model=self.openai_model,
                path=None,
                segments=segs,
            )
        # Local backends need a file; use a temp
        tmp = Path(filename).with_suffix(".tmp.wav")
        tmp.write_bytes(audio_bytes)
        try:
            return self.transcribe_file(tmp, language=language)
        finally:
            try:
                tmp.unlink(missing_ok=True)  # type: ignore[arg-type]
            except Exception:
                pass

    def record_and_transcribe(
        self,
        seconds: float = 5.0,
        samplerate: int = 16000,
        channels: int = 1,
        language: Optional[str] = None,
    ) -> TranscriptResult:
        if sd is None or sf is None:
            raise RuntimeError("sounddevice/soundfile not installed. Install to use recording.")
        seconds = max(0.5, float(seconds))
        audio = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=max(1, channels), dtype="float32")
        sd.wait()
        if channels == 2:
            import numpy as np
            audio = np.mean(audio, axis=1, keepdims=True)
        audio = audio.squeeze()
        buf = io.BytesIO()
        sf.write(buf, audio, samplerate, format="WAV", subtype="PCM_16")
        return self.transcribe_bytes(buf.getvalue(), filename="rec.wav", language=language)

    # ----- Backend workers -----

    # OpenAI (new SDK)
    def _openai_transcribe_path(self, path: str, language: Optional[str]) -> Tuple[str, Optional[str], List[TranscriptSegment]]:
        client = self._openai_client
        segs: List[TranscriptSegment] = []
        text, lang = "", None
        with open(path, "rb") as f:
            try:
                resp = client.audio.transcriptions.create(
                    model=self.openai_model,
                    file=f,
                    response_format="verbose_json" if self.verbose_json else "json",
                    language=language,
                )
                # resp may be a pydantic-like object or dict
                data = resp if isinstance(resp, dict) else resp.__dict__
                # Some SDKs wrap in 'text' or in 'segments' structure
                text = getattr(resp, "text", None) or data.get("text") or ""
                if self.verbose_json:
                    raw_segs = getattr(resp, "segments", None) or data.get("segments") or []
                    for s in raw_segs:
                        segs.append(TranscriptSegment(
                            start=float(getattr(s, "start", s.get("start", 0.0))),
                            end=float(getattr(s, "end", s.get("end", 0.0))),
                            text=str(getattr(s, "text", s.get("text", ""))).strip(),
                        ))
                lang = getattr(resp, "language", None) or data.get("language")
            except Exception:
                # Fallback: try plain text response without segments
                f.seek(0)
                resp = client.audio.transcriptions.create(model=self.openai_model, file=f)
                text = getattr(resp, "text", None) or getattr(resp, "text", "") or ""
                lang = getattr(resp, "language", None)
        return text, lang, segs

    def _openai_transcribe_bytes(self, audio_bytes: bytes, filename: str, language: Optional[str]) -> Tuple[str, Optional[str], List[TranscriptSegment]]:
        client = self._openai_client
        segs: List[TranscriptSegment] = []
        text, lang = "", None
        f = io.BytesIO(audio_bytes)
        f.name = filename  # OpenAI SDK expects a filename on the file-like object
        try:
            resp = client.audio.transcriptions.create(
                model=self.openai_model,
                file=f,
                response_format="verbose_json" if self.verbose_json else "json",
                language=language,
            )
            data = resp if isinstance(resp, dict) else resp.__dict__
            text = getattr(resp, "text", None) or data.get("text") or ""
            if self.verbose_json:
                raw_segs = getattr(resp, "segments", None) or data.get("segments") or []
                for s in raw_segs:
                    segs.append(TranscriptSegment(
                        start=float(getattr(s, "start", s.get("start", 0.0))),
                        end=float(getattr(s, "end", s.get("end", 0.0))),
                        text=str(getattr(s, "text", s.get("text", ""))).strip(),
                    ))
            lang = getattr(resp, "language", None) or data.get("language")
        except Exception:
            f.seek(0)
            resp = client.audio.transcriptions.create(model=self.openai_model, file=f)
            text = getattr(resp, "text", None) or ""
            lang = getattr(resp, "language", None)
        return text, lang, segs

    # faster-whisper
    def _faster_transcribe_path(self, path: str, language: Optional[str], beam_size: int, vad_filter: bool) -> Tuple[str, Optional[str], List[TranscriptSegment]]:
        from faster_whisper import WhisperModel
        if self._fw_model is None:
            self._fw_model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        segments, info = self._fw_model.transcribe(path, beam_size=beam_size, language=language, vad_filter=vad_filter)
        segs: List[TranscriptSegment] = []
        parts: List[str] = []
        for s in segments:
            segs.append(TranscriptSegment(start=float(s.start), end=float(s.end), text=s.text.strip()))
            if s.text.strip():
                parts.append(s.text.strip())
        return " ".join(parts), getattr(info, "language", None), segs

    # openai-whisper (local)
    def _ow_transcribe_path(self, path: str, language: Optional[str]) -> Tuple[str, Optional[str], List[TranscriptSegment]]:
        import whisper
        if self._ow_model is None:
            self._ow_model = whisper.load_model(self.model_size, device=self.device)
        result = self._ow_model.transcribe(path, language=language or None, verbose=False)
        text = (result.get("text") or "").strip()
        lang = result.get("language")
        segs: List[TranscriptSegment] = []
        for s in result.get("segments", []):
            segs.append(TranscriptSegment(
                start=float(s.get("start", 0.0)),
                end=float(s.get("end", 0.0)),
                text=str(s.get("text", "")).strip()
            ))
        return text, lang, segs


# ---------- CLI smoke test ----------

if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="CALI Whisper Interface (unified STT)")
    p.add_argument("--file", type=str, help="Audio path to transcribe")
    p.add_argument("--backend", type=str, default="auto", choices=["auto", "openai", "faster-whisper", "openai-whisper"])
    p.add_argument("--model-size", type=str, default="base")
    p.add_argument("--openai-model", type=str, default=None, help="Server model name, e.g., 'whisper-1'")
    p.add_argument("--device", type=str, default="cpu")
    p.add_argument("--compute-type", type=str, default="int8")
    p.add_argument("--language", type=str, default=None)
    p.add_argument("--json", action="store_true", help="Print JSON result")
    args = p.parse_args()

    wi = WhisperInterface(
        backend=args.backend,
        model_size=args.model_size,
        openai_model=args.openai_model,
        device=args.device,
        compute_type=args.compute_type,
    )

    if args.file:
        res = wi.transcribe_file(args.file, language=args.language)
    elif sd and sf:
        print("No --file provided; recording 5s from mic…")
        res = wi.record_and_transcribe(seconds=5.0, language=args.language)
    else:
        raise SystemExit("Provide --file or install sounddevice/soundfile for recording.")

    print(json.dumps(asdict(res), indent=2, ensure_ascii=False) if args.json else res.text)
