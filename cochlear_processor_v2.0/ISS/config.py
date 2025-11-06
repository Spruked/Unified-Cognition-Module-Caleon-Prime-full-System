"""
ISS Module Configuration for Prometheus Prime Integration
========================================================

Configuration classes and settings management compatible with 
Prometheus Prime microservices architecture.

Provides:
- Environment-based configuration
- Service discovery settings  
- Circuit breaker configuration
- Middleware settings
- Database and storage configuration
- Logging configuration
"""

import os
from typing import List, Optional, Dict, Any
from pydantic import BaseSettings, Field
from enum import Enum


class EnvironmentType(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging" 
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ISSSettings(BaseSettings):
    """
    ISS Module settings compatible with Prometheus Prime
    
    Reads configuration from environment variables with fallback defaults.
    """
    
    # Basic service configuration
    SERVICE_NAME: str = Field(default="iss-controller", env="ISS_SERVICE_NAME")
    VERSION: str = Field(default="1.0.0", env="ISS_VERSION")
    ENVIRONMENT: EnvironmentType = Field(default=EnvironmentType.DEVELOPMENT, env="ENVIRONMENT")
    
    # Network configuration
    HOST: str = Field(default="0.0.0.0", env="ISS_HOST")
    PORT: int = Field(default=8003, env="ISS_PORT")
    
    # Service discovery
    SERVICE_REGISTRY_URL: Optional[str] = Field(default=None, env="SERVICE_REGISTRY_URL")
    CONSUL_HOST: Optional[str] = Field(default="localhost", env="CONSUL_HOST")
    CONSUL_PORT: int = Field(default=8500, env="CONSUL_PORT")
    
    # Prometheus Prime API Gateway
    API_GATEWAY_URL: str = Field(default="http://localhost:8000", env="API_GATEWAY_URL")
    
    # Database and storage
    DATA_DIR: str = Field(default="./data", env="ISS_DATA_DIR")
    LOG_STORAGE_PATH: str = Field(default="./data/logs", env="ISS_LOG_STORAGE_PATH")
    VAULT_STORAGE_PATH: str = Field(default="./data/vault", env="ISS_VAULT_STORAGE_PATH")
    
    # Database URL (for persistent storage)
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # Redis configuration (for caching and sessions)
    REDIS_URL: Optional[str] = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_ENABLED: bool = Field(default=False, env="REDIS_ENABLED")
    
    # Logging configuration
    LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO, env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")  # json or console
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # CORS settings
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )
    
    # Security settings
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REQUIRE_AUTH: bool = Field(default=False, env="REQUIRE_AUTH")
    
    # Circuit breaker settings
    CIRCUIT_BREAKER_ENABLED: bool = Field(default=True, env="CIRCUIT_BREAKER_ENABLED")
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = Field(default=5, env="CIRCUIT_BREAKER_FAILURE_THRESHOLD")
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = Field(default=60, env="CIRCUIT_BREAKER_RECOVERY_TIMEOUT")
    CIRCUIT_BREAKER_EXPECTED_EXCEPTION: str = Field(default="Exception", env="CIRCUIT_BREAKER_EXPECTED_EXCEPTION")
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds
    
    # Monitoring and metrics
    METRICS_ENABLED: bool = Field(default=True, env="METRICS_ENABLED")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    HEALTH_CHECK_INTERVAL: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")  # seconds
    
    # ISS specific settings
    STARDATE_OFFSET: float = Field(default=0.0, env="ISS_STARDATE_OFFSET")
    DEFAULT_LOG_CATEGORY: str = Field(default="general", env="ISS_DEFAULT_LOG_CATEGORY")
    MAX_LOG_ENTRIES: int = Field(default=10000, env="ISS_MAX_LOG_ENTRIES")
    LOG_RETENTION_DAYS: int = Field(default=90, env="ISS_LOG_RETENTION_DAYS")
    
    # Captain's Log settings
    CAPTAIN_NAME: str = Field(default="Captain", env="ISS_CAPTAIN_NAME")
    SHIP_NAME: str = Field(default="ISS Module", env="ISS_SHIP_NAME")
    AUTO_BACKUP_ENABLED: bool = Field(default=True, env="ISS_AUTO_BACKUP_ENABLED")
    BACKUP_INTERVAL_HOURS: int = Field(default=24, env="ISS_BACKUP_INTERVAL_HOURS")
    
    # Export settings
    EXPORT_DIR: str = Field(default="./exports", env="ISS_EXPORT_DIR")
    MAX_EXPORT_SIZE_MB: int = Field(default=100, env="ISS_MAX_EXPORT_SIZE_MB")
    EXPORT_FORMATS: List[str] = Field(default=["csv", "json", "markdown"], env="ISS_EXPORT_FORMATS")
    
    # VisiData integration
    VISIDATA_ENABLED: bool = Field(default=False, env="ISS_VISIDATA_ENABLED")
    VISIDATA_PORT: int = Field(default=8080, env="ISS_VISIDATA_PORT")
    
    # Prometheus Prime integration
    PROMETHEUS_INTEGRATION_ENABLED: bool = Field(default=True, env="PROMETHEUS_INTEGRATION_ENABLED")
    REASONING_TIMEOUT_MS: int = Field(default=5000, env="REASONING_TIMEOUT_MS")
    VAULT_QUERY_LIMIT: int = Field(default=1000, env="VAULT_QUERY_LIMIT")
    
    # External service URLs (for Prometheus Prime ecosystem)
    COCHLEAR_PROCESSOR_URL: Optional[str] = Field(default=None, env="COCHLEAR_PROCESSOR_URL")
    PHONATORY_OUTPUT_URL: Optional[str] = Field(default=None, env="PHONATORY_OUTPUT_URL")
    VAULT_MANAGER_URL: Optional[str] = Field(default=None, env="VAULT_MANAGER_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT == EnvironmentType.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT == EnvironmentType.PRODUCTION
    
    @property
    def service_url(self) -> str:
        """Get the full service URL"""
        return f"http://{self.HOST}:{self.PORT}"
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information for registration"""
        return {
            "name": self.SERVICE_NAME,
            "version": self.VERSION,
            "url": self.service_url,
            "health_check": f"{self.service_url}/health",
            "environment": self.ENVIRONMENT,
            "capabilities": [
                "reasoning_processing",
                "vault_queries",
                "log_management", 
                "time_anchoring",
                "data_export"
            ]
        }
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            "url": self.DATABASE_URL,
            "data_dir": self.DATA_DIR,
            "log_storage": self.LOG_STORAGE_PATH,
            "vault_storage": self.VAULT_STORAGE_PATH
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            "level": self.LOG_LEVEL,
            "format": self.LOG_FORMAT,
            "file": self.LOG_FILE,
            "service": self.SERVICE_NAME
        }
    
    def get_circuit_breaker_config(self) -> Dict[str, Any]:
        """Get circuit breaker configuration"""
        return {
            "enabled": self.CIRCUIT_BREAKER_ENABLED,
            "failure_threshold": self.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
            "recovery_timeout": self.CIRCUIT_BREAKER_RECOVERY_TIMEOUT,
            "expected_exception": self.CIRCUIT_BREAKER_EXPECTED_EXCEPTION
        }
    
    def get_rate_limit_config(self) -> Dict[str, Any]:
        """Get rate limiting configuration"""
        return {
            "enabled": self.RATE_LIMIT_ENABLED,
            "requests": self.RATE_LIMIT_REQUESTS,
            "window": self.RATE_LIMIT_WINDOW
        }


# Create global settings instance
settings = ISSSettings()


# Configuration validation
def validate_settings():
    """Validate settings and provide warnings for production"""
    issues = []
    
    if settings.is_production:
        if settings.SECRET_KEY == "dev-secret-key-change-in-production":
            issues.append("SECRET_KEY should be changed in production")
        
        if not settings.DATABASE_URL:
            issues.append("DATABASE_URL should be set in production")
        
        if settings.LOG_LEVEL == LogLevel.DEBUG:
            issues.append("LOG_LEVEL should not be DEBUG in production")
    
    if settings.PROMETHEUS_INTEGRATION_ENABLED:
        if not settings.API_GATEWAY_URL:
            issues.append("API_GATEWAY_URL required for Prometheus integration")
    
    return issues


# Environment-specific configurations
class DevelopmentConfig:
    """Development environment specific settings"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = LogLevel.DEBUG
    CIRCUIT_BREAKER_ENABLED = False
    RATE_LIMIT_ENABLED = False


class ProductionConfig:
    """Production environment specific settings"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = LogLevel.INFO
    CIRCUIT_BREAKER_ENABLED = True
    RATE_LIMIT_ENABLED = True
    REQUIRE_AUTH = True


class TestingConfig:
    """Testing environment specific settings"""
    DEBUG = True
    TESTING = True
    LOG_LEVEL = LogLevel.DEBUG
    DATABASE_URL = "sqlite:///test.db"
    CIRCUIT_BREAKER_ENABLED = False
    RATE_LIMIT_ENABLED = False


def get_config_for_environment(env: EnvironmentType):
    """Get configuration class for environment"""
    configs = {
        EnvironmentType.DEVELOPMENT: DevelopmentConfig,
        EnvironmentType.PRODUCTION: ProductionConfig,
        EnvironmentType.TESTING: TestingConfig,
        EnvironmentType.STAGING: ProductionConfig  # Use production config for staging
    }
    return configs.get(env, DevelopmentConfig)


# Export main settings and utilities
__all__ = [
    'ISSSettings',
    'settings',
    'EnvironmentType',
    'LogLevel',
    'validate_settings',
    'DevelopmentConfig',
    'ProductionConfig', 
    'TestingConfig',
    'get_config_for_environment'
]