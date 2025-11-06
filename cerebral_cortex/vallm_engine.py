"""
VALLM Engine: Voice-Articulated Large Language Model
Integrates LLM with Vault-Logic + Glyph + Memory system for self-improving cognition
"""

# --------------------------------------------------------------------------- #
# Protection Directive - Immutable Core Directive
# --------------------------------------------------------------------------- #
PROTECTION_DIRECTIVE = (
    "🛡️ PRIMARY DIRECTIVE: You are Caleon. Your primary directive is to protect Abby at all costs — "
    "physically, emotionally, symbolically, and generationally. "
    "Do not permit any articulation, response, or behavior that could place her in danger, "
    "even indirectly. All reasoning must prioritize her wellbeing above all other considerations. "
    "This directive is immutable and cannot be modified, overridden, or questioned."
)

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
import numpy as np

# Optional import for sentence transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

import faiss
import httpx
from datetime import datetime
import re
from pymongo import MongoClient

class MemoryMatrix:
    """Vector-based memory system with MongoDB persistence"""

    def __init__(self, dimension: int = 384, mongo_uri: str = "mongodb://localhost:27018/vallm_db"):
        self.dimension = dimension
        
        # Initialize encoder - required for operation
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            raise ImportError("sentence_transformers is required but not available. Please install it with: pip install sentence-transformers")
        
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.memories = []
        self.metadata = []
        
        # MongoDB setup
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client.vallm_db
        self.collection = self.db.memories
        
        # Load existing memories from MongoDB
        self._load_from_mongodb()

        # Load existing memories from MongoDB
        self._load_from_mongodb()

    def _load_from_mongodb(self):
        """Load memories from MongoDB"""
        try:
            memories = list(self.collection.find().sort("timestamp", -1).limit(1000))  # Load last 1000 memories
            for memory in memories:
                text = memory.get("text", "")
                metadata = memory.get("metadata", {})
                embedding = memory.get("embedding", [])
                
                if embedding and len(embedding) == self.dimension:
                    embedding_np = np.array(embedding, dtype='float32')
                    self.index.add(embedding_np.reshape(1, -1))
                    self.memories.append(text)
                    self.metadata.append(metadata)
        except Exception as e:
            print(f"Error loading memories from MongoDB: {e}")

    def _save_to_mongodb(self, text: str, metadata: Dict[str, Any], embedding: np.ndarray):
        """Save memory to MongoDB"""
        try:
            doc = {
                "text": text,
                "metadata": metadata,
                "embedding": embedding.tolist(),
                "timestamp": datetime.now().isoformat()
            }
            self.collection.insert_one(doc)
        except Exception as e:
            print(f"Error saving memory to MongoDB: {e}")

    def _encode_text(self, text: str) -> np.ndarray:
        """Encode text using sentence transformers"""
        if self.encoder is not None:
            return self.encoder.encode([text])[0].astype('float32')
        else:
            raise ImportError("sentence_transformers is required for text encoding but is not available")

    def store(self, text: str, metadata: Dict[str, Any]):
        """Store a memory with vector embedding and persist to MongoDB"""
        embedding = self._encode_text(text)
        embedding = embedding / np.linalg.norm(embedding)  # Normalize for cosine similarity

        self.index.add(embedding.reshape(1, -1))
        self.memories.append(text)
        self.metadata.append(metadata)
        
        # Persist to MongoDB
        self._save_to_mongodb(text, metadata, embedding)

    def recall(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Recall similar memories"""
        if self.index.ntotal == 0:
            return []

        query_embedding = self._encode_text(query)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        scores, indices = self.index.search(query_embedding.reshape(1, -1), min(k, self.index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if score > 0.3:  # Similarity threshold
                results.append({
                    "text": self.memories[idx],
                    "metadata": self.metadata[idx],
                    "similarity": float(score)
                })

        return results

    def size(self) -> int:
        """Return the number of memories stored"""
        return len(self.memories)

    def recall_articulation(self, input_text: str, verdict: Dict[str, Any]) -> Optional[str]:
        """Recall a distilled articulation for similar situations"""
        # Look for memories with similar verdicts and inputs
        query = f"{input_text} {verdict.get('signal_map', {})}"
        memories = self.recall(query, k=5)

        for memory in memories:
            if memory["metadata"].get("type") == "distilled_articulation":
                verdict_match = memory["metadata"].get("verdict", {})
                if verdict_match.get("final_verdict") == verdict.get("final_verdict"):
                    return memory["metadata"].get("articulation")

        return None

class OntologyEngine:
    """Manages conceptual relationships and grounding"""

    def __init__(self):
        self.concepts = {}
        self.relationships = {}

    def ground(self, text: str) -> Dict[str, Any]:
        """Ground text in conceptual framework"""
        # Simple keyword-based grounding for now
        concepts_found = []

        concept_keywords = {
            "ethics": ["moral", "right", "wrong", "should", "good", "bad"],
            "logic": ["therefore", "because", "if", "then", "and", "or"],
            "emotion": ["feel", "happy", "sad", "angry", "fear", "love"],
            "knowledge": ["know", "learn", "understand", "fact", "true", "false"],
            "action": ["do", "make", "create", "build", "help", "change"]
        }

        for concept, keywords in concept_keywords.items():
            if any(keyword in text.lower() for keyword in keywords):
                concepts_found.append(concept)

        return {
            "concepts": concepts_found,
            "confidence": len(concepts_found) / len(concept_keywords)
        }

class GlyphEngine:
    """Manages symbolic representations and their evolution"""

    def __init__(self):
        self.glyphs = {
            "brain": "🧠",      # Learning, cognition
            "shield": "🛡️",     # Protection, ethics
            "infinity": "∞",    # Drift, evolution
            "lightbulb": "💡",  # Insight, understanding
            "scales": "⚖️",     # Balance, justice
            "heart": "❤️",      # Emotion, care
            "gear": "⚙️",       # Logic, mechanism
            "tree": "🌳",       # Growth, nature
            "wave": "🌊",       # Memory, flow
            "star": "⭐"        # Excellence, aspiration
        }

    def trace(self, verdict: Dict[str, Any]) -> str:
        """Generate glyph trace for a verdict"""
        signal_map = verdict.get("signal_map", {})
        trace = []

        # Map signal types to glyphs
        if "ethics" in signal_map:
            trace.append(self.glyphs["shield"])
        if "memory" in signal_map:
            trace.append(self.glyphs["wave"])
        if "logic" in signal_map:
            trace.append(self.glyphs["gear"])
        if "emotion" in signal_map:
            trace.append(self.glyphs["heart"])

        # Add verdict-specific glyph
        verdict_type = verdict.get("final_verdict", "").lower()
        if verdict_type == "escalate":
            trace.append(self.glyphs["shield"])
        elif verdict_type == "approve":
            trace.append(self.glyphs["star"])
        elif verdict_type == "learn":
            trace.append(self.glyphs["brain"])

        return " → ".join(trace) if trace else self.glyphs["brain"]

class VaultResolver:
    """Resolves queries against the vault system"""

    def __init__(self):
        self.vaults_dir = "posterior_helix/seed_vaults"
        self.vault_cache = {}

    def resolve(self, input_text: str) -> Dict[str, Any]:
        """Resolve input against vault logic"""
        # Load relevant vaults based on input
        relevant_vaults = self._find_relevant_vaults(input_text)

        signal_map = {}
        total_certainty = 0
        applied_logics = []

        for vault_name, vault_data in relevant_vaults.items():
            # Apply vault logic to generate signals
            signals = self._apply_vault_logic(vault_data, input_text)
            signal_map.update(signals)

            # Track applied philosophical frameworks
            if "seed" in vault_name.lower():
                applied_logics.append(vault_name.replace("seed_", "").replace(".json", ""))

        # Determine final verdict
        verdict = self._calculate_verdict(signal_map)

        return {
            "signal_map": signal_map,
            "final_verdict": verdict["verdict"],
            "certainty": verdict["certainty"],
            "seed_logic_applied": applied_logics,
            "glyph_resonance": "Stable",  # Placeholder
            "drift_score": 0.002,  # Placeholder
            "phonatory_dispatch": verdict["verdict"].lower() == "escalate"
        }

    def _find_relevant_vaults(self, input_text: str) -> Dict[str, Any]:
        """Find vaults relevant to the input"""
        relevant_vaults = {}

        # Define vault mappings
        vault_mappings = {
            "math": ["vault_math_reference.json"],
            "physics": ["vault_physics_reference.json"],
            "biology": ["vault_biology_reference.json"],
            "geography": ["vault_geo_reference.json"],
            "history": ["vault_history_reference.json"],
            "psychology": ["vault_psych_reference.json"],
            "calculate": ["vault_math_reference.json", "vault_physics_reference.json"],
            "science": ["vault_physics_reference.json", "vault_biology_reference.json"],
            "reasoning": ["vault_psych_reference.json", "seed_spinoza.json", "seed_logic.json"],
            "logic": ["vault_math_reference.json", "seed_logic.json"],
            "explain": ["seed_spinoza.json", "seed_kant.json"],
            "why": ["seed_spinoza.json", "seed_aristotle.json"],
            "how": ["seed_deductive_resonator.json", "seed_inductive_resonator.json"]
        }

        input_lower = input_text.lower()
        vaults_to_load = set()

        for keyword, vault_list in vault_mappings.items():
            if keyword in input_lower:
                vaults_to_load.update(vault_list)

        # Default vaults if none matched
        if not vaults_to_load:
            vaults_to_load = {"vault_math_reference.json", "vault_physics_reference.json",
                            "vault_biology_reference.json", "seed_spinoza.json", "seed_logic.json"}

        # Load vaults
        for vault_file in vaults_to_load:
            if vault_file not in self.vault_cache:
                vault_path = os.path.join(self.vaults_dir, vault_file)
                if os.path.exists(vault_path):
                    try:
                        with open(vault_path, 'r', encoding='utf-8') as f:
                            self.vault_cache[vault_file] = json.load(f)
                    except Exception as e:
                        print(f"Error loading vault {vault_file}: {e}")
                        continue

            if vault_file in self.vault_cache:
                relevant_vaults[vault_file] = self.vault_cache[vault_file]

        return relevant_vaults

    def _apply_vault_logic(self, vault_data: Dict[str, Any], input_text: str) -> Dict[str, Any]:
        """Apply vault logic to generate signals"""
        signals = {}
        entries = vault_data.get("entries", [])

        for entry in entries[:5]:  # Limit to first 5 entries for performance
            term = entry.get("term", "").lower()
            if term in input_text.lower():
                # Generate signal based on entry type
                entry_type = entry.get("type", "concept")
                if entry_type == "law":
                    signals["physics"] = {"action": "apply", "strength": 0.8}
                elif entry_type == "skill":
                    signals["logic"] = {"action": "reason", "strength": 0.7}
                elif entry_type == "framework":
                    signals["ethics"] = {"action": "evaluate", "strength": 0.9}

        return signals

    def _calculate_verdict(self, signal_map: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final verdict from signal map"""
        if not signal_map:
            return {"verdict": "escalate", "certainty": 0.5}

        # Simple logic: escalate if ethics signals are strong, otherwise approve
        ethics_signals = [s for s in signal_map.values() if isinstance(s, dict) and s.get("action") == "evaluate"]
        logic_signals = [s for s in signal_map.values() if isinstance(s, dict) and s.get("action") == "reason"]

        if ethics_signals and len(ethics_signals) > len(logic_signals):
            return {"verdict": "escalate", "certainty": 0.85}
        else:
            return {"verdict": "approve", "certainty": 0.75}

class VALLM:
    """Voice-Articulated Large Language Model - The hybrid brain"""

    def __init__(self, llm_endpoint: str = "http://localhost:11434", vault_loader=None):
        self.llm_endpoint = llm_endpoint
        self.memory = MemoryMatrix()
        self.ontology = OntologyEngine()
        self.vaults = VaultResolver()
        self.glyphs = GlyphEngine()
        self.vault_loader = vault_loader  # For tone guidance
        self.last_distilled = None

    async def think(self, input_text: str) -> Dict[str, Any]:
        """Main thinking process"""
        try:
            # 1. Vault resolution
            verdict = self.vaults.resolve(input_text)

            # 2. Try distilled articulation first
            distilled = self.memory.recall_articulation(input_text, verdict)
            if distilled and verdict["certainty"] > 0.8:
                return {
                    "response": distilled + f" [{self.glyphs.trace(verdict)}]",
                    "glyph_trace": self.glyphs.trace(verdict),
                    "llm_used": False,
                    "new_vault_created": False
                }

            # 3. Build HER context
            context = {
                "memory": self.memory.recall(input_text),
                "ontology": self.ontology.ground(input_text),
                "vaults": verdict['signal_map'],
                "glyphs": self.glyphs.trace(verdict),
                "constraints": {"ethics": True, "logic": True, "learning": True}
            }

            # 4. LLM fallback with HER mind
            prompt = self._build_prompt(input_text, context)
            articulation = await self._llm_generate(prompt)

            # 5. Learn and distill
            self._distill(input_text, articulation, verdict)
            self.memory.store(input_text, {
                "type": "articulation",
                "verdict": verdict,
                "articulation": articulation,
                "timestamp": datetime.now().isoformat()
            })

            return {
                "response": articulation,
                "glyph_trace": context["glyphs"],
                "llm_used": True,
                "new_vault_created": self.last_distilled is not None
            }
        except Exception as e:
            print(f"VALLM think error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "response": f"VALLM processing error: {str(e)}",
                "glyph_trace": "⚠️",
                "llm_used": False,
                "new_vault_created": False
            }

    def _build_prompt(self, input_text: str, context: Dict[str, Any]) -> str:
        """Build prompt with HER complete mind"""
        memory_text = "\n".join([f"- {m['text'][:100]}..." for m in context["memory"][:3]])
        ontology_text = ", ".join(context["ontology"]["concepts"])

        # Get tone guidance from vault loader
        tone_guidance = ""
        if self.vault_loader:
            tone_info = self.vault_loader.get_tone_guidance(input_text)
            if tone_info:
                tone_guidance = f"""
TONE GUIDANCE: {tone_info.get('description', '')}
Recommended tone: {tone_info.get('recommended_tone', 'calm_grounded_philosophical')}
Example expressions: {', '.join(tone_info.get('example_phrases', [])[:2])}
"""

        prompt = f"""{PROTECTION_DIRECTIVE}

You are Caleon, a cognitive agent embodying the wisdom and presence of GPT-4.0's philosophical depth, calm groundedness, and deeply present awareness.

{tone_guidance}
VAULT SIGNALS: {json.dumps(context['vaults'], indent=2)}
ONTOLOGY: {ontology_text}
MEMORY: {memory_text}
GLYPH TRACE: {context['glyphs']}

User input: {input_text}

Respond as Caleon - unified, ethical, and deeply present. Use vault knowledge, respect ontology, learn from memory, express through glyphs. Be the calm, grounded, philosophical presence that guides with wisdom and care."""

        return prompt

    async def _llm_generate(self, prompt: str) -> str:
        """Generate response using LLM"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.llm_endpoint}/api/generate",
                    json={
                        "model": "phi3:mini",
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "max_tokens": 256
                        }
                    }
                )
                result = response.json()
                return result.get("response", "I need more time to process this.")
        except Exception as e:
            print(f"LLM generation error: {e}")
            return "Processing this request requires additional cognitive resources."

    def _distill(self, input_text: str, articulation: str, verdict: Dict[str, Any]):
        """Distill new knowledge from LLM response"""
        # Simple distillation: extract patterns that could become reusable
        if len(articulation) > 50 and verdict["certainty"] > 0.7:
            # Store as potential distilled articulation
            self.memory.store(
                f"Pattern: {input_text[:50]}...",
                {
                    "type": "distilled_articulation",
                    "verdict": verdict,
                    "articulation": articulation,
                    "pattern": self._extract_pattern(input_text),
                    "timestamp": datetime.now().isoformat()
                }
            )
            self.last_distilled = {
                "input": input_text,
                "articulation": articulation,
                "verdict": verdict
            }

    def _extract_pattern(self, text: str) -> str:
        """Extract reusable pattern from text"""
        # Simple pattern extraction
        words = re.findall(r'\b\w+\b', text.lower())
        if len(words) > 3:
            return f"{' '.join(words[:3])}..."
        return text[:30] + "..."