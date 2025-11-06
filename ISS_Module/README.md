# ISS Module - Integrated Systems Solution

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

A comprehensive data management and time anchoring system designed for microservices architectures, with special compatibility for **Prometheus Prime** cognitive systems.

## ✨ Overview

The ISS Module is a sophisticated data management and time anchoring system that combines Star Trek-inspired logging with modern microservice architecture. It provides time anchoring, structured logging, data export, and seamless integration with cognitive computing systems like Prometheus Prime.

## ✨ Key Features

- �️ **Time Anchoring** - Stardate calculations and Julian date timestamps
- 📝 **Captain's Log System** - Structured logging with metadata and tagging
- 🗄️ **Data Export** - CSV, JSON, and Markdown export capabilities
- 🔍 **VisiData Integration** - Interactive data analysis and visualization
- 🌐 **FastAPI Web Interface** - RESTful API with automatic documentation
- 🐳 **Docker Ready** - Complete containerization for easy deployment
- 🔗 **Microservice Compatible** - Plug-and-play integration with service meshes
- 📊 **Structured Logging** - JSON formatted logs with correlation IDs
- 🛡️ **Production Ready** - Circuit breakers, health checks, and monitoring
- 🧠 **Prometheus Prime Integration** - Native cognitive architecture compatibility

## � Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Spruked/ISS_Module.git
cd ISS_Module

# Install with pip
pip install -e .

# Or install from PyPI (when published)
pip install iss-module
```

### Basic Usage

```python
from iss_module import ISS, CaptainLog, Exporters, get_stardate

# Initialize ISS system
iss = ISS()

# Create captain's log entry
log = CaptainLog()
entry_id = log.add_entry_sync("Mission parameters established", category="system")

# Get current stardate
stardate = get_stardate()
print(f"Stardate {stardate}")

# Export data
entries = log.get_entries_sync()
Exporters.to_csv_sync(entries, "mission_log.csv")
```

### Web Interface

```bash
# Start the web server
python -m iss_module.service

# Or with custom configuration
ISS_HOST=0.0.0.0 ISS_PORT=8003 python -m iss_module.service
```

Visit `http://localhost:8003/docs` for interactive API documentation.

## 🐳 Docker Deployment

### Quick Deploy with Docker Compose

```bash
# Deploy full stack (ISS + Redis + Consul + Monitoring)
./deploy.sh deploy

# Check status
./deploy.sh status

# View logs
./deploy.sh logs
```

### Standalone Docker

```bash
# Build and run
docker build -t iss-module .
docker run -p 8003:8003 iss-module
```

## 🔗 Prometheus Prime Integration

The ISS Module is designed to integrate seamlessly with Prometheus Prime cognitive architectures:

```python
from iss_module.prometheus_integration import create_prometheus_iss_app

# Create Prometheus Prime compatible service
app = create_prometheus_iss_app("iss-controller")

# Reasoning pipeline integration
@app.post("/api/v1/process")
async def process_reasoning(request: ReasoningRequest):
    # Time anchoring + reasoning + logging
    return await prometheus_iss.process_reasoning(request)
```

### API Gateway Integration

```python
# In your Prometheus Prime API Gateway:
@app.post("/api/v1/reason")
async def reasoning_endpoint(request: ReasoningRequest):
    iss_service = await service_registry.get_service("iss-controller")
    response = await client.post(f"{iss_service.url}/api/v1/process", json=request.dict())
    return response.json()
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/health` | GET | Service health check |
| `/api/v1/process` | POST | Reasoning pipeline integration |
| `/api/v1/vault/query` | POST | Query captain's log entries |
| `/api/v1/log` | POST | Add captain's log entry |
| `/api/v1/status` | GET | Detailed service status |
| `/docs` | GET | Interactive API documentation |

## ⚙️ Configuration

### Environment Variables

```bash
# Service Configuration
ISS_SERVICE_NAME=iss-controller
ENVIRONMENT=production
ISS_HOST=0.0.0.0
ISS_PORT=8003

# Prometheus Prime Integration
PROMETHEUS_INTEGRATION_ENABLED=true
API_GATEWAY_URL=http://api-gateway:8000

# Service Discovery
SERVICE_REGISTRY_URL=http://consul:8500
CONSUL_HOST=consul
CONSUL_PORT=8500

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
SECRET_KEY=your-secret-key
REQUIRE_AUTH=false
```

See `.env.example` for complete configuration options.

## 🧪 Testing

```bash
# Run integration tests
python test_integration.py

# Run unit tests (if pytest is installed)
pytest

# Test specific functionality
python -c "from iss_module import get_stardate; print('Stardate:', get_stardate())"
```

## 📊 Use Cases

### For Blockchain/NFT Projects (CertSig)
```python
from iss_module import get_stardate, current_timecodes

# Time anchoring for NFT metadata
timecodes = current_timecodes()
metadata = {
    "stardate": get_stardate(),
    "timestamp": timecodes["iso_timestamp"],
    "anchor_hash": timecodes["anchor_hash"]
}
```

### For AI Systems (Caleon)
```python
from iss_module import CaptainLog

# Log AI decision processes
log = CaptainLog()
log.add_entry_sync(
    "Symbolic cognition pattern detected",
    category="ai_reasoning",
    tags=["caleon", "pattern_recognition"],
    metadata={"confidence": 0.92, "pattern_type": "symbolic"}
)
```

### For Microservice Architectures
```python
from iss_module.prometheus_integration import PrometheusISS

# Service integration with health checks and structured logging
prometheus_iss = PrometheusISS("my-service")
await prometheus_iss.initialize()

# Process with time anchoring and logging
response = await prometheus_iss.process_reasoning(request)
```

## 📁 Project Structure

```
iss-module/
├── iss_module/                 # Main package
│   ├── core/                   # Core utilities
│   │   ├── iss.py             # Main ISS class
│   │   ├── utils.py           # Time anchoring utilities
│   │   └── validators.py      # Data validation
│   ├── captain_mode/          # Logging and export
│   │   ├── captain_log.py     # Captain's log system
│   │   ├── exporters.py       # Data export utilities
│   │   └── vd_wrapper.py      # VisiData integration
│   ├── api/                   # Web interface
│   ├── prometheus_integration.py  # Prometheus Prime compatibility
│   ├── config.py              # Configuration management
│   ├── logging_config.py      # Structured logging
│   └── service.py             # Microservice entry point
├── docker-compose.yml         # Docker deployment
├── Dockerfile                 # Container definition
├── deploy.sh                  # Deployment script
├── test_integration.py        # Integration tests
├── requirements.txt           # Dependencies
└── setup.py                   # Package setup
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black iss_module/
isort iss_module/
```

## VisiData Integration

For advanced data analysis, install VisiData:

```bash
pip install visidata
```

Then use the VisiData wrapper:

```python
from iss_module.captain_mode.vd_wrapper import VisiDataWrapper

vd_wrapper = VisiDataWrapper()
await vd_wrapper.view_log_entries(entries, format_type='csv')
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
