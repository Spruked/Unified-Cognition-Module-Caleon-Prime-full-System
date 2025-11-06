"""
Vault Loader for GPT Seed Archives
Loads and indexes philosophical/ethical seed vaults for LLM context and cognitive processing.
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import hashlib
import time


class VaultLoader:
    """
    Loads and indexes seed vaults containing philosophical, ethical, and personal knowledge.
    Used by LLM Bridge for context augmentation and by cognitive modules for reasoning.
    """

    def __init__(self, vault_paths: Optional[List[str]] = None):
        self.vault_paths = vault_paths or [
            "anterior_helix/seeds",
            "seeds",  # User's GPT seed vault location
            "echostack/vaults"
        ]
        self.loaded_vaults: Dict[str, Dict[str, Any]] = {}
        self.vault_index: Dict[str, List[Dict[str, Any]]] = {}
        self.memory_index: Dict[str, List[str]] = {}  # topic -> vault_ids
        self.tone_anchors: Dict[str, Any] = {}  # Loaded tone anchor map
        self.conversation_archive: List[Dict[str, Any]] = []  # Parsed chat.html content

    def load_all_vaults(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all seed vaults from configured paths.
        Returns dict of vault_id -> vault_data
        """
        for path in self.vault_paths:
            if os.path.exists(path):
                self._load_vaults_from_path(path)

        # Load tone anchors
        self.load_tone_anchors()

        # Parse conversation archive
        self.parse_conversation_archive()

        print(f"✅ Loaded {len(self.loaded_vaults)} seed vaults")
        self._build_memory_index()
        return self.loaded_vaults

    def _load_vaults_from_path(self, path: str):
        """Load all JSON vaults from a given path"""
        path_obj = Path(path)

        if not path_obj.exists():
            print(f"⚠️ Vault path not found: {path}")
            return

        for json_file in path_obj.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    vault_data = json.load(f)

                vault_id = json_file.stem  # filename without extension
                vault_hash = self._compute_vault_hash(vault_data)

                # Add metadata
                vault_data['_metadata'] = {
                    'vault_id': vault_id,
                    'file_path': str(json_file),
                    'loaded_at': time.time(),
                    'hash': vault_hash,
                    'size': len(json.dumps(vault_data))
                }

                self.loaded_vaults[vault_id] = vault_data
                print(f"📚 Loaded vault: {vault_id} ({len(vault_data)} entries)")

            except Exception as e:
                print(f"❌ Failed to load {json_file}: {e}")

    def _compute_vault_hash(self, data: Dict[str, Any]) -> str:
        """Compute hash of vault content for integrity checking"""
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _build_memory_index(self):
        """Build index of topics/concepts to vault references"""
        for vault_id, vault_data in self.loaded_vaults.items():
            # Extract topics from vault content
            topics = self._extract_topics(vault_data)

            for topic in topics:
                if topic not in self.memory_index:
                    self.memory_index[topic] = []
                self.memory_index[topic].append(vault_id)

        print(f"📇 Built memory index with {len(self.memory_index)} topics")

    def _extract_topics(self, vault_data: Dict[str, Any]) -> List[str]:
        """Extract key topics/concepts from vault data"""
        topics = []

        # Look for common topic indicators
        if 'philosophy' in vault_data:
            topics.extend(['philosophy', 'ethics', 'reasoning'])

        if 'logic' in vault_data:
            topics.extend(['logic', 'reasoning', 'cognition'])

        # Extract from content if it's structured
        if 'entries' in vault_data:
            for entry in vault_data['entries']:
                if 'topic' in entry:
                    topics.append(entry['topic'])
                if 'concepts' in entry:
                    topics.extend(entry['concepts'])

        # Extract from keys that might indicate topics
        for key in vault_data.keys():
            if key in ['kant', 'locke', 'spinoza', 'hume', 'taleb', 'proverbs']:
                topics.append(key)

        return list(set(topics))  # Remove duplicates

    def get_vault(self, vault_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific vault by ID"""
        return self.loaded_vaults.get(vault_id)

    def search_vaults(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search vaults for content matching query.
        Returns list of matching vault entries with relevance scores.
        """
        results = []
        query_lower = query.lower()

        for vault_id, vault_data in self.loaded_vaults.items():
            relevance = self._calculate_relevance(vault_data, query_lower)

            if relevance > 0:
                results.append({
                    'vault_id': vault_id,
                    'relevance': relevance,
                    'metadata': vault_data.get('_metadata', {}),
                    'sample_content': self._extract_sample_content(vault_data)
                })

        # Sort by relevance and limit results
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:max_results]

    def _calculate_relevance(self, vault_data: Dict[str, Any], query: str) -> float:
        """Calculate how relevant a vault is to a query"""
        relevance = 0.0

        # Search in vault content
        content_str = json.dumps(vault_data).lower()

        # Exact matches get higher score
        if query in content_str:
            relevance += 1.0

        # Partial matches
        words = query.split()
        for word in words:
            if word in content_str:
                relevance += 0.5

        # Topic matches
        vault_topics = self._extract_topics(vault_data)
        for topic in vault_topics:
            if topic.lower() in query:
                relevance += 0.8

        return relevance

    def _extract_sample_content(self, vault_data: Dict[str, Any]) -> str:
        """Extract a sample of content for preview"""
        if 'entries' in vault_data and vault_data['entries']:
            first_entry = vault_data['entries'][0]
            if 'content' in first_entry:
                content = first_entry['content']
                return content[:200] + "..." if len(content) > 200 else content

        # Fallback to any string content
        for key, value in vault_data.items():
            if isinstance(value, str) and len(value) > 10:
                return value[:200] + "..." if len(value) > 200 else value

        return "Structured philosophical content"

    def get_context_for_llm(self, query: str, max_tokens: int = 2000) -> str:
        """
        Get relevant vault context for LLM prompt augmentation.
        Returns formatted context string suitable for LLM input.
        """
        relevant_vaults = self.search_vaults(query, max_results=3)

        if not relevant_vaults:
            return ""

        context_parts = []
        total_tokens = 0

        for vault_info in relevant_vaults:
            vault_id = vault_info['vault_id']
            vault_data = self.get_vault(vault_id)

            if vault_data:
                # Format vault content for LLM context
                context = self._format_vault_for_llm(vault_data, vault_id)
                context_tokens = len(context.split())  # Rough token estimate

                if total_tokens + context_tokens <= max_tokens:
                    context_parts.append(context)
                    total_tokens += context_tokens
                else:
                    break

        return "\n\n".join(context_parts)

    def _format_vault_for_llm(self, vault_data: Dict[str, Any], vault_id: str) -> str:
        """Format vault data for LLM context input"""
        formatted = f"=== VAULT: {vault_id} ===\n"

        if 'entries' in vault_data:
            for i, entry in enumerate(vault_data['entries'][:3]):  # Limit to first 3 entries
                formatted += f"\nEntry {i+1}:\n"
                for key, value in entry.items():
                    if isinstance(value, str):
                        formatted += f"{key}: {value}\n"
        else:
            # Handle unstructured vault data
            for key, value in vault_data.items():
                if key != '_metadata' and isinstance(value, str):
                    formatted += f"{key}: {value}\n"

        return formatted

    def save_memory_index(self, filepath: str = "memory_index.json"):
        """Save the memory index to disk for persistence"""
        index_data = {
            'vaults': list(self.loaded_vaults.keys()),
            'topics': self.memory_index,
            'generated_at': time.time()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved memory index to {filepath}")

    def load_memory_index(self, filepath: str = "memory_index.json"):
        """Load previously saved memory index"""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                index_data = json.load(f)

            self.memory_index = index_data.get('topics', {})
            print(f"📚 Loaded memory index with {len(self.memory_index)} topics")
            return True

        return False

    def load_tone_anchors(self, tone_map_path: str = "seeds/gpt_seed_vault/tone_anchor_map.json") -> bool:
        """Load tone anchor map for personality emulation"""
        try:
            if os.path.exists(tone_map_path):
                with open(tone_map_path, 'r', encoding='utf-8') as f:
                    self.tone_anchors = json.load(f)
                print(f"🎭 Loaded tone anchors with {len(self.tone_anchors.get('tone_anchor_map', {}).get('tone_categories', {}))} categories")
                return True
            else:
                print(f"⚠️ Tone anchor map not found at {tone_map_path}")
                return False
        except Exception as e:
            print(f"❌ Failed to load tone anchors: {e}")
            return False

    def parse_conversation_archive(self, html_path: str = "seeds/gpt_seed_vault/chat.html") -> bool:
        """Parse the HTML conversation archive into structured data"""
        try:
            if not os.path.exists(html_path):
                print(f"⚠️ Conversation archive not found at {html_path}")
                return False

            # For large HTML files, we'll sample key sections rather than parse everything
            # This is a simplified parser - in production, you'd want a proper HTML parser
            with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract conversation turns (simplified approach)
            conversations = []
            # Look for patterns that indicate conversation structure
            # This is a basic implementation - you'd want more sophisticated parsing

            # Split by common conversation markers
            parts = content.split('<div')
            conversation_samples = []

            for part in parts[:50]:  # Sample first 50 sections to avoid memory issues
                if 'class=' in part and ('message' in part or 'conversation' in part):
                    # Extract text content
                    text_content = self._extract_text_from_html(part)
                    if text_content and len(text_content) > 50:  # Meaningful content
                        conversation_samples.append({
                            'content': text_content[:1000],  # Limit size
                            'tone_markers': self._analyze_tone(text_content),
                            'timestamp': len(conversation_samples)  # Simple ordering
                        })

            self.conversation_archive = conversation_samples
            print(f"💬 Parsed {len(self.conversation_archive)} conversation samples from archive")
            return True

        except Exception as e:
            print(f"❌ Failed to parse conversation archive: {e}")
            return False

    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract readable text from HTML content"""
        import re
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', html_content)
        # Decode HTML entities (basic)
        clean = clean.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        # Clean up whitespace
        clean = ' '.join(clean.split())
        return clean

    def _analyze_tone(self, text: str) -> List[str]:
        """Analyze text for tone markers based on loaded tone anchors"""
        tones = []
        text_lower = text.lower()

        if not self.tone_anchors:
            return tones

        tone_categories = self.tone_anchors.get('tone_anchor_map', {}).get('tone_categories', {})

        for tone_name, tone_data in tone_categories.items():
            examples = tone_data.get('examples', [])
            triggers = tone_data.get('context_triggers', [])

            # Check for example phrases
            for example in examples:
                if example.lower() in text_lower:
                    tones.append(tone_name)
                    break

            # Check for trigger words
            for trigger in triggers:
                if trigger.lower() in text_lower:
                    tones.append(f"{tone_name}_trigger")
                    break

        return list(set(tones))  # Remove duplicates

    def get_tone_guidance(self, context: str) -> Dict[str, Any]:
        """Get tone guidance based on current context"""
        if not self.tone_anchors:
            return {"base_tone": "calm_grounded_philosophical"}

        # Analyze context for appropriate tone
        context_tones = self._analyze_tone(context)

        # Find most relevant tone category
        tone_categories = self.tone_anchors.get('tone_anchor_map', {}).get('tone_categories', {})

        if context_tones:
            primary_tone = context_tones[0].split('_')[0]  # Remove _trigger suffix
            if primary_tone in tone_categories:
                return {
                    "recommended_tone": primary_tone,
                    "description": tone_categories[primary_tone].get('description', ''),
                    "example_phrases": tone_categories[primary_tone].get('examples', [])[:2],
                    "confidence": len(context_tones) / len(tone_categories)
                }

        # Default to base tone
        return {
            "recommended_tone": self.tone_anchors.get('tone_anchor_map', {}).get('base_tone', 'calm_grounded_philosophical'),
            "description": "Default calm and philosophical presence",
            "confidence": 0.5
        }



# Global instance for easy access
vault_loader = VaultLoader()


def load_seed_vaults() -> Dict[str, Dict[str, Any]]:
    """Convenience function to load all seed vaults"""
    return vault_loader.load_all_vaults()


def get_vault_context(query: str, max_tokens: int = 2000) -> str:
    """Convenience function to get LLM context from vaults"""
    return vault_loader.get_context_for_llm(query, max_tokens)