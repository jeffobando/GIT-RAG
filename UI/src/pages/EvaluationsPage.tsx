import { useQuery } from "@tanstack/react-query";

import { EmptyState } from "../components/common/EmptyState";
import { ErrorNotice } from "../components/common/ErrorNotice";
import { LoadingState } from "../components/common/LoadingState";
import { EvaluationCharts } from "../features/evaluation/components/EvaluationCharts";
import { EvaluationTable } from "../features/evaluation/components/EvaluationTable";
import { getEvaluationRuns } from "../services/api/evaluations";

export function EvaluationsPage() {
  const evaluationsQuery = useQuery({
    queryKey: ["evaluation-runs"],
    queryFn: getEvaluationRuns,
    retry: false,
  });

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Evaluaciones</h1>
        <p className="mt-1 text-sm text-slate-500">Revisa corridas de evaluación y puntajes de calidad del comportamiento RAG.</p>
      </div>

      {evaluationsQuery.isPending ? <LoadingState message="Consultando evaluaciones..." /> : null}
      {evaluationsQuery.error instanceof Error ? <ErrorNotice message={evaluationsQuery.error.message} /> : null}

      {evaluationsQuery.data && evaluationsQuery.data.length > 0 ? (
        <>
          <EvaluationCharts runs={evaluationsQuery.data} />
          <EvaluationTable runs={evaluationsQuery.data} />
        </>
      ) : !evaluationsQuery.isPending ? (
        <EmptyState
          title="Endpoint de evaluaciones no disponible"
          description="La UI ya está preparada. Conecta el endpoint backend (ej. /evaluations/runs)."
        />
      ) : null}
    </section>
  );
}

