# Contributing to Unified Cognition Module

Thank you for your interest in contributing to the Unified Cognition Module! This document provides guidelines and information for contributors.

## 🧠 Project Overview

The Unified Cognition Module is a brain-inspired AI system that orchestrates multiple cognitive modules to provide intelligent, emotionally-aware responses. The system is built with FastAPI, Docker, and follows a modular microservices architecture.

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Git
- Python 3.11+ (for local development)
- 4GB+ RAM available

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/unified-cognition-module.git
   cd unified-cognition-module
   ```

2. **Start the system**
   ```bash
   docker-compose up --build -d
   ```

3. **Access the dashboard**
   Open http://localhost:8080 in your browser

## 📝 Development Workflow

### 1. Choose an Issue
- Check the [Issues](https://github.com/yourusername/unified-cognition-module/issues) page
- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to indicate you're working on it

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 3. Make Changes
- Follow the existing code style and patterns
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 4. Test Your Changes
```bash
# Run the system
docker-compose up --build -d

# Test basic functionality
curl http://localhost:8000/health

# Run any existing tests
python -m pytest tests/
```

### 5. Commit and Push
```bash
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name
```

### 6. Create a Pull Request
- Go to the repository on GitHub
- Click "New Pull Request"
- Fill out the pull request template
- Wait for review

## 🏗️ Architecture Guidelines

### Adding New Cognitive Modules

1. **Create Module Structure**
   ```
   new_module/
   ├── main.py          # FastAPI application
   ├── requirements.txt # Dependencies
   ├── Dockerfile       # Container definition
   └── README.md        # Module documentation
   ```

2. **Follow the API Pattern**
   ```python
   from fastapi import FastAPI
   from pydantic import BaseModel

   app = FastAPI(title="New Module")

   class RequestModel(BaseModel):
       input_data: str
       context: dict = {}

   @app.post("/process")
   async def process_request(request: RequestModel):
       # Your cognitive processing logic
       return {"result": "processed_output"}

   @app.get("/health")
   async def health_check():
       return {"status": "healthy"}
   ```

3. **Update Orchestrator**
   - Add module URL to `cerebral_cortex/main.py` MODULES dict
   - Implement query logic in the `query_module` function
   - Update module selection logic if needed

### Code Standards

- **Python**: Follow PEP 8 style guidelines
- **API Design**: RESTful principles with consistent error handling
- **Documentation**: Add docstrings to all functions and classes
- **Error Handling**: Graceful degradation and informative error messages
- **Logging**: Use appropriate log levels and structured logging

## 🧪 Testing

### Unit Tests
```python
# tests/test_new_module.py
import pytest
from fastapi.testclient import TestClient
from new_module.main import app

client = TestClient(app)

def test_process_endpoint():
    response = client.post("/process", json={"input_data": "test"})
    assert response.status_code == 200
    assert "result" in response.json()
```

### Integration Tests
```python
# tests/test_integration.py
def test_full_cognitive_pipeline():
    # Test end-to-end cognitive processing
    response = client.post("/process_query", json={
        "input_data": "What is the meaning of life?",
        "emotion": "thoughtful"
    })
    assert response.status_code == 200
    # Add more assertions
```

## 📚 Documentation

### Code Documentation
- Add docstrings to all public functions and classes
- Include parameter types and return values
- Provide usage examples where helpful

### API Documentation
- All endpoints are automatically documented via FastAPI/Swagger
- Access at `http://localhost:{port}/docs` for each module
- Update README.md for any new endpoints

## 🔍 Code Review Process

### For Contributors
- Ensure CI/CD checks pass
- Address reviewer feedback promptly
- Keep commits focused and atomic
- Update tests and documentation

### For Reviewers
- Check code quality and adherence to standards
- Verify tests are comprehensive
- Ensure documentation is updated
- Test the changes in a development environment

## 🐛 Reporting Issues

### Bug Reports
- Use the bug report template
- Include steps to reproduce
- Provide system information (OS, Docker version, etc.)
- Include relevant logs and error messages

### Feature Requests
- Use the feature request template
- Describe the problem you're trying to solve
- Explain why this feature would be valuable
- Consider alternative solutions

## 📋 Pull Request Template

When creating a pull request, please include:

- **Description**: What changes were made and why
- **Testing**: How the changes were tested
- **Breaking Changes**: Any breaking changes and migration notes
- **Screenshots**: UI changes or new features
- **Related Issues**: Links to related issues or PRs

## 🎯 Areas for Contribution

### High Priority
- **Bug Fixes**: Fix known issues and improve stability
- **Documentation**: Improve setup guides and API docs
- **Testing**: Add comprehensive test coverage

### Medium Priority
- **New Modules**: Add specialized cognitive functions
- **Performance**: Optimize response times and resource usage
- **UI/UX**: Enhance the web dashboard

### Future Enhancements
- **Machine Learning**: Integrate ML models for advanced learning
- **Voice Input**: Add speech-to-text capabilities
- **Multi-language**: Support for multiple languages
- **Advanced Analytics**: Detailed performance monitoring

## 💬 Communication

- **Discussions**: Use GitHub Discussions for questions and ideas
- **Issues**: Report bugs and request features
- **Pull Requests**: Submit code changes
- **Discord/Slack**: Join our community chat (if available)

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

Thank you for contributing to the Unified Cognition Module! Your efforts help advance brain-inspired AI research and development. 🧠✨