from src.app.contracts.responses import Evidence


def lookup_issues(issue_ids: list[str]) -> list[Evidence]:
    evidence = []
    for issue_id in issue_ids:
        evidence.append(
            Evidence(
                source_type="issue",
                locator=issue_id,
                snippet="stub issue evidence",
                confidence="medium",
            )
        )
    return evidence
