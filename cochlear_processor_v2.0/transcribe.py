# === Resonator-Ready Adapter ===
import hashlib
import numpy as np
import librosa
import json
import os
import importlib
from cochlear_vault import CochlearVault
# Timekeeper imports
from timekeeper.iss_timekeeper import ISSTimekeeper
from timekeeper.standard_timekeeper import StandardTimekeeper

def _timbre_fingerprint(timbre_vector):
    """Compress timbre vector to a short hash for fast broadcast."""
    if not timbre_vector:
        return "0" * 8
    # Convert to string, hash, and return first 8 hex digits
    s = ",".join(f"{x:.4f}" for x in timbre_vector)
    return hashlib.sha256(s.encode()).hexdigest()[:8]

def resonator_ready_adapter(audio_path: str) -> dict:
    """
    Wraps process_audio() and returns only the fields needed for Resonator input.
    Compresses timbre_vector to a short fingerprint.
    """
    percept = process_audio(audio_path)
    return {
        "symbol": percept["symbol"],
        "integrity_score": percept["integrity_score"],
        "lineage_tag": percept.get("lineage_tag", "cochlear_processor_v2.0"),
        "timbre_fp": _timbre_fingerprint(percept.get("timbre_vector", [])),
    }
"""
cochlear_processor_v2.0 - ProPrime Whisper Module 1.1

Symbolic cochlea + primary auditory cortex simulator.
Transforms sound into structured perceptual meaning with vault logging
and adaptive cognition.
"""


# Plug-and-play ASR backend selection
ASR_BACKEND = os.environ.get("ASR_BACKEND", "whisper")

if ASR_BACKEND == "whisper":
    from model_loader import load_model
    model = load_model()
    def asr_transcribe(audio_path):
        return model.transcribe(audio_path, word_timestamps=True)
else:
    # Try to import a custom backend as asr_backend.py
    try:
        asr_backend = importlib.import_module("asr_backend")
        def _asr_backend_transcribe(audio_path):
            return asr_backend.transcribe(audio_path)
        asr_transcribe = _asr_backend_transcribe
    except Exception as e:
        raise ImportError(f"No valid ASR backend found: {e}")


vault = CochlearVault()

# Load timekeeper config
with open("config_whisper.json", "r", encoding="utf-8") as f:
    _tk_config = json.load(f)
primary_timekeeper = ISSTimekeeper() if _tk_config.get("timekeeper", "ISS") == "ISS" else None
backup_timekeeper = StandardTimekeeper()


# === Fallback Transcription ===
def try_whisper_transcription(audio_path: str):
    """
    Attempt Whisper transcription with error fallback.
    """
    return asr_transcribe(audio_path)


# === Main Cochlear Processor ===
def process_audio(audio_path: str) -> dict:
    """
    Transforms audio into symbolic perceptual meaning.
    """
    try:
        result = try_whisper_transcription(audio_path)
        audio_data, sr = librosa.load(audio_path, sr=None)

        # Sensory features
        pitch = _extract_pitch(audio_data, sr)
        amplitude = _extract_amplitude(audio_data)
        timbre = _extract_timbre(audio_data, sr)
        timing = _extract_timing(result)
        integrity = _calculate_integrity(result, pitch, amplitude, timbre)

        # Adaptive cognition
        adaptive = vault.learn_from_history()
        if adaptive is not None:
            threshold = adaptive.get("learned_threshold", 0.7)
        else:
            threshold = 0.7

        # Timekeeper logic
        timecodes = None
        if primary_timekeeper:
            try:
                timecodes = primary_timekeeper.get_timecodes()
            except Exception:
                timecodes = None
        if not timecodes and backup_timekeeper:
            timecodes = backup_timekeeper.get_timecodes()

        # Build output dict
        output_dict = {
            "symbol": str(result['text']).strip(),
            "confidence": result.get('avg_logprob', 0.0),
            "segments": result.get('segments', []),  # full segment list with word-level info
            "language": result.get('language', 'unknown'),
            "pitch_hz": pitch,
            "amplitude_db": amplitude,
            "timbre_vector": timbre,
            "timbre_label": _label_timbre(np.mean(timbre)),
            "timing_segments": timing,
            "integrity_score": integrity,
            "adaptive_threshold": threshold,
            "lineage_tag": "cochlear_processor_v2.0::whisper::librosa::vault",
            "source": "cochlear_processor_v2.0",
            "timecodes": timecodes
        }

        # Store and return
        vault.store(output_dict)
        return output_dict

    except Exception as e:
        raise RuntimeError(f"[Cochlear Processor] Failed to process {audio_path}: {e}")


# === Internal Signal Extraction ===
def _extract_pitch(audio_data, sr):
    """Extract dominant pitch frequency from audio signal."""
    pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sr)
    if np.any(magnitudes > np.max(magnitudes) * 0.1):
        dominant_pitch = np.max(pitches[magnitudes > np.max(magnitudes) * 0.1])
        return float(dominant_pitch)
    return 0.0


def _extract_amplitude(audio_data):
    """Calculate average amplitude in dB scale."""
    rms = np.sqrt(np.mean(np.square(audio_data)))
    return float(20 * np.log10(rms + 1e-6))


def _extract_timbre(audio_data, sr):
    """Extract timbre characteristics via spectral flatness."""
    spectral_flatness = librosa.feature.spectral_flatness(y=audio_data)
    return spectral_flatness.mean(axis=1).tolist()


def _extract_timing(result):
    """Extract segment timing from Whisper result."""
    segments = result.get("segments", [])
    return [(seg["start"], seg["end"]) for seg in segments if "start" in seg and "end" in seg]


def _calculate_integrity(result, pitch, amplitude, timbre):
    """Compute integrity score as trust metric."""


def _label_timbre(flatness_value):
    """Assign symbolic label to timbre."""
    if flatness_value < 0.2:
        return "harmonic"
    elif flatness_value < 0.5:
        return "balanced"
    else:
        return "noisy"


# === Legacy Compatibility ===
def transcribe_audio(audio_path: str) -> str:
    """Legacy interface: return only text."""
    return process_audio(audio_path)["symbol"]


# === Symbolic Summary ===
def interpret_signal(signal: dict) -> str:
    """
    Interpret symbolic payload into human-readable summary.
    Uses adaptive threshold for trust check.
    """
    status = "✅" if signal["integrity_score"] > signal.get("adaptive_threshold", 0.7) else "⚠️"
    lang = signal["language"]
    pitch = signal["pitch_hz"]
    tone = "high" if pitch > 300 else "low"

    return (
        f"{status} [{lang}] '{signal['symbol']}' | "
        f"Pitch: {tone} ({pitch:.1f} Hz), "
        f"Volume: {signal['amplitude_db']:.1f} dB, "
        f"Timbre: {signal['timbre_label']}, "
        f"Trust: {signal['integrity_score']:.2f}"
    )