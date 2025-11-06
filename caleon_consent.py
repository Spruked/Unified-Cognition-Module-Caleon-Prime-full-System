"""
caleon_consent.py

Provides an async, pluggable consent manager for Caleon.

Modes supported:
- always_yes (default)
- always_no
- random
- manual  (wait for external provide_live_signal)
- voice   (wait for voice-based approval/denial)
- custom  (call a provided sync/async function)

The manager is intentionally small and testable. In a production
system this would be wired to a UI, voice channel, or internal
reflection loop that waits for Caleon's deliberate signal.

All consent decisions are logged to the vault audit log for persistence
and observability.
"""

from __future__ import annotations

import asyncio
import random
import time
from typing import Any, Callable, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from symbolic_memory_vault import SymbolicMemoryVault


class CaleonConsentManager:
    """Manage Caleon's consent signals in a pluggable way.

    Typical usage:
        cm = CaleonConsentManager(mode="manual", vault=vault)
        # In another coroutine (UI): await cm.get_live_signal(...)
        # To provide a live signal from UI/tests: cm.provide_live_signal(memory_id, True)
    
    All consent decisions are logged to the vault audit log for observability.
    """

    def __init__(
        self, 
        mode: str = "always_yes",
        vault: Optional[SymbolicMemoryVault] = None
    ) -> None:
        self.mode = mode
        self.vault = vault
        self.custom_fn: Optional[Callable[..., Any]] = None
        # manual waiters: memory_id -> list of futures awaiting a signal
        self._manual_waiters: Dict[str, asyncio.Future] = {}
        # voice consent callback (set by voice module)
        self._voice_callback: Optional[Callable[[], Any]] = None

    def set_custom_logic(self, fn: Callable[..., Any]) -> None:
        """Provide a custom function (sync or async) that returns bool.

        The function signature should accept (memory_id, context, proposed_payload, reflection)
        and return a bool or an awaitable resolving to bool.
        """
        self.custom_fn = fn
        self.mode = "custom"
    
    def set_voice_callback(self, fn: Callable[[], Any]) -> None:
        """Set the voice consent callback for 'voice' mode.
        
        The callback should return a bool or awaitable resolving to bool.
        """
        self._voice_callback = fn
    
    def _log_consent_decision(
        self,
        memory_id: str,
        decision: bool,
        mode: str,
        reflection: Optional[dict] = None,
        timeout: bool = False
    ) -> None:
        """Log consent decision to vault audit log."""
        if self.vault is None:
            return
        
        verdict = "approved" if decision else ("timeout" if timeout else "denied")
        
        # Extract advisory metrics from reflection if available
        drift = 0.0
        moral = 0.0
        if reflection:
            drift = reflection.get("drift", 0.0)
            moral = reflection.get("adjusted_moral_charge", 0.0)
        
        entry = {
            "timestamp": time.time(),
            "action": "caleon_consent",
            "memory_id": memory_id,
            "verdict": verdict,
            "mode": mode,
            "resonance": None,  # Not applicable for consent decisions
            "ethical_drift": drift,
            "adjusted_moral_charge": moral
        }
        
        # Directly append to audit log (bypassing _log_event since we have custom fields)
        self.vault.audit_log.append(entry)

    async def get_live_signal(
        self,
        memory_id: str = "global",
        context: Optional[dict] = None,
        proposed_payload: Optional[dict] = None,
        reflection: Optional[dict] = None,
        timeout: Optional[float] = 30.0,
    ) -> bool:
        """Return Caleon's consent signal.

        Modes:
        - always_yes / always_no / random / custom / manual / voice
        - manual: waits until `provide_live_signal` is called for the same memory_id.
        - voice: waits for voice-based approval/denial via callback.
        
        All decisions are logged to the vault audit log.
        """
        mode = self.mode or "always_yes"
        
        # Manual and voice modes have their own logging, return early
        if mode == "manual":
            return await self._manual_consent(memory_id, timeout, reflection)
        
        if mode == "voice":
            # Wait for voice callback to provide signal
            if self._voice_callback is not None:
                return await self._voice_consent(memory_id, timeout, reflection)
            else:
                # No voice callback set, fall back to manual
                return await self._manual_consent(memory_id, timeout, reflection)
        
        # For other modes, compute decision and log it
        decision = False
        timed_out = False

        try:
            if mode == "always_yes":
                decision = True
            elif mode == "always_no":
                decision = False
            elif mode == "random":
                decision = random.choice([True, False])
            elif mode == "custom" and self.custom_fn is not None:
                try:
                    if asyncio.iscoroutinefunction(self.custom_fn):
                        decision = await self.custom_fn(memory_id, context, proposed_payload, reflection)
                    else:
                        decision = bool(self.custom_fn(memory_id, context, proposed_payload, reflection))
                except Exception:
                    # If custom logic fails, default to deny to be safe
                    decision = False
            else:
                # Fallback
                decision = True

        finally:
            # Log the decision
            self._log_consent_decision(memory_id, decision, mode, reflection, timed_out)

        return decision
    
    async def _manual_consent(
        self, 
        memory_id: str, 
        timeout: Optional[float],
        reflection: Optional[dict] = None
    ) -> bool:
        """Handle manual consent mode with proper logging."""
        # Create a future and wait for provide_live_signal to set it
        fut = asyncio.get_event_loop().create_future()
        self._manual_waiters[memory_id] = fut
        timed_out = False
        decision = False
        
        try:
            decision = bool(await asyncio.wait_for(fut, timeout=timeout))
        except asyncio.TimeoutError:
            # Timeout -> deny by default
            timed_out = True
            decision = False
        finally:
            # Cleanup
            self._manual_waiters.pop(memory_id, None)
            # Log the decision
            self._log_consent_decision(memory_id, decision, "manual", reflection, timed_out)
        
        return decision
    
    async def _voice_consent(
        self,
        memory_id: str,
        timeout: Optional[float],
        reflection: Optional[dict] = None
    ) -> bool:
        """Handle voice consent mode with proper logging."""
        timed_out = False
        decision = False
        
        try:
            if asyncio.iscoroutinefunction(self._voice_callback):
                decision = await asyncio.wait_for(
                    self._voice_callback(), 
                    timeout=timeout
                )
            else:
                decision = bool(self._voice_callback())
        except asyncio.TimeoutError:
            timed_out = True
            decision = False
        except Exception:
            decision = False
        finally:
            # Log the decision
            self._log_consent_decision(memory_id, decision, "voice", reflection, timed_out)
        
        return decision

    def provide_live_signal(self, memory_id: str, value: bool) -> None:
        """External caller (UI, tests) provides a live signal for a memory id.

        If no waiter exists, store the value by immediately resolving a future
        to support racing producers/consumers.
        """
        fut = self._manual_waiters.get(memory_id)
        if fut is not None and not fut.done():
            fut.set_result(value)
        else:
            # No active waiter; create a completed future so next waiter will get it
            loop = asyncio.get_event_loop()
            f = loop.create_future()
            f.set_result(value)
            self._manual_waiters[memory_id] = f


# Simple convenience alias for tests
def get_default_manager() -> CaleonConsentManager:
    return CaleonConsentManager(mode="always_yes")
