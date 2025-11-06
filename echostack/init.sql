-- EchoStack Database Initialization
-- PostgreSQL initialization script

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS echostack;
CREATE SCHEMA IF NOT EXISTS telemetry;
CREATE SCHEMA IF NOT EXISTS vault;

-- Create telemetry table
CREATE TABLE IF NOT EXISTS telemetry.system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metric_name VARCHAR(255) NOT NULL,
    metric_value NUMERIC,
    metric_type VARCHAR(50),
    tags JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create vault compliance table
CREATE TABLE IF NOT EXISTS vault.compliance_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vault_name VARCHAR(255) NOT NULL,
    check_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    compliance_level VARCHAR(50),
    issues JSONB DEFAULT '[]',
    score NUMERIC(3,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create alert history table
CREATE TABLE IF NOT EXISTS echostack.alert_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_id VARCHAR(255) NOT NULL,
    rule_name VARCHAR(255) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    message TEXT,
    state VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    details JSONB DEFAULT '{}'
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry.system_metrics (timestamp);
CREATE INDEX IF NOT EXISTS idx_telemetry_metric ON telemetry.system_metrics (metric_name);
CREATE INDEX IF NOT EXISTS idx_compliance_vault ON vault.compliance_checks (vault_name);
CREATE INDEX IF NOT EXISTS idx_compliance_timestamp ON vault.compliance_checks (check_timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_created ON echostack.alert_history (created_at);
CREATE INDEX IF NOT EXISTS idx_alerts_state ON echostack.alert_history (state);

-- Insert initial data
INSERT INTO telemetry.system_metrics (metric_name, metric_value, metric_type, tags)
VALUES
    ('system_health_score', 0.98, 'gauge', '{"component": "core"}'),
    ('active_cycles', 0, 'counter', '{"component": "reasoning"}'),
    ('cpu_usage_percent', 0.0, 'gauge', '{"component": "system"}'),
    ('memory_usage_mb', 0.0, 'gauge', '{"component": "system"}'),
    ('error_rate_percent', 0.0, 'gauge', '{"component": "system"}'),
    ('response_time_p50_ms', 0.0, 'gauge', '{"component": "api"}')
ON CONFLICT DO NOTHING;