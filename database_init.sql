-- Database initialization for Unified Cognition Module
-- Create tables for learning and cognitive data storage

CREATE TABLE IF NOT EXISTS learning_history (
    id SERIAL PRIMARY KEY,
    input_pattern TEXT NOT NULL,
    module_responses JSONB,
    final_decision TEXT,
    outcome_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_learning_input ON learning_history(input_pattern);
CREATE INDEX IF NOT EXISTS idx_learning_created ON learning_history(created_at);

-- Table for storing cognitive patterns
CREATE TABLE IF NOT EXISTS cognitive_patterns (
    id SERIAL PRIMARY KEY,
    pattern_key VARCHAR(255) UNIQUE NOT NULL,
    pattern_data JSONB,
    confidence_score FLOAT DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for pattern lookup
CREATE INDEX IF NOT EXISTS idx_patterns_key ON cognitive_patterns(pattern_key);