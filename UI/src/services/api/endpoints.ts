import { apiRequest } from "./client";
import type {
  EvaluateRequest,
  EvaluateResponse,
  IngestRebuildRequest,
  IngestRebuildResponse,
  IngestStatusResponse,
  IngestUploadPolicyResponse,
  RagQueryRequest,
  RagQueryResponse,
} from "../../types/api";

export function postRagQuery(payload: RagQueryRequest) {
  return apiRequest<RagQueryResponse>("/rag/query", { method: "POST", body: payload });
}

export function postEvaluate(payload: EvaluateRequest) {
  return apiRequest<EvaluateResponse>("/evaluate", { method: "POST", body: payload });
}

export function postEvaluateBase(payload: EvaluateRequest) {
  return apiRequest<EvaluateResponse>("/evaluate/base", { method: "POST", body: payload });
}

export function getIngestStatus() {
  return apiRequest<IngestStatusResponse>("/ingest/status");
}

export function postIngestRebuild(payload: IngestRebuildRequest) {
  return apiRequest<IngestRebuildResponse>("/ingest/rebuild", { method: "POST", body: payload });
}

export function postUploadPolicyPdf(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return apiRequest<IngestUploadPolicyResponse>("/ingest/upload-policy", {
    method: "POST",
    body: formData,
  });
}
