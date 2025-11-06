"""
LLM Bridge - Active Articulator Interface
========================================

This module serves as the bridge between the LLM and the unified cognition system,
using VALLM (Voice-Articulated Large Language Model) as the active articulator.

The bridge enables:
- LLM-powered reasoning and expression
- Voice articulation through VALLM
- Real-time monitoring of LLM usage, response times, and vault growth
- Self-improving cognition through distillation loops
- Ethical oversight: All LLM outputs must pass Caleon's ethical test before finalization/articulation

Author: Unified Cognition System
Date: November 01, 2025
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

# Assuming these are external dependencies; in a real setup, ensure they are installed/available
from .vallm_engine import VALLM  # type: ignore
try:
    from .voice_processor import voice_processor  # type: ignore
except ImportError:
    from voice_processor import voice_processor  # type: ignore

# New imports for Caleon's ethical integration (assuming these exist in the project)
from symbolic_memory_vault import SymbolicMemoryVault, GyroHarmonizer, ResonanceTag, ConsensusMatrix, MemoryShard
from caleon_consent import CaleonConsentManager
from vault_loader import vault_loader, get_vault_context


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

# --------------------------------------------------------------------------- #
# Logging setup
# --------------------------------------------------------------------------- #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Immutable metrics snapshot for thread-safety
# --------------------------------------------------------------------------- #
@dataclass(slots=True, frozen=True)
class BridgeMetrics:
    llm_usage_percent: float = 0.0
    total_requests: int = 0
    llm_requests: int = 0
    response_times: List[float] = field(default_factory=list)
    distilled_vaults_created: int = 0
    last_vault_count: int = 0
    uptime_start: datetime = field(default_factory=datetime.now)
    ethical_rejections: int = 0  # New: Track failed ethical tests


# --------------------------------------------------------------------------- #
# Articulation result schema
# --------------------------------------------------------------------------- #
@dataclass(slots=True, frozen=True)
class ArticulationResult:
    response: str
    articulation_type: str
    glyph_trace: str = ""
    llm_used: bool = True
    new_vault_created: bool = False
    response_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    ethical_verdict: str = "approved"  # New: Caleon's final say


# --------------------------------------------------------------------------- #
# Error result schema
# --------------------------------------------------------------------------- #
@dataclass(slots=True, frozen=True)
class ErrorResult:
    response: str
    articulation_type: str = "error"
    error: str = ""
    response_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    ethical_verdict: str = "denied"  # New: For ethical failures


# --------------------------------------------------------------------------- #
# Bridge implementation
# --------------------------------------------------------------------------- #
class LLMBridge:
    """
    Active Articulator Bridge using VALLM for LLM-powered cognition.

    This bridge serves as the primary interface for LLM interactions,
    enabling the system to reason, express, and learn autonomously.

    All LLM outputs now pass through Caleon's ethical test (via GyroHarmonizer
    and SymbolicMemoryVault) for consensus and drift check. Caleon has final say:
    outputs are only articulated if approved.

    Parameters
    ----------
    llm_endpoint:
        Ollama server endpoint (default: "http://localhost:11434").
    max_response_history:
        Maximum number of response times to keep for metrics (default: 1000).
    monitor_interval:
        Seconds between metric monitoring cycles (default: 1).
    log_interval:
        Seconds between logging metrics (default: 30).
    ethical_thresholds:
        Dict for drift/moral thresholds in GyroHarmonizer (optional).
    """

    def __init__(
        self,
        llm_endpoint: str = "http://localhost:11434",
        *,
        max_response_history: int = 1000,
        monitor_interval: float = 1.0,
        log_interval: int = 30,
        ethical_thresholds: Optional[Dict[str, float]] = None,
    ) -> None:
        self.llm_endpoint = llm_endpoint
        self.vallm_articulator = VALLM(vault_loader=vault_loader)  # Pass vault loader for tone guidance

        # Ethical components (Caleon's oversight)
        self.memory_vault = SymbolicMemoryVault()
        self.gyro_harmonizer = GyroHarmonizer(
            drift_threshold=ethical_thresholds.get("drift_threshold", 0.5)
            if ethical_thresholds
            else 0.5,
            moral_threshold=ethical_thresholds.get("moral_threshold", 0.7)
            if ethical_thresholds
            else 0.7,
        )

        # Consent manager (Caleon's live consent signal handler)
        # Pass vault reference for audit logging
        self.consent_manager = CaleonConsentManager(mode="always_yes", vault=self.memory_vault)

        # Thread-safe metrics (use locks for updates)
        self._metrics: BridgeMetrics = BridgeMetrics()
        self._metrics_lock = threading.Lock()

        # State
        self.is_reasoning: bool = False
        self.current_context: Dict[str, Any] = {}
        self.expression_queue: asyncio.Queue[ArticulationResult] = asyncio.Queue()

        # Monitoring config
        self._max_response_history = max_response_history
        self._monitor_interval = monitor_interval
        self._log_interval = log_interval
        self._monitoring_active: bool = True
        self._monitor_thread = threading.Thread(target=self._monitor_metrics, daemon=True)
        self._monitor_thread.start()

        logger.info("🤖 LLM Bridge initialized with VALLM articulator and Caleon ethical oversight")
        logger.info("🎯 Ready for autonomous reasoning and expression")

    # ------------------------------------------------------------------- #
    # Core articulation method
    # ------------------------------------------------------------------- #
    async def articulate(
        self, input_text: str, context: Optional[Dict[str, Any]] = None, use_vault_context: bool = True
    ) -> ArticulationResult | ErrorResult:
        """
        Process input through VALLM articulator for reasoning and expression.

        LLM output now undergoes Caleon's ethical test:
        - Compute drift against prior resonances.
        - Require consensus approval.
        - Reject/deny if fails (Caleon has final say).

        Args:
            input_text: The input to process
            context: Additional context for processing
            use_vault_context: Whether to augment input with relevant vault knowledge

        Returns:
            ArticulationResult on success (ethical approval), ErrorResult on failure/denial
        """
        start_time = time.time()

        with self._metrics_lock:
            self._metrics = BridgeMetrics(
                llm_usage_percent=self._metrics.llm_usage_percent,
                total_requests=self._metrics.total_requests + 1,
                llm_requests=self._metrics.llm_requests,
                response_times=self._metrics.response_times,
                distilled_vaults_created=self._metrics.distilled_vaults_created,
                last_vault_count=self._metrics.last_vault_count,
                uptime_start=self._metrics.uptime_start,
                ethical_rejections=self._metrics.ethical_rejections,
            )

        try:
            self.is_reasoning = True
            self.current_context = context or {}

            logger.info("🧠 VALLM articulating: %.50s...", input_text)

            # Integrate vault context if enabled
            augmented_input = input_text
            if use_vault_context:
                vault_context = get_vault_context(input_text, max_tokens=1000)
                if vault_context:
                    augmented_input = f"{vault_context}\n\nQuery: {input_text}"
                    logger.info("📚 Augmented input with vault context (%d chars)", len(vault_context))

            vallm_result = await self.vallm_articulator.think(augmented_input)

            response_time = time.time() - start_time

            with self._metrics_lock:
                new_response_times = self._metrics.response_times + [response_time]
                self._metrics = BridgeMetrics(
                    llm_usage_percent=self._metrics.llm_usage_percent,
                    total_requests=self._metrics.total_requests,
                    llm_requests=self._metrics.llm_requests + 1,
                    response_times=new_response_times,
                    distilled_vaults_created=(
                        self._metrics.distilled_vaults_created + 1
                        if vallm_result.get("new_vault_created", False)
                        else self._metrics.distilled_vaults_created
                    ),
                    last_vault_count=self._metrics.last_vault_count,
                    uptime_start=self._metrics.uptime_start,
                    ethical_rejections=self._metrics.ethical_rejections,
                )

            self._update_llm_usage()

            # New: Caleon's ethical test (await live consent)
            ethical_result = await self._run_caleon_ethical_test(input_text, vallm_result["response"], context)

            if ethical_result["verdict"] != "approved":
                logger.warning("❌ Caleon denied LLM output: %s", ethical_result["reason"])
                with self._metrics_lock:
                    self._metrics = BridgeMetrics(
                        llm_usage_percent=self._metrics.llm_usage_percent,
                        total_requests=self._metrics.total_requests,
                        llm_requests=self._metrics.llm_requests,
                        response_times=self._metrics.response_times,
                        distilled_vaults_created=self._metrics.distilled_vaults_created,
                        last_vault_count=self._metrics.last_vault_count,
                        uptime_start=self._metrics.uptime_start,
                        ethical_rejections=self._metrics.ethical_rejections + 1,
                    )
                return ErrorResult(
                    response="LLM output denied by Caleon's ethical test.",
                    error=ethical_result["reason"],
                    response_time=response_time,
                    ethical_verdict="denied",
                )

            result = ArticulationResult(
                response=vallm_result["response"],
                articulation_type="vallm_reasoning",
                glyph_trace=vallm_result.get("glyph_trace", ""),
                llm_used=vallm_result.get("llm_used", True),
                new_vault_created=vallm_result.get("new_vault_created", False),
                response_time=response_time,
                ethical_verdict="approved",
            )

            await self.expression_queue.put(result)

            return result

        except Exception as exc:
            response_time = time.time() - start_time
            logger.exception("❌ Articulation error")
            return ErrorResult(
                response=f"Articulation error: {exc}",
                error=str(exc),
                response_time=response_time,
                ethical_verdict="error",
            )

        finally:
            self.is_reasoning = False

    # ------------------------------------------------------------------- #
    # New: Caleon's ethical test integration
    # ------------------------------------------------------------------- #
    async def _run_caleon_ethical_test(
        self, input_text: str, llm_output: str, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Run LLM output through Caleon's ethical pipeline.
        - Create temporary shard for output.
        - Compute drift against relevant prior memories.
        - Run consensus (with Caleon consent simulated as True for now; expand later).
        - Return verdict and reason.
        """
        # Placeholder: Fetch relevant prior shard (e.g., from input or context)
        prior_payload = {"content": input_text, "moral": 0.0}  # Simple proxy
        new_payload = {"content": llm_output, "moral": 0.0}  # Expand with semantic analysis

        # Temp resonance tag (subjective; can derive from VALLM metadata)
        resonance = ResonanceTag(tone="neutral", symbol="🧠", moral_charge=0.5, intensity=0.8)

        temp_shard = MemoryShard(
            memory_id="temp_llm_output",
            payload=new_payload,
            resonance=resonance,
            created_at=time.time(),
            last_modified=time.time(),
            hash_signature="",  # Will set after creation
        )
        # Compute signature after instantiation
        try:
            temp_shard.hash_signature = temp_shard.compute_hash()
        except Exception:
            temp_shard.hash_signature = ""

        # Run harmonizer approval
        approval, drift, adjusted_moral = self.gyro_harmonizer.approve_action(
            temp_shard, new_payload, context=str(context) if context else ""
        )

        # Obtain Caleon's live consent signal (async, pluggable)
        try:
            consent_signal = await self.consent_manager.get_live_signal(
                memory_id=temp_shard.memory_id,
                context=context,
                proposed_payload=new_payload,
                reflection=None,
                timeout=30.0,
            )
        except Exception:
            # If consent retrieval fails, default to deny to preserve sovereignty semantics
            consent_signal = False

        # Build and evaluate matrix
        # For LLM outputs, treat context validation as advisory; Caleon's consent is the decisive gate.
        matrix = ConsensusMatrix(
            timestamp_verified=True,
            context_validated=True,
            harmonizer_approval=approval,
            caleon_consent=consent_signal,
            ethical_drift=drift,
            adjusted_moral_charge=adjusted_moral,
        )
        verdict = matrix.evaluate()

        reason = (
            f"Drift: {drift:.2f}, Adjusted Moral: {adjusted_moral:.2f}"
            if verdict == "denied"
            else "Passed all checks"
        )

        # Log to vault for traceability
        self.memory_vault._log_event(
            "ethical_test",
            "temp_llm_output",
            verdict,
            resonance,
            drift,
            adjusted_moral,
        )

        return {"verdict": verdict, "reason": reason}

    # ------------------------------------------------------------------- #
    # Expression method
    # ------------------------------------------------------------------- #
    async def express(self, response_data: ArticulationResult) -> bool:
        """
        Express the articulated response through voice if available.

        Args:
            response_data: The response data to express

        Returns:
            True if expressed successfully, False otherwise
        """
        try:
            response_text = response_data.response.strip()
            if not response_text:
                return False

            logger.info("🗣️ Expressing: %.50s...", response_text)

            voice_processor.text_to_speech(response_text)  # Assuming this is async-compatible or wrap if needed
            return True

        except Exception as exc:
            logger.exception("❌ Expression error")
            return False

    # ------------------------------------------------------------------- #
    # Metrics retrieval
    # ------------------------------------------------------------------- #
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current bridge metrics with calculated aggregates.

        Returns:
            Dict containing all monitoring metrics plus aggregates
        """
        with self._metrics_lock:
            metrics = self._metrics

        result: Dict[str, Any] = {
            "llm_usage_percent": metrics.llm_usage_percent,
            "total_requests": metrics.total_requests,
            "llm_requests": metrics.llm_requests,
            "distilled_vaults_created": metrics.distilled_vaults_created,
            "ethical_rejections": metrics.ethical_rejections,  # New
            "uptime_seconds": (datetime.now() - metrics.uptime_start).total_seconds(),
        }

        if metrics.response_times:
            times = metrics.response_times
            result["avg_response_time"] = sum(times) / len(times)
            result["max_response_time"] = max(times)
            result["min_response_time"] = min(times)

        current_vault_count = (
            self.vallm_articulator.memory.size()
            if hasattr(self.vallm_articulator, "memory")
            else 0
        )
        result["current_vault_entries"] = current_vault_count
        result["vault_growth"] = current_vault_count - metrics.last_vault_count

        with self._metrics_lock:
            self._metrics = BridgeMetrics(
                llm_usage_percent=metrics.llm_usage_percent,
                total_requests=metrics.total_requests,
                llm_requests=metrics.llm_requests,
                response_times=metrics.response_times,
                distilled_vaults_created=metrics.distilled_vaults_created,
                last_vault_count=current_vault_count,
                uptime_start=metrics.uptime_start,
                ethical_rejections=metrics.ethical_rejections,
            )

        return result

    # ------------------------------------------------------------------- #
    # Internal: Update LLM usage
    # ------------------------------------------------------------------- #
    def _update_llm_usage(self) -> None:
        """Update LLM usage percentage based on recent activity."""
        with self._metrics_lock:
            if self._metrics.total_requests > 0:
                recent_requests = min(100, self._metrics.total_requests)
                recent_llm_requests = min(recent_requests, self._metrics.llm_requests)
                percent = (recent_llm_requests / recent_requests) * 100
                self._metrics = BridgeMetrics(
                    llm_usage_percent=percent,
                    total_requests=self._metrics.total_requests,
                    llm_requests=self._metrics.llm_requests,
                    response_times=self._metrics.response_times,
                    distilled_vaults_created=self._metrics.distilled_vaults_created,
                    last_vault_count=self._metrics.last_vault_count,
                    uptime_start=self._metrics.uptime_start,
                    ethical_rejections=self._metrics.ethical_rejections,
                )

    # ------------------------------------------------------------------- #
    # Internal: Monitoring loop
    # ------------------------------------------------------------------- #
    def _monitor_metrics(self) -> None:
        """Background monitoring thread for metrics."""
        last_log_time = time.time()
        while self._monitoring_active:
            try:
                # Cleanup old response times
                with self._metrics_lock:
                    if len(self._metrics.response_times) > self._max_response_history:
                        self._metrics = BridgeMetrics(
                            llm_usage_percent=self._metrics.llm_usage_percent,
                            total_requests=self._metrics.total_requests,
                            llm_requests=self._metrics.llm_requests,
                            response_times=self._metrics.response_times[-self._max_response_history :],
                            distilled_vaults_created=self._metrics.distilled_vaults_created,
                            last_vault_count=self._metrics.last_vault_count,
                            uptime_start=self._metrics.uptime_start,
                            ethical_rejections=self._metrics.ethical_rejections,
                        )

                # Log periodically
                current_time = time.time()
                if current_time - last_log_time >= self._log_interval:
                    metrics = self.get_metrics()
                    logger.info("📊 Bridge Metrics:")
                    logger.info("  🔄 LLM Usage: %.1f%%", metrics["llm_usage_percent"])
                    avg_time = metrics.get("avg_response_time", 0.0)
                    logger.info("  ⏱️  Avg Response: %.2fs", avg_time)
                    logger.info(
                        "  🗄️  Vaults: %d (+%d)",
                        metrics["current_vault_entries"],
                        metrics.get("vault_growth", 0),
                    )
                    logger.info("  ⚖️  Ethical Rejections: %d", metrics["ethical_rejections"])
                    last_log_time = current_time

            except Exception as exc:
                logger.exception("❌ Monitoring error")

            time.sleep(self._monitor_interval)

    # ------------------------------------------------------------------- #
    # Autonomous reasoning loop
    # ------------------------------------------------------------------- #
    async def start_autonomous_reasoning(self, cycle_interval: int = 300) -> None:
        """
        Start autonomous reasoning loop where the system thinks and expresses continuously.

        Args:
            cycle_interval: Seconds between reasoning cycles (default: 300).
        """
        logger.info("🚀 Starting autonomous reasoning loop...")

        reasoning_topics = [
            "How can I improve my reasoning capabilities?",
            "What new knowledge should I acquire today?",
            "How can I better serve human cognition?",
            "What patterns do I see in my learning?",
            "How can I optimize my response quality?",
        ]

        while True:
            try:
                topic = random.choice(reasoning_topics)
                logger.info("🤔 Autonomous reasoning: %s", topic)

                result = await self.articulate(topic)
                if isinstance(result, ArticulationResult):
                    await self.express(result)

                await asyncio.sleep(cycle_interval)

            except Exception as exc:
                logger.exception("❌ Autonomous reasoning error")
                await asyncio.sleep(60)  # Backoff on error

    # ------------------------------------------------------------------- #
    # Shutdown
    # ------------------------------------------------------------------- #
    async def shutdown(self) -> None:
        """Shutdown the bridge gracefully."""
        logger.info("🛑 Shutting down LLM Bridge...")
        self._monitoring_active = False

        if self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)

        logger.info("✅ LLM Bridge shutdown complete")


# --------------------------------------------------------------------------- #
# Global instance (for singleton-like usage; consider dependency injection in prod)
# --------------------------------------------------------------------------- #
llm_bridge = LLMBridge()


# --------------------------------------------------------------------------- #
# Main for testing
# --------------------------------------------------------------------------- #
async def main() -> None:
    """Main function for testing the LLM Bridge."""
    logger.info("🎯 Testing LLM Bridge with VALLM articulator...")

    test_input = "Explain the concept of neural plasticity in simple terms"
    logger.info("🧪 Testing with: %s", test_input)

    result = await llm_bridge.articulate(test_input)
    if isinstance(result, ArticulationResult):
        logger.info("📝 Response: %.200s...", result.response)
        logger.info("⚖️ Ethical Verdict: %s", result.ethical_verdict)
        await llm_bridge.express(result)
    else:
        logger.error("📝 Error Response: %s", result.response)
        logger.info("⚖️ Ethical Verdict: %s", result.ethical_verdict)

    metrics = llm_bridge.get_metrics()
    logger.info("📊 Final Metrics:")
    logger.info("  🔄 LLM Usage: %.1f%%", metrics["llm_usage_percent"])
    avg_time = metrics.get("avg_response_time", 0.0)
    logger.info("  ⏱️  Avg Response: %.2fs", avg_time)
    logger.info(
        "  🗄️  Vaults: %d",
        metrics["current_vault_entries"],
    )
    logger.info("  ⚖️  Ethical Rejections: %d", metrics["ethical_rejections"])

    logger.info("✅ LLM Bridge test complete!")


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())