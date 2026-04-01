import { createBrowserRouter } from "react-router-dom";

import { AdminOnlyRoute } from "./admin-mode";
import { AppShell } from "../layouts/AppShell";
import { ChatPage } from "../pages/ChatPage";
import { EvaluationsPage } from "../pages/EvaluationsPage";
import { IngestionPage } from "../pages/IngestionPage";
import { MetricsPage } from "../pages/MetricsPage";
import { RetrievalPage } from "../pages/RetrievalPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      { index: true, element: <ChatPage /> },
      {
        path: "retrieval",
        element: (
          <AdminOnlyRoute>
            <RetrievalPage />
          </AdminOnlyRoute>
        ),
      },
      {
        path: "metrics",
        element: (
          <AdminOnlyRoute>
            <MetricsPage />
          </AdminOnlyRoute>
        ),
      },
      {
        path: "evaluations",
        element: (
          <AdminOnlyRoute>
            <EvaluationsPage />
          </AdminOnlyRoute>
        ),
      },
      { path: "ingestion", element: <IngestionPage /> },
    ],
  },
]);

