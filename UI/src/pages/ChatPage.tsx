import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { useAdminMode } from "../app/admin-mode";
import { useQuerySession } from "../app/query-session";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorNotice } from "../components/common/ErrorNotice";
import { ChatComposer } from "../features/chat/components/ChatComposer";
import { ChatMessage } from "../features/chat/components/ChatMessage";
import { postEvaluate, postEvaluateBase, postRagQuery } from "../services/api/endpoints";
import type { RagQueryResponse } from "../types/api";

function toChatResponse(response: RagQueryResponse | { answer: string; sources: RagQueryResponse["sources"] }): RagQueryResponse {
  return {
    answer: response.answer,
    sources: response.sources ?? [],
  };
}

export function ChatPage() {
  const queryClient = useQueryClient();
  const { isAdminMode } = useAdminMode();
  const { exchanges, addExchange } = useQuerySession();
  const [lastQuestion, setLastQuestion] = useState<string>("");
  const [useBaseMode, setUseBaseMode] = useState<boolean>(false);

  const queryMutation = useMutation({
    mutationFn: async ({ question }: { question: string }) => {
      if (isAdminMode) {
        if (useBaseMode) {
          return postEvaluateBase({
            query: question,
            run_type: "base",
            source_type: "base",
          });
        }
        return postEvaluate({
          query: question,
          run_type: "rag",
          source_type: "rag",
        });
      }
      return postRagQuery({ question });
    },
    onSuccess: async (response) => {
      addExchange(lastQuestion, toChatResponse(response));
      if (isAdminMode) {
        await Promise.all([
          queryClient.invalidateQueries({ queryKey: ["metrics-summary"] }),
          queryClient.invalidateQueries({ queryKey: ["metrics-compare", "rag", "base"] }),
          queryClient.invalidateQueries({ queryKey: ["evaluation-runs"] }),
        ]);
      }
    },
  });

  return (
    <section className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_380px]">
      <div className="space-y-5">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Chat RAG</h1>
          <p className="mt-1 text-sm text-slate-500">
            Haz preguntas sobre la base indexada
            {isAdminMode ? " y valida la respuesta con fuentes recuperadas." : "."}
          </p>
        </div>

        {isAdminMode ? (
          <div className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm">
            <label className="flex cursor-pointer items-center gap-2 text-slate-700">
              <input
                type="checkbox"
                checked={useBaseMode}
                onChange={(event) => setUseBaseMode(event.target.checked)}
              />
              Ejecutar baseline sin RAG
            </label>
            <span className="text-xs text-slate-500">
              Modo activo: {useBaseMode ? "base" : "rag"}
            </span>
          </div>
        ) : null}

        <ChatComposer
          loading={queryMutation.isPending}
          onSubmit={async (question) => {
            setLastQuestion(question);
            await queryMutation.mutateAsync({ question });
          }}
        />

        {queryMutation.error instanceof Error ? <ErrorNotice message={queryMutation.error.message} /> : null}

        <div className="space-y-4">
          {exchanges.length === 0 ? (
            <EmptyState
              title="Aún no hay preguntas"
              description="Haz tu primera pregunta para iniciar la conversación con retrieval."
            />
          ) : (
            exchanges.map((exchange) => <ChatMessage key={exchange.id} exchange={exchange} />)
          )}
        </div>
      </div>

      <aside className="space-y-4">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-panel">
          <p className="text-sm font-semibold text-slate-900">Guía de uso</p>
          <ul className="mt-3 space-y-2 text-sm text-slate-600">
            <li>Haz preguntas concretas para mejorar la precisión del retrieval.</li>
            <li>Usa términos de tu política o documentación cuando sea posible.</li>
            {isAdminMode ? <li>Alterna entre RAG y base para comparar métricas.</li> : null}
            {isAdminMode ? <li>Revisa las tarjetas de fuentes para validar trazabilidad.</li> : null}
          </ul>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-panel">
          <p className="text-sm font-semibold text-slate-900">Estado actual</p>
          {queryMutation.isPending ? (
            <p className="mt-2 text-sm text-slate-500">Generando respuesta...</p>
          ) : (
            <p className="mt-2 text-sm text-slate-500">En espera</p>
          )}
        </div>
      </aside>
    </section>
  );
}

