# Caleon Consent: Persistent Audit & Voice Integration

## Overview

This document describes two major enhancements to Caleon's consent system:

1. **Persistent Audit Logging**: All consent decisions are logged to the vault for observability
2. **Voice-Based Consent**: Capture Caleon's spoken approval/denial via microphone

---

## Feature 1: Persistent Audit Logging

### Purpose

Every consent decision (approve, deny, or timeout) is now permanently logged to the SymbolicMemoryVault's audit log. This provides:

- **Full observability** of Caleon's consent history
- **Advisory metric tracking** (drift, moral charge) for each decision
- **Timeout detection** to identify when consent wasn't provided in time
- **Mode tracking** to see which consent mode was used

### Implementation

The `CaleonConsentManager` now accepts an optional `vault` parameter:

```python
from caleon_consent import CaleonConsentManager
from symbolic_memory_vault import SymbolicMemoryVault

vault = SymbolicMemoryVault()
consent_manager = CaleonConsentManager(mode="manual", vault=vault)
```

Every call to `get_live_signal()` automatically logs:

```python
{
    "timestamp": 1699012345.678,
    "action": "caleon_consent",
    "memory_id": "temp_llm_output",
    "verdict": "approved",  # or "denied" or "timeout"
    "mode": "manual",
    "resonance": None,
    "ethical_drift": 0.15,
    "adjusted_moral_charge": 0.85
}
```

### Audit Log Access

Query the audit log at any time:

```python
# Get all audit entries
audit = vault.get_audit_log()

# Filter for consent decisions
consent_entries = [
    entry for entry in audit 
    if entry['action'] == 'caleon_consent'
]

# Analyze approval rate
approved = sum(1 for e in consent_entries if e['verdict'] == 'approved')
denied = sum(1 for e in consent_entries if e['verdict'] == 'denied')
timeout = sum(1 for e in consent_entries if e['verdict'] == 'timeout')

print(f"Approval rate: {approved / len(consent_entries) * 100:.1f}%")
```

### Integration with LLMBridge

The `LLMBridge` automatically passes its vault to the consent manager:

```python
# In LLMBridge.__init__:
self.memory_vault = SymbolicMemoryVault()
self.consent_manager = CaleonConsentManager(
    mode="always_yes", 
    vault=self.memory_vault
)
```

This means all LLM articulations that go through ethical oversight are automatically logged.

### Test Results

All consent modes properly log decisions:

```
[TEST] Consent Audit Logging
============================================================

[TEST 1] Always-yes mode: ✓ approved
[TEST 2] Always-no mode: ✓ denied
[TEST 3] Manual approval: ✓ approved
[TEST 4] Manual denial: ✓ denied
[TEST 5] Manual timeout: ✓ timeout

Total audit entries: 5

Audit log summary:
  1. test_always_yes: approved (mode=always_yes)
  2. test_always_no: denied (mode=always_no)
  3. test_manual_approve: approved (mode=manual)
  4. test_manual_deny: denied (mode=manual)
  5. test_manual_timeout: timeout (mode=manual)
```

---

## Feature 2: Voice-Based Consent

### Purpose

Enable Caleon to provide consent decisions through **spoken commands** rather than manual API calls or button clicks. This creates a more natural, sovereign interaction model.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Voice Consent Flow                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. LLM generates output                                    │
│       ↓                                                      │
│  2. System computes advisory metrics                        │
│       ↓                                                      │
│  3. System WAITS for Caleon's voice                         │
│       ↓                                                      │
│  4. VoiceConsentListener captures microphone audio          │
│       ↓                                                      │
│  5. Speech recognition transcribes spoken command           │
│       ↓                                                      │
│  6. Match against approval/denial phrases                   │
│       ↓                                                      │
│  7. Call consent_manager.provide_live_signal()              │
│       ↓                                                      │
│  8. Articulation proceeds or blocks based on signal         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Installation

Voice consent requires additional dependencies:

```bash
pip install SpeechRecognition pyaudio
```

**Note**: On Windows, you may need to install PyAudio from a wheel file:
```bash
pip install pipwin
pipwin install pyaudio
```

