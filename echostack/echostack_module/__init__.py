# echostack_module/__init__.py

"""
EchoStack Module Initialization
Anchors logic filters, seed vault access, and trace routing.
"""

from .vault_loader import load_seed_vault
from .echo_logic_filter import apply_logic_filter
from .trace_router import route_trace

# Import from parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from epistemic_filter import apply_epistemic_overlay

# Preload core seed vaults
SEED_FILES = [
    "seed_ockhams_filter.json",
    "seed_hume.json",
    "seed_taleb.json",
    "seed_nonmonotonic.json",
    "seed_apriori.json",
    "seed_aposteriori.json",
    "seed_proverbs.json",
]

seed_vaults = {name: load_seed_vault(name) for name in SEED_FILES}

__all__ = [
    "seed_vaults",
    "apply_logic_filter",
    "route_trace",
    "apply_epistemic_overlay"
]
