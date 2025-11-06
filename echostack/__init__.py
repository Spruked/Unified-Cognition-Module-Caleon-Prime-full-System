# echostack_module/__init__.py

"""
EchoStack Module Initialization
Exposes core logic filters, seed vault access, trace routing, and echo processing.
"""

from .echostack import EchoStack

__all__ = [
    "EchoStack",
]
