"""
EchoRipple Module
Recursive verifier and challenger of EchoStack reflections using randomized logic cycles.
"""

import asyncio
import random
import time
import json
import os
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ReflectionObject:
    """Final stabilized reflection object"""
    delta: float
    magnitude: float
    stability_score: float
    cycles_completed: int
    final_consensus: str
    timestamp: float


class EchoRipple:
    """
    EchoRipple: Recursive verifier using randomized logic cycles (20ms spacing)
    Runs 5 cycles drawing from entire logic seed set including paradox filters.
    """
    
    def __init__(self, logic_seeds: Dict[str, Any] = None):
        self.logic_seeds = logic_seeds or {}
        self.cycles_run = 0
        self.reflection_history = []
        
    async def resonate(self, delta: Dict[str, Any]) -> ReflectionObject:
        """
        Run 5 randomized recursive logic cycles with 20ms spacing.
        Returns final stabilized reflection object.
        
        Args:
            delta: EchoStack delta data with reflection_delta and drift_magnitude
            
        Returns:
            ReflectionObject: Final stabilized reflection
        """
        reflection_delta = delta.get("reflection_delta", 0.0)
        drift_magnitude = delta.get("drift_magnitude", 0.0)
        
        cycle_results = []
        
        # Run 5 randomized cycles
        for cycle in range(5):
            self.cycles_run += 1
            
            # Select random logic seeds for this cycle
            available_seeds = list(self.logic_seeds.keys())
            if not available_seeds:
                # Fallback to basic logic if no seeds
                available_seeds = ["default_logic"]
                self.logic_seeds["default_logic"] = {"name": "default", "weight": 1.0}
            
            selected_seeds = random.sample(available_seeds, min(3, len(available_seeds)))
            
            # Run logic pass
            cycle_result = await self._run_logic_pass(reflection_delta, selected_seeds)
            cycle_results.append(cycle_result)
            
            # Update delta based on cycle result
            reflection_delta = cycle_result["adjusted_delta"]
            
            # 20ms delay between cycles
            await asyncio.sleep(0.02)  # 20ms
        
        # Compute final stabilization
        final_delta = sum(r["adjusted_delta"] for r in cycle_results) / len(cycle_results)
        stability_score = 1.0 - (drift_magnitude / max(abs(final_delta), 0.1))
        stability_score = max(0.0, min(1.0, stability_score))  # Clamp to [0,1]
        
        # Determine consensus
        consensus = self._determine_consensus(cycle_results)
        
        reflection_obj = ReflectionObject(
            delta=final_delta,
            magnitude=drift_magnitude,
            stability_score=stability_score,
            cycles_completed=len(cycle_results),
            final_consensus=consensus,
            timestamp=time.time()
        )
        
        # Log to history
        self.reflection_history.append({
            "reflection": reflection_obj,
            "cycle_results": cycle_results,
            "input_delta": delta
        })
        
        return reflection_obj
    
    async def _run_logic_pass(self, current_delta: float, selected_seeds: List[str]) -> Dict[str, Any]:
        """
        Execute a single logic pass with selected seeds.
        """
        adjustments = []
        
        for seed_name in selected_seeds:
            seed_data = self.logic_seeds.get(seed_name, {"weight": 1.0})
            weight = seed_data.get("weight", 1.0)
            
            # Apply seed-specific adjustment with some randomization
            adjustment = current_delta * weight * random.uniform(0.9, 1.1)
            
            # Add paradox filtering (prevent extreme values)
            if abs(adjustment) > 2.0:
                adjustment = adjustment * 0.5  # Dampen extremes
            
            adjustments.append(adjustment)
        
        # Average the adjustments
        adjusted_delta = sum(adjustments) / len(adjustments) if adjustments else current_delta
        
        return {
            "adjusted_delta": adjusted_delta,
            "seeds_used": selected_seeds,
            "adjustments": adjustments
        }
    
    def _determine_consensus(self, cycle_results: List[Dict[str, Any]]) -> str:
        """
        Determine final consensus from cycle results.
        """
        deltas = [r["adjusted_delta"] for r in cycle_results]
        avg_delta = sum(deltas) / len(deltas)
        
        if avg_delta > 0.5:
            return "positive_resonance"
        elif avg_delta < -0.5:
            return "negative_resonance"
        else:
            return "neutral_stability"
    
    def get_reflection_history(self) -> List[Dict[str, Any]]:
        """Get the history of all reflections processed."""
        return self.reflection_history.copy()