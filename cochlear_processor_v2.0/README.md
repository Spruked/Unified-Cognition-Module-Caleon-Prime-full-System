# cochlear_processor_v2.0 🧠🎧
Modular sensory-input engine for the Caleon AI Core.
Canonical project name: `cochlear_processor_v2.0`
GitHub repository: https://github.com/Spruked/cochlear_processor_v2.0.git

---

### 🔍 Overview
Cochlear Processor v2 converts real-world audio into symbolic, emotional, and temporal data streams.  
It links directly to Caleon’s core through **CoreBridge**, timestamps each sensory event with the ISS module, and records traceable vault entries with contextual hashes.

---

### ⚙️ Key Features
- **Adaptive Fidelity Queue** – automatic down-sampling under load.  
- **Contextual Indexing** – short-term glyph hashing for associative recall.  
- **Vault Integration** – relational trace linking (`context_hash`, `prev_trace_id`).  
- **System Health Ping** – self-diagnostic every 100 packets.  
- **Container Ready** – minimal dependencies, async-safe loop.

---



### 🚀 Quick Start
```bash
git clone https://github.com/Spruked/cochlear_processor_v2.0.git
cd cochlear_processor_v2.0
pip install -r config/requirements.txt
python cochlear_processor.py
```

---

### 🐳 Docker Usage



#### Build and Run with Docker
```bash
docker build -t cochlear_processor_v2.0 .
docker run --rm -it -v %cd%:/app cochlear_processor_v2.0
```

#### Using Docker Compose
```bash
docker-compose up --build
```

- The main service is `cochlear_processor_v2.0`.
- The ISS core service is started automatically as `iss_core`.
- To stop: `docker-compose down`

---

### 🧩 Requirements
- Python 3.11+
- See `config/requirements.txt` for dependencies.

---

### 🔌 Plug-and-Play Architecture

- **Timekeeper Module:**
  - ISS (Interplanetary Stardate Synchrometer) is auto-detected and used if available.
  - If ISS is not present, the system falls back to a standard UTC timekeeper.
  - To add a custom timekeeper, place your module in `timekeeper/` and ensure it implements `get_timecodes()`.

- **Output Endpoint:**
  - All output is routed through a plug-and-play `ResonatorAdapter` (see `resonator_adapter.py`).
  - By default, output is sent via HTTP POST to the core endpoint at `http://core_endpoint:8088/sensory`.
  - You can override the endpoint by setting the `CORE_ENDPOINT_URL` environment variable, or by passing your own object as the `core_endpoint` argument to `main_loop()`.

- **Custom Output:**
  - To plug in your own output logic, pass an object with a `.send(trace_id, matrix)` method as the `core_endpoint` argument to `main_loop()`.

---

### 🧠 ASR Plug-and-Play

- **ASR Backend:**
  - By default, the system uses OpenAI Whisper (via `whisper-main/` and `model_loader.py`).
  - To use a custom ASR backend, set the environment variable `ASR_BACKEND` to `custom` and provide an `asr_backend.py` with a `transcribe(audio_path)` function.
  - All transcription is routed through a unified `asr_transcribe()` interface for easy swapping.

---

### 🧠 Whisper Semantic Output

- **Full Whisper Output:**
  - All semantic fields from Whisper (segments, language, word-level info, etc.) are included in the output pipeline.
  - Downstream adapters and endpoints receive the full segment list and language info for advanced processing.
  - See `transcribe.py` and `resonator_adapter.py` for details on available fields.

---

### 🛠️ Troubleshooting & Edge Cases

- If ISS is not available, the system will automatically use the standard UTC timekeeper.
- If you want to use a custom ASR backend, set `ASR_BACKEND=custom` and provide an `asr_backend.py` with a `transcribe(audio_path)` function.
- All output fields, including Whisper's full semantic output, are always present in the output pipeline.
- For custom output endpoints or adapters, see `resonator_adapter.py` and pass your own object to `main_loop()`.
# cochlear_processor_v2.0
