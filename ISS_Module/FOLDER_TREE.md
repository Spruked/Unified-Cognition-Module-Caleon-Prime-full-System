# ISS Module - Complete Folder and File Tree

```
iss_module/
│
├── 📁 core/                          # Core system components
│   ├── __init__.py                   # Core module exports
│   ├── utils.py                      # Stardate, Julian, market times, time anchors
│   ├── ISS.py                        # Central controller and system orchestration
│   ├── module_loader.py              # Dynamic module management
│   └── validators.py                 # Data validation and safety checks
│
├── 📁 captain_mode/                  # Captain's Log and data management
│   ├── __init__.py                   # Captain mode exports
│   ├── captain_log.py                # Journal/log engine with CRUD operations
│   ├── exporters.py                  # Universal export layer (CSV/JSON/MD)
│   └── vd_wrapper.py                 # VisiData integration wrapper
│
├── 📁 api/                           # FastAPI backend
│   ├── __init__.py                   # API module exports
│   └── api.py                        # FastAPI backend with REST endpoints
│
├── 📁 templates/                     # Web interface templates
│   ├── dashboard.html                # Main dashboard interface
│   └── login.html                    # Authentication page
│
├── 📁 data/                          # Data storage (auto-created)
│   ├── logs/                         # Captain's log storage
│   ├── exports/                      # Export file outputs
│   └── vd_exports/                   # VisiData export staging
│
├── 📁 tests/                         # Test suite (optional)
│   ├── __init__.py
│   ├── test_core.py
│   ├── test_captain_mode.py
│   └── test_api.py
│
├── 📁 docs/                          # Documentation (optional)
│   ├── README.md
│   ├── API.md
│   └── INTEGRATION.md
│
├── __init__.py                       # Main package initialization
├── cli.py                            # Command-line interface
├── setup.py                          # Package installation configuration
├── requirements.txt                  # Python dependencies
├── README.md                         # Main documentation
├── QUICK_START.md                    # Quick start guide
├── CHANGELOG.md                      # Version history
├── LICENSE                           # MIT License
├── .gitignore                        # Git ignore rules
├── Dockerfile                        # Docker containerization (optional)
└── docker-compose.yml               # Docker compose setup (optional)
```

## 🚀 Plug-and-Play Usage

### Time Anchors (Caleon Integration)
```python
from iss_module.core.utils import current_timecodes
anchors = current_timecodes()
# Returns: stardate, julian_date, iso_timestamp, anchor_hash
```

### Captain's Log (Universal Logging)
```python
from iss_module.captain_mode import CaptainLog
log = CaptainLog(captain="Bryan", ship="Prometheus")
await log.add_entry("Engaged harmonizer module", category="System", location="Core")
```

### Export System (CertSig Integration)
```python
from iss_module.captain_mode.exporters import Exporters
entries = await log.get_entries()
Exporters.to_json([entry.to_dict() for entry in entries], "logs.json")
Exporters.to_csv([entry.to_dict() for entry in entries], "logs.csv")
```

### VisiData Analysis
```python
from iss_module.captain_mode.vd_wrapper import VisiDataWrapper
vd = VisiDataWrapper()
vd.export_and_open([entry.to_dict() for entry in entries])
```

### API Server
```bash
uvicorn iss_module.api.api:app --reload
# Dashboard auto-served at http://localhost:8000/dashboard
```

### Validation (Safety Checks)
```python
from iss_module.core.validators import Validator
Validator.check_stardate(12345.6)
Validator.clean_input(user_input)
```

## 📦 Installation

```bash
cd iss_module
pip install -e .
```

## 🔗 Integration Points

- **Caleon**: Time anchors, symbolic cognition logging
- **CertSig**: NFT metadata export, timestamp anchoring
- **VisiData**: Data analysis and visualization
- **Docker**: Containerized deployment
- **FastAPI**: REST API and web dashboard

## 🛡️ Production Ready

- ✅ Type hints throughout
- ✅ Async/await support
- ✅ Error handling and logging
- ✅ UTF-8 safe exports
- ✅ CORS enabled API
- ✅ Security validation
- ✅ Docker ready
- ✅ Pip installable