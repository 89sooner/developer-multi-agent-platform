interface ValidationSummaryProps {
  messages: string[];
}

export function ValidationSummary({ messages }: ValidationSummaryProps) {
  if (messages.length === 0) {
    return null;
  }

  return (
    <section className="status-card status-card-danger" role="alert">
      <p className="eyebrow">Validation</p>
      <h2>Fix the request input</h2>
      <ul className="warning-list">
        {messages.map((message) => (
          <li key={message}>{message}</li>
        ))}
      </ul>
    </section>
  );
}
