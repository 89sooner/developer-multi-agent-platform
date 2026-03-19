from src.app.contracts.responses import Evidence


def search_repo(repo_id: str, branch: str, query: str) -> list[Evidence]:
    return [
        Evidence(
            source_type="repo",
            locator=f"{repo_id}:{branch}:src/example.py",
            snippet=f"stub evidence for query={query}",
            confidence="medium",
        )
    ]
