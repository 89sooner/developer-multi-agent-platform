import type { TestPlanRequest } from "../../api/contracts/requests";

interface TestPlanRequestFormProps {
  value: TestPlanRequest;
  hasPrefill: boolean;
  onChange: (next: TestPlanRequest) => void;
  onSubmit: () => void;
  submitting: boolean;
}

function parseLines(value: string) {
  return value
    .split("\n")
    .map((entry) => entry.trim())
    .filter(Boolean);
}

export function TestPlanRequestForm({ value, hasPrefill, onChange, onSubmit, submitting }: TestPlanRequestFormProps) {
  return (
    <div className="route-stack">
      <section className="panel panel-form">
        <p className="eyebrow">Test-plan workflow</p>
        <div className="form-grid">
          <label>
            Repository ID
            <input value={value.repo_id} onChange={(event) => onChange({ ...value, repo_id: event.target.value })} placeholder="developer-multi-agent-platform" />
          </label>
          <label>
            Branch
            <input value={value.branch} onChange={(event) => onChange({ ...value, branch: event.target.value })} placeholder="main" />
          </label>
        </div>
        {hasPrefill ? <p className="prefill-note">Prefilled from the most recent plan result. You can edit every field before submitting.</p> : null}
        <label>
          Implementation plan
          <textarea
            rows={6}
            value={value.implementation_plan.join("\n")}
            onChange={(event) => onChange({ ...value, implementation_plan: parseLines(event.target.value) })}
            placeholder="Build the review form\nRender review verdicts"
          />
        </label>
        <label>
          Impacted areas
          <textarea
            rows={5}
            value={value.impacted_areas.join("\n")}
            onChange={(event) => onChange({ ...value, impacted_areas: parseLines(event.target.value) })}
            placeholder="frontend/src/routes/RunDetailRoute.tsx"
          />
        </label>
      </section>
      <div className="sticky-submit-bar">
        <button className="primary-button" type="button" onClick={onSubmit} disabled={submitting}>
          {submitting ? "Submitting test-plan request..." : "Submit test-plan request"}
        </button>
      </div>
    </div>
  );
}
