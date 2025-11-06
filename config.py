# Production Settings
from pydantic import BaseSettings
import os
from typing import List, Optional

class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # Server
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 4

    # Database
    postgres_url: str = "postgresql://cortex_user:cortex_pass@postgres:5432/cortex_db"
    redis_url: str = "redis://redis:6379"
    mongo_url: str = "mongodb://mongo:27017"

    # Security
    secret_key: str = "CHANGE_THIS_IN_PRODUCTION"
    jwt_secret_key: str = "CHANGE_THIS_IN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # External APIs
    openai_api_key: Optional[str] = None
    google_speech_api_key: Optional[str] = None
    ollama_endpoint: str = "http://ollama:11434"

    # Voice Settings
    voice_consent_timeout: int = 30
    tts_model: str = "tts_models/en/ljspeech/tacotron2-DDC"

    # Monitoring
    sentry_dsn: Optional[str] = None
    prometheus_metrics: bool = True

    # File Paths
    vault_path: str = "/app/vault"
    logs_path: str = "/app/logs"
    telemetry_path: str = "/app/telemetry"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()