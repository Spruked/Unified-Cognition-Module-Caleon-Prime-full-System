# echostack_module/vault_loader.py

"""
Vault Loader
Loads and parses seed vaults for logic filters, overlays, and trace routing.
"""

import json
import os

def load_seed_vault(path: str) -> dict:
    if not os.path.exists(path):
        return {"error": f"Seed vault not found at {path}"}

    try:
        with open(path, "r", encoding="utf-8") as f:
            vault = json.load(f)
    except Exception as e:
        return {"error": f"Failed to load seed vault: {str(e)}"}

    # Basic schema validation
    required_keys = ["vault_id", "version", "entries"]
    for key in required_keys:
        if key not in vault:
            return {"error": f"Missing required key: {key}"}

    return vault

def extract_entries(vault: dict, entry_type: str = None) -> list:
    if "entries" not in vault:
        return []

    if entry_type:
        return [e for e in vault["entries"] if e.get("type") == entry_type]
    return vault["entries"]