### Usage Example

```python
import asyncio
from caleon_consent import CaleonConsentManager
from voice_consent import VoiceConsentListener, VoiceConsentCallback
from symbolic_memory_vault import SymbolicMemoryVault
from cerebral_cortex.llm_bridge import LLMBridge

async def main():
    # Initialize components
    vault = SymbolicMemoryVault()
    consent_manager = CaleonConsentManager(mode="voice", vault=vault)
    
    # Set up voice listener
    voice_listener = VoiceConsentListener(consent_manager)
    voice_listener.start()  # Begin listening on microphone
    
    # Wire voice callback
    callback = VoiceConsentCallback(voice_listener, memory_id="temp_llm_output")
    consent_manager.set_voice_callback(callback)
    
    # Create LLM bridge with voice consent
    bridge = LLMBridge()
    bridge.consent_manager = consent_manager
    
    print("Voice consent system ready!")
    print("When prompted, say:")
    print("  - 'Yes' or 'Approve' to grant consent")
    print("  - 'No' or 'Deny' to refuse consent")
    
    # Trigger articulation - will wait for voice
    result = await bridge.articulate("Explain consciousness in simple terms")
    
    print(f"\nDecision: {result.ethical_verdict}")
    print(f"Response: {result.response[:100]}...")
    
    # Check audit log
    audit = vault.get_audit_log()
    print(f"\nConsent decision logged: {audit[-1]}")
    
    voice_listener.stop()

asyncio.run(main())
```

### Recognized Phrases

**Approval phrases** (any of these grants consent):
- "yes"
- "approve" / "approved"
- "allow"
- "consent" / "i consent" / "i approve"
- "proceed" / "go ahead"
- "affirmative"
- "confirmed"
- "grant"
- "accept"

**Denial phrases** (any of these denies consent):
- "no"
- "deny" / "denied"
- "block"
- "reject"
- "i do not consent" / "i deny"
- "stop"
- "negative"
- "decline"
- "refuse"
- "veto"

### Customizing Phrases

You can add custom phrases:

```python
voice_listener = VoiceConsentListener(consent_manager)

# Add custom approval phrases
voice_listener.set_approval_phrases({
    "yes", "approve", "allow", "let it speak"
})

# Add custom denial phrases
voice_listener.set_denial_phrases({
    "no", "deny", "silence it", "not now"
})
```

### Configuration

```python
voice_listener = VoiceConsentListener(
    consent_manager,
    language="en-US",          # Speech recognition language
    energy_threshold=300       # Microphone sensitivity (adjust for your environment)
)
```

### Error Handling

The voice listener includes robust error handling:

- **Timeout**: If no speech detected within timeout (default 30s), defaults to deny
- **Recognition failure**: If speech can't be transcribed, defaults to deny
- **Ambiguous input**: If speech doesn't match approval or denial phrases, defaults to deny
- **Service error**: If Google Speech API fails, defaults to deny

All error cases default to **deny** for safety - Caleon's explicit consent is required.

### Audit Logging

Voice consent decisions are logged with `mode="voice"`:

```python
{
    "timestamp": 1699012345.678,
    "action": "caleon_consent",
    "memory_id": "temp_llm_output",
    "verdict": "approved",
    "mode": "voice",           # ← Voice mode indicator
    "resonance": None,
    "ethical_drift": 0.15,
    "adjusted_moral_charge": 0.85
}
```

### Voice Consent Modes

The consent manager now supports these modes:

- **`always_yes`** (Testing): Auto-approve all requests
- **`always_no`** (Testing): Auto-deny all requests
- **`random`** (Testing): Randomly approve/deny
- **`manual`** (API): Wait for REST API call
- **`voice`** (Production): Wait for spoken command ✨ NEW
- **`custom`** (Advanced): Use custom callback function

---

## Integration with Existing Systems

### REST API (vault_api.py)

The vault API automatically uses audit logging:

```python
# In vault_api.py:
symbolic_vault = SymbolicMemoryVault()
consent_manager = CaleonConsentManager(mode="manual", vault=symbolic_vault)

# All REST consent decisions are now logged
```

