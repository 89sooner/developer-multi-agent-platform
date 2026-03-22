export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <section className="status-card status-card-muted">
      <p className="eyebrow">Empty</p>
      <h2>{title}</h2>
      <p>{body}</p>
    </section>
  );
}
