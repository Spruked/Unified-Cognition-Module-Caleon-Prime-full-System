# core_bridge.py
"""
CoreBridge – resilient transmission layer for Cochlear Processor v2
Manages adaptive fidelity, buffering, and back-pressure control.
"""

import queue, time
from threading import Lock


class CoreBridge:
    def __init__(self, buffer_size: int = 128):
        self.queue = queue.Queue(maxsize=buffer_size)
        self.lock = Lock()
        self.adaptive_fidelity: float = 1.0
        self.last_full_signal: float = 0.0

    # --------------------------------------------------------------
    def send_input_vector(self, trace_id: str, matrix: dict):
        """Queue a sensory matrix; if full, trigger adaptive mode."""
        try:
            self.queue.put_nowait((trace_id, matrix))
        except queue.Full:
            self._handle_overflow()

    # --------------------------------------------------------------
    def _handle_overflow(self):
        """Reduce fidelity when buffer saturates."""
        with self.lock:
            self.adaptive_fidelity = 0.5
            self.last_full_signal = time.time()

    # --------------------------------------------------------------
    def drain(self, cortex_callback):
        """
        Flush queued matrices to cortex endpoint.
        Automatically restores fidelity when queue clears.
        """
        while not self.queue.empty():
            trace_id, matrix = self.queue.get()
            if self.adaptive_fidelity < 1.0:
                matrix = downsample_matrix(matrix, self.adaptive_fidelity)
                matrix["fidelity_factor"] = self.adaptive_fidelity
            cortex_callback(trace_id, matrix)
        self.adaptive_fidelity = 1.0  # reset after clear


# --------------------------------------------------------------
def downsample_matrix(matrix: dict, factor: float) -> dict:
    """Return a reduced-size matrix proportional to factor."""
    if not matrix or factor >= 1.0:
        return matrix
    keys = list(matrix.keys())
    keep = max(1, int(len(keys) * factor))
    return {k: matrix[k] for k in keys[:keep]}
