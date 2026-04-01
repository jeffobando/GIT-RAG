import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

import type { RagQueryResponse } from "../types/api";

export type ChatExchange = {
  id: string;
  question: string;
  response: RagQueryResponse;
  createdAt: string;
};

type QuerySessionContextValue = {
  exchanges: ChatExchange[];
  latestExchange: ChatExchange | null;
  addExchange: (question: string, response: RagQueryResponse) => void;
};

const QuerySessionContext = createContext<QuerySessionContextValue | null>(null);

export function AppQueryProvider({ children }: { children: ReactNode }) {
  const [exchanges, setExchanges] = useState<ChatExchange[]>([]);

  const value = useMemo<QuerySessionContextValue>(
    () => ({
      exchanges,
      latestExchange: exchanges.length > 0 ? exchanges[0] : null,
      addExchange: (question, response) => {
        const exchange: ChatExchange = {
          id: crypto.randomUUID(),
          question,
          response,
          createdAt: new Date().toISOString(),
        };
        setExchanges((prev) => [exchange, ...prev]);
      },
    }),
    [exchanges],
  );

  return <QuerySessionContext.Provider value={value}>{children}</QuerySessionContext.Provider>;
}

export function useQuerySession() {
  const ctx = useContext(QuerySessionContext);
  if (!ctx) {
    throw new Error("useQuerySession must be used within AppQueryProvider");
  }
  return ctx;
}
