import type { RequestOptions, WriteAction } from "../../api/contracts/requests";

interface RequestOptionsPanelProps {
  value: RequestOptions;
  onChange: (next: RequestOptions) => void;
}

const WRITE_ACTIONS: WriteAction[] = ["create_pr", "comment_pr", "update_issue", "apply_patch", "update_docs"];

export function RequestOptionsPanel({ value, onChange }: RequestOptionsPanelProps) {
  function toggleWriteAction(action: WriteAction) {
    const next = value.write_actions.includes(action)
      ? value.write_actions.filter((entry) => entry !== action)
      : [...value.write_actions, action];
    onChange({ ...value, write_actions: next });
  }

  return (
    <section className="panel panel-form">
      <p className="eyebrow">Request options</p>
      <div className="form-grid">
        <label>
          Output language
          <input value={value.language} onChange={(event) => onChange({ ...value, language: event.target.value })} />
        </label>
        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={value.include_tests}
            onChange={(event) => onChange({ ...value, include_tests: event.target.checked })}
          />
          Include tests in the workflow response
        </label>
      </div>
      <fieldset className="write-actions-fieldset">
        <legend>Write actions</legend>
        <div className="write-actions-grid">
          {WRITE_ACTIONS.map((action) => (
            <label key={action} className="checkbox-row">
              <input
                type="checkbox"
                checked={value.write_actions.includes(action)}
                onChange={() => toggleWriteAction(action)}
              />
              {action}
            </label>
          ))}
        </div>
      </fieldset>
      <label>
        Approval token
        <input
          value={value.approval_token ?? ""}
          onChange={(event) => onChange({ ...value, approval_token: event.target.value.trim() || null })}
          placeholder="optional; required for write actions"
        />
      </label>
    </section>
  );
}
