from __future__ import annotations

import re
from pathlib import Path

from src.app.contracts.responses import Evidence
from src.app.core.policy import mask_sensitive_text

ROOT = Path(__file__).resolve().parents[3]
STOPWORDS = {
    "정리해줘",
    "하려고",
    "합니다",
    "한다",
    "있는",
    "where",
    "what",
    "when",
    "with",
    "that",
    "this",
    "please",
    "request",
    "review",
    "plan",
    "draft",
}
SEARCHABLE_SUFFIXES = {".py", ".md", ".yaml", ".yml", ".json", ".toml"}


def extract_keywords(text: str) -> list[str]:
    candidates = re.findall(r"[A-Za-z][A-Za-z0-9_-]{1,}|[가-힣]{2,}|[0-9]{2,}", text.lower())
    seen: set[str] = set()
    keywords: list[str] = []
    for candidate in candidates:
        if candidate in STOPWORDS or len(candidate) < 2:
            continue
        if candidate not in seen:
            seen.add(candidate)
            keywords.append(candidate)
    return keywords[:12]


def iter_searchable_files(base_dirs: list[Path]) -> list[Path]:
    files: list[Path] = []
    for base_dir in base_dirs:
        if not base_dir.exists():
            continue
        if base_dir.is_file():
            files.append(base_dir)
            continue
        for path in base_dir.rglob("*"):
            if not path.is_file():
                continue
            if any(part.startswith(".") and part not in {".github"} for part in path.parts):
                continue
            if "__pycache__" in path.parts or ".venv" in path.parts:
                continue
            if path.suffix.lower() not in SEARCHABLE_SUFFIXES:
                continue
            if path.stat().st_size > 200_000:
                continue
            files.append(path)
    return files


def score_file(path: Path, content: str, keywords: list[str], changed_files: list[str] | None = None) -> tuple[int, str | None]:
    normalized_path = str(path.relative_to(ROOT)).lower()
    score = 0
    first_line: str | None = None
    changed_files = changed_files or []
    for keyword in keywords:
        if keyword in normalized_path:
            score += 4
        lowered = content.lower()
        if keyword in lowered:
            score += min(lowered.count(keyword), 3)
            if first_line is None:
                for line in content.splitlines():
                    if keyword in line.lower():
                        first_line = line.strip()
                        break
    if normalized_path in {item.lower() for item in changed_files}:
        score += 8
    return score, first_line


def build_evidence(
    *,
    source_type: str,
    path: Path,
    snippet: str | None,
    score: int,
) -> Evidence:
    if score >= 10:
        confidence = "high"
    elif score >= 5:
        confidence = "medium"
    else:
        confidence = "low"
    return Evidence(
        source_type=source_type,
        locator=str(path.relative_to(ROOT)),
        snippet=mask_sensitive_text(snippet),
        confidence=confidence,
    )
