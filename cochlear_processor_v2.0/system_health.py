# system_health.py
"""
System Health – lightweight diagnostic layer for Cochlear Processor v2
Provides version info, memory load, and injects health data into traces.
"""

import psutil

# Versioning
_VERSION = "v2.0.1-RC.3"

# Counter to reduce overhead (inject once every 100 packets)
_ping_counter = 0


def get_system_version() -> str:
    """Return the current build version."""
    return _VERSION


def get_memory_load() -> float:
    """Return current system memory utilization as a percentage."""
    try:
        return round(psutil.virtual_memory().percent, 2)
    except Exception:
        return -1.0


def inject_health(trace: dict):
    """
    Add version and system metrics to every 100th packet.
    Keeps runtime overhead minimal.
    """
    global _ping_counter
    _ping_counter += 1

    if _ping_counter % 100 == 0:
        trace.update({
            "v2_version": get_system_version(),
            "system_load": get_memory_load()
        })
