import { useState } from "react";

export function RawJsonDrawer({ requestPayload, resultPayload }: { requestPayload: Record<string, unknown>; resultPayload: Record<string, unknown> }) {
  const [open, setOpen] = useState(false);

  return (
    <section className="panel">
      <div className="panel-inline">
        <div>
          <p className="eyebrow">Inspectability</p>
          <h2>Raw payloads</h2>
        </div>
        <button className="ghost-button" type="button" onClick={() => setOpen((value) => !value)}>
          {open ? "Hide raw payloads" : "Show raw payloads"}
        </button>
      </div>
      {open ? (
        <div className="route-stack">
          <div className="json-shell">
            <p className="eyebrow">Request payload</p>
            <pre>{JSON.stringify(requestPayload, null, 2)}</pre>
          </div>
          <div className="json-shell">
            <p className="eyebrow">Result payload</p>
            <pre>{JSON.stringify(resultPayload, null, 2)}</pre>
          </div>
        </div>
      ) : null}
    </section>
  );
}
