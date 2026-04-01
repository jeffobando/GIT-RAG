import { apiRequest } from "./client";
import type { EvaluationRun } from "../../types/api";

// Backend endpoint may not exist yet.
export function getEvaluationRuns() {
  return apiRequest<EvaluationRun[]>("/evaluations/runs");
}
