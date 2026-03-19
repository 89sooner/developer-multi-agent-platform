from src.app.contracts.responses import Evidence


def search_docs(repo_id: str, query: str) -> list[Evidence]:
    return [
        Evidence(
            source_type="docs",
            locator=f"{repo_id}:docs/architecture.md",
            snippet=f"stub doc evidence for query={query}",
            confidence="low",
        )
    ]
