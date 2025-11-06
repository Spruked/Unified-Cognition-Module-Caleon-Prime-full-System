# Resonator

A modular, container-ready reasoning engine for the Caleon system. Runs 2,320 synaptic nodes, aggregates logic verdicts, and exposes a REST API via FastAPI.

## Features
- Deductive, inductive, and intuitive logic layers
- 2,320-node synaptic array with verdict aggregation
- 21-node Reasonator pyramid for final decision distillation
- Telemetry and audit logging to vaults
- REST API (FastAPI) for microservice deployment
- Docker-ready for easy containerization

## Usage

### Docker
Build and run the container:

```sh
cd synaptic_reasonator
# Build the Docker image
 docker build -t resonator .
# Run the container
 docker run -p 8008:8000 resonator
```

### API
POST to `/reasonate` with JSON:
```json
{
  "input": {"your": "data"},
  "telemetry": true
}
```

### Local (CLI)
You can also run `entrypoint.py` for a quick test.

## License
MIT License (see LICENSE file)

## Project Structure
```
synaptic_reasonator/
├── api.py
├── entrypoint.py
├── requirements.txt
├── Dockerfile
├── README.md
├── .gitignore
├── resonator_core/
│   ├── deductive_reasoner.py
│   ├── inductive_reasoner.py
│   ├── intuitive_reasoner.py
│   ├── resonator_vault.py
│   ├── synaptic_nodes.py
│   ├── resonator.py
│   ├── reasonator.py
│   └── utils.py
└── tests/
    └── test_reasonator.py
```
