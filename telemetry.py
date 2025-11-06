"""
Production telemetry and monitoring setup
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastAPIIntegration
from prometheus_client import Counter, Histogram, Gauge
from config import settings

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

CONSENT_DECISIONS = Counter(
    'consent_decisions_total',
    'Total consent decisions',
    ['decision', 'mode']
)

COGNITION_CYCLES = Counter(
    'cognition_cycles_total',
    'Total cognition cycles completed'
)

def setup_monitoring():
    """Initialize monitoring and error tracking"""
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            integrations=[FastAPIIntegration()],
            environment=settings.environment,
            traces_sample_rate=1.0 if settings.environment == "production" else 0.1,
        )

    if settings.prometheus_metrics:
        # Additional setup if needed
        pass