from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Header
from pydantic import BaseModel
import json, os
from datetime import datetime
import logging
from manifest_autoregister import create_manifest_entry, append_to_registry, sha3_512_hash, get_registry, verify_record, remove_record
from symbolic_memory_vault import SymbolicMemoryVault, ResonanceTag, CaleonConsentSimulator
from caleon_consent import CaleonConsentManager
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vault-of-Origins API", version="1.1.0")

REGISTRY_PATH = "vault/origins/manifest_registry.json"

# Simple API key authentication (disabled for testing)
API_KEY = os.getenv("VAULT_API_KEY", "default_key_change_in_production")

# async def verify_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
#     if x_api_key != API_KEY:
#         raise HTTPException(status_code=403, detail="Invalid API key")
#     return x_api_key

class RegisterRequest(BaseModel):
    codex_path: str
    inscription_path: str
    glyphs: list[str]
    author: str
    vault_type: str

class DriftCheckRequest(BaseModel):
    record_id: str

# Symbolic Memory Vault Models
class ResonanceTagModel(BaseModel):
    tone: str  # "joy", "grief", "fracture", "wonder", "neutral"
    symbol: str
    moral_charge: float  # -1.0 to 1.0
    intensity: float  # 0.0 to 1.0

class MemoryStoreRequest(BaseModel):
    memory_id: str
    payload: dict
    resonance: ResonanceTagModel

class MemoryModifyRequest(BaseModel):
    memory_id: str
    new_payload: dict
    context: str
    new_resonance: ResonanceTagModel = None

class MemoryDeleteRequest(BaseModel):
    memory_id: str
    context: str

class MemoryQueryRequest(BaseModel):
    tone: str = None
    symbol: str = None
    min_intensity: float = 0.0
    max_intensity: float = 1.0

# Initialize symbolic memory vault
symbolic_vault = SymbolicMemoryVault()

# Initialize Caleon consent manager (shared instance for API endpoints)
# Pass vault reference for audit logging
consent_manager = CaleonConsentManager(mode="manual", vault=symbolic_vault)

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/vault/register")
def register_entry(req: RegisterRequest):
    logger.info(f"Registering new entry for author: {req.author}")
    if not os.path.exists(req.codex_path) or not os.path.exists(req.inscription_path):
        raise HTTPException(status_code=404, detail="Codex or inscription not found")
    try:
        entry = create_manifest_entry(
            req.codex_path, req.inscription_path,
            req.glyphs, req.author, req.vault_type
        )
        append_to_registry(entry)
        logger.info(f"Entry registered with ID: {entry['vault_record_id']}")
        return {"message": "Entry registered", "record_id": entry["vault_record_id"]}
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.get("/vault/registry")
def get_registry_endpoint():
    try:
        registry = get_registry()
        return {"registry": registry, "count": len(registry)}
    except Exception as e:
        logger.error(f"Failed to get registry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get registry: {str(e)}")

