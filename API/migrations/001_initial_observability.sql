CREATE TABLE IF NOT EXISTS rag_queries (
    id VARCHAR(36) PRIMARY KEY,
    query_text TEXT NOT NULL,
    answer_text TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    run_type VARCHAR(50) NULL,
    source_type VARCHAR(50) NULL,
    top_k INTEGER NOT NULL DEFAULT 5,
    total_latency_ms DOUBLE PRECISION NULL,
    retrieval_latency_ms DOUBLE PRECISION NULL,
    generation_latency_ms DOUBLE PRECISION NULL,
    insufficient_context BOOLEAN NOT NULL DEFAULT FALSE,
    had_error BOOLEAN NOT NULL DEFAULT FALSE,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS ix_rag_queries_created_at ON rag_queries (created_at);
CREATE INDEX IF NOT EXISTS ix_rag_queries_run_type ON rag_queries (run_type);

CREATE TABLE IF NOT EXISTS rag_retrievals (
    id VARCHAR(36) PRIMARY KEY,
    query_id VARCHAR(36) NOT NULL REFERENCES rag_queries(id) ON DELETE CASCADE,
    chunk_id VARCHAR(128) NOT NULL,
    retrieved_text TEXT NULL,
    similarity_score DOUBLE PRECISION NOT NULL,
    rank INTEGER NOT NULL,
    source_file VARCHAR(500) NULL,
    source_type VARCHAR(100) NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS ix_rag_retrievals_query_id ON rag_retrievals (query_id);
CREATE INDEX IF NOT EXISTS ix_rag_retrievals_chunk_id ON rag_retrievals (chunk_id);

CREATE TABLE IF NOT EXISTS rag_evaluations (
    id VARCHAR(36) PRIMARY KEY,
    query_id VARCHAR(36) NOT NULL REFERENCES rag_queries(id) ON DELETE CASCADE,
    recall_at_k DOUBLE PRECISION NULL,
    mrr DOUBLE PRECISION NULL,
    hit_at_k DOUBLE PRECISION NULL,
    ndcg_at_k DOUBLE PRECISION NULL,
    faithfulness DOUBLE PRECISION NULL,
    answer_relevance DOUBLE PRECISION NULL,
    evaluation_timestamp TIMESTAMPTZ NOT NULL,
    evaluator_version VARCHAR(120) NULL,
    notes TEXT NULL
);

CREATE INDEX IF NOT EXISTS ix_rag_evaluations_query_id ON rag_evaluations (query_id);
CREATE INDEX IF NOT EXISTS ix_rag_evaluations_timestamp ON rag_evaluations (evaluation_timestamp);
