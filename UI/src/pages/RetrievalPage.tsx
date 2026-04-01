import { useQuerySession } from "../app/query-session";
import { EmptyState } from "../components/common/EmptyState";
import { RetrievalInspector } from "../features/retrieval/components/RetrievalInspector";

export function RetrievalPage() {
  const { latestExchange } = useQuerySession();

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Inspector de retrieval</h1>
        <p className="mt-1 text-sm text-slate-500">Inspecciona fuentes recuperadas, puntaje y metadata de cada chunk.</p>
      </div>

      {!latestExchange ? (
        <EmptyState
          title="No hay trazabilidad disponible"
          description="Ejecuta una consulta en chat primero. Aquí verás el detalle del retrieval más reciente."
        />
      ) : (
        <RetrievalInspector question={latestExchange.question} sources={latestExchange.response.sources} />
      )}
    </section>
  );
}

