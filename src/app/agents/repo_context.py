from dataclasses import dataclass
from time import perf_counter

from src.app.agents.base import dedupe, load_prompt
from src.app.contracts.agent_results import RepoContextResult
from src.app.contracts.requests import BaseWorkflowRequest
from src.app.core.policy import confidence_from_counts, mask_evidence
from src.app.core.tracing import TraceRecorder, utc_now
from src.app.tools.ci_lookup import lookup_ci
from src.app.tools.docs_search import search_docs
from src.app.tools.issue_lookup import lookup_issues
from src.app.tools.repo_search import search_repo


def _call_tool(
    tracer: TraceRecorder | None,
    step_name: str,
    tool_name: str,
    input_summary: str,
    callback,
):
    started_at = utc_now()
    started_perf = perf_counter()
    try:
        result = callback()
        if tracer is not None:
            tracer.record_tool_call(
                step_name=step_name,
                tool_name=tool_name,
                input_summary=input_summary,
                output_count=len(result),
                started_perf=started_perf,
                started_at=started_at,
            )
        return result
    except Exception as exc:
        if tracer is not None:
            tracer.record_tool_call(
                step_name=step_name,
                tool_name=tool_name,
                input_summary=input_summary,
                output_count=0,
                status="failed",
                error_message=str(exc),
                started_perf=started_perf,
                started_at=started_at,
            )
        raise


def run_repo_context_agent(
    request: BaseWorkflowRequest,
    *,
    tracer: TraceRecorder | None = None,
    step_name: str = "repo_context",
) -> RepoContextResult:
    repo_evidence = _call_tool(
        tracer,
        step_name,
        "repo_search",
        f"repo_id={request.repo_id}, branch={request.branch}",
        lambda: search_repo(
            request.repo_id,
            request.branch,
            request.task_text,
            changed_files=request.artifacts.changed_files,
        ),
    )
    docs_evidence = _call_tool(
        tracer,
        step_name,
        "docs_search",
        f"repo_id={request.repo_id}",
        lambda: search_docs(request.repo_id, request.task_text),
    )
    issue_evidence = _call_tool(
        tracer,
        step_name,
        "issue_lookup",
        f"issue_ids={','.join(request.artifacts.issue_ids)}",
        lambda: lookup_issues(request.artifacts.issue_ids),
    )
    ci_evidence = _call_tool(
        tracer,
        step_name,
        "ci_lookup",
        f"repo_id={request.repo_id}, branch={request.branch}",
        lambda: lookup_ci(request.repo_id, request.branch),
    )

    evidence = mask_evidence(repo_evidence + docs_evidence + issue_evidence + ci_evidence)
    related_files = dedupe(item.locator for item in repo_evidence)
    relevant_docs = dedupe(item.locator for item in docs_evidence + issue_evidence + ci_evidence)
    similar_implementations = dedupe(item.locator for item in repo_evidence[1:4])

    dependency_summary: list[str] = []
    if any("api/" in item for item in related_files) and any("service" in item for item in related_files):
        dependency_summary.append("api layer 와 service layer 사이 호출 경로를 함께 확인해야 한다.")
    if any("contract" in item or "schema" in item for item in related_files):
        dependency_summary.append("계약 모델 변경 시 request/response 스키마 호환성을 검토해야 한다.")
    if any("storage" in item or "repository" in item for item in related_files):
        dependency_summary.append("저장 계층 변경 시 migration 과 rollback 경로가 필요할 수 있다.")

    uncertainty_list: list[str] = []
    if not repo_evidence:
        uncertainty_list.append("repository evidence 를 충분히 찾지 못했다.")
    if request.artifacts.issue_ids and not issue_evidence:
        uncertainty_list.append("요청에 연결된 issue artifact 를 조회하지 못했다.")
    if not ci_evidence:
        uncertainty_list.append("CI 결과가 연결되지 않아 최근 실패 여부를 확인하지 못했다.")

    confidence = confidence_from_counts(
        evidence_count=len(evidence),
        uncertainty_count=len(uncertainty_list),
    )
    return RepoContextResult(
        related_files=related_files,
        relevant_docs=relevant_docs,
        similar_implementations=similar_implementations,
        dependency_summary=dependency_summary,
        uncertainty_list=uncertainty_list,
        evidence=evidence,
        confidence=confidence,
    )


@dataclass
class RepoContextAgentConfig:
    prompt_file: str = "repo_context.md"


def get_repo_context_prompt() -> str:
    return load_prompt(RepoContextAgentConfig.prompt_file)
