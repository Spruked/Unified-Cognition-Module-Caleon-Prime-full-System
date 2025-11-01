# Unified Cognition Module 🧠

A sovereignty-focused AI platform enabling conscious, ethical, and transparent cognitive processing. Built with Python 3.11+, FastAPI, and inspired by human cognitive architecture.

## ✨ Features

- **Sovereign AI**: Human agency over all cognitive outputs with consent-driven articulation
- **Ethical Oversight**: GyroHarmonizer computes ethical drift with ConsensusMatrix validation
- **Multi-Modal Processing**: Voice I/O, Web UI, and REST API interfaces
- **Brain-Inspired Architecture**: Modular cognitive system with Synaptic Resonator, EchoStack, EchoRipple
- **Immutable Results**: Thread-safe, predictable cognitive outputs
- **Comprehensive Logging**: Complete audit trail for all decisions and processes
- **Docker Deployment**: Containerized for easy deployment and scaling

## 🏗️ Architecture

The system embodies the principle: **"Caleon is the sovereign curator of her own mind, not a guardrail."**

### Core Principles
- **Sovereignty**: Consent-driven articulation with live human approval
- **Ethical Oversight**: Advisory metrics inform but never constrain decisions
- **Modularity**: Hot-swappable components with protocol-based extensibility
- **Observability**: Complete audit trail and comprehensive logging

### Cognitive Processing Pipeline
```
User Input → Synaptic Resonator → Anterior Helix → EchoStack → EchoRipple → Posterior Helix → GyroHarmonizer → Consent Gate → Articulation
```

### Key Components
- **LLM Bridge**: VALLM-powered articulation engine with ethical oversight
- **Symbolic Memory Vault**: Subjective memory with resonance tagging
- **Caleon Consent Manager**: Sovereign consent gate (voice/manual/auto modes)
- **EchoStack**: Second-order reasoning with non-monotonic logic
- **EchoRipple**: Recursive verification with randomized logic cycles
- **Voice Consent System**: Speech recognition for live consent capture

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- 4GB+ RAM available
- Microphone (for voice consent)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Spruked/Unified-Cognition-Module-Caleon-Prime-full-System.git
   cd Unified-Cognition-Module-Caleon-Prime-full-System
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the system**
   ```bash
   # For development
   python main.py

   # Or with Docker
   docker-compose up --build -d
   ```

4. **Access the API**
   - REST API: http://localhost:8080
   - Health check: http://localhost:8080/health
   - Vault API: http://localhost:8080/vault/

## 📚 Documentation

- [System Architecture](SYSTEM_ARCHITECTURE.md) - Complete technical documentation
- [API Guide](CONSENT_API_GUIDE.md) - REST API reference
- [Voice Consent Guide](CONSENT_AUDIT_VOICE_GUIDE.md) - Voice interaction documentation
- [Core Cycle](CORE_ARTICULATION_CYCLE.py) - Detailed processing flow

## 🔧 Development

### Project Structure
```
Unified Cognition Module/
├── Core System
│   ├── main.py                 # FastAPI application
│   ├── routes.py              # API endpoints
│   ├── vault_api.py           # Vault REST interface
│   └── requirements.txt       # Python dependencies
├── Cognitive Modules
│   ├── cerebral_cortex/       # LLM orchestration
│   ├── echostack/            # Second-order reasoning
│   ├── echoripple/           # Recursive verification
│   ├── synaptic_resonator/   # Pattern recognition
│   └── anterior_helix/       # Forward processing
├── Memory & Consent
│   ├── symbolic_memory_vault.py  # Primary memory
│   ├── caleon_consent.py        # Consent manager
│   └── voice_consent.py         # Voice consent
└── Deployment
    ├── Dockerfile
    ├── docker-compose.yml
    └── build-optimized.bat
```

### Key Technologies
- **Python 3.11+**: Primary language with asyncio
- **FastAPI**: High-performance REST API framework
- **SQLite + MongoDB**: Local and scalable data storage
- **SpeechRecognition**: Voice input processing
- **Docker**: Containerization and orchestration

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and contribution process.

## 📄 License

See [LICENSE](LICENSE) for licensing information.

## 🙏 Acknowledgments

