export function WarningsBanner({ warnings, title = "Limited-confidence backend result" }: { warnings: string[]; title?: string }) {
  return (
    <section className="status-card status-card-warning">
      <p className="eyebrow">Degraded</p>
      <h2>{title}</h2>
      <ul className="warning-list">
        {warnings.map((warning) => (
          <li key={warning}>{warning}</li>
        ))}
      </ul>
    </section>
  );
}
