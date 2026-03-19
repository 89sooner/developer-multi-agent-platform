from __future__ import annotations

import json

from src.app.contracts.responses import Evidence
from src.app.core.policy import mask_sensitive_text
from src.app.tools.search_utils import ROOT

def lookup_ci(repo_id: str, branch: str) -> list[Evidence]:
    ci_dirs = [
        ROOT / "data" / "ci" / repo_id,
        ROOT / ".runtime" / "ci" / repo_id,
    ]
    candidates = [f"{branch}.json", f"{branch}.md", "latest.json", "latest.md"]
    for ci_dir in ci_dirs:
        for candidate in candidates:
            path = ci_dir / candidate
            if not path.exists():
                continue
            if path.suffix == ".json":
                payload = json.loads(path.read_text(encoding="utf-8"))
                summary = payload.get("summary") or payload.get("status") or json.dumps(payload, ensure_ascii=False)
            else:
                summary = path.read_text(encoding="utf-8", errors="ignore")[:200]
            return [
                Evidence(
                    source_type="ci",
                    locator=str(path.relative_to(ROOT)),
                    snippet=mask_sensitive_text(summary),
                    confidence="medium",
                )
            ]
    return []
