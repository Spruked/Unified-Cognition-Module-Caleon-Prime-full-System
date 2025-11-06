"""
Structured Logging for ISS Module
=================================

Provides structured logging capabilities compatible with Prometheus Prime
microservices logging infrastructure.

Features:
- JSON formatted logs for production
- Console formatted logs for development  
- Correlation IDs for request tracing
- Performance metrics logging
- Error tracking with context
- Log aggregation compatibility
"""

import logging
import time
import uuid
from typing import Dict, Any, Optional
from contextvars import ContextVar
from functools import wraps

import structlog
from structlog.typing import EventDict


# Context variables for request correlation
correlation_id_ctx: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
request_id_ctx: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_ctx: ContextVar[Optional[str]] = ContextVar('user_id', default=None)


def add_correlation_id(logger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add correlation ID to log entries"""
    correlation_id = correlation_id_ctx.get()
    if correlation_id:
        event_dict["correlation_id"] = correlation_id
    
    request_id = request_id_ctx.get()
    if request_id:
        event_dict["request_id"] = request_id
    
    user_id = user_id_ctx.get()
    if user_id:
        event_dict["user_id"] = user_id
    
    return event_dict


def add_service_context(logger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add service context to log entries"""
    event_dict.setdefault("service", "iss-controller")
    event_dict.setdefault("component", "iss-module")
    return event_dict


def add_timestamp_processor(logger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add high-precision timestamp"""
    event_dict["timestamp"] = time.time()
    return event_dict


def configure_structured_logging(
    service_name: str = "iss-controller",
    log_level: str = "INFO",
    format_type: str = "json",
    enable_console: bool = True
):
    """
    Configure structured logging for ISS Module
    
    Args:
        service_name: Name of the service for log context
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        format_type: Output format ('json' or 'console')
        enable_console: Whether to enable console output
    """
    
    # Base processors
    processors = [
        structlog.processors.add_log_level,
        add_correlation_id,
        add_service_context,
        add_timestamp_processor,
        structlog.processors.TimeStamper(fmt="ISO"),
    ]
    
    # Add format-specific processors
    if format_type == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.extend([
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer(colors=enable_console)
        ])
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory() if enable_console else structlog.WriteLoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s" if format_type == "json" else "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


class ISSLogger:
    """
    Enhanced logger for ISS Module with Prometheus Prime compatibility
    
    Provides structured logging with context management, performance tracking,
    and error handling capabilities.
    """
    
    def __init__(self, name: str):
        self.logger = structlog.get_logger(name)
        self.name = name
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context"""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with context"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message with exception context"""
        if error:
            kwargs.update({
                "error_type": type(error).__name__,
                "error_message": str(error),
                "error_details": getattr(error, '__dict__', {})
            })
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with context"""
        self.logger.critical(message, **kwargs)
    
    def log_request(self, method: str, path: str, **kwargs):
        """Log HTTP request"""
        self.info(
            "HTTP request received",
            http_method=method,
            http_path=path,
            **kwargs
        )
    
    def log_response(self, status_code: int, processing_time_ms: float, **kwargs):
        """Log HTTP response"""
        self.info(
            "HTTP response sent",
            http_status=status_code,
            processing_time_ms=processing_time_ms,
            **kwargs
        )
    
    def log_reasoning_start(self, cycle_id: str, cycle_type: str, **kwargs):
        """Log reasoning cycle start"""
        self.info(
            "Reasoning cycle started",
            cycle_id=cycle_id,
            cycle_type=cycle_type,
            stage="start",
            **kwargs
        )
    
    def log_reasoning_complete(self, cycle_id: str, processing_time_ms: float, confidence: float, **kwargs):
        """Log reasoning cycle completion"""
        self.info(
            "Reasoning cycle completed",
            cycle_id=cycle_id,
            processing_time_ms=processing_time_ms,
            confidence_score=confidence,
            stage="complete",
            **kwargs
        )
    
    def log_vault_query(self, query_type: str, result_count: int, query_time_ms: float, **kwargs):
        """Log vault query operation"""
        self.info(
            "Vault query executed",
            query_type=query_type,
            result_count=result_count,
            query_time_ms=query_time_ms,
            **kwargs
        )
    
    def log_captain_log_entry(self, entry_id: str, category: str, **kwargs):
        """Log captain's log entry creation"""
        self.info(
            "Captain's log entry created",
            entry_id=entry_id,
            category=category,
            **kwargs
        )
    
    def log_performance_metric(self, operation: str, duration_ms: float, **kwargs):
        """Log performance metrics"""
        self.info(
            "Performance metric",
            operation=operation,
            duration_ms=duration_ms,
            metric_type="performance",
            **kwargs
        )
    
    def log_health_check(self, status: str, dependencies: list, **kwargs):
        """Log health check results"""
        self.info(
            "Health check performed",
            health_status=status,
            dependencies=dependencies,
            **kwargs
        )


def get_logger(name: str) -> ISSLogger:
    """Get an ISS logger instance"""
    return ISSLogger(name)


def set_correlation_id(correlation_id: str):
    """Set correlation ID for current context"""
    correlation_id_ctx.set(correlation_id)


def set_request_id(request_id: str):
    """Set request ID for current context"""
    request_id_ctx.set(request_id)


def set_user_id(user_id: str):
    """Set user ID for current context"""
    user_id_ctx.set(user_id)


def generate_correlation_id() -> str:
    """Generate a new correlation ID"""
    return str(uuid.uuid4())


def log_execution_time(operation_name: str):
    """
    Decorator to log execution time of functions
    
    Usage:
        @log_execution_time("reasoning_process")
        def process_reasoning(data):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_logger(f"{func.__module__}.{func.__name__}")
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                logger.log_performance_metric(
                    operation=operation_name,
                    duration_ms=execution_time,
                    status="success"
                )
                
                return result
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                
                logger.error(
                    f"Operation {operation_name} failed",
                    error=e,
                    duration_ms=execution_time,
                    status="error"
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_logger(f"{func.__module__}.{func.__name__}")
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                logger.log_performance_metric(
                    operation=operation_name,
                    duration_ms=execution_time,
                    status="success"
                )
                
                return result
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                
                logger.error(
                    f"Operation {operation_name} failed",
                    error=e,
                    duration_ms=execution_time,
                    status="error"
                )
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class LogContext:
    """
    Context manager for scoped logging context
    
    Usage:
        with LogContext(correlation_id="abc-123", user_id="user1"):
            logger.info("This will include correlation_id and user_id")
    """
    
    def __init__(self, correlation_id: str = None, request_id: str = None, user_id: str = None):
        self.correlation_id = correlation_id or generate_correlation_id()
        self.request_id = request_id
        self.user_id = user_id
        
        self.old_correlation_id = None
        self.old_request_id = None
        self.old_user_id = None
    
    def __enter__(self):
        # Save old values
        self.old_correlation_id = correlation_id_ctx.get()
        self.old_request_id = request_id_ctx.get()
        self.old_user_id = user_id_ctx.get()
        
        # Set new values
        if self.correlation_id:
            set_correlation_id(self.correlation_id)
        if self.request_id:
            set_request_id(self.request_id)
        if self.user_id:
            set_user_id(self.user_id)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore old values
        if self.old_correlation_id:
            correlation_id_ctx.set(self.old_correlation_id)
        if self.old_request_id:
            request_id_ctx.set(self.old_request_id)
        if self.old_user_id:
            user_id_ctx.set(self.old_user_id)


# Export public interface
__all__ = [
    'configure_structured_logging',
    'ISSLogger',
    'get_logger',
    'set_correlation_id',
    'set_request_id',
    'set_user_id',
    'generate_correlation_id',
    'log_execution_time',
    'LogContext'
]