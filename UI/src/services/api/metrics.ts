import { apiRequest } from "./client";
import type { MetricsCompareResponse, MetricsSummary } from "../../types/api";

export function getMetricsSummary() {
  return apiRequest<MetricsSummary>("/metrics/summary");
}

export function getMetricsCompare(leftRunType = "rag", rightRunType = "base") {
  const params = new URLSearchParams({
    left_run_type: leftRunType,
    right_run_type: rightRunType,
  });
  return apiRequest<MetricsCompareResponse>(`/metrics/compare?${params.toString()}`);
}

