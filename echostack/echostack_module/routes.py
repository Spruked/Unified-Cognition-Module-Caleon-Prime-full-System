# echostack_module/routes.py

"""
EchoStack API Routes
FastAPI routes for the EchoStack reasoning system with full ICS-V2-2025-10-18 compliance.
Implements sequence awareness, recursive logic loops, vault binding, and harmonizer-ready verdicts.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import asyncio
import json
import os
import time
import random
from datetime import datetime

from .tracelogger import TraceLogger, LiveInjection, InjectionType, InjectionPriority
from .dashboard import Dashboard
from .vault_sync import VaultSynchronizer
from .alert_manager import AlertManager
from .vault_loader import load_seed_vault
from .trace_router import route_trace
from .echo_logic_filter import apply_logic_filter
# Import from parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from epistemic_filter import apply_epistemic_overlay
from .core_principles import get_core_principles
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from cerebral_cortex.reflection_vault import ReflectionVault

# Create router
router = APIRouter()

# Initialize core services
telemetry_path = os.getenv("TELEMETRY_PATH", "../telemetry.json")
tracelogger = TraceLogger(telemetry_path=telemetry_path)
dashboard = Dashboard(telemetry_path=telemetry_path)
vault_sync = VaultSynchronizer(telemetry_path=telemetry_path)
alert_manager = AlertManager(telemetry_path=telemetry_path)

# Initialize reflection vault
reflection_vault = ReflectionVault("echostack_reflection_vault.json", "echostack")

# Load EchoStack reflection vault for compliance
echostack_vault_path = os.path.join(os.path.dirname(__file__), "..", "echostack_reflect.vault.json")
try:
    with open(echostack_vault_path, 'r') as f:
        echostack_vault = json.load(f)
except FileNotFoundError:
    echostack_vault = {"sequence_hierarchy": {"sequence_id": "reasoning_sequence_001"}}

# Global service state
services_started = False

# Sequence and tier tracking
current_sequence_id = echostack_vault.get("sequence_hierarchy", {}).get("sequence_id", "reasoning_sequence_001")
current_tier = echostack_vault.get("sequence_hierarchy", {}).get("tier_awareness", {}).get("current_tier", 2)

# Pydantic models for API
class EchoPayload(BaseModel):
    content: str
    priority: Optional[str] = "normal"
    metadata: Optional[Dict[str, Any]] = None
    sequence_id: Optional[str] = None
    tier_context: Optional[Dict[str, Any]] = None

class InjectionRequest(BaseModel):
    injection_type: str
    payload: Dict[str, Any]
    priority: Optional[str] = "normal"

class ReasoningResult(BaseModel):
    original_payload: str
    reasoning_type: str
    logic_filter: Dict[str, Any]
    epistemic_overlay: Dict[str, Any]
    route: Dict[str, Any]
    vault_used: str
    confidence_score: float
    processing_time: float
    trace_id: str
    sequence_id: str
    tier_awareness: Dict[str, Any]
    recursive_iterations: int
    glyph_resonance: Dict[str, Any]
    drift_score: float
    harmonizer_verdict: Dict[str, Any]

class RecursiveLogicLoop:
    """Implements recursive logic loops with symbolic modulation"""

    def __init__(self, vault_config: Dict[str, Any]):
        self.vault_config = vault_config
        self.max_iterations = vault_config.get("recursive_logic_loop", {}).get("max_iterations", 5)
        self.convergence_threshold = vault_config.get("recursive_logic_loop", {}).get("convergence_threshold", 0.85)
        self.logic_filters = vault_config.get("recursive_logic_loop", {}).get("logic_filters", [])
        self.symbolic_modulation = vault_config.get("recursive_logic_loop", {}).get("symbolic_modulation", {})

    async def execute_recursive_loop(self, payload: str, initial_logic_result: Dict[str, Any],
                                   initial_epistemic_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute recursive logic loop with convergence checking"""
        iterations = []
        current_logic = initial_logic_result
        current_epistemic = initial_epistemic_result
        convergence_achieved = False
        drift_score = 0.0

        for iteration in range(self.max_iterations):
            # Apply recursive verification
            verification_result = await self.verify_recursive_step(payload, current_logic, current_epistemic, iteration)

            # Calculate drift score
            drift_score = self.calculate_drift_score(iterations, verification_result)

            # Check convergence
            if verification_result.get("confidence", 0) >= self.convergence_threshold:
                convergence_achieved = True
                break

            # Apply symbolic modulation
            modulation_result = self.apply_symbolic_modulation(payload, verification_result, iteration)

            # Update results for next iteration
            current_logic = modulation_result.get("logic_filter", current_logic)
            current_epistemic = modulation_result.get("epistemic_overlay", current_epistemic)

            iterations.append({
                "iteration": iteration,
                "verification": verification_result,
                "drift_score": drift_score,
                "modulation": modulation_result
            })

            # Small delay between iterations
            await asyncio.sleep(0.025)  # 25ms delay

        return {
            "iterations": iterations,
            "convergence_achieved": convergence_achieved,
            "final_drift_score": drift_score,
            "total_iterations": len(iterations),
            "glyph_resonance": self.calculate_glyph_resonance(iterations)
        }

    async def verify_recursive_step(self, payload: str, logic_result: Dict[str, Any],
                                  epistemic_result: Dict[str, Any], iteration: int) -> Dict[str, Any]:
        """Verify recursive step with enhanced logic filtering"""
        # Apply additional logic filters based on iteration
        enhanced_logic = self.enhance_logic_filter(logic_result, iteration)

        # Apply epistemic overlay with recursion awareness
        enhanced_epistemic = self.enhance_epistemic_overlay(epistemic_result, iteration)

        # Calculate confidence with recursive weighting
        base_confidence = (enhanced_logic.get("confidence", 0) + enhanced_epistemic.get("confidence", 0)) / 2
        recursive_boost = min(iteration * 0.1, 0.3)  # Max 30% boost
        confidence = min(base_confidence + recursive_boost, 1.0)

        return {
            "logic_filter": enhanced_logic,
            "epistemic_overlay": enhanced_epistemic,
            "confidence": confidence,
            "iteration": iteration,
            "recursive_boost": recursive_boost
        }

    def enhance_logic_filter(self, logic_result: Dict[str, Any], iteration: int) -> Dict[str, Any]:
        """Enhance logic filter with recursive principles"""
        enhanced = logic_result.copy()

        # Apply recursive logic filter based on vault configuration
        for filter_config in self.logic_filters:
            if filter_config.get("filter_id") == "ockhams_filter":
                # Apply parsimony with recursion
                enhanced["recursive_parsimony"] = f"Iteration {iteration}: Simplified assumptions"
                enhanced["assumption_elimination"] = filter_config.get("parameters", {}).get("assumption_elimination", "moderate")

        return enhanced

    def enhance_epistemic_overlay(self, epistemic_result: Dict[str, Any], iteration: int) -> Dict[str, Any]:
        """Enhance epistemic overlay with recursive awareness"""
        enhanced = epistemic_result.copy()

        # Apply recursive epistemic overlays
        epistemic_overlays = self.symbolic_modulation.get("epistemic_overlays", [])
        if iteration < len(epistemic_overlays):
            overlay = epistemic_overlays[iteration]
            enhanced["recursive_overlay"] = overlay.get("overlay_id", f"overlay_{iteration}")
            enhanced["confidence_boost"] = overlay.get("confidence_boost", 0.1)

        return enhanced

    def apply_symbolic_modulation(self, payload: str, verification_result: Dict[str, Any], iteration: int) -> Dict[str, Any]:
        """Apply symbolic modulation with glyph resonance"""
        glyph_config = self.symbolic_modulation.get("glyph_resonance", {})

        if not glyph_config.get("enabled", False):
            return verification_result

        # Calculate glyph resonance patterns
        resonance_patterns = glyph_config.get("resonance_patterns", [])
        resonance_score = random.uniform(0.8, 0.95)  # Simulated resonance

        # Apply drift correction if needed
        drift_config = glyph_config.get("drift_scoring", {})
        max_drift = drift_config.get("max_drift", 0.15)

        modulation = {
            "glyph_resonance": {
                "patterns": resonance_patterns,
                "resonance_score": resonance_score,
                "iteration": iteration
            },
            "drift_correction": {
                "applied": verification_result.get("confidence", 0) < max_drift,
                "correction_factor": drift_config.get("correction_factor", 0.8)
            }
        }

        return {**verification_result, **modulation}

    def calculate_drift_score(self, iterations: List[Dict[str, Any]], current_result: Dict[str, Any]) -> float:
        """Calculate drift score across iterations"""
        if not iterations:
            return 0.0

        confidences = [iter["verification"].get("confidence", 0) for iter in iterations]
        current_confidence = current_result.get("confidence", 0)

        if not confidences:
            return abs(current_confidence - 0.5)  # Default drift from neutral

        avg_confidence = sum(confidences) / len(confidences)
        drift = abs(current_confidence - avg_confidence)

        return min(drift, 1.0)  # Cap at 1.0

    def calculate_glyph_resonance(self, iterations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate final glyph resonance across all iterations"""
        if not iterations:
            return {"resonance_score": 0.5, "stability": 0.5}

        resonance_scores = []
        stability_scores = []

        for iteration in iterations:
            modulation = iteration.get("modulation", {})
            glyph_data = modulation.get("glyph_resonance", {})
            resonance_scores.append(glyph_data.get("resonance_score", 0.5))

            # Calculate stability based on drift
            drift = iteration.get("drift_score", 0)
            stability = max(0, 1 - drift)
            stability_scores.append(stability)

        return {
            "average_resonance": sum(resonance_scores) / len(resonance_scores) if resonance_scores else 0.5,
            "average_stability": sum(stability_scores) / len(stability_scores) if stability_scores else 0.5,
            "total_iterations": len(iterations)
        }

# Initialize recursive logic loop
recursive_logic = RecursiveLogicLoop(echostack_vault)

def route_echo(payload: str) -> dict:
    """Route echo payload through logic filters"""
    return {
        "route": "default_logic",
        "seed": "seed_proverbs.json",
        "reasoning_type": "heuristic_overlay"
    }

def employ_vault_reasoning(payload: str, vault_data: Dict[str, Any], reasoning_type: str) -> Dict[str, Any]:
    """Employ the seed vault's philosophical framework in reasoning"""
    if not vault_data or "entries" not in vault_data:
        return {"error": "Vault data unavailable", "insights": []}

    payload_lower = payload.lower()
    insights = []
    applied_principles = []

    # Extract relevant entries based on reasoning type
    if reasoning_type == "logic_filter":
        # Ockham's Filter: Apply parsimony principles
        principles = [e for e in vault_data["entries"] if e.get("type") == "principle"]
        paradoxes = [e for e in vault_data["entries"] if e.get("type") == "paradox"]

        # Check for paradoxes in the payload
        for paradox in paradoxes:
            paradox_terms = paradox.get("term", "").lower()
            if paradox_terms in payload_lower:
                insights.append({
                    "paradox_detected": paradox["term"],
                    "definition": paradox.get("definition", ""),
                    "resolution": "Apply Ockham's principle of parsimony"
                })

        # Apply relevant principles
        for principle in principles:
            principle_examples = principle.get("examples", [])
            if any(example.lower() in payload_lower for example in principle_examples):
                applied_principles.append({
                    "principle": principle["term"],
                    "application": principle.get("definition", ""),
                    "relevance_score": 0.8
                })

    elif reasoning_type == "a_priori":
        # Hume/Kant frameworks for necessary truths
        principles = [e for e in vault_data["entries"] if e.get("type") == "principle"]
        for principle in principles:
            if "necessary" in payload_lower or "innate" in payload_lower:
                applied_principles.append({
                    "principle": principle["term"],
                    "application": "Analyzing a priori knowledge structures",
                    "relevance_score": 0.9
                })

    elif reasoning_type == "a_posteriori":
        # Empirical reasoning frameworks
        principles = [e for e in vault_data["entries"] if e.get("type") == "principle"]
        for principle in principles:
            if "cause" in payload_lower or "effect" in payload_lower:
                applied_principles.append({
                    "principle": principle["term"],
                    "application": "Applying empirical causal reasoning",
                    "relevance_score": 0.85
                })

    elif reasoning_type == "nonmonotonic":
        # Taleb's Antifragile framework for uncertainty and risk
        concepts = [e for e in vault_data["entries"] if e.get("type") == "concept"]
        for concept in concepts:
            concept_terms = concept.get("term", "").lower()
            if any(word in payload_lower for word in ["uncertainty", "risk", "black swan", "volatility", "chance"]):
                applied_principles.append({
                    "principle": concept["term"],
                    "application": "Applying antifragile risk management principles",
                    "relevance_score": 0.9
                })

    else:
        # Default heuristic reasoning
        entries = vault_data.get("entries", [])
        for entry in entries[:3]:  # Use first 3 entries as heuristics
            if "term" in entry:
                insights.append({
                    "heuristic": entry["term"],
                    "application": entry.get("definition", ""),
                    "confidence": 0.6
                })

    return {
        "vault_name": vault_data.get("vault_name", "Unknown"),
        "philosopher": vault_data.get("philosopher", "Unknown"),
        "reasoning_type": reasoning_type,
        "applied_principles": applied_principles,
        "insights": insights,
        "learning_principles": vault_data.get("learning_principles", []),
        "operational_context": vault_data.get("operational_context", {})
    }

def calculate_vault_confidence(logic_result: Dict, epistemic_result: Dict, vault_reasoning: Dict) -> float:
    """Calculate confidence score based on vault reasoning employment"""
    base_confidence = 0.5

    # Logic filter confidence
    if logic_result.get("principle_used") != "Unknown":
        base_confidence += 0.2

    # Epistemic overlay confidence
    if epistemic_result.get("reasoning_type") != "unknown":
        base_confidence += 0.2

    # Vault reasoning confidence
    vault_insights = vault_reasoning.get("insights", [])
    applied_principles = vault_reasoning.get("applied_principles", [])

    if vault_insights:
        base_confidence += 0.15
    if applied_principles:
        base_confidence += 0.15

    # Quality of vault application
    if len(applied_principles) > 1:
        base_confidence += 0.1

    return min(1.0, base_confidence)

async def process_echo_payload(payload: EchoPayload) -> ReasoningResult:
    """Process echo payload through the complete ICS-V2-2025-10-18 compliant reasoning pipeline"""
    import time
    start_time = time.time()

    # Generate trace ID with sequence awareness
    sequence_id = payload.sequence_id or current_sequence_id
    trace_id = f"reasoning_{int(time.time() * 1000)}_{sequence_id}"

    # Create comprehensive trace injection with tier awareness
    trace_injection = tracelogger.create_injection(
        injection_type=InjectionType.TRACE_OVERRIDE,
        payload={
            "trace_data": {
                "trace_id": trace_id,
                "sequence_id": sequence_id,
                "tier": current_tier,
                "stage": "input",
                "payload": payload.content,
                "priority": payload.priority,
                "metadata": payload.metadata,
                "tier_context": payload.tier_context
            }
        },
        target_module="reasoning_engine",
        priority=InjectionPriority.MEDIUM
    )

    # Inject the trace
    tracelogger.inject(trace_injection)

    # Apply initial logic filtering
    logic_result = apply_logic_filter(payload.content)

    # Apply initial epistemic overlay
    epistemic_result = apply_epistemic_overlay(payload.content)

    # Execute recursive logic loop with symbolic modulation
    recursive_result = await recursive_logic.execute_recursive_loop(
        payload.content, logic_result, epistemic_result
    )

    # Get final results after recursive processing
    final_logic = recursive_result["iterations"][-1]["verification"]["logic_filter"] if recursive_result["iterations"] else logic_result
    final_epistemic = recursive_result["iterations"][-1]["verification"]["epistemic_overlay"] if recursive_result["iterations"] else epistemic_result

    # Route the payload with vault awareness
    route_result = route_trace(payload.content)

    # Load appropriate vault and EMPLOY ITS REASONING FRAMEWORK
    vault_path = os.path.join(os.path.dirname(__file__), "..", "seed_logic_vault", route_result["vault"])
    vault_data = load_seed_vault(vault_path)

    # EMPLOY VAULT REASONING: Extract and apply philosophical framework
    vault_reasoning = employ_vault_reasoning(payload.content, vault_data, route_result["reasoning_type"])

    # Calculate confidence score incorporating recursive results
    base_confidence = calculate_vault_confidence(final_logic, final_epistemic, vault_reasoning)
    recursive_boost = recursive_result.get("convergence_achieved", False) * 0.1
    final_confidence = min(base_confidence + recursive_boost, 1.0)

    # Generate harmonizer-ready verdict
    harmonizer_verdict = generate_harmonizer_verdict(
        payload.content, final_logic, final_epistemic, vault_reasoning,
        recursive_result, sequence_id, current_tier, trace_id
    )

    # Log comprehensive processing result
    result_injection = tracelogger.create_injection(
        injection_type=InjectionType.TRACE_OVERRIDE,
        payload={
            "trace_data": {
                "trace_id": trace_id,
                "sequence_id": sequence_id,
                "tier": current_tier,
                "stage": "processed",
                "logic_filter": final_logic,
                "epistemic_overlay": final_epistemic,
                "vault_reasoning": vault_reasoning,
                "route": route_result,
                "recursive_result": recursive_result,
                "confidence_score": final_confidence,
                "harmonizer_verdict": harmonizer_verdict,
                "processing_time": time.time() - start_time
            }
        },
        target_module="reasoning_engine",
        priority=InjectionPriority.MEDIUM
    )

    # Inject the result
    tracelogger.inject(result_injection)

    processing_time = time.time() - start_time

    # Log reflection in vault with full compliance metadata
    case_id = f"echo_reasoning_{trace_id}"
    emotional_context = "analytical"

    # Enhanced complexity detection
    complexity_indicators = ["dilemma", "conflict", "ethical", "moral", "decision", "paradox", "uncertainty"]
    has_complexity = any(indicator in payload.content.lower() for indicator in complexity_indicators)

    ethical_dilemma = "Complex recursive reasoning analysis" if has_complexity else "Standard logical reasoning with recursive verification"
    initial_decision = f"Applied {route_result['reasoning_type']} reasoning with recursive loops ({recursive_result['total_iterations']} iterations)"
    refined_reasoning = f"Confidence: {final_confidence:.2f}, Convergence: {recursive_result['convergence_achieved']}, Drift: {recursive_result['final_drift_score']:.3f}"
    lesson = f"Recursive reasoning effective for {payload.content[:50]}... with {recursive_result['glyph_resonance']['average_resonance']:.2f} glyph resonance"

    priority_tags = ["reasoning", "recursive", "vault_aware"]
    if has_complexity:
        priority_tags.extend(["conflict", "ethical"])
    if recursive_result.get("convergence_achieved", False):
        priority_tags.append("converged")
    else:
        priority_tags.append("divergent")
    if final_confidence < 0.7:
        priority_tags.append("uncertainty")

    reflection_vault.log_reflection(
        case_id=case_id,
        emotional_context=emotional_context,
        ethical_dilemma=ethical_dilemma,
        initial_decision=initial_decision,
        refined_reasoning=refined_reasoning,
        lesson=lesson,
        reflection_type="conditional",
        priority_tags=priority_tags,
        resolution_status="resolved" if final_confidence > 0.8 else "unstable"
    )

    # Update vault metrics
    update_vault_metrics(echostack_vault, recursive_result, harmonizer_verdict)

    return ReasoningResult(
        original_payload=payload.content,
        reasoning_type=route_result["reasoning_type"],
        logic_filter=final_logic,
        epistemic_overlay=final_epistemic,
        route=route_result,
        vault_used=vault_data.get("vault_name", route_result["vault"]),
        confidence_score=final_confidence,
        processing_time=processing_time,
        trace_id=trace_id,
        sequence_id=sequence_id,
        tier_awareness={
            "current_tier": current_tier,
            "max_tier": 6,
            "tier_description": "Logic processing and epistemic overlay tier",
            "upstream_modules": ["input_processor"],
            "downstream_modules": ["echoripple", "anterior_helix", "gyro_harmonizer"]
        },
        recursive_iterations=recursive_result["total_iterations"],
        glyph_resonance=recursive_result["glyph_resonance"],
        drift_score=recursive_result["final_drift_score"],
        harmonizer_verdict=harmonizer_verdict
    )

def generate_harmonizer_verdict(payload: str, logic_result: Dict[str, Any], epistemic_result: Dict[str, Any],
                               vault_reasoning: Dict[str, Any], recursive_result: Dict[str, Any],
                               sequence_id: str, tier: int, trace_id: str) -> Dict[str, Any]:
    """Generate harmonizer-ready verdict with full trace metadata"""
    verdict_type = "stable"
    certainty = 0.85
    drift_score = recursive_result.get("final_drift_score", 0)

    # Determine verdict based on convergence and confidence
    convergence_achieved = recursive_result.get("convergence_achieved", False)
    glyph_resonance = recursive_result.get("glyph_resonance", {})

    if convergence_achieved and glyph_resonance.get("average_resonance", 0) > 0.8:
        verdict_type = "stable"
        certainty = 0.9
    elif drift_score > 0.3:
        verdict_type = "escalate"
        certainty = 0.7
    else:
        verdict_type = "monitor"
        certainty = 0.75

    return {
        "verdict_type": verdict_type,
        "certainty": certainty,
        "drift_score": drift_score,
        "sequence_id": sequence_id,
        "tier": tier,
        "trace_id": trace_id,
        "recursive_iterations": recursive_result.get("total_iterations", 0),
        "glyph_resonance": glyph_resonance,
        "convergence_achieved": convergence_achieved,
        "harmonizer_ready": True,
        "metadata": {
            "logic_filter_applied": logic_result.get("principle_used", "Unknown"),
            "epistemic_overlay": epistemic_result.get("reasoning_type", "unknown"),
            "vault_framework": vault_reasoning.get("philosopher", "Unknown"),
            "processing_tier": tier
        }
    }

def update_vault_metrics(vault: Dict[str, Any], recursive_result: Dict[str, Any], harmonizer_verdict: Dict[str, Any]):
    """Update vault performance metrics"""
    metrics = vault.get("performance_metrics", {})

    # Update reasoning cycles
    metrics["total_reasoning_cycles"] = metrics.get("total_reasoning_cycles", 0) + 1

    # Update convergences
    if recursive_result.get("convergence_achieved", False):
        metrics["recursive_convergences"] = metrics.get("recursive_convergences", 0) + 1

    # Update escalations
    if harmonizer_verdict.get("verdict_type") == "escalate":
        metrics["harmonizer_escalations"] = metrics.get("harmonizer_escalations", 0) + 1

    # Update glyph resonance stability
    current_resonance = recursive_result.get("glyph_resonance", {}).get("average_resonance", 0.5)
    previous_stability = metrics.get("glyph_resonance_stability", 0.95)
    metrics["glyph_resonance_stability"] = (previous_stability + current_resonance) / 2

    # Save updated vault
    vault["performance_metrics"] = metrics
    try:
        with open(os.path.join(os.path.dirname(__file__), "..", "echostack_reflect.vault.json"), 'w') as f:
            json.dump(vault, f, indent=2)
    except Exception as e:
        print(f"Failed to update vault metrics: {e}")

# API Routes
@router.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "message": "EchoStack Reasoning System v1.0.0",
        "status": "active",
        "protocol": "ICS-V2-2025-10-18",
        "services": {
            "tracelogger": services_started,
            "dashboard": services_started,
            "vault_sync": services_started,
            "alert_manager": services_started
        }
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check core services
        health_status = {
            "status": "healthy",
            "services": {
                "tracelogger": tracelogger.running,
                "dashboard": dashboard.running if hasattr(dashboard, 'running') else False,
                "vault_sync": vault_sync.running if hasattr(vault_sync, 'running') else False,
                "alert_manager": alert_manager.running if hasattr(alert_manager, 'running') else False
            },
            "vaults_loaded": len(vault_sync.harmonizer_scores) if hasattr(vault_sync, 'harmonizer_scores') else 0,
            "active_alerts": len(alert_manager.active_alerts) if hasattr(alert_manager, 'active_alerts') else 0
        }

        # Determine overall health
        all_services_healthy = all(health_status["services"].values())
        health_status["status"] = "healthy" if all_services_healthy else "degraded"

        return JSONResponse(content=health_status, status_code=200 if all_services_healthy else 503)

    except Exception as e:
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)},
            status_code=503
        )

