-- SQL Queue Table for Claude Code Integration
-- Stores requests for natural language to SQL processing

CREATE TABLE IF NOT EXISTS sql_queue (
    -- Identity
    id SERIAL PRIMARY KEY,
    job_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),

    -- Request metadata
    environment VARCHAR(20) NOT NULL CHECK (environment IN ('devtest', 'prod')),
    language VARCHAR(5) NOT NULL CHECK (language IN ('en', 'he')),
    user_id VARCHAR(100),

    -- Input
    question TEXT NOT NULL,
    schema_info JSONB NOT NULL,

    -- Processing status
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'executed', 'completed', 'failed')),

    -- SQL Generation
    sql_query TEXT,
    query_type VARCHAR(20) CHECK (query_type IN ('READ', 'WRITE_SAFE', 'WRITE_RISKY', 'ADMIN')),
    risk_level VARCHAR(20) CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    execution_allowed BOOLEAN DEFAULT false,

    -- Execution Results
    query_results JSONB,
    rows_affected INTEGER,
    execution_time_ms INTEGER,

    -- Natural Language Response
    natural_language_response TEXT,

    -- Error handling
    error_message TEXT,
    error_type VARCHAR(50),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sql_generated_at TIMESTAMP,
    executed_at TIMESTAMP,
    completed_at TIMESTAMP,

    -- Performance tracking
    total_processing_time_ms INTEGER
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_sql_queue_status ON sql_queue(status);
CREATE INDEX IF NOT EXISTS idx_sql_queue_job_id ON sql_queue(job_id);
CREATE INDEX IF NOT EXISTS idx_sql_queue_created ON sql_queue(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sql_queue_environment ON sql_queue(environment);
CREATE INDEX IF NOT EXISTS idx_sql_queue_user ON sql_queue(user_id);

-- View for pending queries (what Claude Code needs to process)
CREATE OR REPLACE VIEW pending_queries AS
SELECT
    job_id,
    question,
    schema_info,
    environment,
    language,
    created_at,
    EXTRACT(EPOCH FROM (NOW() - created_at)) as age_seconds
FROM sql_queue
WHERE status = 'pending'
ORDER BY created_at ASC;

-- View for monitoring
CREATE OR REPLACE VIEW queue_stats AS
SELECT
    environment,
    status,
    COUNT(*) as count,
    AVG(total_processing_time_ms) as avg_processing_ms,
    MAX(created_at) as last_request
FROM sql_queue
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY environment, status;

-- Audit Log Table
CREATE TABLE IF NOT EXISTS sql_audit_log (
    id SERIAL PRIMARY KEY,
    job_id UUID REFERENCES sql_queue(job_id),
    event_type VARCHAR(50) NOT NULL,  -- 'submitted', 'generated', 'executed', 'blocked', 'completed', 'failed'
    event_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_job_id ON sql_audit_log(job_id);
CREATE INDEX IF NOT EXISTS idx_audit_event_type ON sql_audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_created ON sql_audit_log(created_at DESC);

-- Function to log audit events
CREATE OR REPLACE FUNCTION log_audit_event(
    p_job_id UUID,
    p_event_type VARCHAR,
    p_event_data JSONB DEFAULT '{}'
)
RETURNS void AS $$
BEGIN
    INSERT INTO sql_audit_log (job_id, event_type, event_data)
    VALUES (p_job_id, p_event_type, p_event_data);
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically create audit entries
CREATE OR REPLACE FUNCTION sql_queue_audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        PERFORM log_audit_event(NEW.job_id, 'submitted',
            jsonb_build_object('question', NEW.question, 'environment', NEW.environment));
    ELSIF TG_OP = 'UPDATE' THEN
        IF OLD.status != NEW.status THEN
            PERFORM log_audit_event(NEW.job_id, NEW.status,
                jsonb_build_object('old_status', OLD.status, 'new_status', NEW.status));
        END IF;

        IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
            PERFORM log_audit_event(NEW.job_id, 'completed',
                jsonb_build_object(
                    'query_type', NEW.query_type,
                    'execution_allowed', NEW.execution_allowed,
                    'processing_time_ms', NEW.total_processing_time_ms
                ));
        END IF;

        IF NEW.execution_allowed = false AND OLD.execution_allowed IS NULL THEN
            PERFORM log_audit_event(NEW.job_id, 'blocked',
                jsonb_build_object(
                    'query_type', NEW.query_type,
                    'environment', NEW.environment,
                    'reason', 'Query type not allowed in this environment'
                ));
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sql_queue_audit
AFTER INSERT OR UPDATE ON sql_queue
FOR EACH ROW EXECUTE FUNCTION sql_queue_audit_trigger();

-- Clean up old completed requests (optional housekeeping)
CREATE OR REPLACE FUNCTION cleanup_old_requests()
RETURNS void AS $$
BEGIN
    DELETE FROM sql_queue
    WHERE status IN ('completed', 'failed')
    AND completed_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust based on your setup)
-- GRANT SELECT, INSERT, UPDATE ON sql_queue TO your_app_user;
-- GRANT SELECT ON pending_queries, queue_stats TO your_app_user;
-- GRANT SELECT, INSERT ON sql_audit_log TO your_app_user;

-- Sample queries for monitoring

-- Check queue health
/*
SELECT * FROM queue_stats ORDER BY environment, status;
*/

-- Find stuck queries
/*
SELECT job_id, question, environment, status,
       EXTRACT(EPOCH FROM (NOW() - created_at))/60 as minutes_old
FROM sql_queue
WHERE status = 'processing'
  AND sql_generated_at < NOW() - INTERVAL '10 minutes';
*/

-- Recent audit events
/*
SELECT
    a.created_at,
    a.event_type,
    q.question,
    q.environment,
    a.event_data
FROM sql_audit_log a
JOIN sql_queue q ON a.job_id = q.job_id
ORDER BY a.created_at DESC
LIMIT 20;
*/

-- Security violations (blocked queries)
/*
SELECT
    q.created_at,
    q.environment,
    q.question,
    q.query_type,
    q.sql_query,
    q.user_id
FROM sql_queue q
WHERE q.execution_allowed = false
  AND q.created_at > NOW() - INTERVAL '7 days'
ORDER BY q.created_at DESC;
*/
