# EchoStack

EchoStack is a modular, vault-aware reasoning system designed for traceable cognition, ethical logic filtering, and reflexive telemetry. Every module is protocol-compliant with ICS-V2-2025-10-18 and built for legacy stewardship.

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd echostack_module
   ```

2. **Start with Docker Compose**
   ```bash
   # Development environment
   make dev

   # Production environment
   make prod

   # With monitoring stack
   make prod-monitoring
   ```

3. **Access the application**
   - EchoStack API: http://localhost:8003
   - Grafana: http://localhost:3000 (admin/admin2025)
   - Prometheus: http://localhost:9090

### Manual Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   python main.py
   ```

## Architecture

### Core Components

- **EchoStack Core**: Central reasoning engine with vault integration
- **Logic Filters**: Ockham-based principle detection and paradox handling
- **Epistemic Overlays**: A priori/a posteriori classification with reflex tier tracking
- **Trace Routing**: Reasoning type dispatch and seed vault alignment
- **Telemetry System**: Full-spectrum system observability with live injection
- **Vault Sync**: Protocol compliance checking and harmonizer health scoring
- **Alert Manager**: Threshold breach detection with intelligent suppression

### Infrastructure

- **FastAPI**: High-performance async web framework
- **PostgreSQL**: Primary data storage for telemetry and vault compliance
- **Redis**: Caching and session management
- **Prometheus**: Metrics collection and monitoring
- **Grafana**: Visualization and dashboards

## Development

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Make (optional, for using Makefile commands)

### Development Setup

```bash
# Clone repository
git clone <your-repo-url>
cd echostack_module

# Copy environment configuration
cp .env.example .env

# Start development environment
make dev

# Run tests
make test

# Run linting
make lint

# Format code
make format
```

### Available Make Commands

```bash
make help           # Show all available commands
make dev            # Start development environment
make prod           # Start production environment
make test           # Run test suite
make lint           # Run code linting
make format         # Format code with black and isort
make logs           # Show container logs
make shell          # Open shell in container
make clean          # Clean up containers and volumes
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Application
ECHOSTACK_ENV=development
ECHOSTACK_LOG_LEVEL=INFO

# Database
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=echostack_db

# Monitoring
GRAFANA_ADMIN_PASSWORD=your_admin_password

# Security
SECRET_KEY=your-secret-key-here
```

### Docker Services

- **echostack**: Main application (FastAPI)
- **echostack_db**: PostgreSQL database
- **echostack_redis**: Redis cache
- **echostack_monitoring**: Prometheus metrics
- **echostack_grafana**: Grafana dashboards

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc
- **Health Check**: http://localhost:8003/health

## Monitoring & Observability

### Metrics

EchoStack exposes Prometheus metrics at `/metrics` including:
- System health scores
- CPU/memory usage
- Error rates and response times
- Vault compliance status
- Active reasoning cycles

### Dashboards

Pre-configured Grafana dashboards include:
- System Health Overview
- Performance Metrics
- Vault Compliance Status
- Alert History

### Alerting

Built-in alert rules for:
- High CPU/memory usage
- System health degradation
- Vault integrity breaches
- Connection failures
- Error rate spikes

## Deployment

### Production Deployment

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Deploy with monitoring**
   ```bash
   make prod-monitoring
   ```

3. **Scale services** (optional)
   ```bash
   docker-compose up -d --scale echostack=3
   ```

### Kubernetes Deployment

For Kubernetes deployment, use the provided manifests:
```bash
kubectl apply -f k8s/
```

## Protocol Compliance

### ICS-V2-2025-10-18

EchoStack implements full compliance with the Interoperable Cognitive Systems protocol:

- **Vault Structure**: Versioned, immutable seed vaults with hash validation
- **Telemetry Manifest**: JSON-based metrics with hourly snapshots
- **Protocol Handshake**: Automated compliance verification
- **Legacy Stewardship**: Built for long-term system preservation

### Seed Vaults

Located in `seed_logic_vault/`:
- `seed_ockhams_filter.json`: Logic filtering principles
- `seed_hume.json`: Epistemic reasoning frameworks
- `seed_spinoza.json`: Ethical logic foundations
- Additional philosophical frameworks for comprehensive reasoning

## Testing

### Run Test Suite

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test file
docker-compose exec echostack python -m pytest tests/test_vault_sync.py -v
```

### Integration Testing

```bash
# Test full system integration
docker-compose exec echostack python -c "
from echostack_module.vault_sync import VaultSynchronizer
from echostack_module.alert_manager import AlertManager
from echostack_module.dashboard import Dashboard

# Test vault synchronization
sync = VaultSynchronizer()
result = sync.perform_sync()
print(f'Vault sync result: {result}')

# Test alert manager
alerts = AlertManager()
status = alerts.get_alert_status()
print(f'Alert status: {status}')

# Test dashboard
dash = Dashboard()
metrics = dash.get_metric_snapshot()
print(f'Dashboard metrics: {list(metrics.keys())}')
"
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and run tests: `make test`
4. Format code: `make format`
5. Commit changes: `git commit -am 'Add your feature'`
6. Push to branch: `git push origin feature/your-feature`
7. Submit a pull request

## Troubleshooting

### Common Issues

**Port conflicts**: Change ports in `docker-compose.yml`
**Database connection**: Check PostgreSQL logs with `make logs`
**Memory issues**: Increase Docker memory limit
**Import errors**: Ensure all dependencies are installed

### Logs

```bash
# View all logs
make logs

# View specific service logs
make logs-echostack

# Follow logs in real-time
docker-compose logs -f echostack
```

### Health Checks

```bash
# Check all services
make health

# Manual health check
curl http://localhost:8003/health
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Status

- **Version**: `1.0.0`
- **Build**: `EchoStack-2025-10-25`
- **Environment**: `Prometheus Prime`
- **Protocol**: `ICS-V2-2025-10-18`
- **Last Harmonized**: `2025-10-25`
