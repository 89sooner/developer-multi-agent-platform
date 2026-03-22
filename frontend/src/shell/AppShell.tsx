import { Outlet, useLocation } from "react-router-dom";

import { PrimaryNav } from "./PrimaryNav";
import { TopBar } from "./TopBar";
import { useSession } from "../session/SessionProvider";

export function AppShell() {
  const location = useLocation();
  const { bearerToken } = useSession();

  return (
    <div className="app-shell">
      <TopBar />
      <div className="app-frame">
        <aside className="rail">
          <PrimaryNav />
          <section className="rail-card">
            <p className="eyebrow">Foundation status</p>
            <h2>Phase 0 shell active</h2>
            <p>Current route: {location.pathname}</p>
            <p>{bearerToken ? "Protected fetches can send Authorization." : "Use session token for protected routes."}</p>
          </section>
        </aside>
        <main className="main-column">
          <div className="route-hero">
            <p className="eyebrow">Direct-entry ready</p>
            <h2>FastAPI-backed operator routes</h2>
            <p>Phase 0 keeps the console honest: route shells, shared request state, and typed API access before workflow-specific UI.</p>
          </div>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
