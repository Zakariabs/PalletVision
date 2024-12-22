SELECT create_hypertable('public.LogEntry', 'timestamp');
SELECT create_hypertable('public.InferenceRequest', 'timestamp');
SELECT add_retention_policy('public.LogEntry', INTERVAL '30 days');