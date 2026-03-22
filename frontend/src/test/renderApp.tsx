import { render } from "@testing-library/react";
import { createMemoryRouter, RouterProvider } from "react-router-dom";

import { SessionProvider } from "../session/SessionProvider";
import { AppShell } from "../shell/AppShell";
import { HealthRoute } from "../routes/HealthRoute";
import { RunDetailRoute } from "../routes/RunDetailRoute";
import { RunTraceRoute } from "../routes/RunTraceRoute";
import { WorkflowsNewRoute } from "../routes/WorkflowsNewRoute";

const routes = [
  {
    path: "/",
    element: <AppShell />,
    children: [
      { path: "/workflows/new", element: <WorkflowsNewRoute /> },
      { path: "/runs/:runId", element: <RunDetailRoute /> },
      { path: "/runs/:runId/trace", element: <RunTraceRoute /> },
      { path: "/health", element: <HealthRoute /> }
    ]
  }
];

export function renderApp(initialEntry: string) {
  const router = createMemoryRouter(routes, {
    initialEntries: [initialEntry]
  });

  return render(
    <SessionProvider>
      <RouterProvider router={router} />
    </SessionProvider>
  );
}
