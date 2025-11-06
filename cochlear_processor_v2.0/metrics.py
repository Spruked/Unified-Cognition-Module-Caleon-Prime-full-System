"""
metrics.py - Feature extraction for Cochlear Processor v2
Provides robust, pluggable functions for acoustic, spectral, and prosodic analysis.
"""
import numpy as np
import librosa

def extract_metrics(audio_frame: bytes, sr: int = 16000) -> dict:
    """
    Extract acoustic and spectral features from an audio frame.
    Returns a dict with features such as rms, zcr, spectral_centroid, etc.
    """
    # Convert bytes to numpy array (assume float32 PCM)
    audio = np.frombuffer(audio_frame, dtype=np.float32)
    if audio.size == 0:
        return {}
    features = {}
    features['rms'] = float(np.sqrt(np.mean(audio ** 2)))
    features['zcr'] = float(np.mean(librosa.feature.zero_crossing_rate(audio)))
    features['spectral_centroid'] = float(np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr)))
    features['spectral_bandwidth'] = float(np.mean(librosa.feature.spectral_bandwidth(y=audio, sr=sr)))
    features['spectral_flatness'] = float(np.mean(librosa.feature.spectral_flatness(y=audio)))
    features['spectral_rolloff'] = float(np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sr)))
    return features

def extract_prosody(audio_frame: bytes, sr: int = 16000) -> dict:
    """
    Extract prosodic (intonation, rhythm, stress) features from an audio frame.
    Returns a dict with features such as pitch, energy, tempo, etc.
    """
    audio = np.frombuffer(audio_frame, dtype=np.float32)
    if audio.size == 0:
        return {}
    prosody = {}
    pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
    prosody['pitch'] = float(np.max(pitches)) if np.any(pitches) else 0.0
    prosody['energy'] = float(np.mean(magnitudes))
    onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
    prosody['tempo'] = float(librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]) if onset_env.size > 0 else 0.0
    return prosody

def build_sensory_matrix(metrics: dict, prosody: dict) -> dict:
    """
    Combine metrics and prosody into a unified sensory matrix.
    """
    matrix = {}
    matrix.update(metrics)
    matrix.update(prosody)
    # For compatibility, add emotion and energy fields if not present
    matrix.setdefault('emotion', 'neutral')
    matrix.setdefault('energy', metrics.get('rms', 0.0))
    return matrix
