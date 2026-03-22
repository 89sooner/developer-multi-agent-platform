interface TestPlanResultPanelProps {
  unitTests: string[];
  integrationTests: string[];
  regressionTargets: string[];
  edgeCases: string[];
  executionOrder: string[];
}

function renderList(title: string, items: string[]) {
  return (
    <article className="result-card">
      <p className="eyebrow">{title}</p>
      {items.length === 0 ? <p className="muted-copy">No items returned.</p> : <ul className="result-list">{items.map((item) => <li key={item}>{item}</li>)}</ul>}
    </article>
  );
}

export function TestPlanResultPanel({ unitTests, integrationTests, regressionTargets, edgeCases, executionOrder }: TestPlanResultPanelProps) {
  return (
    <section className="panel">
      <p className="eyebrow">Test-plan result</p>
      <div className="result-grid">
        {renderList("Unit tests", unitTests)}
        {renderList("Integration tests", integrationTests)}
        {renderList("Regression targets", regressionTargets)}
        {renderList("Edge cases", edgeCases)}
        {renderList("Execution order", executionOrder)}
      </div>
    </section>
  );
}
