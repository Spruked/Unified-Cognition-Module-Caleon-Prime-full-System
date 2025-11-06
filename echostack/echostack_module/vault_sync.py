"""
Vault Synchronization Module - Protocol Compliance & Harmonizer Health
Provides vault synchronization capabilities with protocol compliance checking and harmonizer health scoring.
"""

import json
import hashlib
import time
from typing import Dict, Any, List, Optional, Tuple, Set, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import threading
import os


class ComplianceLevel(Enum):
    FULL = "full"
    PARTIAL = "partial"
    MINIMAL = "minimal"
    NON_COMPLIANT = "non_compliant"


class HarmonizerState(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    FAILED = "failed"


@dataclass
class ProtocolRule:
    """Represents a protocol compliance rule"""
    name: str
    description: str
    required_fields: List[str]
    validation_function: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
    severity: str = "medium"  # low, medium, high, critical


@dataclass
class HarmonizerScore:
    """Represents harmonizer health scoring"""
    vault_name: str
    compliance_score: float  # 0.0 to 1.0
    integrity_score: float   # 0.0 to 1.0
    coherence_score: float   # 0.0 to 1.0
    overall_health: float    # 0.0 to 1.0
    state: HarmonizerState
    last_updated: datetime
    issues: List[str]


class VaultSynchronizer:
    """
    Vault Synchronization System with Protocol Compliance and Harmonizer Health Scoring
    """

    def __init__(self, vault_directory: str = "../seed_logic_vault", telemetry_path: str = "../telemetry.json"):
        self.vault_directory = vault_directory
        self.telemetry_path = telemetry_path
        self.protocol_rules: Dict[str, ProtocolRule] = {}
        self.harmonizer_scores: Dict[str, HarmonizerScore] = {}
        self.sync_history: List[Dict[str, Any]] = []
        self.running = False
        self.sync_thread: Optional[threading.Thread] = None
        self.sync_interval = 300  # 5 minutes

        # Protocol compliance rules
        self._initialize_protocol_rules()

    def start_synchronization(self):
        """Start the vault synchronization process"""
        if self.running:
            return

        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        print("[VaultSync] Synchronization service started")

    def stop_synchronization(self):
        """Stop the vault synchronization process"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5.0)
        print("[VaultSync] Synchronization service stopped")

    def perform_sync(self) -> Dict[str, Any]:
        """Perform a complete vault synchronization"""
        print("[VaultSync] Starting vault synchronization...")

        vault_files = self._discover_vault_files()
        compliance_results = {}
        harmonizer_scores = {}

        for vault_file in vault_files:
            vault_name = os.path.splitext(os.path.basename(vault_file))[0]
            print(f"[VaultSync] Processing vault: {vault_name}")

            # Load vault content
            vault_content = self._load_vault_content(vault_file)
            if not vault_content:
                continue

            # Check protocol compliance
            compliance = self._check_protocol_compliance(vault_content, vault_name)
            compliance_results[vault_name] = compliance

            # Calculate harmonizer health score
            score = self._calculate_harmonizer_score(vault_content, vault_name, compliance)
            harmonizer_scores[vault_name] = score

        # Update harmonizer scores
        self.harmonizer_scores = harmonizer_scores

        # Update telemetry
        self._update_telemetry(compliance_results, harmonizer_scores)

        # Record sync event
        sync_result = {
            "timestamp": datetime.now().isoformat(),
            "vaults_processed": len(vault_files),
            "compliance_results": compliance_results,
            "harmonizer_scores": {k: v.__dict__ for k, v in harmonizer_scores.items()},
            "overall_health": self._calculate_overall_health(harmonizer_scores)
        }

        self.sync_history.append(sync_result)

        print(f"[VaultSync] Synchronization completed. Overall health: {sync_result['overall_health']:.2f}")
        return sync_result

    def _initialize_protocol_rules(self):
        """Initialize protocol compliance rules"""
        self.protocol_rules = {
            "structure_integrity": ProtocolRule(
                name="Structure Integrity",
                description="Vault must have proper JSON structure with required fields",
                required_fields=["philosopher", "entries", "learning_principles"],
                severity="critical"
            ),
            "entry_completeness": ProtocolRule(
                name="Entry Completeness",
                description="Each entry must have all required fields",
                required_fields=["id", "title", "content", "category", "confidence"],
                severity="high"
            ),
            "learning_principles": ProtocolRule(
                name="Learning Principles",
                description="Vault must define learning principles for integration",
                required_fields=["learning_principles"],
                severity="medium"
            ),
            "operational_context": ProtocolRule(
                name="Operational Context",
                description="Vault must provide operational context for EchoStack integration",
                required_fields=["operational_context"],
                severity="medium"
            ),
            "validation_metadata": ProtocolRule(
                name="Validation Metadata",
                description="Vault must include validation and versioning metadata",
                required_fields=["version", "last_updated"],
                severity="low"
            )
        }

    def _discover_vault_files(self) -> List[str]:
        """Discover all vault files in the directory"""
        if not os.path.exists(self.vault_directory):
            print(f"[VaultSync] Vault directory not found: {self.vault_directory}")
            return []

        vault_files = []
        for file in os.listdir(self.vault_directory):
            if file.endswith('.json'):
                vault_files.append(os.path.join(self.vault_directory, file))

        return vault_files

    def _load_vault_content(self, vault_path: str) -> Optional[Dict[str, Any]]:
        """Load vault content from file"""
        try:
            with open(vault_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[VaultSync] Failed to load vault {vault_path}: {e}")
            return None

    def _check_protocol_compliance(self, vault_content: Dict[str, Any], vault_name: str) -> Dict[str, Any]:
        """Check protocol compliance for a vault"""
        compliance_results = {
            "vault_name": vault_name,
            "overall_compliance": ComplianceLevel.FULL,
            "rule_results": {},
            "issues": []
        }

        for rule_name, rule in self.protocol_rules.items():
            rule_result = self._check_single_rule(vault_content, rule)
            compliance_results["rule_results"][rule_name] = rule_result

            if not rule_result["compliant"]:
                compliance_results["issues"].append(f"{rule_name}: {rule_result['message']}")

                # Update overall compliance level
                if rule.severity == "critical":
                    compliance_results["overall_compliance"] = ComplianceLevel.NON_COMPLIANT
                elif rule.severity == "high" and compliance_results["overall_compliance"] == ComplianceLevel.FULL:
                    compliance_results["overall_compliance"] = ComplianceLevel.MINIMAL
                elif rule.severity == "medium" and compliance_results["overall_compliance"] in [ComplianceLevel.FULL, ComplianceLevel.PARTIAL]:
                    compliance_results["overall_compliance"] = ComplianceLevel.PARTIAL

        return compliance_results

    def _check_single_rule(self, vault_content: Dict[str, Any], rule: ProtocolRule) -> Dict[str, Any]:
        """Check compliance for a single rule"""
        result = {
            "compliant": True,
            "message": "Rule passed",
            "severity": rule.severity
        }

        # Check required fields at vault level
        for field in rule.required_fields:
            if field not in vault_content:
                result["compliant"] = False
                result["message"] = f"Missing required field: {field}"
                return result

        # Special validation for entries
        if rule.name == "Entry Completeness" and "entries" in vault_content:
            entries = vault_content["entries"]
            if not isinstance(entries, list):
                result["compliant"] = False
                result["message"] = "Entries must be a list"
                return result

            for i, entry in enumerate(entries):
                for field in rule.required_fields:
                    if field not in entry:
                        result["compliant"] = False
                        result["message"] = f"Entry {i} missing required field: {field}"
                        return result

        # Custom validation if provided
        if rule.validation_function:
            try:
                custom_result = rule.validation_function(vault_content)
                if not custom_result["valid"]:
                    result["compliant"] = False
                    result["message"] = custom_result["message"]
            except Exception as e:
                result["compliant"] = False
                result["message"] = f"Validation function error: {e}"

        return result

    def _calculate_harmonizer_score(self, vault_content: Dict[str, Any], vault_name: str,
                                  compliance_result: Dict[str, Any]) -> HarmonizerScore:
        """Calculate harmonizer health score for a vault"""
        # Base compliance score
        compliance_score = self._compliance_level_to_score(compliance_result["overall_compliance"])

        # Integrity score (structure and data quality)
        integrity_score = self._calculate_integrity_score(vault_content)

        # Coherence score (internal consistency)
        coherence_score = self._calculate_coherence_score(vault_content)

        # Overall health (weighted average)
        overall_health = (compliance_score * 0.4 + integrity_score * 0.3 + coherence_score * 0.3)

        # Determine state
        state = self._determine_harmonizer_state(overall_health)

        # Collect issues
        issues = compliance_result.get("issues", [])

        return HarmonizerScore(
            vault_name=vault_name,
            compliance_score=compliance_score,
            integrity_score=integrity_score,
            coherence_score=coherence_score,
            overall_health=overall_health,
            state=state,
            last_updated=datetime.now(),
            issues=issues
        )

    def _compliance_level_to_score(self, level: ComplianceLevel) -> float:
        """Convert compliance level to numerical score"""
        mapping = {
            ComplianceLevel.FULL: 1.0,
            ComplianceLevel.PARTIAL: 0.7,
            ComplianceLevel.MINIMAL: 0.4,
            ComplianceLevel.NON_COMPLIANT: 0.0
        }
        return mapping.get(level, 0.0)

    def _calculate_integrity_score(self, vault_content: Dict[str, Any]) -> float:
        """Calculate data integrity score"""
        score = 1.0
        issues = 0

        # Check for required sections
        required_sections = ["philosopher", "entries", "learning_principles", "operational_context"]
        for section in required_sections:
            if section not in vault_content:
                issues += 1
                score -= 0.2

        # Check entries quality
        if "entries" in vault_content and isinstance(vault_content["entries"], list):
            entries = vault_content["entries"]
            if len(entries) == 0:
                issues += 1
                score -= 0.3
            else:
                # Check entry completeness
                complete_entries = 0
                for entry in entries:
                    required_entry_fields = ["id", "title", "content", "category", "confidence"]
                    if all(field in entry for field in required_entry_fields):
                        complete_entries += 1

                completeness_ratio = complete_entries / len(entries)
                score *= completeness_ratio

        return max(0.0, min(1.0, score))

    def _calculate_coherence_score(self, vault_content: Dict[str, Any]) -> float:
        """Calculate internal coherence score"""
        score = 1.0

        # Check category consistency
        if "entries" in vault_content and isinstance(vault_content["entries"], list):
            entries = vault_content["entries"]
            categories = set()

            for entry in entries:
                if "category" in entry:
                    categories.add(entry["category"])

            # Penalize for too few or too many categories
            if len(categories) < 2:
                score -= 0.2
            elif len(categories) > 10:
                score -= 0.1

            # Check confidence value ranges
            valid_confidences = 0
            for entry in entries:
                if "confidence" in entry:
                    conf = entry["confidence"]
                    if isinstance(conf, (int, float)) and 0.0 <= conf <= 1.0:
                        valid_confidences += 1

            if len(entries) > 0:
                confidence_ratio = valid_confidences / len(entries)
                score *= confidence_ratio

        return max(0.0, min(1.0, score))

    def _determine_harmonizer_state(self, health_score: float) -> HarmonizerState:
        """Determine harmonizer state based on health score"""
        if health_score >= 0.9:
            return HarmonizerState.HEALTHY
        elif health_score >= 0.7:
            return HarmonizerState.DEGRADED
        elif health_score >= 0.4:
            return HarmonizerState.CRITICAL
        else:
            return HarmonizerState.FAILED

    def _calculate_overall_health(self, harmonizer_scores: Dict[str, HarmonizerScore]) -> float:
        """Calculate overall system health from all harmonizer scores"""
        if not harmonizer_scores:
            return 0.0

        total_health = sum(score.overall_health for score in harmonizer_scores.values())
        return total_health / len(harmonizer_scores)

    def _update_telemetry(self, compliance_results: Dict[str, Any], harmonizer_scores: Dict[str, HarmonizerScore]):
        """Update telemetry with synchronization results"""
        try:
            # Load existing telemetry
            if os.path.exists(self.telemetry_path):
                with open(self.telemetry_path, 'r') as f:
                    telemetry = json.load(f)
            else:
                telemetry = {}

            # Update vault telemetry section
            if "vault_telemetry" not in telemetry:
                telemetry["vault_telemetry"] = {}

            vault_telemetry = telemetry["vault_telemetry"]
            vault_telemetry["last_sync"] = datetime.now().isoformat()
            vault_telemetry["vault_health_scores"] = {
                name: score.overall_health for name, score in harmonizer_scores.items()
            }
            vault_telemetry["compliance_summary"] = {
                name: result["overall_compliance"].value for name, result in compliance_results.items()
            }
            vault_telemetry["harmonizer_states"] = {
                name: score.state.value for name, score in harmonizer_scores.items()
            }

            # Save updated telemetry
            with open(self.telemetry_path, 'w') as f:
                json.dump(telemetry, f, indent=2, default=str)

        except Exception as e:
            print(f"[VaultSync] Failed to update telemetry: {e}")

    def _sync_loop(self):
        """Main synchronization loop"""
        while self.running:
            try:
                self.perform_sync()
                time.sleep(self.sync_interval)
            except Exception as e:
                print(f"[VaultSync] Sync loop error: {e}")
                time.sleep(60)  # Wait a minute before retrying

    def get_sync_status(self) -> Dict[str, Any]:
        """Get current synchronization status"""
        return {
            "running": self.running,
            "last_sync": self.sync_history[-1] if self.sync_history else None,
            "harmonizer_scores": {k: v.__dict__ for k, v in self.harmonizer_scores.items()},
            "sync_interval": self.sync_interval,
            "vault_directory": self.vault_directory
        }

    def force_sync(self) -> Dict[str, Any]:
        """Force an immediate synchronization"""
        if not self.running:
            return self.perform_sync()
        else:
            # Schedule immediate sync by resetting thread
            self.stop_synchronization()
            result = self.perform_sync()
            self.start_synchronization()
            return result