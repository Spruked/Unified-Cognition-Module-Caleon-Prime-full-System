"""
TraceLogger Module - Live Injection System
Provides real-time trace injection capabilities for EchoStack reasoning cycles.
"""

import json
import time
import threading
import queue
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum


class InjectionPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class InjectionType(Enum):
    TRACE_OVERRIDE = "trace_override"
    VAULT_INJECTION = "vault_injection"
    REASONING_BIAS = "reasoning_bias"
    TELEMETRY_OVERRIDE = "telemetry_override"
    HEALTH_CHECK = "health_check"


@dataclass(order=True)
class LiveInjection:
    """Represents a live injection event"""
    priority: InjectionPriority
    injection_id: str
    injection_type: InjectionType
    payload: Dict[str, Any]
    target_module: str
    timestamp: str
    expires_at: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    executed: bool = False
    execution_count: int = 0


class TraceLogger:
    """
    Live Injection System for EchoStack
    Enables real-time trace injection and dynamic system modification
    """

    def __init__(self, telemetry_path: str = "../telemetry.json"):
        self.telemetry_path = telemetry_path
        self.injection_queue = queue.PriorityQueue()
        self.active_injections: Dict[str, LiveInjection] = {}
        self.injection_history: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None

        # Injection handlers
        self.handlers: Dict[InjectionType, Callable] = {
            InjectionType.TRACE_OVERRIDE: self._handle_trace_override,
            InjectionType.VAULT_INJECTION: self._handle_vault_injection,
            InjectionType.REASONING_BIAS: self._handle_reasoning_bias,
            InjectionType.TELEMETRY_OVERRIDE: self._handle_telemetry_override,
            InjectionType.HEALTH_CHECK: self._handle_health_check,
        }

        # Load existing injections from telemetry
        self._load_persistent_injections()

    def start(self):
        """Start the live injection processing thread"""
        if self.running:
            return

        self.running = True
        self.worker_thread = threading.Thread(target=self._process_injections, daemon=True)
        self.worker_thread.start()
        print("[TraceLogger] Live injection system started")

    def stop(self):
        """Stop the live injection processing thread"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
        print("[TraceLogger] Live injection system stopped")

    def inject(self, injection: LiveInjection) -> bool:
        """Inject a new live injection into the system"""
        with self.lock:
            if injection.injection_id in self.active_injections:
                print(f"[TraceLogger] Injection {injection.injection_id} already exists")
                return False

            # Add to queue with priority
            priority_value = injection.priority.value
            self.injection_queue.put((priority_value, injection))

            # Store as active
            self.active_injections[injection.injection_id] = injection

            print(f"[TraceLogger] Injected: {injection.injection_id} ({injection.injection_type.value})")
            return True

    def cancel_injection(self, injection_id: str) -> bool:
        """Cancel an active injection"""
        with self.lock:
            if injection_id not in self.active_injections:
                return False

            injection = self.active_injections[injection_id]
            injection.executed = True  # Mark as cancelled
            self._log_injection_event(injection, "cancelled")

            del self.active_injections[injection_id]
            print(f"[TraceLogger] Cancelled injection: {injection_id}")
            return True

    def get_active_injections(self) -> List[Dict[str, Any]]:
        """Get list of currently active injections"""
        with self.lock:
            return [asdict(inj) for inj in self.active_injections.values()]

    def get_injection_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent injection history"""
        with self.lock:
            return self.injection_history[-limit:]

    def _process_injections(self):
        """Main processing loop for injections"""
        while self.running:
            try:
                # Process pending injections
                while not self.injection_queue.empty():
                    priority, injection = self.injection_queue.get_nowait()
                    self._execute_injection(injection)
                    self.injection_queue.task_done()

                # Check for expired injections
                self._cleanup_expired_injections()

                # Update telemetry
                self._update_telemetry()

                time.sleep(0.1)  # 100ms processing interval

            except Exception as e:
                print(f"[TraceLogger] Processing error: {e}")
                time.sleep(1.0)

    def _execute_injection(self, injection: LiveInjection):
        """Execute a single injection"""
        try:
            # Check conditions if specified
            if injection.conditions and not self._check_conditions(injection.conditions):
                print(f"[TraceLogger] Conditions not met for injection {injection.injection_id}")
                return

            # Execute via handler
            handler = self.handlers.get(injection.injection_type)
            if handler:
                result = handler(injection)
                injection.executed = True
                injection.execution_count += 1
                self._log_injection_event(injection, "executed", result)
                print(f"[TraceLogger] Executed injection: {injection.injection_id}")
            else:
                print(f"[TraceLogger] No handler for injection type: {injection.injection_type}")

        except Exception as e:
            print(f"[TraceLogger] Execution error for {injection.injection_id}: {e}")
            self._log_injection_event(injection, "error", str(e))

    def _handle_trace_override(self, injection: LiveInjection) -> Dict[str, Any]:
        """Handle trace override injection"""
        # Override current trace with injected payload
        trace_data = injection.payload.get("trace_data", {})
        # Implementation would modify active trace logging
        return {"status": "trace_overridden", "trace_id": trace_data.get("id")}

    def _handle_vault_injection(self, injection: LiveInjection) -> Dict[str, Any]:
        """Handle vault injection"""
        vault_data = injection.payload.get("vault_data", {})
        # Implementation would inject into active vault system
        return {"status": "vault_injected", "vault_id": vault_data.get("id")}

    def _handle_reasoning_bias(self, injection: LiveInjection) -> Dict[str, Any]:
        """Handle reasoning bias injection"""
        bias_data = injection.payload.get("bias_data", {})
        # Implementation would modify reasoning parameters
        return {"status": "bias_applied", "bias_type": bias_data.get("type")}

    def _handle_telemetry_override(self, injection: LiveInjection) -> Dict[str, Any]:
        """Handle telemetry override injection"""
        telemetry_data = injection.payload.get("telemetry_data", {})
        # Implementation would override telemetry values
        return {"status": "telemetry_overridden", "metrics": list(telemetry_data.keys())}

    def _handle_health_check(self, injection: LiveInjection) -> Dict[str, Any]:
        """Handle health check injection"""
        # Perform immediate health assessment
        health_status = self._perform_health_check()
        return {"status": "health_checked", "health_score": health_status}

    def _check_conditions(self, conditions: Dict[str, Any]) -> bool:
        """Check if injection conditions are met"""
        # Implementation would check system state against conditions
        return True  # Placeholder

    def _cleanup_expired_injections(self):
        """Remove expired injections"""
        current_time = datetime.now()
        expired_ids = []

        for inj_id, injection in self.active_injections.items():
            if injection.expires_at:
                expiry_time = datetime.fromisoformat(injection.expires_at)
                if current_time > expiry_time:
                    expired_ids.append(inj_id)
                    self._log_injection_event(injection, "expired")

        for inj_id in expired_ids:
            del self.active_injections[inj_id]

    def _log_injection_event(self, injection: LiveInjection, event_type: str, result: Any = None):
        """Log injection event to history"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "injection_id": injection.injection_id,
            "event_type": event_type,
            "injection_type": injection.injection_type.value,
            "priority": injection.priority.value,
            "target_module": injection.target_module,
            "result": result
        }
        self.injection_history.append(event)

        # Keep history bounded
        if len(self.injection_history) > 1000:
            self.injection_history = self.injection_history[-500:]

    def _load_persistent_injections(self):
        """Load persistent injections from telemetry"""
        try:
            with open(self.telemetry_path, 'r') as f:
                telemetry = json.load(f)

            # Load any persistent injections from telemetry
            persistent_injections = telemetry.get("live_injections", {}).get("persistent", [])
            for inj_data in persistent_injections:
                # Reconstruct injection object
                injection = LiveInjection(**inj_data)
                self.active_injections[injection.injection_id] = injection

        except Exception as e:
            print(f"[TraceLogger] Failed to load persistent injections: {e}")

    def _update_telemetry(self):
        """Update telemetry with current injection status"""
        try:
            telemetry = {}
            try:
                with open(self.telemetry_path, 'r') as f:
                    telemetry = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                # If file doesn't exist or is malformed, start with empty dict
                telemetry = {}

            # Ensure telemetry is a dict
            if not isinstance(telemetry, dict):
                telemetry = {}

            # Update live injection status
            telemetry["live_injections"] = {
                "active_count": len(self.active_injections),
                "queue_size": self.injection_queue.qsize(),
                "last_update": datetime.now().isoformat(),
                "active_injections": [asdict(inj) for inj in self.active_injections.values()]
            }

            with open(self.telemetry_path, 'w') as f:
                json.dump(telemetry, f, indent=2)

        except Exception as e:
            print(f"[TraceLogger] Failed to update telemetry: {e}")

    def _perform_health_check(self) -> float:
        """Perform system health check"""
        # Placeholder health check implementation
        return 0.95

    def create_injection(self, injection_type: InjectionType, payload: Dict[str, Any],
                        target_module: str, priority: InjectionPriority = InjectionPriority.MEDIUM,
                        expires_in_seconds: Optional[int] = None) -> LiveInjection:
        """Create a new injection object"""
        injection_id = f"{injection_type.value}_{int(time.time() * 1000)}"

        expires_at = None
        if expires_in_seconds:
            expires_at = (datetime.now() + timedelta(seconds=expires_in_seconds)).isoformat()

        return LiveInjection(
            injection_id=injection_id,
            injection_type=injection_type,
            priority=priority,
            payload=payload,
            target_module=target_module,
            timestamp=datetime.now().isoformat(),
            expires_at=expires_at
        )