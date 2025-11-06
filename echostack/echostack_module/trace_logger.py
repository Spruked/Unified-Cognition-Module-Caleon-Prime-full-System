# echostack_module/tracelogger.py

"""
Trace Logger
Records echo trace events with metadata for audit, replay, and legacy preservation.
"""

import json
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def log_trace_event(trace: dict, label: str = "echo") -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    filename = f"{label}_trace_{timestamp}.json"
    filepath = os.path.join(LOG_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2)

    return filepath

def summarize_trace(trace: dict) -> dict:
    return {
        "timestamp": trace.get("timestamp"),
        "source": trace.get("source"),
        "seed": trace.get("logic_filter", {}).get("seed"),
        "principle": trace.get("logic_filter", {}).get("principle_used"),
        "paradox": trace.get("logic_filter", {}).get("paradox_triggered"),
        "reasoning_type": trace.get("epistemic_overlay", {}).get("reasoning_type"),
        "reflex_tier": trace.get("epistemic_overlay", {}).get("reflex_tier")
    }
