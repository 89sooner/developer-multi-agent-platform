interface MetadataPanelProps {
  runId: string;
  traceId: string;
  modelVersion: string;
  skillVersions: Record<string, string>;
  promptVersions: Record<string, string>;
  userId: string;
  repoScope: string[];
}

function stringifyMap(value: Record<string, string>) {
  const entries = Object.entries(value);
  if (entries.length === 0) {
    return "No entries";
  }
  return entries.map(([key, item]) => `${key}: ${item}`).join("\n");
}

export function MetadataPanel({ runId, traceId, modelVersion, skillVersions, promptVersions, userId, repoScope }: MetadataPanelProps) {
  return (
    <section className="panel">
      <p className="eyebrow">Metadata</p>
      <div className="result-grid">
        <article className="result-card"><p className="eyebrow">Run ID</p><h3>{runId}</h3></article>
        <article className="result-card"><p className="eyebrow">Trace ID</p><h3>{traceId}</h3></article>
        <article className="result-card"><p className="eyebrow">Model version</p><h3>{modelVersion}</h3></article>
        <article className="result-card"><p className="eyebrow">User</p><h3>{userId}</h3><p>{repoScope.join(", ") || "No repo scope"}</p></article>
        <article className="result-card"><p className="eyebrow">Skill versions</p><pre className="mini-pre">{stringifyMap(skillVersions)}</pre></article>
        <article className="result-card"><p className="eyebrow">Prompt versions</p><pre className="mini-pre">{stringifyMap(promptVersions)}</pre></article>
      </div>
    </section>
  );
}
