export type WorkflowMode = "plan" | "review" | "test-plan";

const LABELS: Record<WorkflowMode, string> = {
  plan: "Plan",
  review: "Review",
  "test-plan": "Test Plan"
};

interface WorkflowModeSwitcherProps {
  mode: WorkflowMode;
  onChange: (mode: WorkflowMode) => void;
}

export function WorkflowModeSwitcher({ mode, onChange }: WorkflowModeSwitcherProps) {
  return (
    <section className="panel">
      <p className="eyebrow">Workflow mode</p>
      <div className="mode-switcher">
        {(Object.keys(LABELS) as WorkflowMode[]).map((entry) => (
          <button
            key={entry}
            type="button"
            className={entry === mode ? "mode-chip mode-chip-active" : "mode-chip"}
            onClick={() => onChange(entry)}
          >
            {LABELS[entry]}
          </button>
        ))}
      </div>
    </section>
  );
}
