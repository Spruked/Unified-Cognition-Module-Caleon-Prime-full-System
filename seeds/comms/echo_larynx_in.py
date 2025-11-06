#!/usr/bin/env python3
"""
echo_larynx_in.py
Speech-to-Text (STT) input for CALI.

Features
- Local transcription (no external API).
- Prefers faster-whisper; falls back to openai-whisper.
- Simple mic recording → 16 kHz mono WAV.
- Clean, structured result usable by your WebSocket/UI.

Install (choose one engine)
  pip install faster-whisper sounddevice soundfile
  # or
  pip install openai-whisper sounddevice soundfile

CLI examples
  python comms/echo_larynx_in.py --record 5
  python comms/echo_larynx_in.py --file samples/test.wav --model-size small
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy as np

# Optional I/O deps (already in your venv per listing)
import sounddevice as sd
import soundfile as sf

# ---------- Backend resolution ----------

_BACKEND = None
_WHISPER_FASTER = None
_WHISPER_STD = None

try:
    from faster_whisper import WhisperModel as _FWModel  # type: ignore
    _WHISPER_FASTER = _FWModel
    _BACKEND = "faster-whisper"
except Exception:
    try:
        import whisper as _stdwhisper  # type: ignore
        _WHISPER_STD = _stdwhisper
        _BACKEND = "openai-whisper"
    except Exception:
        _BACKEND = None


# ---------- Data models ----------

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
    path: str
    segments: List[TranscriptSegment]


# ---------- Core class ----------

class EchoLarynxIn:
    """
    Local STT for CALI.

    Args:
        model_size: e.g., "base", "small", "medium", "large-v3".
        backend: "auto" | "faster-whisper" | "openai-whisper".
        device: "cpu" or "cuda" (if using GPU).
        compute_type: for faster-whisper, e.g., "int8", "int8_float16", "float16", "float32".
        out_dir: where to store recorded WAVs.
    """

    def __init__(
        self,
        model_size: str = "base",
        backend: str = "auto",
        device: str = "cpu",
        compute_type: str = "int8",
        out_dir: Union[str, Path] = "stt_in",
    ) -> None:
        if backend == "auto":
            backend = _BACKEND or "unavailable"

        if backend not in {"faster-whisper", "openai-whisper"}:
            raise ImportError(
                "No local STT backend available. Install one:\n"
                "  pip install faster-whisper sounddevice soundfile\n"
                "  # or\n"
                "  pip install openai-whisper sounddevice soundfile"
            )

        self.backend = backend
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

        if self.backend == "faster-whisper":
            if _WHISPER_FASTER is None:
                raise ImportError("faster-whisper not installed.")
            self.model = _WHISPER_FASTER(self.model_size, device=self.device, compute_type=self.compute_type)
        else:
            if _WHISPER_STD is None:
                raise ImportError("openai-whisper not installed.")
            self.model = _WHISPER_STD.load_model(self.model_size, device=self.device)

    # ---------- Recording ----------

    def record_wav(
        self,
        seconds: float = 5.0,
        samplerate: int = 16000,
        channels: int = 1,
        filename: Optional[str] = None,
    ) -> Path:
        """
        Record from default input device and save as 16 kHz mono WAV.
        """
        seconds = max(0.5, float(seconds))
        if channels not in (1, 2):
            channels = 1

        # Record float32, then write to WAV (soundfile will handle PCM)
        audio = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=channels, dtype="float32")
        sd.wait()

        if channels == 2:
            audio = np.mean(audio, axis=1, keepdims=True)

        audio = np.squeeze(audio)  # mono
        ts = int(time.time())
        name = filename or f"rec-{ts}.wav"
        out = (self.out_dir / name).resolve()
        sf.write(str(out), audio, samplerate, subtype="PCM_16")
        return out

    # ---------- Transcription ----------

    def transcribe_file(
        self,
        path: Union[str, Path],
        language: Optional[str] = None,
        beam_size: int = 1,
        vad_filter: bool = False,
    ) -> TranscriptResult:
        """
        Transcribe a WAV/MP3/etc file and return structured result.
        """
        path = str(Path(path).resolve())
        t0 = time.time()

        if self.backend == "faster-whisper":
            segments, info = self.model.transcribe(
                path,
                beam_size=beam_size,
                language=language,
                vad_filter=vad_filter,
            )
            segs: List[TranscriptSegment] = []
            full_text_parts: List[str] = []
            for s in segments:
                segs.append(TranscriptSegment(start=float(s.start), end=float(s.end), text=s.text.strip()))
                full_text_parts.append(s.text.strip())
            text = " ".join(x for x in full_text_parts if x)
            lang = getattr(info, "language", None)
        else:
            # openai-whisper path
            result = self.model.transcribe(path, language=language or None, verbose=False)
            text = (result.get("text") or "").strip()
            lang = result.get("language")
            segs = []
            for s in result.get("segments", []):
                segs.append(TranscriptSegment(start=float(s.get("start", 0.0)),
                                              end=float(s.get("end", 0.0)),
                                              text=str(s.get("text", "")).strip()))

        dt = time.time() - t0
        return TranscriptResult(
            text=text,
            language=lang,
            duration_s=dt,
            backend=self.backend,
            model=self.model_size,
            path=path,
            segments=segs,
        )

    # Convenience: record then transcribe in one call
    def listen_once(
        self,
        seconds: float = 5.0,
        language: Optional[str] = None,
        **kwargs,
    ) -> TranscriptResult:
        wav = self.record_wav(seconds=seconds)
        return self.transcribe_file(wav, language=language, **kwargs)


# ---------- CLI ----------

def _cli() -> None:
    p = argparse.ArgumentParser(description="CALI local STT (echo_larynx_in)")
    p.add_argument("--record", type=float, default=0.0, help="Record N seconds from mic, then transcribe.")
    p.add_argument("--file", type=str, help="Transcribe an existing audio file.")
    p.add_argument("--model-size", type=str, default="base", help="Whisper model size (e.g., base/small/medium/large-v3).")
    p.add_argument("--backend", type=str, default="auto", choices=["auto", "faster-whisper", "openai-whisper"])
    p.add_argument("--device", type=str, default="cpu", help="cpu or cuda")
    p.add_argument("--compute-type", type=str, default="int8", help="faster-whisper compute type (int8/float16/float32/...).")
    p.add_argument("--language", type=str, default=None, help="Force language code (e.g., en).")
    p.add_argument("--beam-size", type=int, default=1, help="Decoder beam size.")
    p.add_argument("--vad-filter", action="store_true", help="Enable VAD in faster-whisper.")
    p.add_argument("--json-out", action="store_true", help="Print JSON result.")

    args = p.parse_args()

    stt = EchoLarynxIn(
        model_size=args.model_size,
        backend=args.backend,
        device=args.device,
        compute_type=args.compute_type,
    )

    if args.record and args.record > 0:
        res = stt.listen_once(seconds=args.record, language=args.language, beam_size=args.beam_size, vad_filter=args.vad_filter)
    elif args.file:
        res = stt.transcribe_file(args.file, language=args.language, beam_size=args.beam_size, vad_filter=args.vad_filter)
    else:
        print("Nothing to do. Use --record N or --file PATH.", file=sys.stderr)
        sys.exit(2)

    if args.json_out:
        print(json.dumps(asdict(res), indent=2, ensure_ascii=False))
    else:
        print(f"[{res.backend}/{res.model}] {res.language} ({res.duration_s:.2f}s)\n{res.text}")

if __name__ == "__main__":
    _cli()
