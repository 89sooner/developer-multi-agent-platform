import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import { getTrace } from "../api/workflows";
import type { TraceResponse } from "../api/contracts/responses";
import { ApiErrorBanner } from "../components/state/ApiErrorBanner";
import { LoadingState } from "../components/state/LoadingState";
import { type ClientError } from "../api/errors";
import { useSession } from "../session/SessionProvider";

function toClientError(error: unknown): ClientError | null {
  if (error && typeof error === "object" && "clientError" in error) {
    return (error as { clientError: ClientError }).clientError;
  }
  return null;
}

export function RunTraceRoute() {
  const { runId = "" } = useParams();
  const { bearerToken, language } = useSession();
  const [data, setData] = useState<TraceResponse | null>(null);
  const [error, setError] = useState<ClientError | null>(null);

  const requestContext = useMemo(
    () => ({ bearerToken, language, requestId: `fe_trace_${runId}` }),
    [bearerToken, language, runId]
  );

  useEffect(() => {
    let active = true;
    getTrace(runId, requestContext)
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
  }, [requestContext, runId]);

  if (error) {
    return <ApiErrorBanner error={error} />;
  }
  if (!data) {
    return <LoadingState title={`Loading trace for ${runId}`} />;
  }

  return (
    <div className="route-stack">
      <section className="panel panel-inline">
        <div>
          <p className="eyebrow">Protected route</p>
          <h2>Trace scaffold</h2>
        </div>
        <span className="pill">{data.trace_id}</span>
      </section>
      <section className="panel json-shell">
        <p className="eyebrow">Trace payload</p>
        <pre>{JSON.stringify(data, null, 2)}</pre>
      </section>
    </div>
  );
}