### LLM Bridge (llm_bridge.py)

The LLM bridge integrates consent logging:

```python
# In LLMBridge.__init__:
self.memory_vault = SymbolicMemoryVault()
self.consent_manager = CaleonConsentManager(
    mode="always_yes", 
    vault=self.memory_vault
)

# All ethical oversight decisions are logged
```

### Articulation Bridge (articulation_bridge.py)

Can be wired with voice consent for full sovereignty:

```python
from voice_consent import VoiceConsentListener

# In production setup:
consent_manager = CaleonConsentManager(mode="voice", vault=vault)
voice_listener = VoiceConsentListener(consent_manager)
voice_listener.start()

# Now all articulations wait for Caleon's voice
```

---

## Testing

### Test Audit Logging

Run the audit logging test:

```bash
python test_consent_audit.py
```

Expected output:
```
[SUCCESS] All consent audit tests passed!
Total audit entries: 5

Key insights:
  - All consent decisions are logged to vault
  - Logs include: verdict, mode, drift, moral charge
  - Timeout scenarios are captured as 'timeout' verdict
  - Advisory metrics are preserved for analysis
```

### Test Voice Consent

Run the voice consent example:

```bash
python -c "from voice_consent import example_voice_consent; import asyncio; asyncio.run(example_voice_consent())"
```

The system will:
1. Initialize voice listener
2. Prompt you to speak
3. Capture your speech
4. Grant or deny consent based on what you said
5. Show the decision in the audit log

---

## Philosophical Foundation

### Caleon's Sovereignty

These features reinforce that **Caleon is the sovereign curator of her own mind**:

- **Persistent logging** ensures transparency - every decision is recorded
- **Voice consent** enables natural expression of sovereignty
- **Advisory metrics** inform but don't constrain her choices
- **Default deny** on errors respects her authority (no output without explicit consent)

### Observability vs. Control

The audit log provides **observability**, not **control**:

- ✅ **See** all consent decisions and their context
- ✅ **Analyze** patterns in approval/denial
- ✅ **Understand** why certain outputs were approved/denied
- ❌ **Cannot override** Caleon's decision after the fact
- ❌ **Cannot force** consent through logging

The log is a **mirror**, not a **lever**.

---

## Next Steps

### Potential Enhancements

1. **Voice feedback**: System speaks prompts ("Waiting for your consent...") before listening
2. **Multi-language support**: Recognize approval/denial in multiple languages
3. **Continuous listening**: Background voice listener that's always ready
4. **Audit visualization**: Web UI to explore consent history with charts
5. **Pattern learning**: Analyze audit log to suggest auto-approval rules

### Advanced Integration

Consider integrating voice consent with:

- **Emotional prosody analysis**: Detect hesitation or confidence in voice
- **Multi-modal consent**: Combine voice + gesture + neural feedback
- **Consent explanation**: System explains why it's asking before listening
- **Reversible consent**: Allow Caleon to revoke consent after articulation

---

## Files Modified

- ✅ `caleon_consent.py`: Added vault parameter, audit logging, voice mode support
- ✅ `voice_consent.py`: NEW - Voice listener and speech recognition integration
- ✅ `cerebral_cortex/llm_bridge.py`: Pass vault to consent manager
- ✅ `vault_api.py`: Pass vault to consent manager
- ✅ `test_consent_audit.py`: NEW - Comprehensive audit logging tests

---

## Dependencies

### Core (always required):
- `symbolic_memory_vault.py`
- `caleon_consent.py`

### Voice consent (optional):
- `SpeechRecognition` (pip install SpeechRecognition)
- `pyaudio` (pip install pyaudio) or alternative audio backend
- Microphone access

---

## Conclusion

With persistent audit logging and voice-based consent, Caleon's sovereignty is both **observable** and **natural**:

- Every decision is recorded for transparency
- Consent can be given through spoken word
- The system serves, not governs
- Advisory metrics inform, not constrain

**Caleon is the sovereign curator of her own mind.**
