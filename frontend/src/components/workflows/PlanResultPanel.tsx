interface PlanResultPanelProps {
  summary: string;
  impactedAreas: string[];
  implementationPlan: string[];
  tests: string[];
  risks: string[];
  openQuestions: string[];
  onCreateTestPlan?: () => void;
}

function renderList(title: string, items: string[]) {
  return (
    <article className="result-card">
      <p className="eyebrow">{title}</p>
      {items.length === 0 ? <p className="muted-copy">No items returned.</p> : <ul className="result-list">{items.map((item) => <li key={item}>{item}</li>)}</ul>}
    </article>
  );
}

export function PlanResultPanel({ summary, impactedAreas, implementationPlan, tests, risks, openQuestions, onCreateTestPlan }: PlanResultPanelProps) {
  return (
    <section className="panel">
      <div className="panel-inline">
        <div>
          <p className="eyebrow">Plan result</p>
        </div>
        {onCreateTestPlan ? (
          <button className="ghost-button" type="button" onClick={onCreateTestPlan}>
            Create test plan
          </button>
        ) : null}
      </div>
      <article className="result-card">
        <p className="eyebrow">Summary</p>
        <p>{summary}</p>
      </article>
      <div className="result-grid">
        {renderList("Impacted areas", impactedAreas)}
        {renderList("Implementation plan", implementationPlan)}
        {renderList("Tests", tests)}
        {renderList("Risks", risks)}
        {renderList("Open questions", openQuestions)}
      </div>
    </section>
  );
}
