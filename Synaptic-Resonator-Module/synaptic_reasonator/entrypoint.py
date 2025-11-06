# entrypoint.py for resonator
import json
from resonator_core.resonator import Resonator

if __name__ == "__main__":
    print("Starting Resonator...")
    sr = Resonator()
    # Example: read input from a file or stdin (for now, just a static example)
    sample_input = {"input": "dockerized test data"}
    result = sr.process(sample_input, telemetry=True)
    print(json.dumps(result, indent=2))
