import type { RetrievedChunk } from "../../../types/api";

export function RetrievalInspector({
  question,
  sources,
}: {
  question: string;
  sources: RetrievedChunk[];
}) {
  return (
    <div className="space-y-4">
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Pregunta original</p>
        <p className="mt-2 rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-800 shadow-panel">
          {question}
        </p>
      </div>

      <div className="space-y-3">
        {sources.map((source, index) => (
          <article key={`${source.metadata.document_title}-${index}`} className="rounded-xl border border-slate-200 bg-white p-4 shadow-panel">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="text-sm font-semibold text-slate-900">{source.metadata.document_title ?? "Fuente sin título"}</h3>
              <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-700">
                puntaje {source.score.toFixed(3)}
              </span>
            </div>
            <div className="mt-2 text-xs text-slate-500">
              <span>sección: {source.metadata.section_title ?? "N/A"}</span>
              <span className="mx-2">•</span>
              <span>tipo: {source.metadata.source_type ?? "N/A"}</span>
            </div>
            <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">{source.text}</p>
          </article>
        ))}
      </div>
    </div>
  );
}

