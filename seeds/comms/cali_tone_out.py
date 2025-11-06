#!/usr/bin/env python3
"""
cali_tone_out.py
Text-to-Speech output for CALI using Coqui TTS.

• Default model: 'tts_models/en/ljspeech/tacotron2-DDC' (single-speaker).
• Supports multi-speaker models via `speaker` param (e.g., VCTK).
• Produces 16-bit PCM WAV files in an output directory (default: ./tts_out).
"""

from __future__ import annotations
from pathlib import Path
from typing import Iterable, List, Optional, Union
import re
import time

# --- External dependency (Coqui TTS) ---
try:
    from TTS.api import TTS
except Exception as e:  # pragma: no cover
    raise ImportError(
        "Coqui TTS not installed. Add `TTS==0.22.0` (or compatible) to requirements "
        "and `pip install -r requirements.txt`."
    ) from e


def _safe_filename(name: str) -> str:
    """Make a filesystem-safe base filename."""
    base = re.sub(r"[^\w\-]+", "-", name.strip().lower())
    base = re.sub(r"-{2,}", "-", base).strip("-")
    return base or f"utt-{int(time.time())}"


class CaliToneOut:
    """
    High-level TTS wrapper.

    Args:
        model_name: Coqui model id. Single speaker default is robust on CPU.
        output_dir: Directory for rendered WAV files.
        gpu: Set True if CUDA is available and desired.
        progress_bar: Disable for cleaner logs.
    """

    def __init__(
        self,
        model_name: str = "tts_models/en/ljspeech/tacotron2-DDC",
        output_dir: Union[str, Path] = "tts_out",
        gpu: bool = False,
        progress_bar: bool = False,
    ) -> None:
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Coqui TTS initialization
        self.tts = TTS(model_name=self.model_name, progress_bar=progress_bar, gpu=gpu)

        # Introspect model capabilities
        # Note: Not all TTS models expose speaker/language; guard accordingly.
        self.is_multi_speaker = getattr(self.tts, "is_multi_speaker", False)
        self.is_multi_lingual = getattr(self.tts, "is_multi_lingual", False)

    # ---------- Public API ----------

    def synthesize(
        self,
        text: str,
        file_name: Optional[str] = None,
        speaker: Optional[str] = None,
        language: Optional[str] = None,
    ) -> Path:
        """
        Render `text` to a WAV file and return the path.

        • `speaker` only applies to multi-speaker models (e.g., VCTK).
        • `language` only applies to multilingual models.

        Raises:
            ValueError: if text is empty or whitespace.
        """
        if not text or not text.strip():
            raise ValueError("cali_tone_out.synthesize: text cannot be empty.")

        base = _safe_filename(file_name or text[:60])
        out_path = (self.output_dir / f"{base}.wav").resolve()

        kwargs = {"text": text, "file_path": str(out_path)}
        if self.is_multi_speaker and speaker:
            kwargs["speaker"] = speaker
        if self.is_multi_lingual and language:
            kwargs["language"] = language

        # Coqui API
        self.tts.tts_to_file(**kwargs)
        return out_path

    def synthesize_batch(
        self,
        texts: Iterable[str],
        prefix: str = "utt",
        speaker: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[Path]:
        """
        Render a batch of texts. Returns list of output Paths in order.
        Empty/blank strings are skipped.
        """
        paths: List[Path] = []
        for idx, t in enumerate(texts, start=1):
            if not t or not t.strip():
                continue
            name = f"{prefix}-{idx:04d}"
            paths.append(self.synthesize(t, file_name=name, speaker=speaker, language=language))
        return paths

    @staticmethod
    def list_models() -> List[str]:
        """List available Coqui TTS model identifiers."""
        try:
            return TTS.list_models()
        except Exception:
            return []

    # ---------- Convenience CLI ----------

if __name__ == "__main__":
    # Minimal CLI: `python comms/cali_tone_out.py "Hello world"`
    import sys
    text = " ".join(sys.argv[1:]).strip() or "Hello from CALI."
    tts = CaliToneOut()
    out = tts.synthesize(text)
    print(str(out))
