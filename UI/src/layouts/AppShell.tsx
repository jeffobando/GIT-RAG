import { useIsFetching, useIsMutating } from "@tanstack/react-query";
import { NavLink, Outlet } from "react-router-dom";

import { useAdminMode } from "../app/admin-mode";
import { cn } from "../app/cn";

const baseNavItems = [
  { to: "/", label: "Chat RAG" },
  { to: "/ingestion", label: "Ingestión" },
];

const adminNavItems = [
  { to: "/retrieval", label: "Trazabilidad" },
  { to: "/metrics", label: "Métricas" },
  { to: "/evaluations", label: "Evaluaciones" },
];

export function AppShell() {
  const { isAdminMode, setAdminMode } = useAdminMode();
  const navItems = isAdminMode
    ? [baseNavItems[0], ...adminNavItems, baseNavItems[1]]
    : baseNavItems;
  const isFetching = useIsFetching();
  const isMutating = useIsMutating();
  const isLoading = isFetching + isMutating > 0;

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/90 backdrop-blur">
        <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between gap-4 px-6">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-lg bg-slate-900" />
            <div>
              <p className="text-sm font-semibold text-slate-900">Consola RAG</p>
              <p className="text-xs text-slate-500">Asistente interno de conocimiento</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {isLoading ? (
              <div className="hidden items-center gap-2 rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-xs text-slate-600 sm:flex">
                <span className="h-3 w-3 animate-spin rounded-full border-2 border-slate-300 border-t-slate-700" />
                Cargando...
              </div>
            ) : null}

            <label className="flex items-center gap-2 text-sm text-slate-600">
              <span className="hidden font-medium sm:inline">Admin</span>
              <button
                type="button"
                role="switch"
                aria-checked={isAdminMode}
                onClick={() => setAdminMode(!isAdminMode)}
                className={cn(
                  "relative h-6 w-11 rounded-full border transition-colors",
                  isAdminMode ? "border-slate-900 bg-slate-900" : "border-slate-300 bg-slate-300",
                )}
              >
                <span
                  className={cn(
                    "absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white transition-transform",
                    isAdminMode && "translate-x-5",
                  )}
                />
              </button>
            </label>

            <nav className="hidden items-center gap-2 md:flex">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    cn(
                      "rounded-md px-3 py-2 text-sm font-medium text-slate-600 transition",
                      isActive && "bg-slate-900 text-white",
                    )
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-7xl px-6 py-6">
        <Outlet />
      </main>
    </div>
  );
}

