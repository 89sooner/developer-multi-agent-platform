from src.app.contracts.responses import Evidence


def lookup_ci(repo_id: str, branch: str) -> list[Evidence]:
    return [
        Evidence(
            source_type="ci",
            locator=f"{repo_id}:{branch}:latest",
            snippet="stub ci result",
            confidence="low",
        )
    ]
