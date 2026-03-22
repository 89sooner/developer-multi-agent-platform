import type { ReactNode } from "react";

import type { ClientError } from "../../api/errors";

export function ApiErrorBanner({ error, children }: { error: ClientError; children?: ReactNode }) {
  return (
    <section className="status-card status-card-danger" role="alert">
      <p className="eyebrow">{error.code}</p>
      <h2>{error.message}</h2>
      {error.request_id ? <p>Request ID: {error.request_id}</p> : null}
      {error.http_status === 401 ? <p>Update the session token and retry the protected route.</p> : null}
      {error.http_status === 403 ? <p>This repo or run is outside the current bearer scope.</p> : null}
      {error.http_status === 404 ? <p>The requested backend resource was not found.</p> : null}
      {error.http_status === 409 ? <p>This request needs an approval token before write actions can proceed.</p> : null}
      {children}
    </section>
  );
}
