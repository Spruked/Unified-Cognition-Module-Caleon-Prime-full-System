# ISS Module Deployment Guide for Prometheus Prime Integration

## Overview

The ISS Module has been designed as a plug-and-play microservice that integrates seamlessly with the Prometheus Prime cognitive architecture. This guide covers deployment, configuration, and integration steps.

## Quick Start

### 1. Environment Setup

```bash
# Clone or copy the ISS Module
git clone <repository-url> iss-module
cd iss-module

# Copy environment configuration
cp .env.example .env

# Edit configuration (see Configuration section below)
nano .env
```

### 2. Deploy with Docker Compose

```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy all services
./deploy.sh deploy

# Check status
./deploy.sh status
```

### 3. Verify Integration

```bash
# Health check
curl http://localhost:8003/health

# API documentation
open http://localhost:8003/docs

# Test reasoning endpoint (called by API Gateway)
curl -X POST http://localhost:8003/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"input_data": {"query": "test"}, "timeout_ms": 1000}'
```

## Architecture Integration

### Prometheus Prime API Gateway Integration

The ISS Controller service exposes endpoints that are compatible with the Prometheus Prime API Gateway:

```python
# In your API Gateway main.py, add ISS Controller integration:

@app.post("/api/v1/reason", response_model=ReasoningResponse)
async def process_reasoning(request: ReasoningRequest):
    """Route reasoning to ISS Controller"""
    iss_service = await service_registry.get_service("iss-controller")
    
    async with http_client as client:
        response = await client.post(
            f"{iss_service.url}/api/v1/process",
            json=request.dict()
        )
        return response.json()
```

### Service Discovery Registration

The ISS Controller automatically registers with your service discovery system:

```yaml
# Service Registry Entry
service:
  name: iss-controller
  version: 1.0.0
  url: http://iss-controller:8003
  health_check: /health
  capabilities:
    - reasoning_processing
    - vault_queries
    - log_management
    - time_anchoring
```

## Configuration

### Core Settings (.env)

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

# Security (change in production!)
SECRET_KEY=your-secure-secret-key
REQUIRE_AUTH=false
```

### Prometheus Prime Specific

```bash
# External Service URLs
COCHLEAR_PROCESSOR_URL=http://cochlear-processor:8001
PHONATORY_OUTPUT_URL=http://phonatory-output:8002
VAULT_MANAGER_URL=http://vault-manager:8004

# Reasoning Configuration
REASONING_TIMEOUT_MS=5000
VAULT_QUERY_LIMIT=1000

# Logging (JSON format for Prometheus Prime)
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## API Integration Examples

### 1. Reasoning Pipeline Integration

```python
# ISS Controller provides reasoning capabilities
from iss_module.prometheus_integration import ReasoningRequest, ReasoningResponse

# In your Prometheus Prime reasoning pipeline:
async def process_with_iss(input_data: Dict[str, Any]):
    request = ReasoningRequest(
        input_data=input_data,
        cycle_type="auto",
        timeout_ms=5000
    )
    
    # This call provides time anchoring and logging
    response = await iss_client.post("/api/v1/process", json=request.dict())
    return response.json()
```

### 2. Vault Integration

```python
# Query ISS vault from Prometheus Prime services
async def query_iss_vault(query_params: Dict[str, Any]):
    vault_request = VaultQueryRequest(
        query=query_params,
        limit=100
    )
    
    response = await iss_client.post("/api/v1/vault/query", json=vault_request.dict())
    return response.json()["results"]
```

### 3. Captain's Log Integration

```python
# Add entries to captain's log from other services
async def log_to_iss(content: str, category: str = "reasoning"):
    log_request = LogEntryRequest(
        content=content,
        category=category,
        tags=["prometheus-prime", "automated"]
    )
    
    response = await iss_client.post("/api/v1/log", json=log_request.dict())
    return response.json()
```

## Service Endpoints

### Health and Status
- `GET /health` - Service health check
- `GET /api/v1/status` - Detailed service status

### Reasoning Pipeline
- `POST /api/v1/process` - Process reasoning request (called by API Gateway)

### Vault Management
- `POST /api/v1/vault/query` - Query vault entries

### Captain's Log
- `POST /api/v1/log` - Add log entry

### Documentation
- `GET /docs` - OpenAPI documentation
- `GET /redoc` - ReDoc documentation

## Deployment Options

### 1. Docker Compose (Recommended for Development)

