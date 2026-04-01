import type { EvaluationRun } from "../../../types/api";

function formatMetric(value: number | null | undefined) {
  return typeof value === "number" ? value.toFixed(3) : "-";
}

export function EvaluationTable({ runs }: { runs: EvaluationRun[] }) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-panel">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-3">ID corrida</th>
            <th className="px-4 py-3">Puntaje</th>
            <th className="px-4 py-3">Recall@k</th>
            <th className="px-4 py-3">MRR</th>
            <th className="px-4 py-3">Hit@k</th>
            <th className="px-4 py-3">nDCG@k</th>
            <th className="px-4 py-3">Faithfulness</th>
            <th className="px-4 py-3">Answer Relevance</th>
            <th className="px-4 py-3">Creado</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {runs.map((run) => (
            <tr key={run.id}>
              <td className="px-4 py-3 font-medium text-slate-800">{run.id.slice(0, 8)}</td>
              <td className="px-4 py-3 text-slate-700">{formatMetric(run.score)}</td>
              <td className="px-4 py-3 text-slate-700">{formatMetric(run.recall_at_k)}</td>
              <td className="px-4 py-3 text-slate-700">{formatMetric(run.mrr)}</td>
              <td className="px-4 py-3 text-slate-700">{formatMetric(run.hit_at_k)}</td>
              <td className="px-4 py-3 text-slate-700">{formatMetric(run.ndcg_at_k)}</td>
              <td className="px-4 py-3 text-slate-700">{formatMetric(run.faithfulness)}</td>
              <td className="px-4 py-3 text-slate-700">{formatMetric(run.answer_relevance)}</td>
              <td className="px-4 py-3 text-slate-700">{run.created_at ?? "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

