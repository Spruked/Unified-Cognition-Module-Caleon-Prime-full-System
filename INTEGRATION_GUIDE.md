# Unified Cognition Module - Integration Guide

## Plug-and-Play Integration

The Unified Cognition Module is designed as a **sovereign AI cognition platform** that can be integrated into existing systems with minimal configuration.

## Integration Options

### 1. Docker Container (Recommended)
```bash
# Pull and run
docker run -p 8080:8080 spruked/unified-cognition:latest

# Or use docker-compose
curl https://raw.githubusercontent.com/Spruked/Unified-Cognition-Module-Caleon-Prime-full-System/main/docker-compose.yml -o docker-compose.yml
docker-compose up -d
```

### 2. REST API Integration
```python
import requests

# Health check
response = requests.get("http://localhost:8080/health")

# Store memory
requests.post("http://localhost:8080/vault/memory/store", json={
    "memory_id": "user_input_001",
    "payload": {"text": "Hello"},
    "resonance": {"tone": "joy", "symbol": "greeting"}
})

# Get consent decision
consent = requests.get("http://localhost:8080/consent/pending")
```

### 3. Python Library Import
```python
from unified_cognition import UnifiedCognitionLoop

# Initialize
cognition = UnifiedCognitionLoop()

# Process input
result = await cognition.process_cognition("What is consciousness?")
```

## Required Dependencies

### System Requirements
- Docker 20.10+
- Python 3.11+ (if running natively)
- 4GB RAM minimum
- Microphone access (for voice consent)

### External Services
- PostgreSQL (for structured data)
- Redis (for caching)
- MongoDB (for reflection storage)
- Speech Recognition API (Google/Alternative)

## Configuration

### Environment Variables
```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_DB=cortex_db
REDIS_URL=redis://localhost:6379
MONGO_URL=mongodb://localhost:27018

# APIs
GOOGLE_SPEECH_API_KEY=your_key
OLLAMA_ENDPOINT=http://localhost:11434

# Consent
DEFAULT_CONSENT_MODE=voice
VOICE_TIMEOUT=30
```

### Volume Mounts
```yaml
volumes:
  - ./vault:/app/vault
  - ./logs:/app/logs
  - ./telemetry:/app/telemetry
```

## Integration Patterns

### 1. Chatbot Integration
```python
from unified_cognition import CognitionAPI

class ChatBot:
    def __init__(self):
        self.cognition = CognitionAPI("http://localhost:8080")

    async def respond(self, user_input):
        # Process through cognition pipeline
        result = await self.cognition.process(user_input)

        # Only respond if consent granted
        if result.consent_granted:
            return result.final_output
        else:
            return "Request denied by user consent system"
```

### 2. Voice Assistant Integration
```python
from unified_cognition import VoiceConsentListener

class VoiceAssistant:
    def __init__(self):
        self.consent_listener = VoiceConsentListener()

    async def process_command(self, audio_input):
        # Convert speech to text
        text = self.speech_to_text(audio_input)

        # Get cognition result
        result = await self.cognition.process(text)

        # Speak only if approved
        if result.consent_granted:
            self.text_to_speech(result.final_output)
```

### 3. API Gateway Integration
```nginx
# nginx.conf
location /api/cognition {
    proxy_pass http://localhost:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## Security Considerations

### Authentication
- API key authentication for external access
- JWT tokens for session management
- Rate limiting per client

### Data Privacy
- All decisions logged with user consent
- Voice data processed in-memory only
- Configurable data retention policies

### Network Security
- HTTPS required for production
- Firewall rules for service ports
- Container security scanning

## Monitoring & Observability

### Health Checks
```bash
curl http://localhost:8080/health
# Returns: {"status": "healthy", "services": {...}}
```

### Metrics
```bash
curl http://localhost:8080/metrics
# Returns: {"llm_requests": 150, "consent_approvals": 142, ...}
```

### Logs
```bash
docker-compose logs -f cerebral_cortex
```

## Scaling

### Horizontal Scaling
```yaml
services:
  cerebral_cortex:
    scale: 3
    depends_on:
      - load_balancer
```

### Database Scaling
- PostgreSQL read replicas
- MongoDB sharding
- Redis cluster

## Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   docker-compose logs
   # Check for missing environment variables
   ```

2. **Voice consent not working**
   ```bash
   # Check microphone permissions
   docker-compose exec cerebral_cortex python -c "import pyaudio"
   ```

3. **Database connection failed**
   ```bash
   docker-compose ps
   # Ensure postgres/redis/mongo are running
   ```

## Support

- **Documentation**: https://github.com/Spruked/Unified-Cognition-Module-Caleon-Prime-full-System
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## License

This module is released under the MIT License, allowing integration into both open-source and commercial systems.