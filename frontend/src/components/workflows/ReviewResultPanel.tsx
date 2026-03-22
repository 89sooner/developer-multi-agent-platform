import type { Evidence } from "../../api/contracts/responses";

interface ReviewFindingShape {
  category: string;
  severity: string;
  message: string;
  evidence: Evidence[];
}

interface ReviewResultPanelProps {
  summary: string;
  readinessVerdict: "ready" | "needs_changes" | "blocked";
  findings: ReviewFindingShape[];
  missingTests: string[];
  risks: string[];
}

function renderList(title: string, items: string[]) {
  return (
    <article className="result-card">
      <p className="eyebrow">{title}</p>
      {items.length === 0 ? <p className="muted-copy">No items returned.</p> : <ul className="result-list">{items.map((item) => <li key={item}>{item}</li>)}</ul>}
    </article>
  );
}

export function ReviewResultPanel({ summary, readinessVerdict, findings, missingTests, risks }: ReviewResultPanelProps) {
  return (
    <section className="panel">
      <div className="panel-inline">
        <div>
          <p className="eyebrow">Review result</p>
          <h2>{summary}</h2>
        </div>
        <span className={readinessVerdict === "ready" ? "pill pill-success" : readinessVerdict === "blocked" ? "pill pill-danger" : "pill pill-warning"}>
          {readinessVerdict}
        </span>
      </div>
      <div className="result-grid">
        {findings.map((finding) => (
          <article key={`${finding.category}-${finding.message}`} className="result-card">
            <p className="eyebrow">{finding.category}</p>
            <h3>{finding.severity}</h3>
            <p>{finding.message}</p>
            <p className="muted-copy">Evidence items: {finding.evidence.length}</p>
          </article>
        ))}
        {renderList("Missing tests", missingTests)}
        {renderList("Risks", risks)}
      </div>
    </section>
  );
}
