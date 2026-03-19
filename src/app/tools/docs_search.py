from __future__ import annotations

from src.app.contracts.responses import Evidence
from src.app.tools.search_utils import ROOT, build_evidence, extract_keywords, iter_searchable_files, score_file


def search_docs(repo_id: str, query: str) -> list[Evidence]:
    keywords = extract_keywords(" ".join(filter(None, [repo_id, query])))
    if not keywords:
        return []

    files = iter_searchable_files([ROOT / "docs", ROOT / "README.md", ROOT / "prompts", ROOT / "skills"])
    ranked: list[tuple[int, object, str | None]] = []
    for path in files:
        content = path.read_text(encoding="utf-8", errors="ignore")
        score, snippet = score_file(path, content, keywords)
        if score > 0:
            ranked.append((score, path, snippet))

    ranked.sort(key=lambda item: item[0], reverse=True)
    return [
        build_evidence(source_type="docs", path=path, snippet=snippet, score=score)
        for score, path, snippet in ranked[:6]
    ]
