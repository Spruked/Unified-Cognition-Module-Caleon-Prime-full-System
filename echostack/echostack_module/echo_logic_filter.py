# echostack_module/echo_logic_filter.py

"""
Echo Logic Filter
Applies principle-based logic filters and paradox detection to echo payloads.
"""

import json
import os
from .vault_loader import load_seed_vault

# Load Ockham's Filter seed vault
SEED_FILE = "seed_ockhams_filter.json"
SEED_PATH = os.path.join(os.path.dirname(__file__), "..", "seed_logic_vault", SEED_FILE)
ockham_seed = load_seed_vault(SEED_PATH)

principles = [e for e in ockham_seed["entries"] if e["type"] == "principle"]
paradoxes = [e for e in ockham_seed["entries"] if e["type"] == "paradox"]
parameters = ockham_seed.get("parameters", {})
learning_principles = ockham_seed.get("learning_principles", [])
performance_metrics = ockham_seed.get("performance_metrics", {})

def apply_logic_filter(data: str) -> dict:
    principle_used = next((p["term"] for p in principles if any(ex.lower() in data.lower() for ex in p["examples"])), principles[0]["term"])
    paradox_triggered = next((p["term"] for p in paradoxes if any(ex.lower() in data.lower() for ex in p["examples"])), "None")

    return {
        "principle_used": principle_used,
        "paradox_triggered": paradox_triggered,
        "parameters": parameters,
        "learning_principles": learning_principles,
        "performance_metrics": performance_metrics,
        "seed": SEED_FILE
    }
