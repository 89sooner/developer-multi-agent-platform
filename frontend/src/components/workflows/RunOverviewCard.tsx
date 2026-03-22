interface RunOverviewCardProps {
  primaryIntent: string;
  secondaryIntents: string[];
  selectedAgents: string[];
  status: string;
  confidence?: string;
}

export function RunOverviewCard({ primaryIntent, secondaryIntents, selectedAgents, status, confidence }: RunOverviewCardProps) {
  return (
    <section className="panel">
      <p className="eyebrow">Overview</p>
      <div className="metrics-grid">
        <article>
          <p className="eyebrow">Primary intent</p>
          <h3>{primaryIntent}</h3>
        </article>
        <article>
          <p className="eyebrow">Status</p>
          <h3>{status}</h3>
          <p>{confidence ? `Confidence ${confidence}` : "Confidence unavailable"}</p>
        </article>
        <article>
          <p className="eyebrow">Selected agents</p>
          <h3>{selectedAgents.join(", ") || "No agents"}</h3>
          <p>{secondaryIntents.length > 0 ? `Secondary intents: ${secondaryIntents.join(", ")}` : "No secondary intents"}</p>
        </article>
      </div>
    </section>
  );
}
