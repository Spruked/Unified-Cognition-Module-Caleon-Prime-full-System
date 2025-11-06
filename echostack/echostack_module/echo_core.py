# echostack_module/echo_core.py

"""
Echo Core Processor
Handles echo ingestion, hashing, metadata embedding, and logic filter dispatch.
"""

import json
import hashlib
from datetime import datetime
from .echo_logic_filter import apply_logic_filter
from .epistemic_filter import apply_epistemic_overlay
from .trace_router import route_trace

def process_echo(payload: str, source: str = "user") -> dict:
    timestamp = datetime.utcnow().isoformat()
    hash_digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    # Apply logic filters
    logic_result = apply_logic_filter(payload)

    # Apply epistemic overlays
    epistemic_result = apply_epistemic_overlay(payload)

    # Route trace metadata
    trace_result = route_trace(payload)

    echo_trace = {
        "timestamp": timestamp,
        "source": source,
        "original": payload,
        "hash": hash_digest,
        "logic_filter": logic_result,
        "epistemic_overlay": epistemic_result,
        "trace_metadata": trace_result
    }

    return echo_trace

def export_echo_trace(trace: dict, as_json: bool = True) -> str:
    return json.dumps(trace, indent=2) if as_json else str(trace)
