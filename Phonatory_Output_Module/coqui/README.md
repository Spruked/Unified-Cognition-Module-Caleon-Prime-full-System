# Coqui TTS Models and Cache Directory

This directory serves as a placeholder for:

- **Downloaded TTS models**: Coqui TTS models will be cached here
- **Custom voice samples**: Reference audio files for voice cloning
- **Model artifacts**: Tokenizers, configs, and other model-specific files
- **Temporary files**: Processing intermediates and cache files

## Directory Structure (when populated):
```
coqui/
├── models/                    # Downloaded TTS models
│   ├── tts_models/
│   └── vocoder_models/
├── speakers/                  # Voice cloning reference files
│   ├── reference_samples/
│   └── embeddings/
├── cache/                     # Runtime cache
└── temp/                      # Temporary processing files
```

## Usage Notes:
- This directory will be automatically populated when the first TTS model is downloaded
- Voice cloning samples should be placed in `speakers/reference_samples/`
- Cache files can be safely deleted to free up space
- Models are typically 1-2GB each, plan storage accordingly

## Configuration:
- TTS cache location can be configured via environment variables
- See `voice_config.json` for speaker and model preferences