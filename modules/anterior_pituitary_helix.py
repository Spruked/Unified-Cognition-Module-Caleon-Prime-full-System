# anterior_pituitary_helix.py
from __future__ import annotations
import math, json, random
from typing import Any, Dict, List, Optional, Callable, Set
from datetime import datetime
import uuid

try:
    from posterior_pituitary_helix import PosteriorPituitaryHelix
except ImportError:
    PosteriorPituitaryHelix = None  # type: ignore

HarmonizerCb = Callable[[Dict[str, Any]], None]

class AnteriorPituitaryHelix:
    """
    2(a) Anterior Pituitary Helix - Primary reasoning strand
    
    Assigned Logic:
    • Kantian (categorical imperatives, duty ethics)
    • Locke (empirical association, tabula rasa learning)  
    • Monotonic (consistent, non-revising reasoning)
    • Gladwell (thin-slicing, rapid cognition)
    • A priori reasoning (not vault - inherent rational principles)
    • Reflection vault pinging for historical decision matching (speed optimization)
    """

    epigenetic_memory: Dict[str, Dict[str, Any]]
    helix_main: List[Dict[str, Any]]
    transcendental_mapper: TranscendentalMapper
    noumenal_drift: List[str]
    last_exports: Dict[str, Any]
    mirror: Optional[Any]
    harmonizer_cb: Optional[HarmonizerCb]
    json_mix_count: int
    vaults: Dict[str, Any]
    reflection_vault: Dict[str, Any]  # NEW: For historical decision matching
    gladwell_thin_slices: Dict[str, List[float]]  # NEW: Rapid pattern recognition cache

    def __init__(
        self,
        *,
        turn_length: int = 10,
        bond_threshold: float = 0.40,
        base_reiterations: int = 5,
        conflict_reiterations: int = 10,
        harmonizer_cb: Optional[HarmonizerCb] = None,
        random_seed: Optional[int] = None,
        json_mix_count: int = 4,
        vaults: Optional[Dict[str, Any]] = None,
        reflection_vault_path: str = "anterior_reflection_vault.json"  # NEW
    ) -> None:
        # Memory & state
        self.epigenetic_memory: Dict[str, Dict[str, Any]] = {}
        self.helix_main: List[Dict[str, Any]] = []
        self.transcendental_mapper = TranscendentalMapper()
        self.noumenal_drift: List[str] = []
        self.last_exports: Dict[str, Any] = {}
        self.gladwell_thin_slices = {}  # NEW: Pattern cache for rapid cognition
        self.reflection_vault_path = reflection_vault_path
        self.reflection_vault = self._load_reflection_vault()

        # Randomization
        if random_seed is not None:
            random.seed(int(random_seed))

        # Posterior (trailing strand)
        self.mirror: Optional[Any] = None
        if PosteriorPituitaryHelix is not None:
            self.mirror = PosteriorPituitaryHelix(
                store_cb=self._store_epigenetic_memory_bridge,
                harmonizer_cb=self._escalate_via_harmonizer,
                turn_length=turn_length,
                bond_threshold=bond_threshold,
                base_reiterations=base_reiterations,
                conflict_reiterations=conflict_reiterations,
            )

        # External harmonizer route
        self.harmonizer_cb = harmonizer_cb

        # VAULT registry
        self.json_mix_count = int(json_mix_count)
        self.vaults: Dict[str, Any] = vaults or {}

    # ---------- NEW: Reflection Vault for Speed Optimization ----------
    
    def _load_reflection_vault(self) -> Dict[str, Any]:
        """Load historical decisions for rapid pattern matching"""
        try:
            import pathlib
            path = pathlib.Path(self.reflection_vault_path)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    vault = json.load(f)
                    print(f"✅ Loaded reflection vault with {len(vault.get('decisions', []))} historical decisions")
                    return vault
        except Exception as e:
            print(f"⚠️ Could not load reflection vault: {e}")
        return {"decisions": [], "patterns": [], "loaded_at": datetime.now().isoformat()}

    def _save_reflection_vault(self):
        """Save current state to reflection vault"""
        try:
            with open(self.reflection_vault_path, 'w', encoding='utf-8') as f:
                json.dump(self.reflection_vault, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Could not save reflection vault: {e}")

    def _ping_reflection_vault(self, inputs: Dict[str, Any], potential_actions: List[str]) -> Dict[str, Any]:
        """
        NEW: Rapid historical decision matching for speed optimization
        Returns matched decisions and confidence scores
        """
        matches = []
        current_pattern = self._extract_pattern_signature(inputs)
        
        for decision in self.reflection_vault.get("decisions", [])[-100:]:  # Recent decisions
            similarity = self._pattern_similarity(current_pattern, decision.get("pattern", {}))
            if similarity > 0.7:  # High similarity threshold
                matches.append({
                    "decision_id": decision.get("id"),
                    "similarity": similarity,
                    "previous_actions": decision.get("executed_actions", []),
                    "outcome_score": decision.get("outcome_score", 0.5),
                    "timestamp": decision.get("timestamp")
                })
        
        # Sort by similarity and recency
        matches.sort(key=lambda x: (x["similarity"], x.get("timestamp", "")), reverse=True)
        
        return {
            "matches": matches[:3],  # Top 3 matches
            "pattern_signature": current_pattern,
            "suggested_actions": [m["previous_actions"] for m in matches[:2] if m["previous_actions"]],
            "confidence": matches[0]["similarity"] if matches else 0.0
        }

    def _extract_pattern_signature(self, inputs: Dict[str, Any]) -> Dict[str, float]:
        """Extract numerical pattern signature for rapid matching"""
        signature = {}
        for key, value in inputs.items():
            if isinstance(value, (int, float)):
                signature[key] = float(value)
            elif isinstance(value, str):
                # Simple hash-based numerical representation
                signature[f"{key}_hash"] = float(hash(value) % 1000) / 1000.0
            elif isinstance(value, bool):
                signature[key] = 1.0 if value else 0.0
        return signature

    def _pattern_similarity(self, pattern1: Dict[str, float], pattern2: Dict[str, float]) -> float:
        """Calculate similarity between two pattern signatures"""
        common_keys = set(pattern1.keys()) & set(pattern2.keys())
        if not common_keys:
            return 0.0
        
        differences = [abs(pattern1[k] - pattern2[k]) for k in common_keys]
        avg_difference = sum(differences) / len(differences)
        return max(0.0, 1.0 - avg_difference)

    # ---------- NEW: Gladwell Thin-Slicing Logic ----------

    def _gladwell_thin_slice(self, inputs: Dict[str, Any], potential_actions: List[str]) -> List[str]:
        """
        Malcolm Gladwell-style rapid cognition: quick pattern recognition
        based on limited information (thin-slicing)
        """
        # Update pattern cache
        pattern_key = str(sorted(inputs.keys()))
        if pattern_key not in self.gladwell_thin_slices:
            self.gladwell_thin_slices[pattern_key] = []
        
        # Calculate rapid assessment score
        rapid_scores = {}
        for action in potential_actions:
            # Simple heuristic: actions that worked recently get higher priority
            recent_success = self._calculate_recent_success(action)
            input_alignment = self._calculate_input_alignment(action, inputs)
            rapid_scores[action] = (recent_success + input_alignment) / 2.0
        
        # Return actions sorted by rapid assessment
        return sorted(potential_actions, key=lambda a: rapid_scores.get(a, 0), reverse=True)

    def _calculate_recent_success(self, action: str) -> float:
        """Calculate how successful this action has been recently"""
        if action not in self.epigenetic_memory:
            return 0.5  # Neutral for unknown actions
        
        memory = self.epigenetic_memory[action]
        if memory["count"] == 0:
            return 0.5
        
        # Simple heuristic: more executions = more success (for rapid assessment)
        return min(1.0, memory["count"] / 10.0)

    def _calculate_input_alignment(self, action: str, inputs: Dict[str, Any]) -> float:
        """Rapid assessment of how well action aligns with current inputs"""
        action_lower = action.lower()
        input_str = str(inputs).lower()
        
        # Simple keyword matching for rapid assessment
        positive_indicators = ["seek", "pleasure", "explore", "approach"]
        negative_indicators = ["avoid", "pain", "withdraw", "danger"]
        
        score = 0.5  # Neutral baseline
        
        if any(indicator in action_lower for indicator in positive_indicators):
            if inputs.get("desire", 0) > 0.5 or inputs.get("curiosity", 0) > 0.5:
                score += 0.3
        elif any(indicator in action_lower for indicator in negative_indicators):
            if inputs.get("danger", 0) > 0.5 or inputs.get("fear", 0) > 0.5:
                score += 0.3
        
        return max(0.0, min(1.0, score))

    # ---------- NEW: A Priori Reasoning (Non-Vault) ----------

    def _a_priori_reasoning(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        A priori reasoning: inherent rational principles not derived from experience
        These are the 'first principles' of the reasoning system
        """
        principles = {
            "non_contradiction": self._principle_non_contradiction(inputs),
            "sufficient_reason": self._principle_sufficient_reason(inputs),
            "identity_preservation": self._principle_identity_preservation(inputs),
            "causal_consistency": self._principle_causal_consistency(inputs),
        }
        
        return {
            "principles": principles,
            "violations": [k for k, v in principles.items() if not v["satisfied"]],
            "overall_coherence": sum(1 for v in principles.values() if v["satisfied"]) / len(principles),
            "rational_constraints": self._derive_rational_constraints(principles)
        }

    def _principle_non_contradiction(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """A cannot be both true and false in the same respect at the same time"""
        # Check for logical contradictions in inputs
        contradictions = []
        if inputs.get("desire", 0) > 0.8 and inputs.get("aversion", 0) > 0.8:
            contradictions.append("High desire and high aversion for same object")
        if inputs.get("certainty", 0) > 0.9 and inputs.get("doubt", 0) > 0.9:
            contradictions.append("High certainty and high doubt simultaneously")
        
        return {
            "satisfied": len(contradictions) == 0,
            "contradictions": contradictions,
            "principle": "non_contradiction"
        }

    def _principle_sufficient_reason(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Everything must have a sufficient reason or cause"""
        unexplained = []
        for key, value in inputs.items():
            if isinstance(value, (int, float)) and abs(value) > 0.7 and key not in ["desire", "danger", "curiosity"]:
                unexplained.append(f"High value {value} for {key} without clear reason")
        
        return {
            "satisfied": len(unexplained) == 0,
            "unexplained_inputs": unexplained,
            "principle": "sufficient_reason"
        }

    def _principle_identity_preservation(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Maintain coherent identity across decisions"""
        recent_actions = list(self.epigenetic_memory.keys())[-5:]
        diversity = len(set(recent_actions))
        
        return {
            "satisfied": diversity <= 3,  # Prefer consistency over random exploration
            "action_diversity": diversity,
            "principle": "identity_preservation"
        }

    def _principle_causal_consistency(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Maintain consistent cause-effect relationships"""
        if len(self.transcendental_mapper.expectation_history) < 2:
            return {"satisfied": True, "principle": "causal_consistency"}
        
        recent_regret = self.transcendental_mapper.calculate_regret_tension()
        return {
            "satisfied": recent_regret < 0.4,
            "regret_tension": recent_regret,
            "principle": "causal_consistency"
        }

    def _derive_rational_constraints(self, principles: Dict[str, Any]) -> List[str]:
        """Derive action constraints from a priori principles"""
        constraints = []
        
        if not principles["non_contradiction"]["satisfied"]:
            constraints.append("AVOID_CONTRADICTORY_ACTIONS")
        if not principles["sufficient_reason"]["satisfied"]:
            constraints.append("REQUIRE_SUFFICIENT_REASON")
        if not principles["identity_preservation"]["satisfied"]:
            constraints.append("MAINTAIN_IDENTITY_CONSISTENCY")
        if not principles["causal_consistency"]["satisfied"]:
            constraints.append("ENSURE_CAUSAL_PREDICTABILITY")
            
        return constraints

    # ---------- Enhanced VAULT registry ----------

    def set_vaults(self, **vaults: Any) -> None:
        """Register/override vaults with enhanced validation"""
        self.vaults.update(vaults)
        # Ensure reflection vault is always available
        if "reflection_vault" not in self.vaults:
            self.vaults["reflection_vault"] = self.reflection_vault

    def _vault_refs_for(self, framework: str) -> List[str]:
        """Return vault keys relevant to a framework with enhanced mapping"""
        wanted = {
            "kant":         ["seed_vault", "a_priori_vault", "reflection_vault"],
            "locke":        ["seed_vault", "a_posteriori_vault", "reflection_vault"],
            "nonmonotonic": ["seed_vault", "a_posteriori_vault", "reflection_vault"],
            "a_priori":     ["a_priori_vault", "seed_vault"],
            "gladwell":     ["reflection_vault", "seed_vault"],  # NEW: Gladwell uses reflection for patterns
        }.get(framework, ["seed_vault"])
        return [k for k in wanted if k in self.vaults]

    # ---------- Enhanced API with New Logic Integration ----------

    def add_main_logic(
        self,
        action: Callable[[Dict[str, Any]], Any],
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
        pleasure_weight: float = 1.0,
        pain_weight: float = 1.0,
        gladwell_priority: float = 0.5,  # NEW: Thin-slicing priority
        a_priori_constraints: List[str] = None,  # NEW: A priori constraints
    ) -> None:
        self.helix_main.append({
            "action": action,
            "condition": condition,
            "pleasure_weight": float(pleasure_weight),
            "pain_weight": float(pain_weight),
            "gladwell_priority": float(gladwell_priority),  # NEW
            "a_priori_constraints": a_priori_constraints or [],  # NEW
            "action_name": action.__name__  # NEW: For better tracking
        })

    # ---------- Enhanced Execution with New Logic ----------

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        print("\n-- ANTERIOR PITUITARY (PRIMARY) RUNNING --")
        
        # NEW: Apply a priori reasoning first
        a_priori_analysis = self._a_priori_reasoning(inputs)
        print(f"[A Priori] Coherence: {a_priori_analysis['overall_coherence']:.2f}")
        
        # NEW: Ping reflection vault for historical matching
        potential_actions = [step["action_name"] for step in self.helix_main]
        reflection_match = self._ping_reflection_vault(inputs, potential_actions)
        if reflection_match["confidence"] > 0.8:
            print(f"[Reflection Vault] High confidence match: {reflection_match['confidence']:.2f}")
        
        # NEW: Apply Gladwell thin-slicing
        thin_sliced_actions = self._gladwell_thin_slice(inputs, potential_actions)
        
        executed: List[str] = []
        suppressed: List[str] = []

        # Process actions with enhanced logic
        for step in self.helix_main:
            action_name = step["action_name"]
            
            # Check conditions with enhanced logic
            cond = step["condition"]
            if cond and not cond(inputs):
                continue

            # NEW: Check a priori constraints
            if any(constraint in a_priori_analysis["rational_constraints"] 
                   for constraint in step["a_priori_constraints"]):
                print(f"🚨 A Priori Constraint Violation: {action_name} suppressed!")
                suppressed.append(action_name)
                continue

            pleasure = step["pleasure_weight"]
            pain = step["pain_weight"]
            risk_factor = self._pleasure_pain_balance(pleasure, pain)
            
            # NEW: Incorporate Gladwell priority
            gladwell_boost = step["gladwell_priority"]
            adjusted_risk = risk_factor * (1.0 + gladwell_boost * 0.2)  # 20% max boost

            if adjusted_risk < 0:  # projected pain dominates
                print(f"🚨 PAIN DOMINATES: {action_name} suppressed!")
                self.transcendental_mapper.log_decision(expected_reward=pleasure, actual_outcome=-pain)
                self.noumenal_drift.append(f"Suppressed {action_name} due to excessive projected pain.")
                suppressed.append(action_name)
                continue

            print(f"Executing action: {action_name} (Risk: {adjusted_risk:.2f}, Gladwell: {gladwell_boost:.2f})")
            result = step["action"](inputs)
            executed.append(action_name)
            self.store_epigenetic_memory("main", action_name, result)
            self.transcendental_mapper.log_decision(expected_reward=pleasure, actual_outcome=pleasure)

        # Posterior helix trails and reflects
        mirror_report = self.mirror.reflect_recursive(inputs, executed, suppressed) if self.mirror else {}

        print("\n-- CROSSOVER NODE ACTIVATED --")
        self._cross_node()
        print("\n-- NOUMENAL DRIFT ANALYSIS --")
        self._analyze_noumenal_drift()

        # ---------- Enhanced JSON exports with new frameworks ----------
        active_intents = self._active_intents_from_mirror(mirror_report)
        kant_j    = self._export_json_kant(inputs, executed, suppressed, active_intents)
        locke_j   = self._export_json_locke(inputs)
        nonmono_j = self._export_json_nonmonotonic(executed, suppressed, mirror_report)
        apriori_j = self._export_json_a_priori(a_priori_analysis)  # ENHANCED
        gladwell_j = self._export_json_gladwell(inputs, thin_sliced_actions, reflection_match)  # NEW

        # Ensure VAULT presence
        self.vaults.setdefault("a_priori_vault", apriori_j)
        self.vaults.setdefault("a_posteriori_vault", locke_j)
        self.vaults.setdefault("reflection_vault", self.reflection_vault)

        # Enhanced framework mixing
        frameworks = [
            ("kant", kant_j),
            ("locke", locke_j),
            ("nonmonotonic", nonmono_j),
            ("a_priori", apriori_j),
            ("gladwell", gladwell_j),  # NEW
        ]
        k = max(1, min(self.json_mix_count, len(frameworks)))
        pool = frameworks[:] if k == len(frameworks) else random.sample(frameworks, k)

        mixed = []
        for (t, d) in pool:
            mixed.append({
                "type": t,
                "vault_refs": self._vault_refs_for(t),
                "data": d,
            })
        random.shuffle(mixed)

        self.last_exports = {
            "canonical": {
                "kant": kant_j, "locke": locke_j, "nonmonotonic": nonmono_j, 
                "a_priori": apriori_j, "gladwell": gladwell_j,
            },
            "vaults": self.vaults,
            "mixed_order": mixed,
            "reflection_match": reflection_match,  # NEW
            "a_priori_analysis": a_priori_analysis,  # NEW
        }

        print("\n-- PHILOSOPHICAL JSON (Mixed Order) --")
        for item in mixed:
            print(f"\n[{item['type'].upper()}]\n" + json.dumps(item["data"], indent=2))

        # Save to reflection vault for future speed optimization
        self._update_reflection_vault(inputs, executed, suppressed)

        # Harmonizer route on high conflict
        if self._conflict_is_high(mirror_report, a_priori_analysis):
            self._escalate_via_harmonizer({
                "reason": "high_conflict",
                "mirror_report": mirror_report,
                "exports": self.last_exports,
                "inputs": inputs,
                "a_priori_violations": a_priori_analysis["violations"],  # NEW
            })

        return {"mirror_report": mirror_report, "exports": self.last_exports}

    def _update_reflection_vault(self, inputs: Dict[str, Any], executed: List[str], suppressed: List[str]):
        """Update reflection vault with current decision for future matching"""
        decision_id = str(uuid.uuid4())[:8]
        decision_record = {
            "id": decision_id,
            "timestamp": datetime.now().isoformat(),
            "pattern": self._extract_pattern_signature(inputs),
            "executed_actions": executed,
            "suppressed_actions": suppressed,
            "outcome_score": len(executed) / max(1, len(executed) + len(suppressed)),
            "input_keys": list(inputs.keys()),
        }
        
        self.reflection_vault.setdefault("decisions", []).append(decision_record)
        # Keep only recent decisions
        self.reflection_vault["decisions"] = self.reflection_vault["decisions"][-200:]
        self._save_reflection_vault()

    # ---------- Enhanced JSON exporters ----------

    def _export_json_a_priori(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced a priori export with principle analysis"""
        return {
            "framework": "a_priori",
            "principles": analysis["principles"],
            "violations": analysis["violations"],
            "overall_coherence": analysis["overall_coherence"],
            "rational_constraints": analysis["rational_constraints"],
            "parameters": {
                "balance_function": "tanh(pleasure - pain)",
                "risk_threshold": 0.0,
                "identity_preservation_threshold": 3,
            }
        }

    def _export_json_gladwell(self, inputs: Dict[str, Any], thin_sliced_actions: List[str], 
                            reflection_match: Dict[str, Any]) -> Dict[str, Any]:
        """NEW: Gladwell thin-slicing framework export"""
        return {
            "framework": "gladwell",
            "thin_sliced_priority": thin_sliced_actions,
            "reflection_matches": reflection_match["matches"],
            "pattern_signature": reflection_match["pattern_signature"],
            "confidence": reflection_match["confidence"],
            "cached_patterns_count": len(self.gladwell_thin_slices),
            "rapid_assessment_notes": "Based on first 2 seconds of information (thin-slicing)"
        }

    def _export_json_kant(
        self,
        inputs: Dict[str, Any],
        executed: List[str],
        suppressed: List[str],
        active_intents: List[str],
    ) -> Dict[str, Any]:
        """Enhanced Kantian export with a priori integration"""
        categories = {
            "quantity":  "unity" if len(executed) <= 1 else "plurality",
            "quality":   "reality" if executed else ("negation" if suppressed else "limitation"),
            "relation":  "cause-effect" if executed else "inherence", 
            "modality":  "assertoric" if executed else "problematic",
        }
        maxims = [{"intent": m, "universalizable": True, "notes": "Heuristic: non-harm, coherence"} for m in active_intents]
        duty_over_inclination = len(suppressed) > 0
        
        return {
            "framework": "kant",
            "a_priori_categories": categories,
            "maxims": maxims,
            "duty_over_inclination": duty_over_inclination,
            "inputs_snapshot": inputs,
            "memory_index": {k: v["count"] for k, v in self.epigenetic_memory.items()},
            "regret_tension": self.transcendental_mapper.calculate_regret_tension(),
            "categorical_imperative_check": self._kantian_universalizability_check(executed),
        }

    def _kantian_universalizability_check(self, actions: List[str]) -> Dict[str, bool]:
        """Check if actions can be universalized without contradiction"""
        checks = {}
        for action in actions:
            action_lower = action.lower()
            if any(word in action_lower for word in ["deceive", "harm", "exploit"]):
                checks[action] = False
            else:
                checks[action] = True
        return checks

    # ---------- Enhanced conflict detection ----------

    def _conflict_is_high(self, mirror_report: Dict[str, Any], a_priori_analysis: Dict[str, Any]) -> bool:
        """Enhanced conflict detection with a priori principles"""
        mirror_escalate = mirror_report.get("escalate_to_human", False)
        recent = mirror_report.get("iterations", [])[-3:]
        recent_conflict = any(x.get("conflict") for x in recent)
        tension = self.transcendental_mapper.calculate_regret_tension()
        a_priori_violations = len(a_priori_analysis["violations"]) > 0
        
        return bool(mirror_escalate or recent_conflict or tension > 0.6 or a_priori_violations)

    # ---------- Rest of original methods (unchanged) ----------
    
    def _pleasure_pain_balance(self, pleasure: float, pain: float) -> float:
        return math.tanh(pleasure - pain)

    def store_epigenetic_memory(self, helix_type: str, key: str, result: Any) -> None:
        if key not in self.epigenetic_memory:
            self.epigenetic_memory[key] = {"count": 0, "results": []}
        self.epigenetic_memory[key]["count"] += 1
        self.epigenetic_memory[key]["results"].append(result)

    def _store_epigenetic_memory_bridge(self, helix_type: str, key: str, result: Any) -> None:
        k = f"{helix_type}:{key}"
        self.store_epigenetic_memory(helix_type, k, result)

    def _cross_node(self) -> None:
        print("EchoStack analyzing twin spiral convergence...")
        print("Result: Stable — intent and action are aligned.")

    def _analyze_noumenal_drift(self) -> None:
        print("\n-- Paths Not Taken --")
        for drift in self.noumenal_drift:
            print(f"↪ {drift}")
        adjustment = self.transcendental_mapper.recommend_adjustment()
        print(f"🔁 Adjustment Recommendation: {adjustment}")

    def _active_intents_from_mirror(self, mirror_report: Dict[str, Any]) -> List[str]:
        iters = mirror_report.get("iterations", [])
        if not iters:
            return []
        last_pairs = iters[-1].get("pairs", [])
        intents = [p.get("mirror_intent") for p in last_pairs if p.get("mirror_intent")]
        seen: Set[str] = set()
        out: List[str] = []
        for i in intents:
            if i not in seen:
                seen.add(i)
                out.append(i)
        return out

    def _escalate_via_harmonizer(self, payload: Dict[str, Any]) -> None:
        if self.harmonizer_cb:
            try:
                self.harmonizer_cb(payload)
            except Exception:
                pass

    def _export_json_locke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        simple_ideas = {k: float(v) for k, v in inputs.items() if isinstance(v, (int, float))}
        complex_ideas = {
            "approach_avoidance": {
                "desire": float(inputs.get("desire", 0)),
                "danger": float(inputs.get("danger", 0)),
                "curiosity": float(inputs.get("curiosity", 0)),
            },
            "affect_bias": {
                "pleasure_bias": bool(float(inputs.get("desire", 0)) > 0.7),
                "pain_bias": bool(float(inputs.get("danger", 0)) > 0.8),
            },
        }
        associations = {
            key: {"count": data["count"], "last_result": data["results"][-1] if data["results"] else None}
            for key, data in self.epigenetic_memory.items()
        }
        return {
            "framework": "locke",
            "simple_ideas": simple_ideas,
            "complex_ideas": complex_ideas,
            "associative_memory": associations,
        }

    def _export_json_nonmonotonic(
        self,
        executed: List[str],
        suppressed: List[str],
        mirror_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        defaults = [{"do": name, "status": "expected"} for name in executed + suppressed]
        exceptions = [{"withhold": name, "reason": "projected_pain"} for name in suppressed]
        recent_conflict = any(x.get("conflict") for x in mirror_report.get("iterations", [])[-3:])
        status = "cautious" if recent_conflict else "stable"
        return {
            "framework": "nonmonotonic",
            "defaults": defaults,
            "exceptions": exceptions,
            "noumenal_drift": list(self.noumenal_drift),
            "status": status,
            "mirror_escalate": mirror_report.get("escalate_to_human", False),
            "crossovers": mirror_report.get("crossovers", []),
        }


class TranscendentalMapper:
    """Enhanced with a priori principle tracking"""
    expectation_history: List[float]
    outcome_memory: List[float]
    principle_violations: List[str]

    def __init__(self) -> None:
        self.expectation_history = []
        self.outcome_memory = []
        self.principle_violations = []

    def log_decision(self, expected_reward: float, actual_outcome: float) -> None:
        self.expectation_history.append(float(expected_reward))
        self.outcome_memory.append(float(actual_outcome))

    def calculate_regret_tension(self) -> float:
        if not self.expectation_history: return 0.0
        regrets = [abs(e - a) for e, a in zip(self.expectation_history, self.outcome_memory)]
        return sum(regrets) / len(regrets)

    def recommend_adjustment(self) -> str:
        t = self.calculate_regret_tension()
        if t > 0.5:  return "Increase Mirror Influence"
        if t < 0.2:  return "Permit Rational Acceleration" 
        return "Maintain Balanced Oscillation"


# ---------- Enhanced wiring example ----------
if __name__ == "__main__":
    def seek_pleasure(inputs): return "PLEASURE PURSUED"
    def avoid_pain(inputs):    return "PAIN AVOIDED"
    def explore_curiosity(inputs): return "CURIOSITY SATISFIED"

    def harmonizer(payload: Dict[str, Any]) -> None:
        print("\n[HARMONIZER] High-conflict bundle received.")
        print(json.dumps({"reason": payload.get("reason"), "escalate": True}, indent=2))

    core = AnteriorPituitaryHelix(harmonizer_cb=harmonizer, random_seed=42, json_mix_count=5)

    # Enhanced action registration with new parameters
    core.add_main_logic(seek_pleasure, 
                       lambda i: i.get("desire", 0) > 0.7, 
                       pleasure_weight=1.2, 
                       pain_weight=0.5,
                       gladwell_priority=0.8,  # High thin-slicing priority
                       a_priori_constraints=["REQUIRE_SUFFICIENT_REASON"])
    
    core.add_main_logic(avoid_pain, 
                       lambda i: i.get("danger", 0) > 0.8, 
                       pleasure_weight=0.3, 
                       pain_weight=1.5,
                       gladwell_priority=0.9,  # Very high for danger avoidance
                       a_priori_constraints=["AVOID_CONTRADICTORY_ACTIONS"])
    
    core.add_main_logic(explore_curiosity,
                       lambda i: i.get("curiosity", 0) > 0.6,
                       pleasure_weight=0.8,
                       pain_weight=0.4, 
                       gladwell_priority=0.6,
                       a_priori_constraints=[])

    # VAULTs
    core.set_vaults(
        seed_vault={"id":"seed:v1","notes":"seed VAULT payload here"},
        a_priori_vault={"id":"apriori:v1","axioms":["consistency","non_harm","coherence"]},
        a_posteriori_vault={"id":"aposteriori:v1","evidence":["runtime_observation_1"]},
    )

    # Run enhanced execution
    result = core.execute({"desire": 0.8, "danger": 0.2, "curiosity": 0.6, "certainty": 0.3})
    print(f"\nFinal result keys: {list(result.keys())}")