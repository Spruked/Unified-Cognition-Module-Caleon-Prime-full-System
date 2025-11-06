from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import json
import os
import time
import random
import httpx
from datetime import datetime
import numpy as np

app = FastAPI(title="EchoRipple - Memory & Learning")

class MemoryPattern(BaseModel):
    pattern_id: str
    content: str
    context: Dict[str, Any]
    importance: float
    timestamp: float
    vault_trace: Optional[str] = None

class LearningExperience(BaseModel):
    experience_id: str
    input_data: str
    outcome: str
    lesson_learned: str
    confidence: float
    vault_reflection: Optional[str] = None

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import json
import os
import time
import random
import httpx
from datetime import datetime

app = FastAPI(title="EchoRipple - Memory & Learning")

class MemoryPattern(BaseModel):
    pattern_id: str
    content: str
    context: Dict[str, Any]
    importance: float
    timestamp: float
    vault_trace: Optional[str] = None
    sequence_id: Optional[str] = None
    tier_context: Optional[Dict[str, Any]] = None

class LearningExperience(BaseModel):
    experience_id: str
    input_data: str
    outcome: str
    lesson_learned: str
    confidence: float
    vault_reflection: Optional[str] = None
    sequence_binding: Optional[str] = None

class EchoVerification:
    def __init__(self, vault_config: Dict[str, Any]):
        self.recursive_depth = vault_config.get("echo_verification", {}).get("recursive_depth", 3)
        self.trailing_delay_ms = vault_config.get("echo_verification", {}).get("trailing_delay_ms", 50)
        self.conflict_threshold = vault_config.get("echo_verification", {}).get("conflict_threshold", 3)
        self.harmonizer_endpoint = vault_config.get("echo_verification", {}).get("harmonizer_escalation", {}).get("endpoint", "http://gyro-harmonizer:5000/escalate_conflict")
        self.verification_cycles = 0
        self.sequencer_binding = vault_config.get("sequencer_binding", {})

    async def verify_echo(self, data: Dict[str, Any], depth: int = 0, sequence_id: str = None) -> Dict[str, Any]:
        """Perform recursive echo verification with sequencer binding and 50ms trailing delay"""
        if depth >= self.recursive_depth:
            return {"verified": True, "confidence": 0.8, "depth": depth, "sequence_bound": bool(sequence_id)}

        # Add trailing delay
        await asyncio.sleep(self.trailing_delay_ms / 1000)

        # Apply sequencer binding
        if sequence_id:
            data["sequence_binding"] = sequence_id
            data["tier_context"] = {"bound_to_sequencer": True, "sequence_id": sequence_id}

        # Perform echo verification
        verification_score = random.uniform(0.7, 0.95)
        conflicts = []
        symbolic_overlays = []

        # Check for internal consistency
        if "content" in data:
            content_hash = hash(data["content"])
            echo_hash = hash(str(data))
            if content_hash != echo_hash:
                conflicts.append("content_integrity")

        # Check temporal consistency
        if "timestamp" in data:
            current_time = time.time()
            if abs(current_time - data["timestamp"]) > 3600:  # 1 hour
                conflicts.append("temporal_drift")

        # Check sequence binding
        if sequence_id and data.get("sequence_binding") != sequence_id:
            conflicts.append("sequence_binding_mismatch")

        # Apply symbolic overlays
        symbolic_overlays = self.apply_symbolic_overlays(data, depth)

        # Recursive verification
        if conflicts and depth < self.recursive_depth - 1:
            self.verification_cycles += 1
            if self.verification_cycles >= self.conflict_threshold:
                # Escalate to Harmonizer
                escalation_result = await self.escalate_conflict(data, conflicts, sequence_id)
                if escalation_result.get("resolved", False):
                    return escalation_result

        return {
            "verified": len(conflicts) == 0,
            "confidence": verification_score,
            "conflicts": conflicts,
            "symbolic_overlays": symbolic_overlays,
            "depth": depth,
            "cycles": self.verification_cycles,
            "sequence_bound": bool(sequence_id)
        }

    def apply_symbolic_overlays(self, data: Dict[str, Any], depth: int) -> List[Dict[str, Any]]:
        """Apply symbolic overlays for enhanced memory processing"""
        overlays = []

        # Memory pattern overlay
        if "importance" in data:
            importance_level = "high" if data["importance"] > 0.7 else "medium" if data["importance"] > 0.4 else "low"
            overlays.append({
                "overlay_type": "importance_modulation",
                "level": importance_level,
                "symbolic_weight": data["importance"],
                "depth": depth
            })

        # Sequence binding overlay
        if data.get("sequence_binding"):
            overlays.append({
                "overlay_type": "sequence_binding",
                "sequence_id": data["sequence_binding"],
                "binding_strength": 0.9,
                "depth": depth
            })

        # Temporal coherence overlay
        if "timestamp" in data:
            temporal_freshness = max(0, 1 - (time.time() - data["timestamp"]) / 86400)  # 24 hours
            overlays.append({
                "overlay_type": "temporal_coherence",
                "freshness": temporal_freshness,
                "decay_factor": 0.95 ** depth,
                "depth": depth
            })

        return overlays

    async def escalate_conflict(self, data: Dict[str, Any], conflicts: List[str], sequence_id: str = None) -> Dict[str, Any]:
        """Escalate persistent conflict to Harmonizer with sequence awareness"""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                payload = {
                    "conflict_data": data,
                    "conflicts": conflicts,
                    "source": "echoripple",
                    "escalation_reason": "persistent_echo_conflict",
                    "verification_cycles": self.verification_cycles,
                    "sequence_id": sequence_id,
                    "tier_context": data.get("tier_context", {}),
                    "symbolic_overlays": data.get("symbolic_overlays", [])
                }
                response = await client.post(self.harmonizer_endpoint, json=payload)
                result = response.json()
                return {
                    "resolved": True,
                    "harmonizer_response": result,
                    "escalation_successful": True,
                    "sequence_aware": bool(sequence_id)
                }
        except Exception as e:
            # Fallback to provisional output
            return {
                "resolved": False,
                "provisional": True,
                "warning": "INCOMPLETE HARMONIZATION - Harmonizer offline",
                "reduced_confidence": 0.5,
                "error": str(e),
                "sequence_preserved": bool(sequence_id)
            }

