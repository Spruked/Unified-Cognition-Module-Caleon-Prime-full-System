# glyph_encoder.py
"""
Glyph Encoder – symbolic context layer for Cochlear Processor v2
Tracks recent glyphs and produces short-term context hashes
for vault linking and associative recall.
"""

from hashlib import sha256

# Short-term context memory (ring buffer)
_CONTEXT_BUFFER: list[str] = []


def encode_glyph(emotion: str, energy: float) -> str:
    """
    Map emotion + energy into a symbolic glyph.
    Light mapping: extend later with vault-based glyph tables.
    """
    if emotion.lower() in ("anger", "fear"):
        return "⚡"
    if emotion.lower() in ("joy", "excitement"):
        return "🌞"
    if emotion.lower() in ("sadness", "fatigue"):
        return "💧"
    if energy < 0.3:
        return "💤"
    return "💠"  # neutral / balanced


def update_context(glyph_symbol: str):
    """Append the latest glyph and trim buffer to 50 entries."""
    _CONTEXT_BUFFER.append(glyph_symbol)
    if len(_CONTEXT_BUFFER) > 50:
        _CONTEXT_BUFFER.pop(0)


def get_context_hash(window: int = 10) -> str:
    """Return hash of the last N glyphs for relational indexing."""
    seq = "|".join(_CONTEXT_BUFFER[-window:])
    if not seq:
        return "0" * 16
    return sha256(seq.encode()).hexdigest()[:16]
