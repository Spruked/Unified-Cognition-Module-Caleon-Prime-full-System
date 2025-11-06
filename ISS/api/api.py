"""
FastAPI backend for ISS Module
Provides REST API endpoints for web interface and external integrations

Usage:
    uvicorn iss_module.api.api:app --reload
    
Dashboard auto-served at /dashboard
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging
import os
import asyncio
from pathlib import Path as PathLib

# Import ISS Module components
from ..core.ISS import ISS  # Changed from get_iss_instance to ISS
from ..core.utils import get_stardate, format_timestamp
from ..captain_mode.captain_log import CaptainLog, LogEntry
from ..captain_mode.exporters import DataExporter


# Pydantic models for API
class LogEntryCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    category: str = Field(default="personal", max_length=50)
    tags: Optional[List[str]] = Field(default_factory=list)
    mood: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=100)


class LogEntryUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    tags: Optional[List[str]] = None
    mood: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=100)


class LogEntryResponse(BaseModel):
    id: str
    timestamp: str
    stardate: float
    content: str
    category: str
    tags: List[str]
    mood: Optional[str]
    location: Optional[str]
    attachments: Optional[List[str]]


class SystemStatusResponse(BaseModel):
    status: str
    uptime: Optional[str]
    active_modules: List[str]
    current_time: str
    stardate: float
    total_log_entries: int


class ExportRequest(BaseModel):
    format: str = Field(..., pattern="^(json|csv|markdown)$")
    include_metadata: bool = True
    category_filter: Optional[str] = None
    tag_filter: Optional[List[str]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


# Initialize FastAPI app
app = FastAPI(
    title="ISS Module API",
    description="Integrated Starship Systems Module API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Security
security = HTTPBearer(auto_error=False)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
iss_instance = None
captain_log = None
data_exporter = None
logger = logging.getLogger('ISS.API')

# Templates and static files
templates_dir = PathLib(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@app.on_event("startup")
async def startup_event():
    """Initialize the ISS system and components"""
    global iss_instance, captain_log, data_exporter
    
    try:
        # Initialize ISS
        iss_instance = ISS()  # Removed await iss_instance.initialize()
        
        # Initialize Captain's Log
        captain_log = CaptainLog()
        await captain_log.initialize()
        
        # Initialize Data Exporter
        data_exporter = DataExporter()
        
        logger.info("ISS Module API started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start ISS Module API: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global iss_instance
    
    if iss_instance:
        await iss_instance.shutdown()
    
    logger.info("ISS Module API shutdown complete")


# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simple bearer token authentication (implement proper auth as needed)"""
    # For now, just check if token exists
    # In production, implement proper JWT validation
    if credentials is None:
        # Allow unauthenticated access for demo purposes
        return None
    return {"user": "authenticated"}


# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


# Dashboard endpoint (alias)
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the dashboard at /dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


