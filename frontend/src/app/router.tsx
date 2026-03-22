import { createBrowserRouter, Navigate } from "react-router-dom";

import { AppShell } from "../shell/AppShell";
import { HealthRoute } from "../routes/HealthRoute";
import { RunDetailRoute } from "../routes/RunDetailRoute";
import { RunTraceRoute } from "../routes/RunTraceRoute";
import { WorkflowsNewRoute } from "../routes/WorkflowsNewRoute";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      { index: true, element: <Navigate to="/workflows/new" replace /> },
      { path: "/workflows/new", element: <WorkflowsNewRoute /> },
      { path: "/runs/:runId", element: <RunDetailRoute /> },
      { path: "/runs/:runId/trace", element: <RunTraceRoute /> },
      { path: "/health", element: <HealthRoute /> }
    ]
  }
]);
