
-- PostgreSQL Database Schema for CloudGuard AI
-- Cloud Guard AI Security Scanner Database Schema

-- Findings table (main security issues)
CREATE TABLE IF NOT EXISTS findings (
    id SERIAL PRIMARY KEY,
    finding_id VARCHAR(255) UNIQUE NOT NULL,
    resource_type VARCHAR(50),
    finding_type VARCHAR(50),
    severity VARCHAR(20),
    risk_score FLOAT,
    estimated_cost INT,
    description TEXT,
    recommendation TEXT,
    resource_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_resolved BOOLEAN DEFAULT FALSE
);

-- ML Predictions table
CREATE TABLE IF NOT EXISTS ml_predictions (
    id SERIAL PRIMARY KEY,
    finding_id VARCHAR(255) UNIQUE,
    predicted_severity VARCHAR(20),
    predicted_risk_score FLOAT,
    predicted_cost INT,
    model_version VARCHAR(20),
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (finding_id) REFERENCES findings(finding_id) ON DELETE CASCADE
);

-- Scan history table
CREATE TABLE IF NOT EXISTS scan_history (
    id SERIAL PRIMARY KEY,
    scan_id VARCHAR(255) UNIQUE NOT NULL,
    total_findings INT,
    critical_count INT,
    high_count INT,
    medium_count INT,
    low_count INT,
    scan_duration_seconds FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity);
CREATE INDEX IF NOT EXISTS idx_findings_created_at ON findings(created_at);
CREATE INDEX IF NOT EXISTS idx_findings_resource_type ON findings(resource_type);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_finding_id ON ml_predictions(finding_id);
CREATE INDEX IF NOT EXISTS idx_scan_history_created_at ON scan_history(created_at);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;