# System endpoints
@app.get("/api/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get current system status"""
    try:
        status = iss_instance.get_status()
        
        # Get log entry count
        total_entries = len(captain_log.entries) if captain_log else 0
        
        # Calculate uptime
        startup_time = status['system_state'].get('startup_time')
        uptime = None
        if startup_time:
            delta = datetime.now(timezone.utc) - datetime.fromisoformat(startup_time)
            uptime = str(delta).split('.')[0]  # Remove microseconds
        
        return SystemStatusResponse(
            status=status['system_state']['system_status'],
            uptime=uptime,
            active_modules=status['system_state']['active_modules'],
            current_time=status['current_time'],
            stardate=status['stardate'],
            total_log_entries=total_entries
        )
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system status")


@app.get("/api/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": format_timestamp(),
        "stardate": get_stardate()
    }


# Captain's Log endpoints
@app.post("/api/log/entries", response_model=LogEntryResponse)
async def create_log_entry(
    entry_data: LogEntryCreate,
    current_user=Depends(get_current_user)
):
    """Create a new log entry"""
    try:
        entry = await captain_log.create_entry(
            content=entry_data.content,
            category=entry_data.category,
            tags=entry_data.tags,
            mood=entry_data.mood,
            location=entry_data.location
        )
        
        return LogEntryResponse(**entry.to_dict())
        
    except Exception as e:
        logger.error(f"Failed to create log entry: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/log/entries", response_model=List[LogEntryResponse])
async def get_log_entries(
    category: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: Optional[int] = Query(50, le=1000),
    current_user=Depends(get_current_user)
):
    """Get log entries with optional filtering"""
    try:
        # Parse dates if provided
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        entries = await captain_log.get_entries(
            category=category,
            tags=tags,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit
        )
        
        return [LogEntryResponse(**entry.to_dict()) for entry in entries]
        
    except Exception as e:
        logger.error(f"Failed to get log entries: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/log/entries/{entry_id}", response_model=LogEntryResponse)
async def get_log_entry(
    entry_id: str = Path(...),
    current_user=Depends(get_current_user)
):
    """Get a specific log entry by ID"""
    try:
        entry = await captain_log.get_entry_by_id(entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Log entry not found")
        
        return LogEntryResponse(**entry.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get log entry {entry_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put("/api/log/entries/{entry_id}", response_model=LogEntryResponse)
async def update_log_entry(
    entry_id: str = Path(...),
    update_data: LogEntryUpdate = Body(...),
    current_user=Depends(get_current_user)
):
    """Update a log entry"""
    try:
        success = await captain_log.update_entry(
            entry_id=entry_id,
            content=update_data.content,
            tags=update_data.tags,
            mood=update_data.mood,
            location=update_data.location
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Log entry not found")
        
        # Return updated entry
        entry = await captain_log.get_entry_by_id(entry_id)
        return LogEntryResponse(**entry.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update log entry {entry_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/log/entries/{entry_id}")
async def delete_log_entry(
    entry_id: str = Path(...),
    current_user=Depends(get_current_user)
):
    """Delete a log entry"""
    try:
        success = await captain_log.delete_entry(entry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Log entry not found")
        
        return {"message": "Log entry deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete log entry {entry_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/log/search")
async def search_log_entries(
    q: str = Query(..., min_length=1),
    current_user=Depends(get_current_user)
):
    """Search log entries"""
    try:
        entries = await captain_log.search_entries(q)
        return [LogEntryResponse(**entry.to_dict()) for entry in entries]
        
    except Exception as e:
        logger.error(f"Failed to search log entries: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/log/statistics")
async def get_log_statistics(current_user=Depends(get_current_user)):
    """Get log statistics"""
    try:
        stats = await captain_log.get_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get log statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Export endpoints
@app.post("/api/export")
async def export_data(
    export_request: ExportRequest,
    current_user=Depends(get_current_user)
):
    """Export log data in various formats"""
    try:
        # Get filtered entries
        start_dt = None
        end_dt = None
        
        if export_request.start_date:
            start_dt = datetime.fromisoformat(export_request.start_date)
        if export_request.end_date:
            end_dt = datetime.fromisoformat(export_request.end_date)
        
        entries = await captain_log.get_entries(
            category=export_request.category_filter,
            tags=export_request.tag_filter,
            start_date=start_dt,
            end_date=end_dt
        )
        
        # Export in requested format
        if export_request.format == "json":
            filepath = await data_exporter.export_log_entries_json(
                entries,
                include_metadata=export_request.include_metadata
            )
        elif export_request.format == "csv":
            filepath = await data_exporter.export_log_entries_csv(
                entries,
                include_content=True
            )
        elif export_request.format == "markdown":
            filepath = await data_exporter.export_log_entries_markdown(
                entries,
                include_toc=True
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
        
        # Return file
        filename = os.path.basename(filepath)
        return FileResponse(
            filepath,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export data: {e}")
        raise HTTPException(status_code=500, detail="Export failed")


@app.post("/api/backup")
async def create_backup(current_user=Depends(get_current_user)):
    """Create a complete backup of all data"""
    try:
        backup_dir = await data_exporter.create_backup(captain_log)
        
        # Create a zip file of the backup directory
        import zipfile
        import tempfile
        
        zip_fd, zip_path = tempfile.mkstemp(suffix='.zip')
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(backup_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, backup_dir)
                        zipf.write(file_path, arc_name)
            
            return FileResponse(
                zip_path,
                filename=f"iss_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                media_type='application/zip'
            )
            
        finally:
            os.close(zip_fd)
            
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise HTTPException(status_code=500, detail="Backup failed")


# Utility endpoints
@app.get("/api/stardate")
async def get_current_stardate():
    """Get current stardate"""
    return {
        "stardate": get_stardate(),
        "timestamp": format_timestamp(),
        "format": "TNG Era"
    }


@app.get("/api/time")
async def get_current_time():
    """Get current time in various formats"""
    return {
        "iso": format_timestamp(format_type='iso'),
        "stardate": format_timestamp(format_type='stardate'),
        "julian": format_timestamp(format_type='julian'),
        "human": format_timestamp(format_type='human')
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Not found", "detail": "The requested resource was not found"}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": "An unexpected error occurred"}


# Development helper
def main():
    """Main entry point for running the server"""
    import uvicorn
    uvicorn.run(
        "iss_module.api.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()