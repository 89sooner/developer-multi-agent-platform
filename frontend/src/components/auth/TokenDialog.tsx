import { FormEvent, useState } from "react";
import { createPortal } from "react-dom";

import { useSession } from "../../session/SessionProvider";

interface TokenDialogProps {
  open: boolean;
  onClose: () => void;
}

export function TokenDialog({ open, onClose }: TokenDialogProps) {
  const { bearerToken, setBearerToken, clearBearerToken, language, setLanguage } = useSession();
  const [draftToken, setDraftToken] = useState(bearerToken);
  const [draftLanguage, setDraftLanguage] = useState(language);

  if (!open) {
    return null;
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setBearerToken(draftToken.trim());
    setLanguage(draftLanguage.trim() || "ko");
    onClose();
  }

  const dialog = (
    <div className="dialog-backdrop" role="presentation" onClick={onClose}>
      <div className="dialog-panel" role="dialog" aria-modal="true" aria-labelledby="token-dialog-title" onClick={(event) => event.stopPropagation()}>
        <div className="dialog-header">
          <div>
            <p className="eyebrow">Session Access</p>
            <h2 id="token-dialog-title">Bearer token and request defaults</h2>
          </div>
          <button className="ghost-button" type="button" onClick={onClose}>
            Close
          </button>
        </div>
        <form className="dialog-form" onSubmit={handleSubmit}>
          <label>
            Bearer token
            <textarea
              value={draftToken}
              onChange={(event) => setDraftToken(event.target.value)}
              placeholder="sub=alice;repos=developer-multi-agent-platform;roles=developer"
              rows={4}
            />
          </label>
          <label>
            Request language
            <input value={draftLanguage} onChange={(event) => setDraftLanguage(event.target.value)} placeholder="ko" />
          </label>
          <div className="dialog-actions">
            <button
              className="ghost-button"
              type="button"
              onClick={() => {
                clearBearerToken();
                setDraftToken("");
              }}
            >
              Clear token
            </button>
            <button className="primary-button" type="submit">
              Save session settings
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  return createPortal(dialog, document.body);
}
