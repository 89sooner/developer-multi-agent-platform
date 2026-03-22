export function LoadingState({ title = "Loading route" }: { title?: string }) {
  return (
    <section className="status-card">
      <p className="eyebrow">In progress</p>
      <h2>{title}</h2>
      <p>The console is waiting for the backend response and preserving route context.</p>
    </section>
  );
}
