import { useState } from "react";

import { useSession } from "../session/SessionProvider";
import { TokenDialog } from "../components/auth/TokenDialog";

export function TopBar() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const { bearerToken, language, lastRunId } = useSession();

  return (
    <>
      <header className="top-bar">
        <div>
          <p className="eyebrow">Developer Multi-Agent Platform</p>
          <h1>Operator Console</h1>
        </div>
        <div className="top-bar-actions">
          <button className="ghost-button" type="button" onClick={() => setMobileNavOpen((open) => !open)}>
            Menu
          </button>
          <button className="primary-button" type="button" onClick={() => setDialogOpen(true)}>
            {bearerToken ? "Edit Session Token" : "Add Session Token"}
          </button>
        </div>
        <div className="top-bar-meta">
          <span className="pill">Language {language}</span>
          <span className="pill">{bearerToken ? "Protected requests ready" : "Token missing"}</span>
          {lastRunId ? <span className="pill">Last run {lastRunId}</span> : null}
        </div>
      </header>
      {mobileNavOpen ? (
        <div className="mobile-nav-panel">
          <p className="eyebrow">Route access</p>
          <a href="/workflows/new">New Workflow</a>
          <a href="/health">Health</a>
          <button className="ghost-button" type="button" onClick={() => setMobileNavOpen(false)}>
            Close menu
          </button>
        </div>
      ) : null}
      <TokenDialog open={dialogOpen} onClose={() => setDialogOpen(false)} />
    </>
  );
}
