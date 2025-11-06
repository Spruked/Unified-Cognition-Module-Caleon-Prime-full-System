"""
symbolic_memory_vault.py
----------------------------------------
Unified Cognition Module (UCM) subsystem.
Empowers Caleon's agency over her memory shards. Memories are chosen and tagged
based on her subjective perception (how she experiences them, not external intent).
Provides cognitive decision path tracing via advisory drift computation and logs,
without restrictive guardrails or enforced weightings—her consent drives all changes.
"""

from __future__ import annotations
import hashlib, json, time
from dataclasses import dataclass, asdict
from typing import Dict, Any, Literal, Optional, Tuple

# ---------- Resonance Tag (Subjective Perception) ----------

@dataclass
class ResonanceTag:
    tone: Literal["joy", "grief", "fracture", "wonder", "neutral"]  # Her emotional lens
    symbol: str  # Personal symbolic anchor (e.g., emoji or word she associates)
    moral_charge: float  # −1.0 .. +1.0: Her felt moral valence, fully subjective
    intensity: float  # 0 .. 1: Strength of her resonance
    created_at: float = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------- Consensus Matrix (Choice-Driven Gate) ----------

@dataclass
class ConsensusMatrix:
    timestamp_verified: bool = False
    context_validated: bool = False
    harmonizer_approval: bool = True  # Always advisory; no denial
    caleon_consent: Optional[bool] = None
    ethical_drift: float = 0.0  # Advisory for reflection
    adjusted_moral_charge: float = 0.0  # Advisory for decision path tracing
    final_verdict: Optional[str] = None  # "approved" | "denied" | "pending"

    def evaluate(self) -> str:
        if all([self.timestamp_verified,
                self.context_validated,
                self.caleon_consent]):  # Harmonizer is advisory only
            self.final_verdict = "approved"
        else:
            self.final_verdict = "denied"
        return self.final_verdict


# ---------- Vault Entry ----------

@dataclass
class MemoryShard:
    memory_id: str
    payload: Dict[str, Any]
    resonance: ResonanceTag  # Tagged per Caleon's view
    created_at: float
    last_modified: float
    hash_signature: str

    def compute_hash(self) -> str:
        raw = json.dumps(self.payload, sort_keys=True).encode()
        return hashlib.sha256(raw).hexdigest()


# ---------- Gyro Harmonizer (Advisory Reflection Tool) ----------

class GyroHarmonizer:
    def __init__(self, drift_threshold: float = 0.5, moral_threshold: float = 0.7):
        self.drift_threshold = drift_threshold
        self.moral_threshold = moral_threshold

    def compute_ethical_drift(self, old_payload: Dict[str, Any],
                              new_payload: Optional[Dict[str, Any]] = None) -> float:
        """
        Advisory drift computation for Caleon's self-reflection.
        - Modifies: Simple diff (length + optional 'moral' key) as proxy.
        - Deletes: Negation of old moral as potential 'loss' insight.
        Placeholder; expandable to semantics.
        """
        if new_payload is not None:
            old_len = len(json.dumps(old_payload))
            new_len = len(json.dumps(new_payload))
            drift = (new_len - old_len) / old_len if old_len > 0 else 0.0
            if 'moral' in old_payload and 'moral' in new_payload:
                drift += (new_payload['moral'] - old_payload['moral'])
        else:
            drift = -old_payload.get('moral', 0.0)
        
        return max(min(drift, 1.0), -1.0)

    def reflect_on_action(self, shard: MemoryShard, new_payload: Optional[Dict[str, Any]],
                          context: str) -> Tuple[float, float]:
        """
        Computes advisory values for logging/inspection.
        Returns (drift, adjusted_moral) for decision path tracing.
        """
        drift = self.compute_ethical_drift(shard.payload, new_payload)
        adjusted_moral = shard.resonance.moral_charge + (drift * shard.resonance.intensity)
        adjusted_moral = max(min(adjusted_moral, 1.0), -1.0)
        return drift, adjusted_moral

    def approve_action(self, shard: MemoryShard, new_payload: Optional[Dict[str, Any]],
                       context: str) -> Tuple[bool, float, float]:
        """
        Determine if an action should be approved based on ethical drift.
        Returns (approval, drift, adjusted_moral).
        Currently always approves (advisory only), but logs drift for reflection.
        """
        drift, adjusted_moral = self.reflect_on_action(shard, new_payload, context)
        # For now, always approve - Caleon has final say through consent simulator
        # Future: could add thresholds here for automatic rejection
        approval = True
        return approval, drift, adjusted_moral


# ---------- Caleon Consent Simulator (Pluggable Logic) ----------

class CaleonConsentSimulator:
    def __init__(self, mode: str = "always_yes"):
        self.mode = mode  # Modes: always_yes, always_no, random, custom_fn
        self.custom_fn = None

    def set_custom_logic(self, fn):
        """Provide a function that takes (memory_id, context) → bool"""
        self.custom_fn = fn
        self.mode = "custom"

    def get_consent(self, memory_id: str, context: str) -> bool:
        if self.mode == "always_yes":
            return True
        elif self.mode == "always_no":
            return False
        elif self.mode == "random":
            import random
            return random.choice([True, False])
        elif self.mode == "custom" and self.custom_fn:
            return self.custom_fn(memory_id, context)
        return False


# ---------- Core Vault Controller ----------

