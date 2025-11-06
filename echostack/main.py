# main.py

"""
EchoStack Main Application
FastAPI application with integrated reasoning engine, live injection, monitoring, and vault synchronization.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os

from echostack_module.routes import router
from echostack_module.vault_loader import load_seed_vault
from echostack_module.tracelogger import TraceLogger
from echostack_module.dashboard import Dashboard
from echostack_module.vault_sync import VaultSynchronizer
from echostack_module.alert_manager import AlertManager
from reflection_vault import ReflectionVault

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="EchoStack Reasoning System",
    description="Modular vault-aware reasoning system with traceable cognition",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
tracelogger = None
dashboard = None
vault_sync = None
alert_manager = None
reflection_vault = None

@app.on_event("startup")
async def startup_event():
    """Initialize EchoStack services on startup"""
    global tracelogger, dashboard, vault_sync, alert_manager, reflection_vault

    logger.info("Initializing EchoStack services...")

    try:
        # Get telemetry path from environment
        telemetry_path = os.getenv("TELEMETRY_PATH", "../telemetry.json")

        # Load ICS-V2-2025-10-18 protocol and vault compliance
        logger.info("Loading vault protocol...")
        # Initialize vault system by loading a sample vault
        sample_vault = load_seed_vault("../seed_logic_vault/seed_ockhams_filter.json")
        logger.info(f"Loaded sample vault with {len(sample_vault.get('entries', []))} entries")

        # Initialize reflection vault
        logger.info("Starting Reflection Vault...")
        reflection_vault = ReflectionVault("echostack_reflection_vault.json", "echostack")

        # Initialize core services
        logger.info("Starting TraceLogger...")
        tracelogger = TraceLogger(telemetry_path=telemetry_path)
        tracelogger.start()

        logger.info("Starting Dashboard...")
        dashboard = Dashboard(telemetry_path=telemetry_path)
        dashboard.start()

        logger.info("Starting Vault Synchronizer...")
        vault_sync = VaultSynchronizer(telemetry_path=telemetry_path)
        vault_sync.start_synchronization()

        logger.info("Starting Alert Manager...")
        alert_manager = AlertManager(telemetry_path=telemetry_path)
        alert_manager.start_monitoring()

        logger.info("EchoStack initialization complete!")

    except Exception as e:
        logger.error(f"Failed to initialize EchoStack services: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up EchoStack services on shutdown"""
    global tracelogger, dashboard, vault_sync, alert_manager

    logger.info("Shutting down EchoStack services...")

    try:
        if tracelogger:
            logger.info("Stopping TraceLogger...")
            tracelogger.stop()

        if dashboard:
            logger.info("Stopping Dashboard...")
            dashboard.stop()

        if vault_sync:
            logger.info("Stopping Vault Synchronizer...")
            vault_sync.stop_synchronization()

        if alert_manager:
            logger.info("Stopping Alert Manager...")
            alert_manager.stop_monitoring()

        logger.info("EchoStack shutdown complete!")

    except Exception as e:
        logger.error(f"Error during EchoStack shutdown: {e}")

# Include EchoStack routes
app.include_router(router)

# Custom exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn

    # Get port from environment or default to 8003
    port = int(os.getenv("PORT", 8003))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting EchoStack server on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,  # Disable reload in production
        log_level="info",
        access_log=True
    )
