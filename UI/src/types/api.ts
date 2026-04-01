export type RetrievedChunk = {
  score: number;
  text: string;
  metadata: {
    document_title?: string | null;
    section_title?: string | null;
    source_type?: string | null;
    [key: string]: unknown;
  };
};

export type RagQueryRequest = {
  question: string;
  k?: number;
};

export type RagQueryResponse = {
  answer: string;
  sources: RetrievedChunk[];
};

export type EvaluateRequest = {
  query: string;
  k?: number;
  run_type?: string;
  source_type?: string;
  relevant_chunk_ids?: string[];
  metadata?: Record<string, unknown>;
  notes?: string;
  evaluator_version?: string;
};

export type RetrievedDocument = {
  chunk_id: string;
  rank: number;
  score: number;
  text: string;
  metadata: Record<string, unknown>;
};

export type EvaluateResponse = {
  query_id: string;
  evaluation_id: string;
  query: string;
  answer: string;
  top_k: number;
  retrieved_documents: RetrievedDocument[];
  sources: RetrievedChunk[];
  metrics: {
    recall_at_k?: number | null;
    mrr?: number | null;
    hit_at_k?: number | null;
    ndcg_at_k?: number | null;
    faithfulness?: number | null;
    answer_relevance?: number | null;
    evaluator_version?: string | null;
  };
};

export type IngestStatusResponse = {
  ready: boolean;
  chunks_loaded: number;
  index_exists: boolean;
  processed_chunks_path: string;
  embeddings_path: string;
  faiss_index_path: string;
  manifest_path: string;
  llm_provider: string;
  llm_model: string;
};

export type IngestRebuildRequest = {
  source_paths?: string[];
};

export type IngestRebuildResponse = {
  ready: boolean;
  raw_records: number;
  parsed_documents: number;
  chunks: number;
  embedding_dimension: number;
  source_files: string[];
  processed_chunks_path: string;
  embeddings_path: string;
  faiss_index_path: string;
  manifest_path: string;
};

export type IngestUploadPolicyResponse = {
  uploaded_pdf_path: string;
  generated_json_path: string;
  generated_chunks: number;
};

export type MetricsSummary = {
  total_queries: number;
  avg_total_latency_ms: number;
  avg_retrieval_latency_ms: number;
  avg_generation_latency_ms: number;
  insufficient_context_rate: number;
  error_rate: number;
};

export type RunTypeMetrics = {
  run_type: string;
  samples: number;
  avg_score?: number | null;
  avg_recall_at_k?: number | null;
  avg_mrr?: number | null;
  avg_hit_at_k?: number | null;
  avg_ndcg_at_k?: number | null;
  avg_faithfulness?: number | null;
  avg_answer_relevance?: number | null;
  avg_total_latency_ms?: number | null;
};

export type MetricsCompareResponse = {
  left: RunTypeMetrics;
  right: RunTypeMetrics;
};

export type EvaluationRun = {
  id: string;
  name?: string;
  created_at?: string;
  status?: string;
  score?: number;
  run_type?: string | null;
  recall_at_k?: number | null;
  mrr?: number | null;
  hit_at_k?: number | null;
  ndcg_at_k?: number | null;
  faithfulness?: number | null;
  answer_relevance?: number | null;
};