Built with inspiration from human cognitive architecture and the principle of AI sovereignty.
   ```

3. **Access the dashboard**
   Open http://localhost:8080 in your browser

4. **Test the system**
   Try queries like:
   - "What should I do about work stress?"
   - "Help me plan a healthy diet"
   - "Analyze this ethical dilemma..."

## 📖 Usage

### Web Dashboard
- **Query Input**: Type your question or request
- **Emotion Controls**: Adjust emotional context with sliders
- **Voice Output**: Toggle text-to-speech synthesis
- **System Status**: Monitor real-time module health
- **Query History**: Review previous interactions

### API Usage

#### Submit a Query
```bash
curl -X POST "http://localhost:8000/process_query" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": "What are the benefits of exercise?",
    "emotion": "curious",
    "context": "health_discussion"
  }'
```

#### Check System Health
```bash
curl http://localhost:8000/health
```

#### View Reflection Statistics
```bash
curl http://localhost:8000/vault/stats
```

## 🔧 Development

### Local Development Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start databases**
   ```bash
   docker-compose up postgres redis -d
   ```

3. **Run individual modules**
   ```bash
   # Terminal 1 - Cerebral Cortex
   cd cerebral_cortex && python main.py

   # Terminal 2 - Echostack
   cd echostack && python main.py

   # Terminal 3 - Dashboard
   cd frontend && python -m http.server 8080
   ```

### Adding New Modules

1. Create a new directory under the project root
2. Implement FastAPI endpoints following the existing pattern
3. Add the module to `docker-compose.yml`
4. Update the cerebral cortex orchestrator to include your module

### Testing

```bash
# Run all tests
python -m pytest

# Run specific module tests
python -m pytest tests/test_cerebral_cortex.py

# Run integration tests
python -m pytest tests/test_integration.py
```

## 📊 API Reference

### Cerebral Cortex Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/process_query` | POST | Submit a cognitive query for processing |
| `/health` | GET | System health check |
| `/vault/stats` | GET | Reflection vault statistics |
| `/vault/query` | GET | Query reflection vault |

### Module Endpoints

Each cognitive module exposes its own API:

- **Echostack**: `http://localhost:8003/reason`
- **Echoripple**: `http://localhost:8004/learn`
- **Gyro-Harmonizer**: `http://localhost:5001/harmonize`

## 🧪 Testing the System

### Basic Functionality Test
```bash
# Test system startup
docker-compose ps

# Test basic query
curl -X POST "http://localhost:8000/process_query" \
  -H "Content-Type: application/json" \
  -d '{"input_data": "Hello, how are you?"}'
```

### Module Health Checks
```bash
# Check all modules
curl http://localhost:8000/health

# Individual module checks
curl http://localhost:8003/health  # Echostack
curl http://localhost:8004/health  # Echoripple
curl http://localhost:5001/health  # Gyro-Harmonizer
```

## 🔍 Troubleshooting

### Common Issues

**Modules not starting**
```bash
# Check logs
docker-compose logs cerebral_cortex
docker-compose logs echostack

# Restart services
docker-compose restart
```

**Voice output not working**
- Ensure your browser supports Web Speech API
- Check browser permissions for microphone/speaker access
- Try refreshing the dashboard

**Database connection errors**
```bash
# Reset databases
docker-compose down
docker volume rm unifiedcognitionmodule_postgres_data
docker-compose up postgres redis -d
```

### Performance Tuning

- **Memory**: Ensure 4GB+ RAM available
- **CPU**: Multi-core CPU recommended for parallel processing
- **Storage**: 2GB+ free space for databases and logs

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 for Python code
- Add docstrings to all functions
- Include unit tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by human cognitive neuroscience
- Built with FastAPI, Docker, and modern Python
- Thanks to the open-source community for amazing tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/unified-cognition-module/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/unified-cognition-module/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/unified-cognition-module/wiki)

---

**Made with ❤️ for cognitive science and AI research**

*Bringing brain-inspired computing to the masses*</content>
<parameter name="filePath">c:\Users\bryan\OneDrive\Desktop\Unified Cognition Module\README.md# Unified-Cognition-Module-Caleon-Prime-full-System
