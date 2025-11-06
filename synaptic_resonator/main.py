from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import asyncio
import numpy as np
import json

app = FastAPI(title="Synaptic Resonator")

class NeuralSignal(BaseModel):
    signal_type: str
    amplitude: float
    frequency: float
    source_module: str
    target_module: str
    payload: Dict[str, Any]

class ResonancePattern(BaseModel):
    pattern_id: str
    signals: List[Dict[str, Any]]
    resonance_score: float

# Neural network for pattern recognition
class ResonanceNetwork:
    def __init__(self):
        self.patterns = {}
        self.signal_history = []

    def process_signal(self, signal: NeuralSignal) -> Dict[str, Any]:
        """Process incoming neural signal and find resonance patterns"""
        signal_data = {
            "type": signal.signal_type,
            "amplitude": signal.amplitude,
            "frequency": signal.frequency,
            "source": signal.source_module,
            "target": signal.target_module,
            "payload": signal.payload
        }

        self.signal_history.append(signal_data)

        # Keep only recent signals
        if len(self.signal_history) > 100:
            self.signal_history = self.signal_history[-100:]

        # Find resonance patterns
        resonance_patterns = self.find_resonance_patterns(signal_data)

        # Calculate amplification factor
        amplification = self.calculate_amplification(signal_data, resonance_patterns)

        return {
            "processed_signal": signal_data,
            "resonance_patterns": resonance_patterns,
            "amplification_factor": amplification,
            "transmission_ready": True
        }

    def find_resonance_patterns(self, signal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find patterns that resonate with the current signal"""
        patterns = []

        for pattern_id, pattern_data in self.patterns.items():
            similarity = self.calculate_similarity(signal, pattern_data)
            if similarity > 0.7:  # Resonance threshold
                patterns.append({
                    "pattern_id": pattern_id,
                    "similarity": similarity,
                    "pattern_data": pattern_data
                })

        return patterns

    def calculate_similarity(self, signal1: Dict[str, Any], signal2: Dict[str, Any]) -> float:
        """Calculate similarity between two signals"""
        # Simple similarity based on signal type and amplitude
        type_match = 1.0 if signal1.get("type") == signal2.get("type") else 0.0
        amp_diff = abs(signal1.get("amplitude", 0) - signal2.get("amplitude", 0))
        amp_similarity = max(0, 1.0 - amp_diff / 10.0)  # Normalize

        return (type_match + amp_similarity) / 2.0

    def calculate_amplification(self, signal: Dict[str, Any], patterns: List[Dict[str, Any]]) -> float:
        """Calculate signal amplification based on resonance"""
        base_amplitude = signal.get("amplitude", 1.0)
        pattern_boost = len(patterns) * 0.1  # Each resonant pattern adds 10%

        # Frequency-based amplification
        frequency = signal.get("frequency", 1.0)
        freq_boost = min(2.0, frequency / 10.0)  # Higher frequency = more amplification

        return base_amplitude * (1.0 + pattern_boost) * freq_boost

    def learn_pattern(self, pattern_id: str, signals: List[Dict[str, Any]]):
        """Learn a new resonance pattern"""
        self.patterns[pattern_id] = {
            "signals": signals,
            "learned_at": asyncio.get_event_loop().time(),
            "usage_count": 0
        }

resonance_network = ResonanceNetwork()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Synaptic Resonator"}

@app.post("/process_signal")
async def process_neural_signal(signal: NeuralSignal):
    """Process an incoming neural signal"""
    try:
        result = resonance_network.process_signal(signal)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create_resonance")
async def create_resonance_pattern(pattern: ResonancePattern):
    """Create a new resonance pattern for learning"""
    try:
        resonance_network.learn_pattern(pattern.pattern_id, pattern.signals)
        return {"status": "pattern_learned", "pattern_id": pattern.pattern_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/resonance_patterns")
async def get_resonance_patterns():
    """Get all learned resonance patterns"""
    return {"patterns": resonance_network.patterns}

@app.get("/signal_history")
async def get_signal_history(limit: int = 10):
    """Get recent signal processing history"""
    recent_signals = resonance_network.signal_history[-limit:]
    return {"history": recent_signals}

@app.post("/amplify_signal")
async def amplify_signal(signal: NeuralSignal):
    """Amplify a signal based on resonance patterns"""
    try:
        processed = resonance_network.process_signal(signal)
        amplified_signal = signal.copy()
        amplified_signal.amplitude = processed["amplification_factor"]

        return {
            "original_signal": signal.dict(),
            "amplified_signal": amplified_signal.dict(),
            "amplification_factor": processed["amplification_factor"],
            "resonance_patterns": processed["resonance_patterns"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)