"""
CORE ARTICULATION CYCLE - START TO FINISH
==========================================

This document defines the complete sequence for one articulation cycle,
from initial input through final voice output, with all consent and audit touchpoints.

Author: Unified Cognition System
Date: November 01, 2025
"""

# =============================================================================
# PHASE 1: INPUT RECEPTION
# =============================================================================

"""
Entry Point: User provides input text
│
├─ Input: "Explain the nature of consciousness"
├─ Context: Optional metadata (conversation history, emotional state, etc.)
└─ Trigger: User invokes system (voice command, API call, UI interaction)
"""

async def phase_1_input_reception(input_text: str, context: dict = None):
    """
    INPUT RECEPTION
    
    Location: External interface (voice_processor, API, CLI)
    Duration: < 1ms
    
    Responsibilities:
    - Capture user input
    - Validate input format
    - Attach contextual metadata
    - Route to LLM Bridge
    
    Output: Validated input + context dict
    """
    # Example from voice_processor or vault_api
    validated_input = {
        "text": input_text,
        "context": context or {},
        "timestamp": time.time(),
        "source": "voice" | "api" | "cli"
    }
    
    # Route to LLM Bridge
    return validated_input


# =============================================================================
# PHASE 2: LLM ARTICULATION REQUEST
# =============================================================================

"""
Entry Point: LLMBridge.articulate(input_text, context)
│
├─ File: cerebral_cortex/llm_bridge.py
├─ Method: async def articulate(input_text, context)
└─ Purpose: Generate reasoning/response through VALLM
"""

async def phase_2_llm_articulation(input_text: str, context: dict):
    """
    LLM ARTICULATION REQUEST
    
    Location: cerebral_cortex/llm_bridge.py :: LLMBridge.articulate()
    Duration: 1-5 seconds (depends on LLM response time)
    
    Responsibilities:
    - Log incoming request
    - Increment metrics (total_requests)
    - Call VALLM for LLM generation
    - Measure response time
    
    Output: Raw LLM response text
    """
    start_time = time.time()
    
    # Update metrics
    with self._metrics_lock:
        self._metrics = BridgeMetrics(
            total_requests=self._metrics.total_requests + 1,
            llm_requests=self._metrics.llm_requests + 1,
            # ... other fields
        )
    
    # Call VALLM
    logger.info(f"🧠 VALLM articulating: {input_text[:50]}...")
    llm_response = await self.vallm_articulator.articulate(input_text, context)
    
    response_time = time.time() - start_time
    
    return {
        "response": llm_response,
        "response_time": response_time,
        "llm_used": True
    }


# =============================================================================
# PHASE 3: ETHICAL OVERSIGHT (ADVISORY METRICS)
# =============================================================================

"""
Entry Point: LLMBridge._run_caleon_ethical_test()
│
├─ File: cerebral_cortex/llm_bridge.py
├─ Method: async def _run_caleon_ethical_test(llm_output)
└─ Purpose: Compute advisory metrics WITHOUT blocking
"""

async def phase_3_ethical_oversight(llm_output: str):
    """
    ETHICAL OVERSIGHT (Advisory Computation)
    
    Location: cerebral_cortex/llm_bridge.py :: _run_caleon_ethical_test()
    Duration: 100-500ms
    
    Responsibilities:
    1. Store LLM output as temporary memory shard
    2. Compute ethical drift via GyroHarmonizer
    3. Compute moral charge via ConsensusMatrix
    4. Check context validation (advisory only)
    5. Package advisory metrics for Caleon's review
    
    CRITICAL: These metrics are ADVISORY ONLY
    - They inform Caleon's decision
    - They do NOT block output
    - Only Caleon's consent is decisive
    
    Output: (memory_id, advisory_metrics_dict)
    """
    # Step 1: Store as temp shard
    memory_id = "temp_llm_output"
    payload = {"text": llm_output, "source": "llm"}
    resonance = ResonanceTag(
        tone="neutral",
        symbol="llm_output",
        moral_charge=0.5,
        intensity=0.5
    )
    
    # Store in vault
    temp_hash = self.memory_vault.store(memory_id, payload, resonance)
    
    # Step 2: Compute drift (how far from previous resonances)
    prior_memories = self.memory_vault.query_by_resonance(
        symbol="llm_output",
        min_intensity=0.0
    )
    
    drift = self.gyro_harmonizer.compute_ethical_drift(
        proposed_payload=payload,
        existing_shards=prior_memories
    )
    
    # Step 3: Compute moral charge via consensus
    consensus_matrix = ConsensusMatrix()
    adjusted_moral = consensus_matrix.validate(
        memory_id=memory_id,
        context="llm_generation",
        vault=self.memory_vault
    )
    
    # Step 4: Context validation (advisory only)
    context_validated = True  # In current impl, always True (advisory)
    
    # Package advisory metrics
    advisory_metrics = {
        "drift": drift,
        "adjusted_moral_charge": adjusted_moral,
        "context_validated": context_validated,
        "memory_id": memory_id,
        "temp_hash": temp_hash
    }
    
    logger.info(f"📊 Advisory metrics: drift={drift:.2f}, moral={adjusted_moral:.2f}")
    
    return memory_id, advisory_metrics