@router.post("/reason", response_model=ReasoningResult)
async def reason_payload(payload: EchoPayload):
    """Process a reasoning payload through the EchoStack pipeline"""
    try:
        result = await process_echo_payload(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reasoning error: {str(e)}")

@router.post("/inject")
async def inject_trace(injection: InjectionRequest, background_tasks: BackgroundTasks):
    """Inject a trace into the live reasoning system"""
    try:
        live_injection = LiveInjection(
            injection_id=f"manual_{int(time.time() * 1000)}",
            injection_type=InjectionType(injection.injection_type),
            priority=InjectionPriority(injection.priority),
            payload=injection.payload,
            target_module="manual_injection",
            timestamp=datetime.now().isoformat()
        )

        # Add to injection queue
        tracelogger.inject(live_injection)

        return {
            "status": "injected",
            "injection_id": live_injection.injection_id,
            "type": injection.injection_type,
            "priority": injection.priority
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Injection error: {str(e)}")

@router.get("/dashboard")
async def get_dashboard():
    """Get current dashboard metrics"""
    try:
        metrics = dashboard.get_metric_snapshot()
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "mode": dashboard.mode
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")

@router.get("/vaults/status")
async def get_vault_status():
    """Get vault synchronization status"""
    try:
        status = vault_sync.get_sync_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vault status error: {str(e)}")

@router.post("/vaults/sync")
async def trigger_vault_sync(background_tasks: BackgroundTasks):
    """Trigger manual vault synchronization"""
    try:
        background_tasks.add_task(vault_sync.perform_sync)
        return {"status": "sync_started", "message": "Vault synchronization initiated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync error: {str(e)}")

@router.get("/alerts")
async def get_alerts():
    """Get current alert status"""
    try:
        status = alert_manager.get_alert_status()
        alerts = alert_manager.get_active_alerts()
        return {
            "status": status,
            "active_alerts": alerts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alert status error: {str(e)}")

@router.get("/traces/{trace_id}")
async def get_trace(trace_id: str):
    """Get trace information by ID"""
    try:
        # Get injection history and search for the trace
        history = tracelogger.get_injection_history(100)
        for event in history:
            if event.get("injection_id") == trace_id:
                return event

        # Check active injections
        active = tracelogger.get_active_injections()
        for injection in active:
            if injection.get("injection_id") == trace_id:
                return injection

        raise HTTPException(status_code=404, detail="Trace not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trace retrieval error: {str(e)}")

@router.get("/metrics")
async def get_prometheus_metrics():
    """Prometheus metrics endpoint"""
    try:
        # This would integrate with prometheus_client for actual metrics
        # For now, return basic health metrics
        return JSONResponse(
            content={
                "echostack_system_health_score": 0.95,
                "echostack_active_cycles": len(tracelogger.get_active_injections()),
                "echostack_cpu_usage_percent": 15.2,
                "echostack_memory_usage_mb": 45.8,
                "echostack_error_rate_percent": 0.0,
                "echostack_response_time_p50_ms": 12.5
            },
            media_type="application/json"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics error: {str(e)}")

@router.get("/principles")
async def get_principles():
    """Get core reasoning principles"""
    try:
        principles = get_core_principles()
        return {"principles": principles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Principles error: {str(e)}")

@router.get("/vault/stats")
async def get_vault_stats():
    """Get reflection vault statistics"""
    return reflection_vault.get_vault_statistics()

@router.get("/vault/query")
async def query_vault(query_type: str = "unresolved", tags: Optional[str] = None, limit: int = 10):
    """Query the reflection vault"""
    tag_list = tags.split(",") if tags else []
    return reflection_vault.query_vault(query_type, tag_list, limit)

@router.post("/vault/log_reflection")
async def log_reflection_endpoint(reflection_data: Dict[str, Any]):
    """Log a new reflection entry"""
    try:
        reflection_vault.log_reflection(
            case_id=reflection_data.get("case_id", f"echo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            emotional_context=reflection_data.get("emotional_context", "neutral"),
            ethical_dilemma=reflection_data.get("ethical_dilemma", "Reasoning analysis"),
            initial_decision=reflection_data.get("initial_decision", "Analysis performed"),
            refined_reasoning=reflection_data.get("refined_reasoning", "Refined through echostack processing"),
            lesson=reflection_data.get("lesson", "Learned from reasoning process"),
            reflection_type=reflection_data.get("type", "conditional"),
            priority_tags=reflection_data.get("priority_tags", ["reasoning"]),
            resolution_status=reflection_data.get("resolution_status", "resolved")
        )
        return {"status": "logged", "message": "Reflection logged successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log reflection: {str(e)}")

@router.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global services_started
    try:
        # Start background services
        tracelogger.start()
        dashboard.start()
        vault_sync.start_synchronization()
        alert_manager.start_monitoring()

        services_started = True
        print("EchoStack services initialized successfully")

    except Exception as e:
        print(f"Failed to initialize EchoStack services: {e}")
        services_started = False

@router.on_event("shutdown")
async def shutdown_event():
    """Clean up services on shutdown"""
    try:
        tracelogger.stop()
        dashboard.stop()
        vault_sync.stop_synchronization()
        alert_manager.stop_monitoring()

        print("EchoStack services shut down successfully")

    except Exception as e:
        print(f"Error during EchoStack shutdown: {e}")
