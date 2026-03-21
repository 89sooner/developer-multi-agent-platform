from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import httpx

from src.app.main import app

AUTH_HEADERS = {
    "Authorization": "Bearer sub=ralph-gate;repos=developer-multi-agent-platform;roles=developer"
}
SCENARIOS = [
    {
        "id": "plan-run-trace",
        "task_text": "workflow service 에 persistent run store 와 trace export 를 추가할 때 영향 범위와 구현 계획을 정리해줘.",
    },
    {
        "id": "api-schema-change",
        "task_text": "API response schema 에 prompt_versions 필드를 추가할 때 영향 범위와 구현 계획을 정리해줘.",
    },
    {
        "id": "auth-scope-guard",
        "task_text": "repo scope enforcement 와 structured error response 를 강화하려고 해. 구현 계획을 정리해줘.",
    },
]


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


async def run_gate() -> dict[str, object]:
    latencies: list[int] = []
    results: list[dict[str, object]] = []
    success_count = 0
    evidence_coverage_count = 0
    low_confidence_violations = 0

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        for scenario in SCENARIOS:
            started = perf_counter()
            response = await client.post(
                "/v1/workflows/plan",
                headers=AUTH_HEADERS,
                json={
                    "repo_id": "developer-multi-agent-platform",
                    "branch": "main",
                    "task_text": scenario["task_text"],
                    "artifacts": {"issue_ids": [], "changed_files": []},
                    "options": {"include_tests": True, "language": "ko"},
                },
            )
            latency_ms = int((perf_counter() - started) * 1000)
            latencies.append(latency_ms)

            payload = response.json()
            ok = response.status_code == 200
            has_evidence = bool(payload.get("evidence")) if ok else False
            if ok:
                success_count += 1
            if has_evidence:
                evidence_coverage_count += 1

            violates_low_confidence_rule = (
                ok
                and not has_evidence
                and (
                    payload.get("confidence") != "low"
                    or (not payload.get("warnings") and not payload.get("open_questions"))
                )
            )
            if violates_low_confidence_rule:
                low_confidence_violations += 1

            results.append(
                {
                    "id": scenario["id"],
                    "status_code": response.status_code,
                    "latency_ms": latency_ms,
                    "ok": ok,
                    "has_evidence": has_evidence,
                    "confidence": payload.get("confidence"),
                    "violates_low_confidence_rule": violates_low_confidence_rule,
                    "run_id": payload.get("run_id"),
                }
            )

    report = {
        "generated_at": utc_now(),
        "scenario_count": len(SCENARIOS),
        "success_rate": success_count / len(SCENARIOS),
        "evidence_coverage_rate": evidence_coverage_count / len(SCENARIOS),
        "low_confidence_rule_violations": low_confidence_violations,
        "p95_latency_ms": _p95(latencies),
        "results": results,
    }
    output_dir = Path(".runtime/reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "phase1_gate.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def _p95(values: list[int]) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(len(ordered) * 0.95) - 1))
    return ordered[index]


def main() -> None:
    report = asyncio.run(run_gate())
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