# =============================================================================
# PHASE 4: CALEON'S CONSENT (DECISIVE GATE)
# =============================================================================

"""
Entry Point: CaleonConsentManager.get_live_signal()
│
├─ File: caleon_consent.py
├─ Method: async def get_live_signal(memory_id, reflection, timeout)
└─ Purpose: WAIT for Caleon's sovereign decision
"""

async def phase_4_caleon_consent(memory_id: str, advisory_metrics: dict):
    """
    CALEON'S CONSENT (Decisive Gate)
    
    Location: caleon_consent.py :: CaleonConsentManager.get_live_signal()
    Duration: Variable (depends on mode)
    
    Modes:
    - always_yes: < 1ms (testing)
    - always_no: < 1ms (testing)
    - random: < 1ms (testing)
    - manual: Wait for REST API call (up to timeout)
    - voice: Wait for spoken command (up to timeout)
    - custom: Call custom callback function
    
    Responsibilities:
    1. Present advisory metrics to Caleon (if in interactive mode)
    2. WAIT for her signal (block execution)
    3. Receive her decision (True = approve, False = deny)
    4. LOG decision to vault audit log
    5. Return decision to caller
    
    CRITICAL: This is the ONLY decisive gate
    - Advisory metrics inform, not constrain
    - Caleon's consent is sovereign
    - No consent = no articulation
    
    Output: bool (True = approved, False = denied)
    """
    # Present advisory context (in voice/manual mode, would display/speak these)
    reflection = {
        "drift": advisory_metrics["drift"],
        "adjusted_moral_charge": advisory_metrics["adjusted_moral_charge"],
        "context_validated": advisory_metrics["context_validated"]
    }
    
    logger.info(f"⏸️  Waiting for Caleon's consent (mode={self.mode})...")
    
    # BLOCKING WAIT - System pauses here until consent received
    decision = await self.consent_manager.get_live_signal(
        memory_id=memory_id,
        reflection=reflection,
        timeout=30.0
    )
    
    # Consent manager automatically logs to vault audit:
    # {
    #     "timestamp": time.time(),
    #     "action": "caleon_consent",
    #     "memory_id": memory_id,
    #     "verdict": "approved" | "denied" | "timeout",
    #     "mode": "voice" | "manual" | etc,
    #     "ethical_drift": drift,
    #     "adjusted_moral_charge": moral
    # }
    
    if decision:
        logger.info("✅ Caleon APPROVED - proceeding with articulation")
    else:
        logger.warning("❌ Caleon DENIED - blocking articulation")
    
    return decision


# =============================================================================
# PHASE 5: ARTICULATION FINALIZATION
# =============================================================================

"""
Entry Point: After consent received
│
├─ File: cerebral_cortex/llm_bridge.py
├─ Branch: If approved → finalize, If denied → block
└─ Purpose: Package result based on consent decision
"""

