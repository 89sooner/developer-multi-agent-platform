import type { ReviewRequest } from "../../api/contracts/requests";
import { ArtifactRefsPanel } from "./ArtifactRefsPanel";
import { RequestOptionsPanel } from "./RequestOptionsPanel";

interface ReviewRequestFormProps {
  value: ReviewRequest;
  onChange: (next: ReviewRequest) => void;
  onSubmit: () => void;
  submitting: boolean;
}

export function ReviewRequestForm({ value, onChange, onSubmit, submitting }: ReviewRequestFormProps) {
  return (
    <div className="route-stack">
      <section className="panel panel-form">
        <p className="eyebrow">Review workflow</p>
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
          Review request
          <textarea
            rows={4}
            value={value.task_text}
            onChange={(event) => onChange({ ...value, task_text: event.target.value })}
            placeholder="Review the current workflow change for readiness and missing tests."
          />
        </label>
        <label>
          Diff text
          <textarea
            rows={6}
            value={value.diff_text ?? ""}
            onChange={(event) => onChange({ ...value, diff_text: event.target.value || null })}
            placeholder="Optional raw diff input"
          />
        </label>
      </section>
      <ArtifactRefsPanel value={value.artifacts} onChange={(artifacts) => onChange({ ...value, artifacts })} />
      <RequestOptionsPanel value={value.options} onChange={(options) => onChange({ ...value, options })} />
      <div className="sticky-submit-bar">
        <button className="primary-button" type="button" onClick={onSubmit} disabled={submitting}>
          {submitting ? "Submitting review request..." : "Submit review request"}
        </button>
      </div>
    </div>
  );
}