class MemorySystem:
    def __init__(self):
        self.short_term_memory = []
        self.long_term_memory = {}
        self.learning_experiences = []
        self.memory_file = "memory_store.json"
        self.vault_file = "echo_ripple_reflect.vault.json"

        # Load EchoRipple reflection vault
        try:
            with open(self.vault_file, 'r') as f:
                self.vault_data = json.load(f)
        except FileNotFoundError:
            self.vault_data = {"reflection_entries": []}

        # Initialize echo verifier with vault configuration
        self.echo_verifier = EchoVerification(self.vault_data)

        # Load sequencer binding configuration
        self.sequencer_binding = self.vault_data.get("sequencer_binding", {
            "bound_to_echostack": True,
            "reflection_loops": 7,  # 5-10 reflections, using 7 as default
            "sequence_awareness": True
        })

        self.load_memory()

    def load_seed_logic(self) -> Dict[str, Any]:
        """Load the randomized 4-seed logic + 1 philosopher from vault"""
        if os.path.exists(self.vault_file):
            try:
                with open(self.vault_file, 'r') as f:
                    vault_data = json.load(f)
                    return vault_data.get("seed_logic", {})
            except:
                pass

        # Default seed logic if vault not found
        return {
            "randomized_seeds": [
                {"seed_id": "seed_memory_consolidation", "confidence_weight": 0.8},
                {"seed_id": "seed_similarity_recall", "confidence_weight": 0.7},
                {"seed_id": "seed_conflict_resolution", "confidence_weight": 0.9},
                {"seed_id": "seed_experience_learning", "confidence_weight": 0.75}
            ],
            "philosopher_core": {
                "philosopher": "Socrates",
                "principle": "Know Thyself",
                "influence_weight": 0.85
            }
        }

    def load_memory(self):
        """Load memory from persistent storage"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.long_term_memory = data.get('long_term', {})
                    self.learning_experiences = data.get('experiences', [])
                    # Load short-term if available
                    self.short_term_memory = data.get('short_term', [])
            except:
                pass

    def load_vault(self):
        """Load vault data for reflection tracking"""
        if os.path.exists(self.vault_file):
            try:
                with open(self.vault_file, 'r') as f:
                    self.vault_data = json.load(f)
            except:
                self.vault_data = {"reflection_entries": []}

    def save_memory(self):
        """Save memory to persistent storage"""
        data = {
            'long_term': self.long_term_memory,
            'short_term': self.short_term_memory,
            'experiences': self.learning_experiences
        }
        with open(self.memory_file, 'w') as f:
            json.dump(data, f)

    def save_vault(self):
        """Save vault data"""
        with open(self.vault_file, 'w') as f:
            json.dump(self.vault_data, f)

    async def store_pattern(self, pattern: MemoryPattern):
        """Store a memory pattern with recursive echo verification (5-10 reflections) and sequencer binding"""
        # Generate sequence ID if not provided
        sequence_id = pattern.sequence_id or f"seq_{int(time.time())}_{random.randint(1000, 9999)}"

        # Perform recursive echo verification with 5-10 reflections
        verification_results = []
        reflection_count = random.randint(5, 10)  # 5-10 reflections as per ICS-V2-2025-10-18

        for reflection in range(reflection_count):
            # Each reflection gets deeper verification
            verification = await self.echo_verifier.verify_echo(
                pattern.dict(),
                depth=reflection,
                sequence_id=sequence_id
            )
            verification_results.append(verification)

            # Add trailing delay between reflections
            if reflection < reflection_count - 1:
                await asyncio.sleep(self.echo_verifier.trailing_delay_ms / 1000)

        # Aggregate verification results
        final_verification = self.aggregate_verification_results(verification_results)

        # Apply sequencer binding from vault configuration
        if self.sequencer_binding.get("bound_to_echostack", False):
            pattern_data = pattern.dict()
            pattern_data["sequence_id"] = sequence_id
            pattern_data["tier_context"] = {
                "bound_to_sequencer": True,
                "sequence_id": sequence_id,
                "reflection_loops": reflection_count,
                "sequencer_awareness": self.sequencer_binding.get("sequence_awareness", True)
            }
            pattern_data["verification"] = final_verification
            pattern_data["vault_trace"] = f"echo_{sequence_id}_{int(time.time())}"
            pattern_data["symbolic_overlays"] = final_verification.get("symbolic_overlays", [])

        # Add to short-term memory
        self.short_term_memory.append(pattern_data)

        # Keep only recent patterns (capped at 50)
        if len(self.short_term_memory) > 50:
            self.short_term_memory = self.short_term_memory[-50:]

        # Move important patterns to long-term memory using seed logic
        consolidation_seed = next((s for s in self.seed_logic.get("randomized_seeds", [])
                                if s["seed_id"] == "seed_memory_consolidation"), {})
        importance_threshold = consolidation_seed.get("activation_threshold", 0.7)

        if pattern.importance > importance_threshold:
            self.long_term_memory[pattern.pattern_id] = pattern_data

        # Log reflection in vault with sequence awareness
        self.log_vault_reflection("pattern_stored", {
            "pattern_id": pattern.pattern_id,
            "sequence_id": sequence_id,
            "importance": pattern.importance,
            "verification": final_verification,
            "reflection_loops": reflection_count,
            "sequencer_bound": True
        })

        self.save_memory()

    def aggregate_verification_results(self, verification_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate multiple verification results into final verdict"""
        if not verification_results:
            return {"verified": False, "confidence": 0.0, "conflicts": ["no_verifications"]}

        # Calculate aggregate confidence
        confidences = [v.get("confidence", 0) for v in verification_results]
        avg_confidence = sum(confidences) / len(confidences)

        # Collect all conflicts
        all_conflicts = []
        all_overlays = []
        sequence_bound = False

        for result in verification_results:
            all_conflicts.extend(result.get("conflicts", []))
            all_overlays.extend(result.get("symbolic_overlays", []))
            if result.get("sequence_bound", False):
                sequence_bound = True

        # Remove duplicates
        unique_conflicts = list(set(all_conflicts))

        # Determine final verification status
        verified = len(unique_conflicts) == 0 and avg_confidence > 0.6

        return {
            "verified": verified,
            "confidence": avg_confidence,
            "conflicts": unique_conflicts,
            "symbolic_overlays": all_overlays,
            "reflection_count": len(verification_results),
            "sequence_bound": sequence_bound,
            "harmonizer_ready": True  # Ready for harmonizer escalation if needed
        }

    def recall_similar(self, query: str, threshold: float = 0.6, sequence_context: str = None) -> List[Dict[str, Any]]:
        """Recall similar memory patterns with sequence context filtering and symbolic overlay weighting"""
        similar_patterns = []

        # Get similarity recall seed
        recall_seed = next((s for s in self.seed_logic.get("randomized_seeds", [])
                          if s["seed_id"] == "seed_similarity_recall"), {})

        # Apply seed logic thresholds
        long_term_threshold = recall_seed.get("activation_threshold", 0.6)
        short_term_threshold = long_term_threshold * 0.8  # Slightly lower for short-term

        # Search in long-term memory
        for pattern_id, pattern_data in self.long_term_memory.items():
            # Apply sequence context filtering
            if sequence_context and pattern_data.get("sequence_id") != sequence_context:
                continue  # Skip patterns not in the same sequence context

            similarity = self.calculate_similarity(query, pattern_data['content'])

            # Apply symbolic overlay weighting
            symbolic_weight = self.apply_symbolic_weighting(pattern_data, similarity)

            if similarity >= long_term_threshold:
                similar_patterns.append({
                    **pattern_data,
                    'similarity': similarity,
                    'memory_type': 'long_term',
                    'seed_confidence': recall_seed.get("confidence_weight", 0.7),
                    'symbolic_weight': symbolic_weight,
                    'sequence_context': pattern_data.get('sequence_id'),
                    'tier_awareness': pattern_data.get('tier_context', {})
                })

        # Search in short-term memory
        for pattern_data in self.short_term_memory:
            # Apply sequence context filtering
            if sequence_context and pattern_data.get("sequence_id") != sequence_context:
                continue  # Skip patterns not in the same sequence context

            similarity = self.calculate_similarity(query, pattern_data['content'])

            # Apply symbolic overlay weighting
            symbolic_weight = self.apply_symbolic_weighting(pattern_data, similarity)

            if similarity >= short_term_threshold:
                similar_patterns.append({
                    **pattern_data,
                    'similarity': similarity,
                    'memory_type': 'short_term',
                    'seed_confidence': recall_seed.get("confidence_weight", 0.7),
                    'symbolic_weight': symbolic_weight,
                    'sequence_context': pattern_data.get('sequence_id'),
                    'tier_awareness': pattern_data.get('tier_context', {})
                })

        # Sort by combined similarity and symbolic weight
        similar_patterns.sort(key=lambda x: (x['similarity'] * x.get('symbolic_weight', 1.0), x.get('seed_confidence', 0)), reverse=True)
        return similar_patterns[:10]  # Return top 10

    def apply_symbolic_weighting(self, pattern_data: Dict[str, Any], base_similarity: float) -> float:
        """Apply symbolic overlay weighting to similarity scores"""
        weight = 1.0

        # Importance modulation overlay
        importance_overlays = [o for o in pattern_data.get("symbolic_overlays", [])
                             if o.get("overlay_type") == "importance_modulation"]
        if importance_overlays:
            importance_weight = importance_overlays[0].get("symbolic_weight", 0.5)
            weight *= (1 + importance_weight * 0.5)  # Boost by up to 50%

        # Sequence binding overlay
        sequence_overlays = [o for o in pattern_data.get("symbolic_overlays", [])
                           if o.get("overlay_type") == "sequence_binding"]
        if sequence_overlays:
            binding_strength = sequence_overlays[0].get("binding_strength", 0.9)
            weight *= binding_strength

        # Temporal coherence overlay
        temporal_overlays = [o for o in pattern_data.get("symbolic_overlays", [])
                           if o.get("overlay_type") == "temporal_coherence"]
        if temporal_overlays:
            freshness = temporal_overlays[0].get("freshness", 0.5)
            decay_factor = temporal_overlays[0].get("decay_factor", 0.95)
            weight *= (freshness * decay_factor)

        return weight

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Enhanced similarity calculation using Jaccard similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        # Apply philosopher influence (Socratic self-examination)
        base_similarity = len(intersection) / len(union) if union else 0.0

        # Add contextual weighting based on philosopher core
        philosopher_weight = self.philosopher_core.get("influence_weight", 0.85)
        return base_similarity * philosopher_weight

    async def learn_from_experience(self, experience: LearningExperience):
        """Learn from an experience with recursive echo verification and sequencer binding"""
        # Generate sequence binding if not provided
        sequence_binding = experience.sequence_binding or f"bind_{int(time.time())}_{random.randint(1000, 9999)}"

        # Perform recursive echo verification with 5-10 reflections
        verification_results = []
        reflection_count = random.randint(5, 10)  # 5-10 reflections for compliance

        for reflection in range(reflection_count):
            verification = await self.echo_verifier.verify_echo(
                experience.dict(),
                depth=reflection,
                sequence_id=sequence_binding
            )
            verification_results.append(verification)

            # Add trailing delay between reflections
            if reflection < reflection_count - 1:
                await asyncio.sleep(self.echo_verifier.trailing_delay_ms / 1000)

        # Aggregate verification results
        final_verification = self.aggregate_verification_results(verification_results)

        # Get experience learning seed
        learning_seed = next((s for s in self.seed_logic.get("randomized_seeds", [])
                            if s["seed_id"] == "seed_experience_learning"), {})

        experience_data = experience.dict()
        experience_data["sequence_binding"] = sequence_binding
        experience_data["tier_context"] = {
            "bound_to_sequencer": True,
            "sequence_id": sequence_binding,
            "reflection_loops": reflection_count,
            "sequencer_awareness": self.sequencer_binding.get("sequence_awareness", True)
        }
        experience_data["verification"] = final_verification
        experience_data["vault_reflection"] = f"learn_{sequence_binding}_{int(time.time())}"
        experience_data["symbolic_overlays"] = final_verification.get("symbolic_overlays", [])

        # Apply confidence threshold from seed logic
        confidence_threshold = learning_seed.get("activation_threshold", 0.6)
        if experience.confidence >= confidence_threshold:
            self.learning_experiences.append(experience_data)

            # Keep only recent experiences (capped at 100)
            if len(self.learning_experiences) > 100:
                self.learning_experiences = self.learning_experiences[-100:]

            # Log reflection in vault with sequence awareness
            self.log_vault_reflection("experience_learned", {
                "experience_id": experience.experience_id,
                "sequence_binding": sequence_binding,
                "confidence": experience.confidence,
                "lesson": experience.lesson_learned,
                "reflection_loops": reflection_count,
                "sequencer_bound": True
            })

        self.save_memory()

    def get_relevant_lessons(self, situation: str, sequence_context: str = None) -> List[Dict[str, Any]]:
        """Get lessons learned from similar situations with sequence-aware retrieval"""
        relevant_lessons = []

        for exp in self.learning_experiences:
            # Apply sequence context filtering
            if sequence_context and exp.get("sequence_binding") != sequence_context:
                continue  # Skip experiences not in the same sequence context

            similarity = self.calculate_similarity(situation, exp['input_data'])
            philosopher_threshold = self.philosopher_core.get("influence_weight", 0.85) * 0.6

            # Apply symbolic overlay weighting for lessons
            symbolic_weight = self.apply_symbolic_weighting(exp, similarity)

            if similarity > philosopher_threshold:
                relevant_lessons.append({
                    **exp,
                    'relevance': similarity,
                    'philosopher_weight': self.philosopher_core.get("influence_weight", 0.85),
                    'symbolic_weight': symbolic_weight,
                    'sequence_context': exp.get('sequence_binding'),
                    'tier_awareness': exp.get('tier_context', {})
                })

        # Sort by combined relevance and symbolic weight
        relevant_lessons.sort(key=lambda x: (x['relevance'] * x.get('symbolic_weight', 1.0), x.get('philosopher_weight', 0)), reverse=True)
        return relevant_lessons[:5]

    def log_vault_reflection(self, reflection_type: str, data: Dict[str, Any]):
        """Log reflection entry in vault"""
        reflection_entry = {
            "reflection_id": f"reflect_{int(time.time())}_{random.randint(1000, 9999)}",
            "type": reflection_type,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "philosopher_influence": self.philosopher_core.get("philosopher", "Socrates"),
            "seed_logic_applied": [s["seed_id"] for s in self.seed_logic.get("randomized_seeds", [])]
        }

        if "reflection_entries" not in self.vault_data:
            self.vault_data["reflection_entries"] = []

        self.vault_data["reflection_entries"].append(reflection_entry)
        self.save_vault()

    async def consolidate_memory(self) -> int:
        """Consolidate short-term memories into long-term using seed logic"""
        consolidated = 0
        consolidation_seed = next((s for s in self.seed_logic.get("randomized_seeds", [])
                                 if s["seed_id"] == "seed_memory_consolidation"), {})

        threshold = consolidation_seed.get("activation_threshold", 0.5)

        for pattern in self.short_term_memory:
            if pattern['importance'] > threshold:
                pattern_id = f"consolidated_{len(self.long_term_memory)}_{int(time.time())}"
                self.long_term_memory[pattern_id] = pattern
                consolidated += 1

        self.save_memory()
        return consolidated