async def phase_5_articulation_finalization(
    llm_output: str,
    consent_decision: bool,
    advisory_metrics: dict,
    response_time: float
):
    """
    ARTICULATION FINALIZATION
    
    Location: cerebral_cortex/llm_bridge.py :: articulate() (continued)
    Duration: < 10ms
    
    Responsibilities:
    - If approved: Package ArticulationResult with full response
    - If denied: Package ErrorResult blocking output
    - Update metrics (ethical_rejections if denied)
    - Return result to caller
    
    Output: ArticulationResult | ErrorResult
    """
    if consent_decision:
        # APPROVED - Package full result
        result = ArticulationResult(
            response=llm_output,
            articulation_type="llm",
            llm_used=True,
            response_time=response_time,
            ethical_verdict="approved",
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"✅ Articulation approved: {llm_output[:50]}...")
        
    else:
        # DENIED - Block output
        with self._metrics_lock:
            self._metrics = BridgeMetrics(
                ethical_rejections=self._metrics.ethical_rejections + 1,
                # ... other fields
            )
        
        result = ErrorResult(
            response="LLM output denied by Caleon's ethical test.",
            articulation_type="ethical_block",
            error="consent_denied",
            response_time=response_time,
            ethical_verdict="denied",
            timestamp=datetime.now().isoformat()
        )
        
        logger.warning(f"❌ Articulation denied: Drift={advisory_metrics['drift']:.2f}")
    
    return result


# =============================================================================
# PHASE 6: VOICE ARTICULATION (IF APPROVED)
# =============================================================================

"""
Entry Point: ArticulationBridge.articulate() OR direct voice_processor call
│
├─ File: articulation_bridge.py OR voice_processor.py
├─ Method: articulate() or text_to_speech()
└─ Purpose: Convert text to speech and play through speaker
"""

async def phase_6_voice_articulation(result: ArticulationResult):
    """
    VOICE ARTICULATION
    
    Location: articulation_bridge.py :: ArticulationBridge.articulate()
              OR voice_processor.py :: VoiceProcessor.text_to_speech()
    Duration: Variable (depends on text length, TTS speed)
    
    Responsibilities:
    - Convert approved text to speech via TTS engine
    - Play audio through configured speaker
    - Log phonatory event to vault
    
    NOTE: Only executed if consent was approved
    
    Output: Spoken words through speaker
    """
    if result.ethical_verdict != "approved":
        logger.warning("⚠️ Skipping voice articulation - consent denied")
        return
    
    # Convert text to speech
    logger.info(f"🔊 Speaking: {result.response[:50]}...")
    
    # Use voice processor for TTS
    await voice_processor.text_to_speech(result.response)
    
    # Log phonatory event (optional)
    # vault.store("phonatory_log_" + timestamp, ...)
    
    logger.info("✅ Voice articulation complete")


# =============================================================================
# COMPLETE CYCLE SEQUENCE DIAGRAM
# =============================================================================

