export function MetricCard({
  label,
  value,
  suffix,
}: {
  label: string;
  value: string;
  suffix?: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-panel">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-3 text-2xl font-semibold text-slate-900">
        {value}
        {suffix ? <span className="ml-1 text-base font-medium text-slate-500">{suffix}</span> : null}
      </p>
    </div>
  );
}