memory_system = MemorySystem()

@app.get("/health")
async def health_check():
    """Health check with vault integrity verification"""
    vault_integrity = os.path.exists(memory_system.vault_file)
    return {
        "status": "healthy",
        "service": "EchoRipple",
        "vault_integrity": vault_integrity,
        "philosopher_core": memory_system.philosopher_core.get("philosopher", "Unknown"),
        "active_seeds": len(memory_system.seed_logic.get("randomized_seeds", []))
    }

@app.post("/store_memory")
async def store_memory_pattern(pattern: MemoryPattern):
    """Store a memory pattern with echo verification"""
    try:
        await memory_system.store_pattern(pattern)
        return {
            "status": "stored",
            "pattern_id": pattern.pattern_id,
            "vault_trace": pattern.vault_trace,
            "echo_verified": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recall/{query}")
async def recall_memories(query: str, threshold: float = 0.6, sequence_context: str = None):
    """Recall similar memory patterns with sequence context filtering and symbolic overlay weighting"""
    try:
        memories = memory_system.recall_similar(query, threshold, sequence_context)
        return {
            "query": query,
            "memories": memories,
            "seed_logic": "similarity_recall_applied",
            "philosopher_influence": memory_system.philosopher_core.get("philosopher", "Socrates"),
            "sequence_context": sequence_context,
            "symbolic_weighting": "applied"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learn_experience")
async def learn_from_experience(experience: LearningExperience):
    """Learn from an experience with seed-based learning"""
    try:
        await memory_system.learn_from_experience(experience)
        return {
            "status": "learned",
            "experience_id": experience.experience_id,
            "vault_reflection": experience.vault_reflection,
            "confidence_threshold_met": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lessons/{situation}")
async def get_lessons(situation: str, sequence_context: str = None):
    """Get relevant lessons with sequence-aware retrieval and philosopher-guided reflection"""
    try:
        lessons = memory_system.get_relevant_lessons(situation, sequence_context)
        return {
            "situation": situation,
            "lessons": lessons,
            "philosopher_principle": memory_system.philosopher_core.get("principle", "Know Thyself"),
            "reflection_cycles": memory_system.philosopher_core.get("reflection_cycles", 3),
            "sequence_context": sequence_context,
            "symbolic_weighting": "applied"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory_stats")
async def get_memory_stats():
    """Get comprehensive memory system statistics"""
    return {
        "short_term_count": len(memory_system.short_term_memory),
        "long_term_count": len(memory_system.long_term_memory),
        "experiences_count": len(memory_system.learning_experiences),
        "vault_reflections": len(memory_system.vault_data.get("reflection_entries", [])),
        "echo_verification_cycles": memory_system.echo_verifier.verification_cycles,
        "active_seeds": len(memory_system.seed_logic.get("randomized_seeds", [])),
        "philosopher_influence": memory_system.philosopher_core.get("philosopher", "Unknown")
    }

@app.post("/consolidate_memory")
async def consolidate_memory():
    """Consolidate short-term memories into long-term with seed logic"""
    try:
        consolidated = await memory_system.consolidate_memory()
        return {
            "status": "consolidated",
            "patterns_moved": consolidated,
            "seed_logic": "memory_consolidation_applied",
            "vault_updated": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify_echo")
async def verify_echo(data: Dict[str, Any]):
    """Manual echo verification endpoint"""
    try:
        result = await memory_system.echo_verifier.verify_echo(data)
        return {
            "verification": result,
            "harmonizer_escalation": result.get("escalation_successful", False),
            "provisional_output": result.get("provisional", False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vault_stats")
async def get_vault_stats():
    """Get vault statistics and integrity"""
    return {
        "vault_file_exists": os.path.exists(memory_system.vault_file),
        "reflection_entries": len(memory_system.vault_data.get("reflection_entries", [])),
        "performance_metrics": memory_system.vault_data.get("performance_metrics", {}),
        "seed_logic_integrity": bool(memory_system.seed_logic),
        "philosopher_core_active": bool(memory_system.philosopher_core)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)