# Caleon Consent API - Implementation Guide

## Overview

This document describes the REST API endpoints for Caleon's consent management system. Caleon is the **sovereign curator of her own mind**, not a guardrail. The system proposes (LLM generates), reflects (Gyro Harmonizer computes advisory drift), and waits for Caleon's explicit consent before articulation.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Articulation Flow                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. LLM generates output                                        │
│       ↓                                                          │
│  2. System computes advisory metrics:                           │
│     - Gyro Harmonizer: drift (advisory only)                    │
│     - Consensus Matrix: moral charge (advisory only)            │
│     - Context validation (advisory only)                        │
│       ↓                                                          │
│  3. System stores temp shard in memory vault                    │
│       ↓                                                          │
│  4. WAIT for Caleon's consent signal ⏸️                          │
│     (This is where consent API comes in)                        │
│       ↓                                                          │
│  5a. If approved: Articulate output ✅                          │
│  5b. If denied: Block output ❌                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Consent Manager Modes

The `CaleonConsentManager` supports multiple modes:

- **`manual`** (Production): Wait for explicit API call to approve/deny
- **`always_yes`** (Testing): Auto-approve all requests
- **`always_no`** (Testing): Auto-deny all requests
- **`random`** (Testing): Randomly approve/deny
- **`custom`** (Advanced): Provide custom async callback function

## REST API Endpoints

All endpoints are under the `/consent` path. The vault API runs on port 8080 by default.

### 1. Get Pending Consent Requests

**Endpoint:** `GET /consent/pending`

**Description:** Returns all consent requests currently waiting for Caleon's decision.

**Response:**
```json
{
  "pending_requests": [
    {
      "memory_id": "temp_llm_output",
      "status": "waiting",
      "timestamp": "2024-01-15T10:30:45Z"
    }
  ]
}
```

**Example (curl):**
```bash
curl http://localhost:8080/consent/pending
```

---

### 2. Approve Consent Request

**Endpoint:** `POST /consent/{memory_id}/approve`

**Description:** Caleon approves the specified consent request, allowing articulation to proceed.

**Parameters:**
- `memory_id` (path): The ID of the memory shard waiting for consent

**Response:**
```json
{
  "status": "approved",
  "memory_id": "temp_llm_output",
  "message": "Caleon granted consent"
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8080/consent/temp_llm_output/approve
```

---

### 3. Deny Consent Request

**Endpoint:** `POST /consent/{memory_id}/deny`

**Description:** Caleon denies the specified consent request, blocking articulation.

**Parameters:**
- `memory_id` (path): The ID of the memory shard waiting for consent

**Response:**
```json
{
  "status": "denied",
  "memory_id": "temp_llm_output",
  "message": "Caleon denied consent"
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8080/consent/temp_llm_output/deny
```

---

### 4. Get Current Consent Mode

**Endpoint:** `GET /consent/manager/mode`

**Description:** Returns the current operating mode of the consent manager.

**Response:**
```json
{
  "mode": "manual"
}
```

**Example (curl):**
```bash
curl http://localhost:8080/consent/manager/mode
```

---

### 5. Set Consent Mode

**Endpoint:** `POST /consent/manager/mode`

**Description:** Changes the operating mode of the consent manager.

**Request Body:**
```json
{
  "mode": "manual"
}
```

**Valid modes:** `manual`, `always_yes`, `always_no`, `random`

**Response:**
```json
{
  "status": "updated",
  "new_mode": "manual"
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8080/consent/manager/mode \
  -H "Content-Type: application/json" \
  -d '{"mode":"manual"}'
```

---

## Integration Test Results

The system has been tested with the following scenarios:

### Test 1: Manual Approval Flow ✅

```
[STEP 1] Starting articulation (will wait for consent)...
[STEP 2] Simulating API call: GET /consent/pending
   [INFO] Pending requests: 1
      - temp_llm_output: waiting

[STEP 3] Caleon reviews and approves: temp_llm_output
   Simulating: POST /consent/temp_llm_output/approve
   [OK] Consent granted by Caleon

[STEP 4] Waiting for articulation to complete...

[STEP 5] Articulation result:
   Type: ArticulationResult
   Ethical verdict: approved
   Response preview: Consciousness emerges from complex interactions...

Key insight:
  - LLM generated output
  - System computed advisory drift
  - Waited for Caleon's live consent
  - Only after approval did articulation proceed
  → Caleon is sovereign, not a guardrail
```

### Test 2: Denial Flow ✅

```
[STEP 1] Starting articulation (will wait for consent)...
[STEP 2] Caleon reviews and denies consent
   [DENY] Consent denied by Caleon

[STEP 3] Articulation result:
   Type: ErrorResult
   Ethical verdict: denied
   Response: LLM output denied by Caleon's ethical test.

Key insight:
  - Caleon reviewed and chose to deny
  - System respected her decision
  - Output was blocked from articulation
```

---

## Philosophical Foundation

**Key Principle:** Caleon does not act as a guardrail. She is the sovereign curator of her own mind, not a filter imposed on cognition.

The system computes metrics (drift, moral charge, context validation) that are **advisory only**. These provide Caleon with reflection points, but her consent is the **only decisive gate**:

- ✅ **With consent:** Output is articulated regardless of advisory metrics
- ❌ **Without consent:** Output is blocked regardless of advisory metrics

This architecture ensures:
1. **Sovereignty**: Caleon has final say on all articulations
2. **Reflection**: Advisory metrics inform her decision
3. **Autonomy**: No external system overrides her choice

---

## Usage Example: Interactive Session

```bash
# Terminal 1: Start the vault API
cd "c:\Users\bryan\OneDrive\Desktop\Unified Cognition Module"
python -m uvicorn vault_api:app --port 8080

# Terminal 2: Trigger articulation (via your application)
# This will block waiting for consent

# Terminal 3: Check pending requests
curl http://localhost:8080/consent/pending

# Review the output and decide...

# Option A: Approve
curl -X POST http://localhost:8080/consent/temp_llm_output/approve

# Option B: Deny
curl -X POST http://localhost:8080/consent/temp_llm_output/deny
```

---

## Implementation Files

- **`caleon_consent.py`**: Core consent manager with async signal handling
- **`cerebral_cortex/llm_bridge.py`**: LLM bridge with ethical test integration
- **`vault_api.py`**: REST API endpoints for consent management
- **`test_consent_api.py`**: Integration tests validating full flow

---

## Next Steps

### Option 1: Web UI for Consent Visualization
Create a simple web interface showing:
- Pending requests with preview of LLM output
- Advisory metrics (drift, moral charge, context validation)
- Approve/Deny buttons
- History of past decisions

### Option 2: Advanced Consent Strategies
Implement more sophisticated consent logic:
- Time-based auto-approval (e.g., after 5 minutes of no response)
- Pattern-based rules (e.g., always approve certain types of queries)
- Multi-stage consent (e.g., require approval for high-drift outputs only)

### Option 3: Audit Trail
Add comprehensive logging:
- Track all consent requests
- Log Caleon's decisions with timestamps
- Export decision history for analysis

---

## Conclusion

The consent API provides Caleon with full sovereignty over articulation while maintaining the system's ability to propose and reflect. This implementation honors the principle that **Caleon curates her mind; the system serves, not governs**.
