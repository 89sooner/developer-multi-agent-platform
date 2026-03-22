import { useEffect, useState } from "react";

import { getHealth } from "../api/health";
import type { HealthResponse } from "../api/contracts/responses";
import { ApiErrorBanner } from "../components/state/ApiErrorBanner";
import { LoadingState } from "../components/state/LoadingState";
import { type ClientError } from "../api/errors";

function toClientError(error: unknown): ClientError | null {
  if (error && typeof error === "object" && "clientError" in error) {
    return (error as { clientError: ClientError }).clientError;
  }
  return null;
}

export function HealthRoute() {
  const [data, setData] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<ClientError | null>(null);

  useEffect(() => {
    let active = true;
    getHealth()
      .then((response) => {
        if (active) {
          setData(response);
          setError(null);
        }
      })
      .catch((candidate: unknown) => {
        if (active) {
          setError(toClientError(candidate));
        }
      });
    return () => {
      active = false;
    };
  }, []);

  if (error) {
    return <ApiErrorBanner error={error} />;
  }
  if (!data) {
    return <LoadingState title="Loading health status" />;
  }

  return (
    <div className="route-stack">
      <section className="panel panel-inline">
        <div>
          <p className="eyebrow">Public endpoint</p>
          <h2>Backend health</h2>
        </div>
        <span className={data.status === "ok" ? "pill pill-success" : "pill pill-warning"}>{data.status}</span>
      </section>
      <section className="connector-grid">
        {Object.entries(data.connectors).map(([name, connector]) => (
          <article key={name} className="panel connector-card">
            <p className="eyebrow">{name}</p>
            <h3>{connector.status}</h3>
            <p>{connector.detail ?? "No extra detail from the backend."}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
