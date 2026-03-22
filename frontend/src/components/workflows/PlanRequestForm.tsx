import type { PlanRequest } from "../../api/contracts/requests";
import { ArtifactRefsPanel } from "./ArtifactRefsPanel";
import { RequestOptionsPanel } from "./RequestOptionsPanel";

interface PlanRequestFormProps {
  value: PlanRequest;
  onChange: (next: PlanRequest) => void;
  onSubmit: () => void;
  submitting: boolean;
}

export function PlanRequestForm({ value, onChange, onSubmit, submitting }: PlanRequestFormProps) {
  return (
    <div className="route-stack">
      <section className="panel panel-form">
        <p className="eyebrow">Plan workflow</p>
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
        <label>
          Task text
          <textarea
            rows={6}
            value={value.task_text}
            onChange={(event) => onChange({ ...value, task_text: event.target.value })}
            placeholder="Add a Phase 1 workflow form and semantic result panels."
          />
        </label>
      </section>
      <ArtifactRefsPanel value={value.artifacts} onChange={(artifacts) => onChange({ ...value, artifacts })} />
      <RequestOptionsPanel value={value.options} onChange={(options) => onChange({ ...value, options })} />
      <div className="sticky-submit-bar">
        <button className="primary-button" type="button" onClick={onSubmit} disabled={submitting}>
          {submitting ? "Submitting plan request..." : "Submit plan request"}
        </button>
      </div>
    </div>
  );
}