```bash
# Full stack with monitoring
docker-compose up -d

# ISS Controller only
docker-compose up -d iss-controller redis
```

### 2. Kubernetes (Production)

```yaml
# k8s/iss-controller-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: iss-controller
spec:
  replicas: 3
  selector:
    matchLabels:
      app: iss-controller
  template:
    metadata:
      labels:
        app: iss-controller
    spec:
      containers:
      - name: iss-controller
        image: iss-module:1.0.0
        ports:
        - containerPort: 8003
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: REDIS_URL
          value: "redis://redis-service:6379"
```

### 3. Standalone Docker

```bash
# Build and run standalone
docker build -t iss-module .
docker run -d -p 8003:8003 \
  -e ENVIRONMENT=production \
  -e ISS_HOST=0.0.0.0 \
  -e ISS_PORT=8003 \
  iss-module
```

## Monitoring and Logging

### Structured Logging

The ISS Module provides JSON-formatted logs compatible with Prometheus Prime:

```json
{
  "timestamp": "2025-10-02T22:15:30.123Z",
  "level": "info",
  "service": "iss-controller",
  "correlation_id": "abc-123-def",
  "message": "Reasoning request completed",
  "cycle_id": "iss_1696284930123",
  "processing_time_ms": 450.2
}
```

### Health Checks

```bash
# Service health
curl http://localhost:8003/health

# Detailed status
curl http://localhost:8003/api/v1/status
```

### Metrics (if Prometheus is enabled)

- Request/response times
- Error rates
- Reasoning cycle metrics
- Vault query performance
- Log entry statistics

## Troubleshooting

### Common Issues

1. **Service not starting**
   ```bash
   # Check logs
   docker-compose logs iss-controller
   
   # Check configuration
   ./deploy.sh test
   ```

2. **Integration issues**
   ```bash
   # Verify network connectivity
   docker-compose exec api-gateway curl http://iss-controller:8003/health
   
   # Check service discovery
   curl http://localhost:8500/v1/catalog/services
   ```

3. **Performance issues**
   ```bash
   # Monitor resource usage
   docker stats
   
   # Check processing times in logs
   docker-compose logs iss-controller | grep processing_time_ms
   ```

### Debugging

```bash
# Access container shell
./deploy.sh shell

# View real-time logs
./deploy.sh logs iss-controller

# Test individual endpoints
curl -X POST http://localhost:8003/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"input_data": {"test": true}, "timeout_ms": 1000}'
```

## Security Considerations

### Production Deployment

1. **Change default secrets**
   ```bash
   # Generate secure secret key
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Enable authentication**
   ```bash
   REQUIRE_AUTH=true
   ```

3. **Configure CORS properly**
   ```bash
   CORS_ORIGINS=["https://your-domain.com"]
   ```

4. **Use HTTPS in production**
   - Configure reverse proxy (nginx, traefik)
   - Set up SSL certificates

### Network Security

```bash
# Use internal networks for service communication
docker network create --internal prometheus-prime-internal
```

## Integration Checklist

- [ ] ISS Controller deployed and healthy
- [ ] Service registered with discovery system
- [ ] API Gateway configured to route to ISS Controller
- [ ] Structured logging configured
- [ ] Health checks responding
- [ ] Reasoning endpoint accessible from API Gateway
- [ ] Vault queries working
- [ ] Captain's log entries being created
- [ ] Time anchoring providing stardates
- [ ] Monitoring/metrics configured (optional)

## Support and Maintenance

### Updates

```bash
# Update to new version
git pull
docker-compose build iss-controller
docker-compose up -d

# Or use deployment script
./deploy.sh build
./deploy.sh deploy
```

### Backup

```bash
# Backup data
docker-compose exec iss-controller tar -czf /tmp/backup.tar.gz /app/data
docker cp iss-controller:/tmp/backup.tar.gz ./backup-$(date +%Y%m%d).tar.gz
```

### Logs Rotation

```bash
# Configure log rotation in docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Conclusion

The ISS Module is now ready for plug-and-play integration with Prometheus Prime. The service provides:

- ✅ Compatible API contracts
- ✅ Service discovery registration  
- ✅ Structured logging
- ✅ Health checks and monitoring
- ✅ Time anchoring capabilities
- ✅ Vault management
- ✅ Captain's log system
- ✅ Docker deployment ready

For additional support or custom integrations, refer to the API documentation at `/docs` when the service is running.