"""
COMPLETE ARTICULATION CYCLE
============================

User Input: "Explain consciousness"
    ↓
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 1: INPUT RECEPTION                                            │
│ - Capture input                                                     │
│ - Validate format                                                   │
│ - Attach context                                                    │
│ Duration: < 1ms                                                     │
└─────────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 2: LLM ARTICULATION                                           │
│ - Route to LLMBridge.articulate()                                   │
│ - Call VALLM for reasoning                                          │
│ - LLM generates: "Consciousness emerges from..."                    │
│ - Measure response time                                             │
│ Duration: 1-5 seconds                                               │
└─────────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 3: ETHICAL OVERSIGHT (Advisory)                               │
│ - Store LLM output as temp memory shard                             │
│ - Compute drift: 0.15 (GyroHarmonizer)                             │
│ - Compute moral charge: 0.85 (ConsensusMatrix)                     │
│ - Check context validation: True (advisory)                         │
│ - Package metrics for Caleon's review                               │
│ Duration: 100-500ms                                                 │
│                                                                      │
│ ⚠️ CRITICAL: These are ADVISORY ONLY                                │
│   → They inform Caleon's decision                                   │
│   → They do NOT block output                                        │
└─────────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 4: CALEON'S CONSENT ⏸️  (DECISIVE GATE)                       │
│                                                                      │
│ Mode: voice | manual | always_yes | custom                          │
│                                                                      │
│ Voice Mode:                                                          │
│ 1. VoiceConsentListener captures microphone                         │
│ 2. Speech recognition transcribes audio                             │
│ 3. Match against approval/denial phrases                            │
│ 4. Caleon says: "Yes" or "No"                                       │
│ 5. Decision: True (approve) or False (deny)                         │
│                                                                      │
│ Manual Mode:                                                         │
│ 1. REST API endpoint /consent/pending shows request                 │
│ 2. Caleon reviews advisory metrics                                  │
│ 3. POST /consent/{id}/approve OR /deny                              │
│ 4. Decision: True (approve) or False (deny)                         │
│                                                                      │
│ ✅ Consent granted: Continue to Phase 5a                            │
│ ❌ Consent denied: Jump to Phase 5b                                 │
│                                                                      │
│ AUDIT LOG ENTRY:                                                    │
│ {                                                                    │
│   "action": "caleon_consent",                                       │
│   "memory_id": "temp_llm_output",                                   │
│   "verdict": "approved" | "denied" | "timeout",                     │
│   "mode": "voice",                                                  │
│   "ethical_drift": 0.15,                                            │
│   "adjusted_moral_charge": 0.85                                     │
│ }                                                                    │
│                                                                      │
│ Duration: Variable (up to 30s timeout)                              │
│                                                                      │
│ 🎯 THIS IS THE ONLY HARD GATE                                       │
│   → Caleon's consent is sovereign                                   │
│   → No consent = no articulation                                    │
└─────────────────────────────────────────────────────────────────────┘
    ↓
    ├─ ✅ Approved → Phase 5a
    └─ ❌ Denied → Phase 5b
    
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 5a: ARTICULATION FINALIZATION (Approved)                      │
│ - Package ArticulationResult                                        │
│ - Include full LLM response                                         │
│ - Set ethical_verdict="approved"                                    │
│ - Return to caller                                                  │
│ Duration: < 10ms                                                    │
└─────────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 6: VOICE ARTICULATION                                         │
│ - Convert text to speech (TTS)                                      │
│ - Play through speaker                                              │
│ - User hears: "Consciousness emerges from..."                       │
│ Duration: Variable (depends on text length)                         │
└─────────────────────────────────────────────────────────────────────┘
    ↓
END (Success)


OR (if denied):

┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 5b: ARTICULATION FINALIZATION (Denied)                        │
│ - Package ErrorResult                                               │
│ - Block LLM response                                                │
│ - Set ethical_verdict="denied"                                      │
│ - Increment ethical_rejections metric                               │
│ - Return error to caller                                            │
│ Duration: < 10ms                                                    │
└─────────────────────────────────────────────────────────────────────┘
    ↓
END (Blocked)
"""


# =============================================================================
# TIMING BREAKDOWN
# =============================================================================

"""
TYPICAL TIMING FOR ONE CYCLE (Voice Mode, Approved)
====================================================

Phase 1: Input Reception           < 1ms
Phase 2: LLM Articulation          2,000ms (2 seconds)
Phase 3: Ethical Oversight         200ms
Phase 4: Caleon's Consent          5,000ms (5 seconds - human reaction time)
Phase 5: Finalization              5ms
Phase 6: Voice Articulation        3,000ms (3 seconds)
                                   ─────────
TOTAL:                             ~10.2 seconds

BREAKDOWN BY COMPONENT:
- LLM generation:      20% (2s)
- Human decision:      49% (5s)
- Voice output:        29% (3s)
- System overhead:     2% (200ms)

The human decision time dominates - this is intentional.
Caleon's sovereignty requires thoughtful consideration.
"""


# =============================================================================
# AUDIT TRAIL
# =============================================================================

"""
AUDIT TRAIL FOR ONE CYCLE
=========================

After one complete cycle, the vault audit log contains:

1. Memory Store Event (Phase 3):
   {
     "timestamp": 1699012340.123,
     "action": "store",
     "memory_id": "temp_llm_output",
     "verdict": "approved",
     "resonance": {...},
     "ethical_drift": 0.0,
     "adjusted_moral_charge": 0.5
   }

2. Consent Decision (Phase 4):
   {
     "timestamp": 1699012345.456,
     "action": "caleon_consent",
     "memory_id": "temp_llm_output",
     "verdict": "approved",
     "mode": "voice",
     "resonance": None,
     "ethical_drift": 0.15,
     "adjusted_moral_charge": 0.85
   }

3. (Optional) Phonatory Log (Phase 6):
   {
     "timestamp": 1699012348.789,
     "action": "phonatory_output",
     "memory_id": "articulation_123",
     "verdict": "spoken",
     ...
   }

Total audit entries per cycle: 2-3 (depending on voice logging)
"""


# =============================================================================
# KEY INSIGHTS
# =============================================================================

