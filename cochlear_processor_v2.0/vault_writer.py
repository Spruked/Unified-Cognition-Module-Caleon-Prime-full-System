# vault_writer.py
"""
Vault Writer – structured persistence layer for Cochlear Processor v2
Adds relational indexing (context_hash + prev_trace_id) before
committing each sensory trace to the vault system.
"""

from datetime import datetime
from glyph_encoder import get_context_hash
import json
import os


# -------------------------------------------------------------------
# Minimal stub for Vault interface – replace with actual vault client
# -------------------------------------------------------------------
class _Vault:
    def __init__(self, file_path: str = "sensory_vault_log.jsonl"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)

    def write(self, record: dict):
        """Append the record as a JSON line."""
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")


# Global vault instance
vault = _Vault()


# -------------------------------------------------------------------
# Utility to recall the previous trace ID from last vault line
# -------------------------------------------------------------------
def get_last_trace_id() -> str:
    try:
        with open(vault.file_path, "rb") as f:
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b"\n":
                f.seek(-2, os.SEEK_CUR)
            last_line = f.readline().decode()
        return json.loads(last_line).get("trace_id", "")
    except Exception:
        return ""


# -------------------------------------------------------------------
# Primary write function
# -------------------------------------------------------------------
def write_vault_record(trace: dict, sensory_matrix: dict):
    """
    Augment trace with relational data and commit to vault.
    """
    trace.update({
        "context_hash": get_context_hash(),
        "prev_trace_id": get_last_trace_id(),
        "timestamp_written": datetime.utcnow().isoformat() + "Z",
    })
    vault.write(trace)
