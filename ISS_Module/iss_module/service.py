"""
ISS Controller Microservice
===========================

Standalone microservice that integrates ISS Module capabilities into 
the Prometheus Prime cognitive architecture.

This service provides:
- Health checks compatible with Prometheus Prime
- Reasoning pipeline integration
- Vault management and queries  
- Captain's log management
- Time anchoring for all operations
- Service discovery registration

Usage:
    python -m iss_module.service
    
Or with custom configuration:
    ISS_HOST=0.0.0.0 ISS_PORT=8003 python -m iss_module.service
"""

import asyncio
import signal
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
import structlog

from iss_module.config import settings, validate_settings
from iss_module.prometheus_integration import create_prometheus_iss_app


# Configure structured logging for Prometheus Prime compatibility
def setup_logging():
    """Setup structured logging compatible with Prometheus Prime"""
    
    processors = [
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" else structlog.dev.ConsoleRenderer()
    ]
    
    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )


def create_app() -> FastAPI:
    """
    Create the ISS Controller FastAPI application
    
    Returns:
        FastAPI application configured for Prometheus Prime integration
    """
    # Setup logging first
    setup_logging()
    
    logger = structlog.get_logger("iss-controller")
    
    # Validate configuration
    config_issues = validate_settings()
    if config_issues:
        logger.warning("Configuration issues detected", issues=config_issues)
    
    # Create the Prometheus Prime compatible app
    app = create_prometheus_iss_app(settings.SERVICE_NAME)
    
    # Add custom metadata
    app.state.settings = settings
    app.state.start_time = None
    
    # Update app metadata
    app.title = "ISS Controller Service"
    app.description = """
    Integrated Systems Solution Controller for Prometheus Prime
    
    Provides time anchoring, captain's log management, vault queries,
    and reasoning pipeline integration for the Prometheus Prime 
    cognitive architecture.
    
    Key Features:
    - Compatible with Prometheus Prime API Gateway
    - Structured logging with JSON output
    - Health checks and service discovery
    - Circuit breaker pattern support
    - Vault management and queries
    - Captain's log with stardate anchoring
    """
    app.version = settings.VERSION
    
    return app


async def register_with_service_discovery():
    """Register this service with service discovery system"""
    logger = structlog.get_logger("iss-controller.registration")
    
    if not settings.SERVICE_REGISTRY_URL:
        logger.info("Service registry not configured, skipping registration")
        return
    
    try:
        # Here you would implement actual service registration
        # This is a placeholder for the actual implementation
        
        service_info = settings.get_service_info()
        
        logger.info(
            "Service registration attempted",
            service=service_info["name"],
            url=service_info["url"],
            registry=settings.SERVICE_REGISTRY_URL
        )
        
        # Example: Register with Consul
        # await register_with_consul(service_info)
        
    except Exception as e:
        logger.error("Service registration failed", error=str(e))


async def deregister_from_service_discovery():
    """Deregister this service from service discovery"""
    logger = structlog.get_logger("iss-controller.deregistration")
    
    if not settings.SERVICE_REGISTRY_URL:
        return
    
    try:
        # Implement deregistration logic
        logger.info("Service deregistration attempted")
        
    except Exception as e:
        logger.error("Service deregistration failed", error=str(e))


def setup_signal_handlers(app: FastAPI):
    """Setup signal handlers for graceful shutdown"""
    logger = structlog.get_logger("iss-controller.signals")
    
    def signal_handler(signum, frame):
        logger.info("Shutdown signal received", signal=signum)
        # Trigger graceful shutdown
        asyncio.create_task(shutdown_handler())
    
    async def shutdown_handler():
        logger.info("Initiating graceful shutdown")
        await deregister_from_service_discovery()
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def run_server():
    """
    Run the ISS Controller microservice
    
    This function starts the service with proper configuration,
    logging, and signal handling.
    """
    logger = structlog.get_logger("iss-controller.startup")
    
    logger.info(
        "Starting ISS Controller",
        service=settings.SERVICE_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        host=settings.HOST,
        port=settings.PORT
    )
    
    # Create the application
    app = create_app()
    
    # Setup signal handlers
    setup_signal_handlers(app)
    
    # Configure uvicorn
    uvicorn_config = {
        "host": settings.HOST,
        "port": settings.PORT,
        "log_level": settings.LOG_LEVEL.lower(),
        "reload": settings.is_development,
        "access_log": True,
    }
    
    # Add SSL configuration for production
    if settings.is_production:
        # Add SSL/TLS configuration here if needed
        pass
    
    try:
        # Start the server
        uvicorn.run(app, **uvicorn_config)
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server startup failed", error=str(e))
        sys.exit(1)


# CLI interface for the service
def main():
    """Main entry point for the ISS Controller service"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ISS Controller Microservice for Prometheus Prime"
    )
    
    parser.add_argument(
        "--host",
        default=settings.HOST,
        help=f"Host to bind to (default: {settings.HOST})"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=settings.PORT,
        help=f"Port to bind to (default: {settings.PORT})"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        default=settings.is_development,
        help="Enable auto-reload on code changes"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=settings.LOG_LEVEL,
        help=f"Logging level (default: {settings.LOG_LEVEL})"
    )
    
    parser.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate configuration and exit"
    )
    
    args = parser.parse_args()
    
    # Override settings with CLI arguments
    if args.host != settings.HOST:
        settings.HOST = args.host
    if args.port != settings.PORT:
        settings.PORT = args.port
    if hasattr(args, 'log_level'):
        settings.LOG_LEVEL = args.log_level
    
    # Validate configuration if requested
    if args.validate_config:
        setup_logging()
        logger = structlog.get_logger("iss-controller.config")
        
        issues = validate_settings()
        if issues:
            logger.error("Configuration validation failed", issues=issues)
            sys.exit(1)
        else:
            logger.info("Configuration validation passed")
            sys.exit(0)
    
    # Run the server
    run_server()


if __name__ == "__main__":
    main()