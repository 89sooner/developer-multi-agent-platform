from __future__ import annotations

import json
from pathlib import Path

from src.app.contracts.responses import Evidence
from src.app.core.policy import mask_sensitive_text
from src.app.tools.search_utils import ROOT

def lookup_issues(issue_ids: list[str]) -> list[Evidence]:
    evidence: list[Evidence] = []
    issue_dirs = [ROOT / "data" / "issues", ROOT / ".runtime" / "issues"]
    for issue_id in issue_ids:
        issue_file = _find_issue_file(issue_dirs, issue_id)
        if issue_file is None:
            continue
        snippet = _load_issue_snippet(issue_file)
        evidence.append(Evidence(source_type="issue", locator=str(issue_file.relative_to(ROOT)), snippet=snippet, confidence="medium"))
    return evidence


def _find_issue_file(issue_dirs: list[Path], issue_id: str) -> Path | None:
    for issue_dir in issue_dirs:
        for suffix in (".md", ".json", ".txt"):
            candidate = issue_dir / f"{issue_id}{suffix}"
            if candidate.exists():
                return candidate
    return None


def _load_issue_snippet(path: Path) -> str:
    if path.suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        text = payload.get("summary") or payload.get("title") or json.dumps(payload, ensure_ascii=False)
        return mask_sensitive_text(text[:200]) or ""
    return mask_sensitive_text(path.read_text(encoding="utf-8", errors="ignore")[:200]) or ""
