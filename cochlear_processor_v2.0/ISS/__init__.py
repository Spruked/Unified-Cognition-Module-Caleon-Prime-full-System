"""
ISS Module - Integrated Systems Solution
========================================

A comprehensive data management and time anchoring system designed for:
- Captain's Log system with stardate calculations
- Universal data export (CSV, JSON, Markdown)
- VisiData integration for data analysis
- FastAPI web interface with automatic documentation
- Time anchoring for blockchain/NFT applications
- Cross-project compatibility (Caleon, CertSig)

Quick Start:
    from iss_module import ISS, CaptainLog, Exporters
    from iss_module.core.utils import get_stardate, current_timecodes
    
    # Initialize system
    iss = ISS()
    
    # Add log entry
    log = CaptainLog()
    log.add_entry("Mission parameters established")
    
    # Export data
    entries = log.get_entries()
    Exporters.to_csv(entries, "mission_log.csv")
    
    # Get current stardate
    stardate = get_stardate()
    print(f"Stardate {stardate}")

Components:
    - core: System utilities, validators, time anchoring
    - captain_mode: Logging and export systems
    - api: FastAPI web interface
    - templates: Web UI templates

For Caleon Integration:
    from iss_module import ISS
    from iss_module.core.utils import current_timecodes
    
    # Use for symbolic cognition timestamps
    timecodes = current_timecodes()
    
For CertSig Integration:
    from iss_module.core.utils import get_stardate
    from iss_module.captain_mode import Exporters
    
    # Use for NFT metadata timestamps
    stardate = get_stardate()
    metadata = {"stardate": stardate, "timestamp": timecodes["iso_timestamp"]}
"""

__version__ = "1.0.0"
__author__ = "ISS Development Team"
__email__ = "iss@enterprise.starfleet"

# Core imports for easy access
from iss_module.core.ISS import ISS
from iss_module.captain_mode.captain_log import CaptainLog
from iss_module.captain_mode.exporters import Exporters
from iss_module.core.utils import get_stardate, current_timecodes

# Prometheus Prime integration (optional import)
try:
    from iss_module.prometheus_integration import (
        PrometheusISS,
        create_prometheus_iss_app,
        ReasoningRequest,
        ReasoningResponse
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Configuration
try:
    from iss_module.config import settings
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# Structured logging
try:
    from iss_module.logging_config import get_logger, configure_structured_logging
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False

# Main components
__all__ = [
    'ISS',
    'CaptainLog', 
    'Exporters',
    'get_stardate',
    'current_timecodes',
    '__version__',
]

# Add Prometheus Prime components if available
if PROMETHEUS_AVAILABLE:
    __all__.extend([
        'PrometheusISS',
        'create_prometheus_iss_app',
        'ReasoningRequest',
        'ReasoningResponse'
    ])

# Add configuration if available
if CONFIG_AVAILABLE:
    __all__.append('settings')

# Add logging if available  
if LOGGING_AVAILABLE:
    __all__.extend(['get_logger', 'configure_structured_logging'])

# Package metadata
PACKAGE_INFO = {
    'name': 'iss-module',
    'version': __version__,
    'description': 'Integrated Systems Solution - Universal data management and time anchoring',
    'author': __author__,
    'email': __email__,
    'url': 'https://github.com/your-org/iss-module',
    'license': 'MIT',
    'requires': ['fastapi', 'uvicorn', 'pydantic', 'jinja2'],
    'optional_requires': {
        'visidata': ['visidata>=2.8'],
        'dev': ['pytest', 'black', 'isort', 'flake8', 'mypy'],
        'prometheus': ['structlog', 'pydantic-settings', 'redis', 'httpx'],
    },
    'integrations': {
        'prometheus_prime': PROMETHEUS_AVAILABLE,
        'structured_logging': LOGGING_AVAILABLE,
        'configuration': CONFIG_AVAILABLE,
    }
}