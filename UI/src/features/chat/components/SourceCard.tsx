import type { RetrievedChunk } from "../../../types/api";

export function SourceCard({ source }: { source: RetrievedChunk }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs font-semibold text-slate-700">
          {source.metadata.document_title ?? "Fuente sin título"}
        </p>
        <span className="rounded-full bg-slate-200 px-2 py-1 text-[11px] font-medium text-slate-700">
          puntaje {source.score.toFixed(3)}
        </span>
      </div>
      <p className="mt-1 text-xs text-slate-500">
        {source.metadata.section_title ?? "Sin sección"} • {source.metadata.source_type ?? "desconocido"}
      </p>
      <p className="mt-3 line-clamp-4 whitespace-pre-wrap text-sm leading-6 text-slate-700">{source.text}</p>
    </div>
  );
}

