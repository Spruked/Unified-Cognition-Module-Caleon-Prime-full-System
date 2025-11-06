# ISS Module - Quick Start Guide 🚀

## Installation (Plug-and-Play)

```powershell
# Navigate to the ISS Module directory
cd "c:\Users\bryan\OneDrive\Desktop\ISS_Module"

# Install in development mode (editable)
pip install -e .

# Or install from current directory
pip install .
```

## Usage Examples

### 1. Time Anchors (for Caleon/CertSig)
```python
from iss_module.core.utils import current_timecodes

# Get all time representations for anchoring
timecodes = current_timecodes()
print(f"Stardate: {timecodes['stardate']}")
print(f"Anchor Hash: {timecodes['anchor_hash']}")
```

### 2. Captain's Log (Core Logging)
```python
from iss_module.captain_mode import CaptainLog
import asyncio

async def main():
    # Initialize with captain and ship info
    log = CaptainLog(captain="Bryan", ship="Prometheus")
    await log.initialize()
    
    # Add entries
    await log.add_entry(
        "Engaged harmonizer module", 
        category="System", 
        location="Core"
    )
    
    # Get entries
    entries = await log.get_entries()
    print(f"Total entries: {len(entries)}")

asyncio.run(main())
```

### 3. API Server
```python
# Option 1: Direct import
from iss_module.api.api import app
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)

# Option 2: CLI command
# iss-server

# Option 3: Python -m
# python -m iss_module.api.api
```

### 4. Data Export
```python
from iss_module.captain_mode.exporters import Exporters
import asyncio

async def export_data():
    # Assuming you have entries from CaptainLog
    await Exporters.to_json(entries, "logs.json")
    await Exporters.to_csv(entries, "logs.csv") 
    await Exporters.to_markdown(entries, "logs.md")

asyncio.run(export_data())
```

### 5. VisiData Integration
```python
from iss_module.captain_mode.vd_wrapper import VisiDataWrapper
import asyncio

async def analyze_data():
    vd = VisiDataWrapper()
    # This will export and immediately open in VisiData
    await vd.export_and_open(entries)

asyncio.run(analyze_data())
```

### 6. Validation
```python
from iss_module.core.validators import Validator

# Validate various data types
is_valid_stardate = Validator.check_stardate(12345.6)
is_valid_timestamp = Validator.check_timestamp("2024-01-01T00:00:00Z")
clean_text = Validator.clean_input("User input text...")
```

## CLI Commands

```powershell
# Start server
iss-server

# Get current time codes
iss-module timecodes

# Create log entry
iss-module log "Test entry" --category mission --tags "test,demo"

# Help
iss-module --help
```

## API Endpoints

Once server is running (`iss-server` or `uvicorn iss_module.api.api:app`):

- **Dashboard**: http://localhost:8000 or http://localhost:8000/dashboard
- **API Docs**: http://localhost:8000/api/docs  
- **Health Check**: http://localhost:8000/api/health
- **Current Stardate**: http://localhost:8000/api/stardate

## Integration with Caleon & CertSig

### For Caleon (Symbolic Cognition)
```python
# Time-anchored symbolic processing
from iss_module import current_timecodes, CaptainLog

async def caleon_integration():
    # Get time anchor for symbolic processing
    anchor = current_timecodes()
    
    # Log symbolic cognition events
    log = CaptainLog(captain="Caleon", ship="Cognitive-Engine")
    await log.initialize()
    
    await log.add_entry(
        f"Symbolic processing at anchor {anchor['anchor_hash']}", 
        category="cognitive",
        tags=["symbolic", "processing", "caleon"]
    )
```

### For CertSig (NFT Timestamp Anchoring)
```python
# NFT timestamp anchoring
from iss_module import current_timecodes

def certsig_integration():
    # Get cryptographic time anchor
    anchor = current_timecodes()
    
    # Use for NFT metadata
    nft_metadata = {
        "timestamp": anchor['iso_timestamp'],
        "stardate": anchor['stardate'], 
        "anchor_hash": anchor['anchor_hash'],
        "julian_date": anchor['julian_date']
    }
    
    return nft_metadata
```

## File Structure Reference

```
iss_module/
├── __init__.py           # Main package exports
├── cli.py               # Command line interface
├── core/               
│   ├── __init__.py      # Core exports
│   ├── utils.py         # Time anchors, stardate functions
│   ├── ISS.py          # Central controller
│   ├── module_loader.py # Dynamic module management
│   └── validators.py    # Data validation + Validator class
├── captain_mode/
│   ├── __init__.py      # Captain mode exports  
│   ├── captain_log.py   # CaptainLog class
│   ├── exporters.py     # Exporters class
│   └── vd_wrapper.py    # VisiDataWrapper class
├── api/
│   ├── __init__.py      # API exports
│   └── api.py          # FastAPI app with auto-dashboard
├── templates/
│   ├── dashboard.html   # Web interface
│   └── login.html      # Authentication page
├── setup.py            # Package configuration
├── requirements.txt    # Dependencies
└── README.md          # Full documentation
```

---

**Ready for Caleon and CertSig integration!** 🛸✨