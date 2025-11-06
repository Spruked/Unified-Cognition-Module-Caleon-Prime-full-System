"""
Manifest Auto-Register Module for Vault-of-Origins
Handles creation and registration of philosophical/ethical entries.
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Any
import uuid

REGISTRY_PATH = "vault/origins/manifest_registry.json"

def sha3_512_hash(file_path: str) -> str:
    """Compute SHA3-512 hash of a file."""
    hash_sha3_512 = hashlib.sha3_512()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha3_512.update(chunk)
        return hash_sha3_512.hexdigest()
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")

def create_manifest_entry(codex_path: str, inscription_path: str, glyphs: List[str], author: str, vault_type: str) -> Dict[str, Any]:
    """Create a new manifest entry for the vault registry."""
    if not os.path.exists(codex_path):
        raise ValueError(f"Codex file not found: {codex_path}")
    if not os.path.exists(inscription_path):
        raise ValueError(f"Inscription file not found: {inscription_path}")

    # Generate unique record ID
    record_id = str(uuid.uuid4())

    # Compute hash of inscription
    inscription_hash = sha3_512_hash(inscription_path)

    # Create entry
    entry = {
        "vault_record_id": record_id,
        "timestamp": datetime.utcnow().isoformat(),
        "author": author,
        "vault_type": vault_type,
        "glyphs": glyphs,
        "codex_link": codex_path,
        "inscription_link": inscription_path,
        "hash_sha3_512": inscription_hash,
        "drift_score": 0.0,  # Initial drift score
        "status": "Active"
    }

    return entry

def append_to_registry(entry: Dict[str, Any]):
    """Append a new entry to the manifest registry."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)

    # Load existing registry or create empty list
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)
    else:
        registry = []

    # Append new entry
    registry.append(entry)

    # Save back to file
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

def get_registry() -> List[Dict[str, Any]]:
    """Get the current manifest registry."""
    if not os.path.exists(REGISTRY_PATH):
        return []
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def verify_record(record_id: str) -> Dict[str, Any]:
    """Verify a record's integrity by re-computing hash."""
    registry = get_registry()
    for record in registry:
        if record["vault_record_id"] == record_id:
            current_hash = sha3_512_hash(record["inscription_link"])
            verified = current_hash == record["hash_sha3_512"]
            return {
                "record_id": record_id,
                "verified": verified,
                "current_hash": current_hash,
                "original_hash": record["hash_sha3_512"]
            }
    raise ValueError(f"Record not found: {record_id}")

def remove_record(record_id: str):
    """Soft-delete a record by marking it as Deprecated."""
    registry = get_registry()
    for record in registry:
        if record["vault_record_id"] == record_id:
            record["status"] = "Deprecated"
            record["deprecated_at"] = datetime.utcnow().isoformat()
            # Save updated registry
            with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            return
    raise ValueError(f"Record not found: {record_id}")