import { useQuery } from "@tanstack/react-query";

import { EmptyState } from "../components/common/EmptyState";
import { ErrorNotice } from "../components/common/ErrorNotice";
import { LoadingState } from "../components/common/LoadingState";
import { EvaluationCharts } from "../features/evaluation/components/EvaluationCharts";
import { MetricCard } from "../features/metrics/components/MetricCard";
import { getEvaluationRuns } from "../services/api/evaluations";
import { getMetricsCompare, getMetricsSummary } from "../services/api/metrics";
import type { RunTypeMetrics } from "../types/api";

function formatMetric(value: number | null | undefined, digits = 3) {
  return typeof value === "number" ? value.toFixed(digits) : "-";
}

function CompareBlock({ label, left, right }: { label: string; left: number | null | undefined; right: number | null | undefined }) {
  const delta = typeof left === "number" && typeof right === "number" ? left - right : null;
  const deltaText = delta === null ? "-" : `${delta >= 0 ? "+" : ""}${delta.toFixed(3)}`;

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-sm text-slate-700">RAG: {formatMetric(left)}</p>
      <p className="text-sm text-slate-700">Base: {formatMetric(right)}</p>
      <p className="mt-1 text-xs text-slate-500">Delta: {deltaText}</p>
    </div>
  );
}

function ComparisonPanel({ left, right }: { left: RunTypeMetrics; right: RunTypeMetrics }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <div className="mb-3 flex items-center justify-between">
        <p className="text-sm font-semibold text-slate-900">Comparación RAG vs Base</p>
        <p className="text-xs text-slate-600">
          muestras: {left.samples} vs {right.samples}
        </p>
      </div>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <CompareBlock label="Score promedio" left={left.avg_score} right={right.avg_score} />
        <CompareBlock label="Recall@k" left={left.avg_recall_at_k} right={right.avg_recall_at_k} />
        <CompareBlock label="MRR" left={left.avg_mrr} right={right.avg_mrr} />
        <CompareBlock label="Hit@k" left={left.avg_hit_at_k} right={right.avg_hit_at_k} />
        <CompareBlock label="nDCG@k" left={left.avg_ndcg_at_k} right={right.avg_ndcg_at_k} />
        <CompareBlock label="Faithfulness" left={left.avg_faithfulness} right={right.avg_faithfulness} />
        <CompareBlock label="Answer Relevance" left={left.avg_answer_relevance} right={right.avg_answer_relevance} />
        <CompareBlock label="Latencia total (ms)" left={left.avg_total_latency_ms} right={right.avg_total_latency_ms} />
      </div>
    </div>
  );
}

export function MetricsPage() {
  const metricsQuery = useQuery({
    queryKey: ["metrics-summary"],
    queryFn: getMetricsSummary,
    retry: false,
  });
  const compareQuery = useQuery({
    queryKey: ["metrics-compare", "rag", "base"],
    queryFn: () => getMetricsCompare("rag", "base"),
    retry: false,
  });
  const evaluationsQuery = useQuery({
    queryKey: ["evaluation-runs"],
    queryFn: getEvaluationRuns,
    retry: false,
  });

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Métricas y observabilidad</h1>
        <p className="mt-1 text-sm text-slate-500">Vista ejecutiva y técnica de latencia, calidad y estabilidad del sistema.</p>
      </div>

      {metricsQuery.isPending ? <LoadingState message="Consultando métricas..." /> : null}
      {metricsQuery.error instanceof Error ? <ErrorNotice message={metricsQuery.error.message} /> : null}
      {compareQuery.error instanceof Error ? <ErrorNotice message={compareQuery.error.message} /> : null}

      {metricsQuery.data ? (
        <>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <MetricCard label="Consultas totales" value={String(metricsQuery.data.total_queries)} />
            <MetricCard label="Latencia total promedio" value={metricsQuery.data.avg_total_latency_ms.toFixed(1)} suffix="ms" />
            <MetricCard label="Latencia retrieval promedio" value={metricsQuery.data.avg_retrieval_latency_ms.toFixed(1)} suffix="ms" />
            <MetricCard label="Latencia generación promedio" value={metricsQuery.data.avg_generation_latency_ms.toFixed(1)} suffix="ms" />
            <MetricCard label="Tasa de contexto insuficiente" value={(metricsQuery.data.insufficient_context_rate * 100).toFixed(1)} suffix="%" />
            <MetricCard label="Tasa de error" value={(metricsQuery.data.error_rate * 100).toFixed(1)} suffix="%" />
          </div>
          {compareQuery.data ? <ComparisonPanel left={compareQuery.data.left} right={compareQuery.data.right} /> : null}
          {evaluationsQuery.data && evaluationsQuery.data.length > 0 ? (
            <EvaluationCharts runs={evaluationsQuery.data} />
          ) : null}
        </>
      ) : !metricsQuery.isPending ? (
        <EmptyState
          title="Endpoint de métricas no disponible"
          description="La UI está lista. Conecta el endpoint backend (ej. /metrics/summary) para poblar esta vista."
        />
      ) : null}
    </section>
  );
}

