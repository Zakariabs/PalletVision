SELECT create_hypertable('public.LogEntry', 'timestamp');
SELECT create_hypertable('public.InferenceRequest', 'timestamp');
SELECT add_retention_policy('public.LogEntry', INTERVAL '30 days');

ALTER TABLE "InferenceRequest" ADD COLUMN IF NOT EXISTS model_version VARCHAR(64);
ALTER TABLE "InferenceRequest" ADD COLUMN IF NOT EXISTS flagged_for_review BOOLEAN NOT NULL DEFAULT FALSE;
