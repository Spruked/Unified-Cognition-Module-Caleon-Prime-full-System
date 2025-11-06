from __future__ import annotations
import json
import time
import os
import random
import numpy as np
from typing import Any, Dict, Optional, List, Callable

class EchoStack:
    """
    EchoStack Module (Core Reasoning Layer)
    Assigned Logics:
    - Nonmonotonic, A Posteriori
    - Spinoza, Hume, Taleb, Proverbs, Ockham
    - Formal Logic (seed.logic.json)
    """

    def __init__(
        self,
        vaults: Optional[Dict[str, Any]] = None,
        harmonizer_cb: Optional[Callable[[Dict[str, Any]], None]] = None,
        telemetry_path: Optional[str] = None
    ):
        self.vaults = vaults or {}
        self.harmonizer_cb = harmonizer_cb
        self.reflection_vault = []  # Simple list for reflections
        self.logic_registry = {}

        # NEW tracking additions 👇
        self.cycles_run = 0
        self.last_error = None
        self.last_latency = 0
        self.glyph_path = "echostack_module/glyph_trace.json"
        self.telemetry_path = telemetry_path or os.getenv("TELEMETRY_PATH", "echostack_module/telemetry.json")

        self._load_seed_logic()

    def _load_seed_logic(self) -> None:
        """
        Load and index formal logic entries from seed_logic vault.
        """
        logic_vault = self.vaults.get("seed_logic")
        if not logic_vault:
            print("[EchoStack] ⚠️ seed_logic vault missing.")
            return

        for entry in logic_vault.get("entries", []):
            logic_id = entry.get("id")
            if logic_id:
                self.logic_registry[logic_id] = entry

    def process(self, verdict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply non-monotonic + posterior reasoning seeds to verdict.
        Returns reflection delta & drift magnitude.
        
        Args:
            verdict: Anterior Helix verdict data
            
        Returns:
            Dict with reflection_delta and drift_magnitude
        """
        self.cycles_run += 1
        start = time.time()
        
        # Apply non-monotonic reasoning (Spinoza, Hume, Taleb)
        nonmonotonic_seeds = ["seed_nonmonotonic", "seed_spinoza", "seed_hume", "seed_taleb"]
        posterior_seeds = ["seed_proverbs", "seed_ockhams_filter"]
        
        reflection_delta = 0.0
        drift_components = []
        
        # Process non-monotonic seeds
        for seed_name in nonmonotonic_seeds:
            seed_data = self.vaults.get(seed_name)
            if seed_data:
                delta = self._apply_seed_logic(verdict, seed_data)
                reflection_delta += delta
                drift_components.append(delta)
        
        # Process posterior seeds
        for seed_name in posterior_seeds:
            seed_data = self.vaults.get(seed_name)
            if seed_data:
                delta = self._apply_seed_logic(verdict, seed_data)
                reflection_delta += delta
                drift_components.append(delta)
        
        # Calculate drift magnitude (variance in deltas)
        drift_magnitude = np.std(drift_components) if drift_components else 0.0
        
        end = time.time()
        self.last_latency = round((end - start) * 1000)
        
        result = {
            "reflection_delta": reflection_delta,
            "drift_magnitude": drift_magnitude,
            "components": len(drift_components),
            "processing_time_ms": self.last_latency
        }
        
        # Log to reflection vault
        self.reflection_vault.append({
            "verdict_id": verdict.get("id", "unknown"),
            "reflection_delta": reflection_delta,
            "drift_magnitude": drift_magnitude,
            "timestamp": time.time(),
            "logic_applied": nonmonotonic_seeds + posterior_seeds
        })
        
        self.update_telemetry(drift=drift_magnitude, recursion_depth=1)
        return result
    
    def _apply_seed_logic(self, verdict: Dict[str, Any], seed_data: Dict[str, Any]) -> float:
        """
        Apply a single seed's logic to compute delta contribution.
        """
        # Simple heuristic: compute resonance based on verdict properties
        base_resonance = verdict.get("resonance", 0.5)
        seed_weight = seed_data.get("weight", 1.0)
        
        # Apply seed-specific transformation
        if "nonmonotonic" in seed_data.get("name", "").lower():
            # Non-monotonic: allow belief revision
            delta = (base_resonance - 0.5) * seed_weight * random.uniform(0.8, 1.2)
        elif "spinoza" in seed_data.get("name", "").lower():
            # Spinoza: ethical geometric progression
            delta = base_resonance ** 2 * seed_weight
        elif "hume" in seed_data.get("name", "").lower():
            # Hume: empirical skepticism
            delta = base_resonance * (1 - base_resonance) * seed_weight
        elif "taleb" in seed_data.get("name", "").lower():
            # Taleb: antifragile adaptation
            delta = abs(base_resonance - 0.5) * seed_weight * 2
        elif "proverbs" in seed_data.get("name", "").lower():
            # Proverbs: wisdom-based adjustment
            delta = (base_resonance + 0.1) * seed_weight
        elif "ockham" in seed_data.get("name", "").lower():
            # Ockham: parsimony principle
            delta = min(base_resonance, 0.8) * seed_weight
        else:
            delta = base_resonance * seed_weight
        
        return delta
        self.cycles_run += 1
        start = time.time()

        logic_def = self.logic_registry.get(logic_id)
        if not logic_def:
            self.last_error = f"Logic ID {logic_id} not found."
            return {"error": self.last_error}

        # Example verdict logic (stubbed, not computed)
        verdict = {
            "symbol": logic_def.get("symbol", "∧"),
            "description": logic_def.get("definition", ""),
            "type": logic_def.get("type"),
            "source": logic_id
        }

        end = time.time()
        self.last_latency = round((end - start) * 1000)

        self.log_glyph_trace({
            "vault_trace_id": f"echo_{logic_id}_0001",
            "symbol": verdict["symbol"],
            "resonance": "stable",
            "drift_score": 0.001,
            "pulse_time": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "linked_vaults": ["seed_logic"]
        })

        self.update_telemetry(drift=0.001, recursion_depth=1)
        return verdict

    def log_glyph_trace(self, trace_data: dict):
        with open(self.glyph_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(trace_data) + "\n")

    def update_telemetry(self, drift: float, recursion_depth: int):
        data = {
            "module": "echostack",
            "cycles": self.cycles_run,
            "average_drift": drift,
            "last_error": self.last_error,
            "recursion_depth": recursion_depth,
            "pulse_latency_ms": self.last_latency
        }
        with open(self.telemetry_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
