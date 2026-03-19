from typing import Literal

from pydantic import BaseModel, Field

RequestType = Literal["feature", "bugfix", "refactor", "review", "test_plan"]
WriteAction = Literal["create_pr", "comment_pr", "update_issue", "apply_patch", "update_docs"]


class ArtifactRefs(BaseModel):
    issue_ids: list[str] = Field(default_factory=list)
    pr_url: str | None = None
    changed_files: list[str] = Field(default_factory=list)


class RequestOptions(BaseModel):
    include_tests: bool = True
    language: str = "ko"
    write_actions: list[WriteAction] = Field(default_factory=list)
    approval_token: str | None = None


class BaseWorkflowRequest(BaseModel):
    request_type: RequestType | None = None
    repo_id: str
    branch: str
    task_text: str
    artifacts: ArtifactRefs = Field(default_factory=ArtifactRefs)
    options: RequestOptions = Field(default_factory=RequestOptions)


class PlanRequest(BaseWorkflowRequest):
    pass


class ReviewRequest(BaseWorkflowRequest):
    diff_text: str | None = None


class TestPlanRequest(BaseModel):
    repo_id: str
    branch: str
    implementation_plan: list[str]
    impacted_areas: list[str]


class FeedbackRequest(BaseModel):
    run_id: str
    rating: int = Field(ge=1, le=5)
    useful: bool
    comment: str | None = None
