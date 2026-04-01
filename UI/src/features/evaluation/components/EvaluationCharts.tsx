import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { EvaluationRun } from "../../../types/api";

function formatTooltipValue(value: unknown): string {
  if (typeof value === "number") {
    return value.toFixed(3);
  }
  if (Array.isArray(value)) {
    return value.join(", ");
  }
  return String(value ?? "-");
}

function formatLabel(value: string | undefined) {
  if (!value) {
    return "-";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleDateString("es-CR", { month: "short", day: "2-digit" });
}

function normalizeRuns(runs: EvaluationRun[]) {
  return [...runs]
    .map((run) => ({
      score: typeof run.score === "number" ? run.score : null,
      ndcg: typeof run.ndcg_at_k === "number" ? run.ndcg_at_k : null,
      hit: typeof run.hit_at_k === "number" ? run.hit_at_k : null,
      createdAt: run.created_at ?? "",
      shortDate: formatLabel(run.created_at),
      runId: run.id.slice(0, 8),
    }))
    .reverse()
    .slice(-20);
}

export function EvaluationCharts({ runs }: { runs: EvaluationRun[] }) {
  const chartData = normalizeRuns(runs);
  if (chartData.length === 0) {
    return null;
  }

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-panel">
        <p className="mb-3 text-sm font-semibold text-slate-900">Tendencia score y nDCG@k</p>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="shortDate" tick={{ fill: "#64748b", fontSize: 12 }} />
              <YAxis domain={[0, 1]} tick={{ fill: "#64748b", fontSize: 12 }} />
              <Tooltip formatter={(value) => formatTooltipValue(value)} />
              <Line type="monotone" dataKey="score" name="score" stroke="#0f172a" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="ndcg" name="nDCG@k" stroke="#334155" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-panel">
        <p className="mb-3 text-sm font-semibold text-slate-900">Hit@k reciente</p>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="runId" tick={{ fill: "#64748b", fontSize: 12 }} />
              <YAxis domain={[0, 1]} tick={{ fill: "#64748b", fontSize: 12 }} />
              <Tooltip formatter={(value) => formatTooltipValue(value)} />
              <Bar dataKey="hit" name="Hit@k" fill="#1e293b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

