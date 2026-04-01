import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { EmptyState } from "../components/common/EmptyState";
import { ErrorNotice } from "../components/common/ErrorNotice";
import { LoadingState } from "../components/common/LoadingState";
import { Button } from "../components/ui/Button";
import { Card, CardBody, CardHeader } from "../components/ui/Card";
import {
  getIngestStatus,
  postIngestRebuild,
  postUploadPolicyPdf,
} from "../services/api/endpoints";

export function IngestionPage() {
  const queryClient = useQueryClient();

  const statusQuery = useQuery({
    queryKey: ["ingest-status"],
    queryFn: getIngestStatus,
  });

  const rebuildMutation = useMutation({
    mutationFn: () => postIngestRebuild({}),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["ingest-status"] });
    },
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => postUploadPolicyPdf(file),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["ingest-status"] });
    },
  });

  const status = statusQuery.data;

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Control de ingestión</h1>
        <p className="mt-1 text-sm text-slate-500">Sube PDF de política, reconstruye artefactos y valida readiness del runtime.</p>
      </div>

      {(statusQuery.error || rebuildMutation.error || uploadMutation.error) && (
        <ErrorNotice
          message={
            String(
              statusQuery.error instanceof Error
                ? statusQuery.error.message
                : rebuildMutation.error instanceof Error
                  ? rebuildMutation.error.message
                  : uploadMutation.error instanceof Error
                    ? uploadMutation.error.message
                    : "Error inesperado en ingestión",
            )
          }
        />
      )}

      {statusQuery.isPending ? <LoadingState message="Consultando estado de ingestión..." /> : null}

      <Card>
        <CardHeader>
          <p className="text-sm font-semibold text-slate-900">Subir PDF de política</p>
          <p className="text-xs text-slate-500">Convierte PDF a JSON para el rebuild.</p>
        </CardHeader>
        <CardBody>
          <label className="block text-sm text-slate-700">
            <span className="mb-2 block">Selecciona un archivo PDF</span>
            <input
              type="file"
              accept="application/pdf"
              className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) {
                  uploadMutation.mutate(file);
                }
              }}
            />
          </label>
          {uploadMutation.isPending && <p className="mt-3 text-sm text-slate-500">Subiendo y convirtiendo PDF...</p>}
          {uploadMutation.data && (
            <p className="mt-3 text-sm text-emerald-700">
              Generados {uploadMutation.data.generated_chunks} chunks en {uploadMutation.data.generated_json_path}
            </p>
          )}
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <p className="text-sm font-semibold text-slate-900">Reconstruir artefactos</p>
          <p className="text-xs text-slate-500">Ejecuta el pipeline de ingestión y refresca el runtime RAG en memoria.</p>
        </CardHeader>
        <CardBody>
          <Button onClick={() => rebuildMutation.mutate()} disabled={rebuildMutation.isPending}>
            {rebuildMutation.isPending ? "Reconstruyendo..." : "Ejecutar /ingest/rebuild"}
          </Button>

          {status ? (
            <div className="mt-4 grid gap-3 text-sm text-slate-700 md:grid-cols-2">
              <p>Listo: <strong>{String(status.ready)}</strong></p>
              <p>Chunks cargados: <strong>{status.chunks_loaded}</strong></p>
              <p>Índice existe: <strong>{String(status.index_exists)}</strong></p>
              <p>LLM: <strong>{status.llm_provider} / {status.llm_model}</strong></p>
            </div>
          ) : !statusQuery.isPending ? (
            <EmptyState title="Aún no hay estado" description="Ejecuta rebuild o refresca estado para inicializar runtime." className="mt-4" />
          ) : null}
        </CardBody>
      </Card>
    </section>
  );
}

