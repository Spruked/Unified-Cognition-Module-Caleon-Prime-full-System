# resonator.py
"""
Reasonator Brain: Orchestrates 2,320 SynapticNodes, routes data, collects verdicts, feeds into 21-node inverted pyramid, emits final verdict.
"""
from typing import List, Dict, Any
from resonator_core.synaptic_nodes import SynapticArray
from resonator_core.resonator_vault import log_to_vault
import time
import json

class ReasonatorPyramid:
    def __init__(self, num_nodes: int = 21):
        self.nodes = [f"Pyramid_{i+1:02d}" for i in range(num_nodes)]

    def distill(self, verdicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Simple aggregation: majority logic type, average confidence, most common verdict
        logic_types = [v["logic_type"] for v in verdicts]
        verdict_msgs = [v["verdict"] for v in verdicts]
        confidences = [v["confidence"] for v in verdicts]
        glyphs = [v.get("glyph", "") for v in verdicts]
        # Majority logic type
        majority_logic = max(set(logic_types), key=logic_types.count)
        # Most common verdict
        common_verdict = max(set(verdict_msgs), key=verdict_msgs.count)
        # Average confidence
        avg_conf = round(sum(confidences) / len(confidences), 3) if confidences else 0.0
        # Use first glyph as representative (could be improved)
        glyph = glyphs[0] if glyphs else ""
        return {
            "node_id": "PYRAMID_FINAL",
            "logic_type": majority_logic,
            "verdict": common_verdict,
            "glyph": glyph,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "confidence": avg_conf
        }

class Resonator:
    def __init__(self):
        self.synaptic_array = SynapticArray()
        self.pyramid = ReasonatorPyramid()

    def process(self, input_data: Dict[str, Any], telemetry: bool = True) -> Dict[str, Any]:
        # Run all 2,320 nodes
        verdicts = self.synaptic_array.run_all(input_data)
        # Optionally log all verdicts
        if telemetry:
            for v in verdicts:
                log_to_vault(v, vault_name="SynapticVault")
        # Feed into 21-node pyramid
        final_verdict = self.pyramid.distill(verdicts)
        if telemetry:
            log_to_vault(final_verdict, vault_name="PyramidVault")
        return final_verdict

if __name__ == "__main__":
    sr = Resonator()
    sample_input = {"input": "test data"}
    result = sr.process(sample_input, telemetry=True)
    print(json.dumps(result, indent=2))
