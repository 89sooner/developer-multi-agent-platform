import type { ArtifactRefs } from "../../api/contracts/requests";

interface ArtifactRefsPanelProps {
  value: ArtifactRefs;
  onChange: (next: ArtifactRefs) => void;
}

function parseLines(value: string) {
  return value
    .split("\n")
    .map((entry) => entry.trim())
    .filter(Boolean);
}

export function ArtifactRefsPanel({ value, onChange }: ArtifactRefsPanelProps) {
  return (
    <section className="panel panel-form">
      <p className="eyebrow">Artifact references</p>
      <div className="form-grid">
        <label>
          Issue IDs
          <textarea
            rows={3}
            value={value.issue_ids.join("\n")}
            onChange={(event) => onChange({ ...value, issue_ids: parseLines(event.target.value) })}
            placeholder="ENG-101"
          />
        </label>
        <label>
          PR URL
          <input
            value={value.pr_url ?? ""}
            onChange={(event) => onChange({ ...value, pr_url: event.target.value.trim() || null })}
            placeholder="https://github.com/org/repo/pull/123"
          />
        </label>
      </div>
      <label>
        Changed files
        <textarea
          rows={4}
          value={value.changed_files.join("\n")}
          onChange={(event) => onChange({ ...value, changed_files: parseLines(event.target.value) })}
          placeholder="src/app/services/workflow_service.py"
        />
      </label>
    </section>
  );
}