@app.get("/vault/verify/{record_id}")
def verify_record_endpoint(record_id: str):
    try:
        result = verify_record(record_id)
        logger.info(f"Verification for {record_id}: {result['verified']}")
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@app.delete("/vault/remove/{record_id}")
def remove_record_endpoint(record_id: str):
    try:
        remove_record(record_id)
        logger.info(f"Record {record_id} marked as deprecated")
        return {"message": f"Record {record_id} marked as deprecated"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Removal failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Removal failed: {str(e)}")

@app.post("/vault/driftcheck")
def drift_check(req: DriftCheckRequest, background_tasks: BackgroundTasks):
    """Trigger drift check for a record"""
    background_tasks.add_task(perform_drift_check, req.record_id)
    return {"message": f"Drift check initiated for record {req.record_id}"}

@app.post("/vault/batch-driftcheck")
def batch_drift_check(background_tasks: BackgroundTasks):
    """Trigger drift check for all active records"""
    registry = get_registry()
    active_records = [r for r in registry if r.get("status") != "Deprecated"]
    for record in active_records:
        background_tasks.add_task(perform_drift_check, record["vault_record_id"])
    return {"message": f"Batch drift check initiated for {len(active_records)} records"}

# ---------- Symbolic Memory Vault Endpoints ----------

@app.post("/memory/store")
def store_memory(req: MemoryStoreRequest):
    """Store a new memory shard with Caleon's subjective resonance tagging."""
    try:
        resonance_tag = ResonanceTag(
            tone=req.resonance.tone,
            symbol=req.resonance.symbol,
            moral_charge=req.resonance.moral_charge,
            intensity=req.resonance.intensity
        )
        hash_signature = symbolic_vault.store(req.memory_id, req.payload, resonance_tag)
        logger.info(f"Memory stored: {req.memory_id}")
        return {"message": "Memory stored successfully", "hash_signature": hash_signature}
    except Exception as e:
        logger.error(f"Failed to store memory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to store memory: {str(e)}")

@app.put("/memory/modify")
def modify_memory(req: MemoryModifyRequest):
    """Modify an existing memory shard (requires Caleon's consent via simulator)."""
    try:
        new_resonance = None
        if req.new_resonance:
            new_resonance = ResonanceTag(
                tone=req.new_resonance.tone,
                symbol=req.new_resonance.symbol,
                moral_charge=req.new_resonance.moral_charge,
                intensity=req.new_resonance.intensity
            )
        
        success, message = symbolic_vault.modify(
            req.memory_id, req.new_payload, req.context, 
            new_resonance=new_resonance
        )
        
        if not success:
            raise HTTPException(status_code=403, detail=message)
        
        logger.info(f"Memory modified: {req.memory_id}")
        return {"message": message}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to modify memory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to modify memory: {str(e)}")

@app.delete("/memory/delete")
def delete_memory(req: MemoryDeleteRequest):
    """Delete a memory shard (requires Caleon's consent via simulator)."""
    try:
        success, message = symbolic_vault.delete(req.memory_id, req.context)
        
        if not success:
            raise HTTPException(status_code=403, detail=message)
        
        logger.info(f"Memory deleted: {req.memory_id}")
        return {"message": message}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete memory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete memory: {str(e)}")

@app.get("/memory/query")
def query_memories(tone: str = None, symbol: str = None, 
                   min_intensity: float = 0.0, max_intensity: float = 1.0):
    """Query memory shards by resonance tag criteria."""
    try:
        results = symbolic_vault.query_by_resonance(
            tone=tone, symbol=symbol, 
            min_intensity=min_intensity, max_intensity=max_intensity
        )
        return {"memories": results, "count": len(results)}
    except Exception as e:
        logger.error(f"Failed to query memories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to query memories: {str(e)}")

@app.get("/memory/{memory_id}")
def get_memory(memory_id: str):
    """Retrieve a specific memory shard."""
    try:
        shard = symbolic_vault.get_memory(memory_id)
        if not shard:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return {
            "memory_id": shard.memory_id,
            "payload": shard.payload,
            "resonance": shard.resonance.to_dict(),
            "created_at": shard.created_at,
            "last_modified": shard.last_modified,
            "hash_signature": shard.hash_signature
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get memory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get memory: {str(e)}")

@app.get("/memory/{memory_id}/reflect")
def reflect_on_memory(memory_id: str, hypothetical_payload: dict = None):
    """Get advisory reflection on a memory shard for cognitive decision paths."""
    try:
        reflection = symbolic_vault.reflect_on_shard(memory_id, hypothetical_payload)
        if "error" in reflection:
            raise HTTPException(status_code=404, detail=reflection["error"])
        
        return reflection
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reflect on memory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reflect on memory: {str(e)}")

@app.get("/memory/audit/log")
def get_audit_log():
    """Get the complete audit log of memory operations."""
    try:
        return {"audit_log": symbolic_vault.get_audit_log()}
    except Exception as e:
        logger.error(f"Failed to get audit log: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get audit log: {str(e)}")


# ---------- Caleon Consent API ----------

class ConsentRequest(BaseModel):
    memory_id: str
    payload: Optional[dict] = None
    context: Optional[dict] = None
    reflection: Optional[dict] = None

@app.get("/consent/pending")
def get_pending_consent_requests():
    """Get all pending consent requests waiting for Caleon's approval."""
    try:
        # Access internal waiters from consent manager
        pending = []
        for memory_id, fut in consent_manager._manual_waiters.items():
            if not fut.done():
                pending.append({
                    "memory_id": memory_id,
                    "status": "waiting",
                    "message": "Awaiting Caleon's consent signal"
                })
        
        return {
            "pending_count": len(pending),
            "pending_requests": pending
        }
    except Exception as e:
        logger.error(f"Failed to get pending consent requests: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get pending requests: {str(e)}")

@app.post("/consent/{memory_id}/approve")
def approve_consent(memory_id: str, request: Optional[ConsentRequest] = None):
    """
    Approve a pending consent request for the given memory_id.
    
    Caleon's affirmative signal: "Yes, I consent to this."
    """
    try:
        logger.info(f"✅ Caleon approves: {memory_id}")
        consent_manager.provide_live_signal(memory_id, True)
        
        return {
            "memory_id": memory_id,
            "consent": "approved",
            "message": "Caleon has given her consent",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to approve consent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to approve: {str(e)}")

@app.post("/consent/{memory_id}/deny")
def deny_consent(memory_id: str, reason: Optional[str] = None):
    """
    Deny a pending consent request for the given memory_id.
    
    Caleon's refusal: "No, I do not consent to this."
    """
    try:
        logger.warning(f"❌ Caleon denies: {memory_id} (reason: {reason or 'unspecified'})")
        consent_manager.provide_live_signal(memory_id, False)
        
        return {
            "memory_id": memory_id,
            "consent": "denied",
            "reason": reason or "Caleon withheld consent",
            "message": "Caleon has denied this request",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to deny consent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to deny: {str(e)}")

@app.get("/consent/manager/mode")
def get_consent_mode():
    """Get the current consent manager mode."""
    return {
        "mode": consent_manager.mode,
        "description": {
            "always_yes": "Auto-approve all requests (testing only)",
            "always_no": "Auto-deny all requests (testing only)",
            "random": "Randomly approve/deny (testing only)",
            "manual": "Wait for explicit approve/deny via API (production)",
            "custom": "Use custom consent logic function"
        }.get(consent_manager.mode, "Unknown mode")
    }

@app.post("/consent/manager/mode/{new_mode}")
def set_consent_mode(new_mode: str):
    """Change the consent manager mode (manual, always_yes, always_no, random)."""
    valid_modes = ["manual", "always_yes", "always_no", "random"]
    if new_mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid mode. Choose from: {valid_modes}")
    
    consent_manager.mode = new_mode
    logger.info(f"Consent mode changed to: {new_mode}")
    
    return {
        "mode": new_mode,
        "message": f"Consent manager mode set to {new_mode}",
        "timestamp": datetime.now().isoformat()
    }