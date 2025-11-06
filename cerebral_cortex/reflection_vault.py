import json
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class ReflectionVault:
    """
    Anterior Reflection Vault - Autonomous learning and ethical reasoning system
    Enables modules to reflect on past decisions and improve future reasoning
    """

    def __init__(self, vault_path: str, module_name: str):
        self.vault_path = vault_path
        self.module_name = module_name
        self.vault_data = self._load_vault()
        self.idle_timer = None
        self.is_idle = False
        self.last_activity = datetime.now()

        # Start idle monitoring
        self.idle_thread = threading.Thread(target=self._idle_monitor, daemon=True)
        self.idle_thread.start()

    def _load_vault(self) -> Dict[str, Any]:
        """Load existing vault data or create new vault structure"""
        if os.path.exists(self.vault_path):
            try:
                with open(self.vault_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load vault {self.vault_path}: {e}")

        # Create new vault structure
        return {
            "vault_name": f"{self.module_name}_reflection_vault.json",
            "schema": {
                "case_id": "string",
                "timestamp": "ISO8601",
                "emotional_context": "string",
                "ethical_dilemma": "string",
                "initial_decision": "string",
                "refined_reasoning": "string",
                "lesson": "string",
                "type": "absolute | conditional",
                "priority_tags": ["conflict", "emotion", "urgency"],
                "resolution_status": "resolved | unresolved | unstable"
            },
            "entries": [],
            "idle_loop": {
                "frequency_minutes": 15,
                "reflection_duration_seconds": 120,
                "priority_tags": ["conflict", "emotion", "urgency"],
                "autonomy_rule": "Choose unresolved or unstable emotional/ethical cases and determine better action logic if found."
            },
            "statistics": {
                "total_entries": 0,
                "resolved_cases": 0,
                "unresolved_cases": 0,
                "last_reflection": None,
                "reflection_cycles": 0
            }
        }

    def _save_vault(self):
        """Save vault data to disk"""
        try:
            with open(self.vault_path, 'w') as f:
                json.dump(self.vault_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save vault {self.vault_path}: {e}")

    def log_reflection(self, case_id: str, emotional_context: str, ethical_dilemma: str,
                       initial_decision: str, refined_reasoning: str, lesson: str,
                       reflection_type: str = "conditional",
                       priority_tags: List[str] = None,
                       resolution_status: str = "unresolved"):
        """
        Log a new reflection entry to the vault

        Args:
            case_id: Unique identifier for the decision case
            emotional_context: Emotional tone during the decision
            ethical_dilemma: Description of the moral conflict
            initial_decision: What was originally chosen
            refined_reasoning: Updated logic after reflection
            lesson: Insight gained
            reflection_type: "absolute" or "conditional"
            priority_tags: List of tags like ["conflict", "emotion", "urgency"]
            resolution_status: "resolved", "unresolved", or "unstable"
        """
        entry = {
            "case_id": case_id,
            "timestamp": datetime.now().isoformat(),
            "emotional_context": emotional_context,
            "ethical_dilemma": ethical_dilemma,
            "initial_decision": initial_decision,
            "refined_reasoning": refined_reasoning,
            "lesson": lesson,
            "type": reflection_type,
            "priority_tags": priority_tags or [],
            "resolution_status": resolution_status,
            "module": self.module_name
        }

        self.vault_data["entries"].append(entry)
        self.vault_data["statistics"]["total_entries"] += 1

        if resolution_status == "resolved":
            self.vault_data["statistics"]["resolved_cases"] += 1
        else:
            self.vault_data["statistics"]["unresolved_cases"] += 1

        self._save_vault()
        logger.info(f"Logged reflection for case {case_id} in {self.module_name}")

    def query_vault(self, query_type: str = "unresolved", tags: List[str] = None,
                   limit: int = 10) -> List[Dict[str, Any]]:
        """
        Query the vault for specific types of reflections

        Args:
            query_type: "unresolved", "resolved", "unstable", "all"
            tags: List of priority tags to filter by
            limit: Maximum number of entries to return
        """
        entries = self.vault_data.get("entries", [])

        if query_type != "all":
            entries = [e for e in entries if e.get("resolution_status") == query_type]

        if tags:
            entries = [e for e in entries if any(tag in e.get("priority_tags", []) for tag in tags)]

        # Sort by timestamp (most recent first)
        entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return entries[:limit]

    def update_resolution_status(self, case_id: str, new_status: str, refined_reasoning: str = None):
        """Update the resolution status of an existing case"""
        for entry in self.vault_data.get("entries", []):
            if entry.get("case_id") == case_id:
                old_status = entry.get("resolution_status")
                entry["resolution_status"] = new_status
                if refined_reasoning:
                    entry["refined_reasoning"] = refined_reasoning
                entry["last_updated"] = datetime.now().isoformat()

                # Update statistics
                if old_status != "resolved" and new_status == "resolved":
                    self.vault_data["statistics"]["resolved_cases"] += 1
                    self.vault_data["statistics"]["unresolved_cases"] -= 1

                self._save_vault()
                logger.info(f"Updated case {case_id} status to {new_status}")
                break

    def get_insights_for_case(self, input_pattern: str, emotional_context: str = None) -> Dict[str, Any]:
        """
        Get relevant insights from past reflections for a new case

        Args:
            input_pattern: The new input/query to find similar cases for
            emotional_context: Current emotional state

        Returns:
            Dictionary with relevant insights and lessons learned
        """
        relevant_entries = []

        # Find entries with similar emotional context or related dilemmas
        for entry in self.vault_data.get("entries", []):
            if emotional_context and entry.get("emotional_context") == emotional_context:
                relevant_entries.append(entry)
            elif any(word in input_pattern.lower() for word in entry.get("ethical_dilemma", "").lower().split()):
                relevant_entries.append(entry)

        if not relevant_entries:
            return {"insights": [], "recommendations": []}

        # Extract lessons and refined reasoning
        insights = []
        recommendations = []

        for entry in relevant_entries[:3]:  # Top 3 most relevant
            insights.append({
                "lesson": entry.get("lesson", ""),
                "refined_reasoning": entry.get("refined_reasoning", ""),
                "case_id": entry.get("case_id")
            })

            if entry.get("resolution_status") == "resolved":
                recommendations.append(entry.get("refined_reasoning", ""))

        return {
            "insights": insights,
            "recommendations": recommendations,
            "similar_cases_count": len(relevant_entries)
        }

    def _idle_monitor(self):
        """Monitor for idle periods and trigger autonomous reflection"""
        while True:
            time.sleep(60)  # Check every minute

            now = datetime.now()
            idle_threshold = timedelta(minutes=self.vault_data["idle_loop"]["frequency_minutes"])

            if now - self.last_activity > idle_threshold and not self.is_idle:
                self.is_idle = True
                logger.info(f"{self.module_name} entering idle state, starting reflection cycle")
                self._perform_idle_reflection()

    def _perform_idle_reflection(self):
        """Perform autonomous reflection during idle periods"""
        try:
            reflection_duration = self.vault_data["idle_loop"]["reflection_duration_seconds"]
            priority_tags = self.vault_data["idle_loop"]["priority_tags"]

            # Find unresolved or unstable cases with priority tags
            target_entries = []
            for entry in self.vault_data.get("entries", []):
                if entry.get("resolution_status") in ["unresolved", "unstable"]:
                    if any(tag in entry.get("priority_tags", []) for tag in priority_tags):
                        target_entries.append(entry)

            if not target_entries:
                logger.info(f"No priority cases found for reflection in {self.module_name}")
                return

            # Select case autonomously (prioritize most recent unstable cases)
            target_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            selected_case = target_entries[0]

            logger.info(f"{self.module_name} autonomously reflecting on case: {selected_case.get('case_id')}")

            # Simulate reflection process (in real implementation, this would involve actual reasoning)
            # For now, we'll mark as resolved with improved reasoning
            refined_reasoning = f"Autonomous reflection: {selected_case.get('initial_decision')} improved through idle processing. {selected_case.get('ethical_dilemma')} resolved with enhanced ethical consideration."

            lesson = f"Autonomous reflection revealed that {selected_case.get('emotional_context')} contexts benefit from additional processing time and cross-referencing with similar cases."

            self.update_resolution_status(
                selected_case["case_id"],
                "resolved",
                refined_reasoning
            )

            # Log the autonomous reflection
            self.log_reflection(
                case_id=f"auto_reflection_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                emotional_context="autonomous_processing",
                ethical_dilemma=f"Autonomous review of case {selected_case['case_id']}",
                initial_decision="Idle state reflection initiated",
                refined_reasoning=refined_reasoning,
                lesson=lesson,
                reflection_type="absolute",
                priority_tags=["autonomous", "reflection"],
                resolution_status="resolved"
            )

            self.vault_data["statistics"]["reflection_cycles"] += 1
            self.vault_data["statistics"]["last_reflection"] = datetime.now().isoformat()
            self._save_vault()

            logger.info(f"{self.module_name} completed autonomous reflection cycle")

        except Exception as e:
            logger.error(f"Error during idle reflection in {self.module_name}: {e}")

    def record_activity(self):
        """Record that activity occurred, resetting idle timer"""
        self.last_activity = datetime.now()
        self.is_idle = False

    def get_vault_statistics(self) -> Dict[str, Any]:
        """Get vault statistics and health metrics"""
        return self.vault_data.get("statistics", {})