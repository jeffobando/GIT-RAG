import { cn } from "../../app/cn";

export function LoadingState({
  message = "Cargando datos...",
  className,
}: {
  message?: string;
  className?: string;
}) {
  return (
    <div className={cn("rounded-xl border border-slate-200 bg-white px-6 py-8 text-center shadow-panel", className)}>
      <div className="mx-auto h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-slate-700" />
      <p className="mt-3 text-sm text-slate-600">{message}</p>
    </div>
  );
}

