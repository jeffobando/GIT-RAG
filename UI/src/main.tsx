import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "react-router-dom";

import "./index.css";
import { AdminModeProvider } from "./app/admin-mode";
import { AppQueryProvider } from "./app/query-session";
import { router } from "./app/router";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <AdminModeProvider>
        <AppQueryProvider>
          <RouterProvider router={router} />
        </AppQueryProvider>
      </AdminModeProvider>
    </QueryClientProvider>
  </React.StrictMode>,
);
