-- Simplified database initialization for PostgreSQL
-- No TimescaleDB extensions needed

-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: Tables will be created by the Flask application on startup
-- Indexes will be created after tables exist

-- Optional: Create partition for large datasets (can be added later)
-- This is much simpler than TimescaleDB hypertables
-- Example for future partitioning:
-- CREATE TABLE inference_request_y2024 PARTITION OF "InferenceRequest" 
-- FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- Basic cleanup job can be added as a cron job instead of TimescaleDB retention policy
-- Example cleanup (to be run periodically):
-- DELETE FROM "LogEntry" WHERE timestamp < NOW() - INTERVAL '30 days';