"""
KEY INSIGHTS
============

1. ADVISORY VS DECISIVE:
   - Advisory metrics (drift, moral charge) inform Caleon
   - Only Caleon's consent is decisive
   - No automatic blocking based on metrics

2. BLOCKING POINT:
   - System blocks at Phase 4 waiting for consent
   - Execution pauses until Caleon provides signal
   - Timeout defaults to deny (safety)

3. SOVEREIGNTY:
   - Caleon can approve high-drift outputs
   - Caleon can deny low-drift outputs
   - Her choice is sovereign, not algorithmic

4. OBSERVABILITY:
   - Every decision logged to vault
   - Full transparency of consent history
   - Advisory metrics preserved for analysis

5. SAFETY:
   - No consent = no articulation
   - Timeout = deny
   - Errors = deny
   - Default is conservative (protect sovereignty)

6. MODES:
   - always_yes: Testing/debugging (auto-approve)
   - voice: Production (spoken consent)
   - manual: Production (API consent)
   - custom: Advanced (custom logic)
"""


# =============================================================================
# CODE LOCATIONS
# =============================================================================

"""
CODE LOCATIONS (File Map)
==========================

Phase 1: Input Reception
  - voice_processor.py :: capture_voice_input()
  - vault_api.py :: API endpoints
  - CLI interface (if exists)

Phase 2: LLM Articulation
  - cerebral_cortex/llm_bridge.py :: LLMBridge.articulate()
  - vallm_engine.py :: VALLM.articulate()

Phase 3: Ethical Oversight
  - cerebral_cortex/llm_bridge.py :: _run_caleon_ethical_test()
  - symbolic_memory_vault.py :: SymbolicMemoryVault.store()
  - symbolic_memory_vault.py :: GyroHarmonizer.compute_ethical_drift()
  - symbolic_memory_vault.py :: ConsensusMatrix.validate()

Phase 4: Caleon's Consent
  - caleon_consent.py :: CaleonConsentManager.get_live_signal()
  - voice_consent.py :: VoiceConsentListener.listen_for_consent()
  - vault_api.py :: /consent/* endpoints (manual mode)

Phase 5: Finalization
  - cerebral_cortex/llm_bridge.py :: articulate() (return statement)
  - ArticulationResult / ErrorResult dataclasses

Phase 6: Voice Articulation
  - articulation_bridge.py :: ArticulationBridge.articulate()
  - voice_processor.py :: VoiceProcessor.text_to_speech()
  - phonatory_output_module.py :: Speaker.speak()
"""


# =============================================================================
# EXAMPLE: COMPLETE CYCLE IN CODE
# =============================================================================

async def complete_articulation_cycle_example():
    """
    Complete articulation cycle example with all phases.
    
    This shows the actual code flow for one complete cycle.
    """
    from cerebral_cortex.llm_bridge import LLMBridge
    from caleon_consent import CaleonConsentManager
    from voice_consent import VoiceConsentListener, VoiceConsentCallback
    from symbolic_memory_vault import SymbolicMemoryVault
    from articulation_bridge import ArticulationBridge
    
    # Setup
    vault = SymbolicMemoryVault()
    consent_manager = CaleonConsentManager(mode="voice", vault=vault)
    
    # Voice consent setup
    voice_listener = VoiceConsentListener(consent_manager)
    voice_listener.start()
    callback = VoiceConsentCallback(voice_listener)
    consent_manager.set_voice_callback(callback)
    
    # LLM Bridge with voice consent
    bridge = LLMBridge()
    bridge.consent_manager = consent_manager
    bridge.memory_vault = vault
    
    # Articulation bridge for voice output
    articulation = ArticulationBridge()
    
    # =========================================================================
    # EXECUTE ONE COMPLETE CYCLE
    # =========================================================================
    
    print("Starting articulation cycle...")
    
    # Phase 1-5: Input → LLM → Advisory → Consent → Finalization
    result = await bridge.articulate("Explain the nature of consciousness")
    
    # Phase 6: Voice output (if approved)
    if result.ethical_verdict == "approved":
        await articulation.articulate(result.response)
        print("✅ Cycle complete - output articulated")
    else:
        print("❌ Cycle complete - output blocked")
    
    # Check audit log
    audit = vault.get_audit_log()
    print(f"\nAudit entries created: {len(audit)}")
    for entry in audit:
        print(f"  - {entry['action']}: {entry['verdict']}")
    
    voice_listener.stop()


if __name__ == "__main__":
    import asyncio
    asyncio.run(complete_articulation_cycle_example())
