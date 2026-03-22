import type { Evidence } from "../../api/contracts/responses";
import { EmptyState } from "../state/EmptyState";

export function EvidenceList({ evidence }: { evidence: Evidence[] }) {
  if (evidence.length === 0) {
    return <EmptyState title="No evidence returned" body="The backend completed this workflow without evidence records for the current run." />;
  }

  return (
    <section className="panel">
      <p className="eyebrow">Evidence</p>
      <div className="result-grid">
        {evidence.map((item, index) => (
          <article key={`${item.locator}-${index}`} className="result-card">
            <p className="eyebrow">{item.source_type}</p>
            <h3>{item.locator}</h3>
            <p>{item.snippet ?? "No snippet included."}</p>
            <p className="muted-copy">Confidence {item.confidence}{item.timestamp ? ` · ${item.timestamp}` : ""}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