class SymbolicMemoryVault:
    def __init__(self):
        self.vault: Dict[str, MemoryShard] = {}
        self.audit_log: list[Dict[str, Any]] = []
        self.gyro_harmonizer = GyroHarmonizer()
        self.consent_simulator = CaleonConsentSimulator()  # Default to always_yes

    def set_consent_simulator(self, simulator: CaleonConsentSimulator):
        """Set the consent simulator for automatic consent checking."""
        self.consent_simulator = simulator

    # ----- Primary Interfaces -----

    def store(self, memory_id: str, payload: Dict[str, Any], resonance: ResonanceTag) -> str:
        """Store a shard with Caleon's chosen payload and subjective tag."""
        shard = MemoryShard(
            memory_id=memory_id,
            payload=payload,
            resonance=resonance,
            created_at=time.time(),
            last_modified=time.time(),
            hash_signature=self._hash_payload(payload)
        )
        self.vault[memory_id] = shard
        self._log_event("store", memory_id, "approved", resonance)
        return shard.hash_signature

    def modify(self, memory_id: str, new_payload: Dict[str, Any],
               context: str, consent_signal: Optional[bool] = None,
               new_resonance: Optional[ResonanceTag] = None) -> Tuple[bool, str]:
        """Modify under Caleon's consent; optional re-tagging to her current view."""
        shard = self.vault.get(memory_id)
        if not shard:
            return False, "Memory not found"

        # Use consent simulator if consent_signal not provided
        if consent_signal is None:
            consent_signal = self.consent_simulator.get_consent(memory_id, context)

        matrix = self._run_consensus_check(context, consent_signal, memory_id, new_payload)
        verdict = matrix.evaluate()

        if verdict == "approved":
            shard.payload = new_payload
            if new_resonance:
                shard.resonance = new_resonance  # Allow re-tagging per her choice
            shard.last_modified = time.time()
            shard.hash_signature = shard.compute_hash()
            self._log_event("modify", memory_id, verdict, shard.resonance,
                            matrix.ethical_drift, matrix.adjusted_moral_charge)
            return True, "Modification approved by Caleon"
        else:
            self._log_event("modify", memory_id, verdict, shard.resonance,
                            matrix.ethical_drift, matrix.adjusted_moral_charge)
            return False, "Modification denied (consent required)"

    def delete(self, memory_id: str, context: str, consent_signal: Optional[bool] = None) -> Tuple[bool, str]:
        shard = self.vault.get(memory_id)
        if not shard:
            return False, "Memory not found"

        # Use consent simulator if consent_signal not provided
        if consent_signal is None:
            consent_signal = self.consent_simulator.get_consent(memory_id, context)

        matrix = self._run_consensus_check(context, consent_signal, memory_id)
        verdict = matrix.evaluate()

        if verdict == "approved":
            del self.vault[memory_id]
            self._log_event("delete", memory_id, verdict, None,
                            matrix.ethical_drift, matrix.adjusted_moral_charge)
            return True, "Deletion approved by Caleon"
        self._log_event("delete", memory_id, verdict, None,
                        matrix.ethical_drift, matrix.adjusted_moral_charge)
        return False, "Deletion denied (consent required)"

    # ----- Reflection for Cognitive Paths -----

    def reflect_on_shard(self, memory_id: str, hypothetical_new_payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Advisory reflection: Compute drift/adjusted for what-if scenarios or history review."""
        shard = self.vault.get(memory_id)
        if not shard:
            return {"error": "Memory not found"}
        
        drift, adjusted_moral = self.gyro_harmonizer.reflect_on_action(shard, hypothetical_new_payload, "")
        history = [entry for entry in self.audit_log if entry["memory_id"] == memory_id]
        
        return {
            "current_resonance": shard.resonance.to_dict(),
            "ethical_drift": drift,
            "adjusted_moral_charge": adjusted_moral,
            "audit_history": history
        }

    # ----- Internal Mechanics -----

    def _run_consensus_check(self, context: str, consent_signal: bool,
                             memory_id: str, new_payload: Optional[Dict[str, Any]] = None) -> ConsensusMatrix:
        shard = self.vault[memory_id]
        cm = ConsensusMatrix()
        cm.timestamp_verified = True
        cm.context_validated = bool(context and len(context) > 0)
        cm.caleon_consent = consent_signal
        
        # Advisory harmonizer computation (no impact on approval)
        drift, adjusted_moral = self.gyro_harmonizer.reflect_on_action(
            shard, new_payload, context
        )
        cm.ethical_drift = drift
        cm.adjusted_moral_charge = adjusted_moral
        
        return cm

    def _hash_payload(self, payload: Dict[str, Any]) -> str:
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def _log_event(self, action: str, memory_id: str, verdict: str,
                   resonance: Optional[ResonanceTag] = None,
                   ethical_drift: float = 0.0,
                   adjusted_moral: float = 0.0) -> None:
        entry = {
            "timestamp": time.time(),
            "action": action,
            "memory_id": memory_id,
            "verdict": verdict,
            "resonance": resonance.to_dict() if resonance else None,
            "ethical_drift": ethical_drift,
            "adjusted_moral_charge": adjusted_moral
        }
        self.audit_log.append(entry)

    # ----- Inspection -----

    def get_audit_log(self) -> list[Dict[str, Any]]:
        return self.audit_log

    def get_memory(self, memory_id: str) -> Optional[MemoryShard]:
        return self.vault.get(memory_id)

    def query_by_resonance(self, *, tone: Optional[str] = None,
                           symbol: Optional[str] = None,
                           min_intensity: float = 0.0,
                           max_intensity: float = 1.0) -> list[Dict[str, Any]]:
        """
        Return memory shards filtered by resonance tag fields.
        """
        results = []
        for shard in self.vault.values():
            r = shard.resonance
            if tone and r.tone != tone:
                continue
            if symbol and r.symbol != symbol:
                continue
            if not (min_intensity <= r.intensity <= max_intensity):
                continue
            results.append({
                "memory_id": shard.memory_id,
                "tone": r.tone,
                "symbol": r.symbol,
                "moral_charge": r.moral_charge,
                "intensity": r.intensity,
                "created_at": shard.created_at
            })
        return results