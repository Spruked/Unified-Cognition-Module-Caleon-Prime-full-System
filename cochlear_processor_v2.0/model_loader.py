import whisper
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config_whisper.json')

def load_model():
    """
    Loads the Whisper model based on config_whisper.json settings.

    Returns:
        whisper.model.Whisper: Loaded Whisper model instance.
    """
    try:
        with open(CONFIG_PATH, 'r') as config_file:
            config = json.load(config_file)

        model_size = config.get("model_size", "base")
        model = whisper.load_model(model_size)
        return model

    except Exception as e:
        raise RuntimeError(f"[Model Loader] Failed to load model: {e}")
