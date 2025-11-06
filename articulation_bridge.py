# articulation_bridge.py
"""
Articulation Bridge – Gyro-Cortical → Phonatory Output

Receives a *harmonized verdict* from the Gyro-Cortical Harmonizer,
transforms it into a natural-language utterance, and hands it to the
configured phonatory output module.

Design goals
-------------
* Zero side-effects on the harmonizer – pure transformation.
* Thread-safe / async-ready.
* Pluggable speaker (TTS, mock, remote service, etc.).
* Full audit trail of what was spoken.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, asdict
from typing import Any, Callable, Dict, Optional, Protocol, TypedDict

# --------------------------------------------------------------------------- #
# Public contract expected from the phonatory output layer
# --------------------------------------------------------------------------- #
class Speaker(Protocol):
    """Minimal interface required from any phonatory module."""
    def speak(self, text: str, **kwargs: Any) -> None: ...

# --------------------------------------------------------------------------- #
# Harmonized verdict schema (strictly typed)
# --------------------------------------------------------------------------- #
class HarmonizedVerdict(TypedDict, total=False):
    final_verdict: str                     # required
    consensus: bool                        # required
    meta_reason: str                       # optional
    confidence: float                      # optional, 0.0-1.0

# --------------------------------------------------------------------------- #
# Internal immutable representation
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class _SpokenPhrase:
    text: str
    verdict: str
    consensus: bool
    confidence: Optional[float] = None

# --------------------------------------------------------------------------- #
# Bridge implementation
# --------------------------------------------------------------------------- #
class ArticulationBridge:
    """
    Direct articulation bridge.

    Parameters
    ----------
    speaker:
        Any object satisfying the ``Speaker`` protocol.
        Defaults to the legacy ``phonatory_output_module.speak`` function.
    logger:
        Optional ``logging.Logger`` – if omitted a module-level logger is used.
    voice_style:
        Free-form string passed through to the speaker (e.g. "calm", "excited").
    on_spoken:
        Optional callback ``(phrase: _SpokenPhrase) -> None`` for audit hooks.
    """

    def __init__(
        self,
        speaker: Speaker | None = None,
        *,
        logger: Optional[logging.Logger] = None,
        voice_style: str = "",
        on_spoken: Optional[Callable[[_SpokenPhrase], None]] = None,
    ) -> None:
        # ------------------------------------------------------------------- #
        # Resolve speaker
        # ------------------------------------------------------------------- #
        if speaker is None:
            # Legacy import – kept for backward compatibility
            try:
                from cerebral_cortex.phonatory_output_module import speak as _legacy_speak  # type: ignore
                speaker = _LegacyAdapter(_legacy_speak)  # type: ignore
            except ImportError:
                print("[ARTICULATION] Legacy phonatory module not available, using default speaker")
                speaker = None

        self._speaker: Speaker = speaker
        self._voice_style: str = voice_style
        self._on_spoken: Optional[Callable[[_SpokenPhrase], None]] = on_spoken
        self._log = logger or logging.getLogger(__name__)

        self.active: bool = True
        """Toggle to silence the bridge without re-instantiating."""

    # ------------------------------------------------------------------- #
    # Core public method
    # ------------------------------------------------------------------- #
    def articulate(self, harmonized_result: HarmonizedVerdict) -> Dict[str, Any]:
        """
        Convert a harmonized verdict into spoken language.

        Returns
        -------
        dict
            ``spoken`` – the exact text that was sent to the speaker (or ``None``).
            ``verdict`` – the final verdict string.
            ``consensus`` – whether the harmonizer reached full agreement.
            ``error`` – present only on validation / inactive-bridge failures.
        """
        if not self.active:
            return {"spoken": None, "error": "Bridge is inactive."}

        # ------------------------------------------------------------------- #
        # 1. Validate input (early-exit with clear error)
        # ------------------------------------------------------------------- #
        try:
            verdict = _ValidatedVerdict.from_dict(harmonized_result)
        except ValueError as exc:
            self._log.error("Invalid harmonized verdict: %s", exc)
            return {"spoken": None, "error": str(exc)}

        # ------------------------------------------------------------------- #
        # 2. Build natural phrase
        # ------------------------------------------------------------------- #
        phrase = self._build_phrase(verdict)

        # ------------------------------------------------------------------- #
        # 3. Emit via speaker
        # ------------------------------------------------------------------- #
        try:
            self._speaker.speak(phrase.text, style=self._voice_style)
        except Exception as exc:  # pragma: no cover – speaker-specific
            self._log.exception("Speaker failed")
            return {"spoken": None, "error": f"Speaker error: {exc}"}

        # ------------------------------------------------------------------- #
        # 4. Audit / callbacks
        # ------------------------------------------------------------------- #
        spoken = _SpokenPhrase(
            text=phrase.text,
            verdict=verdict.final_verdict,
            consensus=verdict.consensus,
            confidence=verdict.confidence,
        )
        self._log.info(
            "Articulated verdict=%s consensus=%s confidence=%s",
            verdict.final_verdict,
            verdict.consensus,
            verdict.confidence,
        )
        if self._on_spoken:
            try:
                self._on_spoken(spoken)
            except Exception as exc:  # pragma: no cover
                self._log.warning("on_spoken callback raised: %s", exc)

        # ------------------------------------------------------------------- #
        # 5. Return structured result
        # ------------------------------------------------------------------- #
        return {
            "spoken": spoken.text,
            "verdict": spoken.verdict,
            "consensus": spoken.consensus,
            "confidence": spoken.confidence,
        }

    # ------------------------------------------------------------------- #
    # Phrase construction – easy to override in subclasses
    # ------------------------------------------------------------------- #
    def _build_phrase(self, verdict: "_ValidatedVerdict") -> _SpokenPhrase:
        parts = [f"My harmonized verdict is {verdict.final_verdict}."]

        if not verdict.consensus:
            parts.append("There was conflict, so I deferred to caution.")

        if verdict.meta_reason:
            parts.append(f"My reasoning: {verdict.meta_reason}.")

        if verdict.confidence is not None:
            parts.append(f"Confidence level: {verdict.confidence:.2f}.")

        text = " ".join(parts)
        return _SpokenPhrase(
            text=text,
            verdict=verdict.final_verdict,
            consensus=verdict.consensus,
            confidence=verdict.confidence,
        )


# --------------------------------------------------------------------------- #
# Internal validation helper (keeps the public API clean)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class _ValidatedVerdict:
    final_verdict: str
    consensus: bool
    meta_reason: str = ""
    confidence: Optional[float] = None

    @classmethod
    def from_dict(cls, data: HarmonizedVerdict) -> "_ValidatedVerdict":
        missing = {"final_verdict", "consensus"} - data.keys()
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        conf = data.get("confidence")
        if conf is not None and not (0.0 <= conf <= 1.0):
            raise ValueError("confidence must be in [0.0, 1.0]")

        return cls(
            final_verdict=data["final_verdict"],
            consensus=data["consensus"],
            meta_reason=data.get("meta_reason", ""),
            confidence=conf,
        )


# --------------------------------------------------------------------------- #
# Legacy adapter – makes the old ``speak(text)`` function conform to Speaker
# --------------------------------------------------------------------------- #
class _LegacyAdapter:
    """Wraps the historic ``phonatory_output_module.speak`` function."""
    def __init__(self, legacy_func: Callable[[str], None]):
        self._func = legacy_func

    def speak(self, text: str, **kwargs: Any) -> None:
        # ``style`` is ignored for the legacy path – kept for API compatibility.
        self._func(text)


# --------------------------------------------------------------------------- #
# Example usage (when run as a script)
# --------------------------------------------------------------------------- #
if __name__ == "__main__":  # pragma: no cover
    logging.basicConfig(level=logging.INFO)

    bridge = ArticulationBridge()
    sample = {
        "final_verdict": "approved",
        "consensus": True,
        "meta_reason": "All subsystems aligned on ethical drift.",
        "confidence": 0.94,
    }
    print(bridge.articulate(sample))