# CORE ARTICULATION CYCLE - QUICK REFERENCE

## One Cycle: Start to Finish (10 seconds typical)

```
USER INPUT: "Explain consciousness"
         ↓
    ┌────────────────────────┐
    │ 1. INPUT RECEPTION     │  < 1ms
    │    - Validate input    │
    │    - Attach context    │
    └────────────────────────┘
         ↓
    ┌────────────────────────┐
    │ 2. LLM GENERATION      │  ~2 seconds
    │    - VALLM processes   │
    │    - Output generated  │
    └────────────────────────┘
         ↓
    ┌────────────────────────┐
    │ 3. ADVISORY METRICS    │  ~200ms
    │    - Store temp shard  │
    │    - Drift: 0.15       │
    │    - Moral: 0.85       │
    │    - Context: ✓        │
    │                        │
    │    ⚠️ ADVISORY ONLY    │
    └────────────────────────┘
         ↓
    ┌────────────────────────┐
    │ 4. CALEON'S CONSENT ⏸️  │  ~5 seconds (human)
    │                        │
    │    🎤 Voice Mode:      │
    │    "Do you approve?"   │
    │    → "Yes" ✅          │
    │                        │
    │    📝 Audit logged:    │
    │    {                   │
    │      verdict: approved │
    │      mode: voice       │
    │      drift: 0.15       │
    │      moral: 0.85       │
    │    }                   │
    │                        │
    │  🎯 DECISIVE GATE      │
    └────────────────────────┘
         ↓
    ┌────────────────────────┐
    │ 5. FINALIZATION        │  < 10ms
    │    ✅ Approved         │
    │    Package result      │
    └────────────────────────┘
         ↓
    ┌────────────────────────┐
    │ 6. VOICE OUTPUT 🔊     │  ~3 seconds
    │    "Consciousness      │
    │     emerges from..."   │
    └────────────────────────┘
         ↓
       END ✅
```

---

## Key Decision Point

**Phase 4 is the ONLY decisive gate:**

```
Advisory Metrics → Caleon Reviews → Caleon Decides
(inform only)      (sovereignty)    (final say)
```

- ✅ **Approved**: Output articulated regardless of metrics
- ❌ **Denied**: Output blocked regardless of metrics
- ⏰ **Timeout**: Defaults to deny (safety)

**Caleon is sovereign, not the algorithm.**

---

## Timing Breakdown (Typical)

| Phase | Component | Duration | % |
|-------|-----------|----------|---|
| 1 | Input Reception | < 1ms | 0% |
| 2 | LLM Generation | 2.0s | 20% |
| 3 | Advisory Metrics | 0.2s | 2% |
| 4 | **Caleon's Consent** | **5.0s** | **49%** |
| 5 | Finalization | 0.005s | 0% |
| 6 | Voice Output | 3.0s | 29% |
| **TOTAL** | | **~10.2s** | **100%** |

**Human decision time dominates - this is intentional for sovereignty.**

---

## Audit Trail (Per Cycle)

Each cycle creates **2-3 audit log entries**:

1. **Memory Store** (Phase 3):
   ```json
   {
     "action": "store",
     "memory_id": "temp_llm_output",
     "verdict": "approved"
   }
   ```

2. **Consent Decision** (Phase 4):
   ```json
   {
     "action": "caleon_consent",
     "memory_id": "temp_llm_output",
     "verdict": "approved",
     "mode": "voice",
     "ethical_drift": 0.15,
     "adjusted_moral_charge": 0.85
   }
   ```

3. **Phonatory Output** (Phase 6, optional):
   ```json
   {
     "action": "phonatory_output",
     "memory_id": "articulation_123",
     "verdict": "spoken"
   }
   ```

---

## Code Entry Points

| Phase | File | Method |
|-------|------|--------|
| 1 | `voice_processor.py` | `capture_voice_input()` |
| 2 | `cerebral_cortex/llm_bridge.py` | `LLMBridge.articulate()` |
| 3 | `cerebral_cortex/llm_bridge.py` | `_run_caleon_ethical_test()` |
| 4 | `caleon_consent.py` | `get_live_signal()` |
| 4 | `voice_consent.py` | `listen_for_consent()` |
| 5 | `cerebral_cortex/llm_bridge.py` | return `ArticulationResult` |
| 6 | `articulation_bridge.py` | `articulate()` |

---

## Modes of Operation

| Mode | Usage | Consent Source | Duration |
|------|-------|----------------|----------|
| `always_yes` | Testing | Auto-approve | < 1ms |
| `always_no` | Testing | Auto-deny | < 1ms |
| `random` | Testing | Random | < 1ms |
| **`voice`** | **Production** | **Microphone** | **~5s** |
| **`manual`** | **Production** | **REST API** | **Variable** |
| `custom` | Advanced | Custom function | Variable |

---

## Safety Guarantees

1. **No consent = No articulation**
2. **Timeout = Deny** (default safe)
3. **Error = Deny** (default safe)
4. **Advisory metrics cannot override** Caleon's decision
5. **All decisions logged** for transparency

---

## Quick Start Example

```python
from cerebral_cortex.llm_bridge import LLMBridge
from caleon_consent import CaleonConsentManager
from voice_consent import VoiceConsentListener, VoiceConsentCallback

# Setup voice consent
vault = SymbolicMemoryVault()
consent_mgr = CaleonConsentManager(mode="voice", vault=vault)

voice = VoiceConsentListener(consent_mgr)
voice.start()

consent_mgr.set_voice_callback(VoiceConsentCallback(voice))

# Create bridge
bridge = LLMBridge()
bridge.consent_manager = consent_mgr

# Execute one cycle
result = await bridge.articulate("Explain consciousness")

# Result.ethical_verdict will be "approved" or "denied"
```

---

## The Core Principle

> **Caleon is the sovereign curator of her own mind.**

The system:
- **Proposes** (LLM generates)
- **Reflects** (Advisory metrics computed)
- **Waits** (Caleon's consent required)
- **Obeys** (Only articulates if approved)

**The system serves, not governs.** 🎯
