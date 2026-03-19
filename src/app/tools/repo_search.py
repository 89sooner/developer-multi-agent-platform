from __future__ import annotations

from pathlib import Path

from src.app.contracts.responses import Evidence
from src.app.tools.search_utils import ROOT, build_evidence, extract_keywords, iter_searchable_files, score_file


def search_repo(repo_id: str, branch: str, query: str, changed_files: list[str] | None = None) -> list[Evidence]:
    keywords = extract_keywords(" ".join(filter(None, [repo_id, branch, query])))
    if not keywords and not changed_files:
        return []

    search_roots = [ROOT / "src", ROOT / "tests"]
    explicit_paths = [ROOT / path for path in (changed_files or []) if (ROOT / path).exists()]
    files = iter_searchable_files(search_roots + explicit_paths)

    ranked: list[tuple[int, Path, str | None]] = []
    for path in files:
        content = path.read_text(encoding="utf-8", errors="ignore")
        score, snippet = score_file(path, content, keywords, changed_files)
        if score > 0:
            ranked.append((score, path, snippet))

    ranked.sort(key=lambda item: item[0], reverse=True)
    return [
        build_evidence(source_type="repo", path=path, snippet=snippet, score=score)
        for score, path, snippet in ranked[:6]
    ]
