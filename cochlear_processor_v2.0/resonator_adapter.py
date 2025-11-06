import hashlib
import numpy as np
from transcribe import process_audio
import os
import requests

def _timbre_fingerprint(timbre_vector: list) -> str:
    """
    Compress timbre vector into a stable hash fingerprint.
    Uses SHA1 over rounded values for lightweight broadcast.
    """
    if not timbre_vector:
        return "empty"
    arr = np.array(timbre_vector, dtype=float)
    rounded = np.round(arr, 4).astype(str)
    joined = ",".join(rounded)
    return hashlib.sha1(joined.encode("utf-8")).hexdigest()[:12]  # short hash


def cochlear_to_resonator(audio_path: str) -> dict:
    """
    Adapter: Converts Cochlear Processor output into Resonator-ready format.
    Includes all Whisper semantic output (segments, language, etc.).
    """
    signal = process_audio(audio_path)

    resonator_input = {
        "symbol": signal["symbol"],                 # primary percept (transcribed speech)
        "confidence": signal["confidence"],         # whisper certainty
        "integrity": signal["integrity_score"],     # trustworthiness
        "threshold": signal["adaptive_threshold"],  # adaptive cutoff
        "lineage": signal["lineage_tag"],           # provenance
        "timbre": signal["timbre_label"],           # categorical sound type
        "timbre_fp": _timbre_fingerprint(signal.get("timbre_vector", [])),  # compressed hash
        "segments": signal.get("segments", []),      # full Whisper segments
        "language": signal.get("language", "unknown")
    }

    return resonator_input

class ResonatorAdapter:
    """
    Plug-and-play adapter for routing output to core/cortex modules.
    Extend or replace this class for custom output handling.
    """
    def __init__(self, endpoint=None):
        self.endpoint = endpoint or os.environ.get("CORE_ENDPOINT_URL", "http://core_endpoint:8088/sensory")

    def send(self, data: dict):
        # Default: HTTP POST to core/cortex endpoint
        try:
            resp = requests.post(self.endpoint, json=data, timeout=2)
            resp.raise_for_status()
            print(f"[ResonatorAdapter] Sent to {self.endpoint} (status {resp.status_code})")
        except Exception as e:
            print(f"[ResonatorAdapter] Failed to send: {e}")
