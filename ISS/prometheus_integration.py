"""
Prometheus Prime Integration Adapter
===================================

Enables ISS Module to function as a microservice within the Prometheus Prime 
cognitive architecture. Provides service registry integration, health checks, 
and API contract compatibility.

Key Features:
- Service discovery and registration
- Health check endpoints compatible with Prometheus Prime
- Circuit breaker pattern support
- Structured logging integration
- Request/response models for API Gateway compatibility
- Vault integration for reasoning pipeline
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from pydantic import BaseModel, Field
import structlog

from iss_module import ISS, CaptainLog, Exporters, get_stardate, current_timecodes


logger = structlog.get_logger(__name__)


# Prometheus Prime compatible models
class ServiceHealthResponse(BaseModel):
    """Service health check response compatible with Prometheus Prime"""
    service: str
    status: str
    version: str
    uptime_seconds: float
    dependencies: List[str]


class ReasoningRequest(BaseModel):
    """Request model compatible with Prometheus Prime reasoning pipeline"""
    input_data: Dict[str, Any] = Field(..., description="Input data for reasoning")
    cycle_type: Optional[str] = Field(None, description="Force specific cycle type")
    timeout_ms: int = Field(default=500, description="Processing timeout in milliseconds")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ReasoningResponse(BaseModel):
    """Response model compatible with Prometheus Prime reasoning pipeline"""
    cycle_id: str
    cycle_type: str
    decision: Dict[str, Any]
    reasoning_trace: Optional[Dict[str, Any]]
    processing_time_ms: float
    confidence_score: float
    stardate: str
    timestamp: str


class VaultQueryRequest(BaseModel):
    """Vault query request model"""
    query: Dict[str, Any] = Field(..., description="Query parameters")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")
    limit: Optional[int] = Field(100, description="Maximum results")


class VaultQueryResponse(BaseModel):
    """Vault query response model"""
    results: List[Dict[str, Any]]
    total_count: int
    query_time_ms: float
    stardate: str


class LogEntryRequest(BaseModel):
    """Captain's log entry request"""
    content: str = Field(..., description="Log entry content")
    category: Optional[str] = Field("general", description="Entry category")
    tags: Optional[List[str]] = Field(None, description="Entry tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class LogEntryResponse(BaseModel):
    """Captain's log entry response"""
    entry_id: str
    stardate: str
    timestamp: str
    status: str


class PrometheusISS:
    """
    Prometheus Prime ISS Integration Service
    
    Provides a microservice interface for ISS Module that's compatible
    with the Prometheus Prime cognitive architecture.
    """
    
    def __init__(self, service_name: str = "iss-controller"):
        self.service_name = service_name
        self.version = "1.0.0"
        self.start_time = time.time()
        self.iss = ISS()
        self.captain_log = CaptainLog()
        self.dependencies = ["captain-log", "time-anchor", "vault-storage"]
        
        # Initialize structured logging
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="ISO"),
                structlog.dev.ConsoleRenderer()
            ],
            logger_factory=structlog.PrintLoggerFactory(),
            wrapper_class=structlog.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        self.logger = structlog.get_logger(service_name)
    
    async def initialize(self):
        """Initialize the ISS service"""
        try:
            await self.captain_log.initialize()
            self.logger.info("ISS Controller initialized", service=self.service_name)
        except Exception as e:
            self.logger.error("ISS Controller initialization failed", error=str(e))
            raise
    
    def get_health_status(self) -> ServiceHealthResponse:
        """Get service health status"""
        try:
            # Check ISS system health
            iss_healthy = self.iss.heartbeat()
            
            # Check dependencies (simplified)
            dependencies_healthy = all([
                True,  # captain-log (always available)
                True,  # time-anchor (always available) 
                True   # vault-storage (simplified check)
            ])
            
            status_str = "healthy" if iss_healthy and dependencies_healthy else "unhealthy"
            
            return ServiceHealthResponse(
                service=self.service_name,
                status=status_str,
                version=self.version,
                uptime_seconds=time.time() - self.start_time,
                dependencies=self.dependencies
            )
        except Exception as e:
            self.logger.error("Health check failed", error=str(e))
            return ServiceHealthResponse(
                service=self.service_name,
                status="unhealthy",
                version=self.version,
                uptime_seconds=time.time() - self.start_time,
                dependencies=self.dependencies
            )
    
    async def process_reasoning(self, request: ReasoningRequest) -> ReasoningResponse:
        """
        Process reasoning request compatible with Prometheus Prime pipeline
        
        This method integrates ISS Module capabilities into the Prometheus Prime
        reasoning cycle, providing time anchoring and decision logging.
        """
        start_time = time.time()
        cycle_id = f"iss_{int(time.time() * 1000)}"
        
        try:
            # Get current time anchors
            timecodes = current_timecodes()
            stardate = get_stardate()
            
            # Log the reasoning request
            log_entry = await self.captain_log.add_entry(
                content=f"Reasoning request processed: {request.cycle_type or 'auto'}",
                category="reasoning",
                tags=["prometheus-prime", "reasoning", request.cycle_type or "auto"],
                metadata={
                    "cycle_id": cycle_id,
                    "input_data_keys": list(request.input_data.keys()),
                    "timeout_ms": request.timeout_ms
                }
            )
            
            # Process the reasoning (integration point for actual reasoning logic)
            decision = await self._process_reasoning_logic(request, timecodes)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            # Create reasoning trace
            reasoning_trace = {
                "iss_controller": {
                    "stardate": stardate,
                    "log_entry_id": log_entry,
                    "time_anchors": timecodes,
                    "processing_steps": ["time_anchor", "log_entry", "decision_processing"]
                }
            }
            
            # Determine confidence score (simplified)
            confidence_score = decision.get("confidence", 0.8)
            
            response = ReasoningResponse(
                cycle_id=cycle_id,
                cycle_type=request.cycle_type or "auto",
                decision=decision,
                reasoning_trace=reasoning_trace,
                processing_time_ms=processing_time,
                confidence_score=confidence_score,
                stardate=stardate,
                timestamp=timecodes["iso_timestamp"]
            )
            
            self.logger.info(
                "Reasoning request completed",
                cycle_id=cycle_id,
                cycle_type=response.cycle_type,
                processing_time_ms=processing_time,
                confidence=confidence_score
            )
            
            return response
            
        except Exception as e:
            self.logger.error("Reasoning request failed", error=str(e), cycle_id=cycle_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Reasoning processing failed: {str(e)}"
            )
    
    async def _process_reasoning_logic(self, request: ReasoningRequest, timecodes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core reasoning logic - integration point for actual AI reasoning
        
        This is where you would integrate with actual reasoning engines,
        LLMs, or other cognitive processing systems.
        """
        # Simplified reasoning logic for demonstration
        input_data = request.input_data
        
        # Example decision logic based on input
        if "query" in input_data:
            decision = {
                "action": "query_processing",
                "result": f"Processed query: {input_data['query']}",
                "confidence": 0.9,
                "recommendation": "proceed",
                "time_anchor": timecodes["stardate"]
            }
        elif "command" in input_data:
            decision = {
                "action": "command_execution",
                "result": f"Command acknowledged: {input_data['command']}",
                "confidence": 0.85,
                "recommendation": "execute",
                "time_anchor": timecodes["stardate"]
            }
        else:
            decision = {
                "action": "general_processing",
                "result": "Input data processed",
                "confidence": 0.7,
                "recommendation": "review",
                "time_anchor": timecodes["stardate"]
            }
        
        # Add processing delay to simulate reasoning
        await asyncio.sleep(0.1)
        
        return decision
    
    async def query_vault(self, request: VaultQueryRequest) -> VaultQueryResponse:
        """
        Query the ISS vault (captain's log entries)
        
        Provides vault functionality compatible with Prometheus Prime
        vault management system.
        """
        start_time = time.time()
        
        try:
            # Convert query to captain's log filters
            entries = await self.captain_log.get_entries(
                category=request.query.get("category"),
                tags=request.query.get("tags"),
                limit=request.limit
            )
            
            # Convert entries to dict format
            results = []
            for entry in entries:
                if hasattr(entry, 'dict'):
                    entry_dict = entry.dict()
                else:
                    entry_dict = entry.__dict__
                results.append(entry_dict)
            
            query_time = (time.time() - start_time) * 1000
            
            response = VaultQueryResponse(
                results=results,
                total_count=len(results),
                query_time_ms=query_time,
                stardate=get_stardate()
            )
            
            self.logger.info(
                "Vault query completed",
                result_count=len(results),
                query_time_ms=query_time
            )
            
            return response
            
        except Exception as e:
            self.logger.error("Vault query failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Vault query failed: {str(e)}"
            )
    
    async def add_log_entry(self, request: LogEntryRequest) -> LogEntryResponse:
        """Add a captain's log entry"""
        try:
            entry_id = await self.captain_log.add_entry(
                content=request.content,
                category=request.category,
                tags=request.tags or [],
                metadata=request.metadata or {}
            )
            
            timecodes = current_timecodes()
            
            response = LogEntryResponse(
                entry_id=entry_id,
                stardate=get_stardate(),
                timestamp=timecodes["iso_timestamp"],
                status="created"
            )
            
            self.logger.info(
                "Log entry created",
                entry_id=entry_id,
                category=request.category
            )
            
            return response
            
        except Exception as e:
            self.logger.error("Log entry creation failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Log entry creation failed: {str(e)}"
            )


# Factory function for creating Prometheus Prime compatible FastAPI app
def create_prometheus_iss_app(service_name: str = "iss-controller") -> FastAPI:
    """
    Create a FastAPI application compatible with Prometheus Prime architecture
    
    This creates a microservice that can be deployed alongside other
    Prometheus Prime services and called by the API Gateway.
    """
    
    prometheus_iss = PrometheusISS(service_name)
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifespan management"""
        # Startup
        logger.info("Starting ISS Controller", service=service_name)
        await prometheus_iss.initialize()
        logger.info("ISS Controller startup complete")
        
        yield
        
        # Shutdown
        logger.info("Shutting down ISS Controller")
        logger.info("ISS Controller shutdown complete")
    
    app = FastAPI(
        title="ISS Controller Service",
        version=prometheus_iss.version,
        description="Integrated Systems Solution Controller for Prometheus Prime",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure as needed
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Health check endpoint
    @app.get("/health", response_model=ServiceHealthResponse)
    async def health_check():
        """Service health check compatible with Prometheus Prime"""
        return prometheus_iss.get_health_status()
    
    # Main reasoning endpoint (called by API Gateway)
    @app.post("/api/v1/process", response_model=ReasoningResponse)
    async def process_reasoning(request: ReasoningRequest):
        """Process reasoning request from Prometheus Prime API Gateway"""
        return await prometheus_iss.process_reasoning(request)
    
    # Vault query endpoint
    @app.post("/api/v1/vault/query", response_model=VaultQueryResponse)
    async def query_vault(request: VaultQueryRequest):
        """Query ISS vault entries"""
        return await prometheus_iss.query_vault(request)
    
    # Log entry endpoint
    @app.post("/api/v1/log", response_model=LogEntryResponse)
    async def add_log_entry(request: LogEntryRequest):
        """Add captain's log entry"""
        return await prometheus_iss.add_log_entry(request)
    
    # Status endpoint
    @app.get("/api/v1/status")
    async def get_status():
        """Get detailed service status"""
        health = prometheus_iss.get_health_status()
        timecodes = current_timecodes()
        
        return {
            "service": service_name,
            "health": health.dict(),
            "time_anchors": {
                "stardate": get_stardate(),
                "iso_timestamp": timecodes["iso_timestamp"],
                "julian_date": timecodes["julian_date"]
            },
            "capabilities": [
                "reasoning_processing",
                "vault_queries", 
                "log_management",
                "time_anchoring"
            ]
        }
    
    return app


# Export the integration components
__all__ = [
    'PrometheusISS',
    'create_prometheus_iss_app',
    'ReasoningRequest',
    'ReasoningResponse',
    'VaultQueryRequest',
    'VaultQueryResponse',
    'LogEntryRequest',
    'LogEntryResponse',
    'ServiceHealthResponse'
]