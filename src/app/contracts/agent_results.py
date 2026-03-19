from __future__ import annotations

from pydantic import BaseModel, Field

from src.app.contracts.requests import RequestType
from src.app.contracts.responses import ConfidenceLevel, Evidence


class IntentClassification(BaseModel):
    primary_intent: RequestType
    secondary_intents: list[RequestType] = Field(default_factory=list)
    selected_agents: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = "medium"


class RequirementsResult(BaseModel):
    feature_summary: str
    assumptions: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    non_goals: list[str] = Field(default_factory=list)
    impacted_areas: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = "medium"


class RepoContextResult(BaseModel):
    related_files: list[str] = Field(default_factory=list)
    relevant_docs: list[str] = Field(default_factory=list)
    similar_implementations: list[str] = Field(default_factory=list)
    dependency_summary: list[str] = Field(default_factory=list)
    uncertainty_list: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: ConfidenceLevel = "medium"


class ImplementationResult(BaseModel):
    change_plan: list[str] = Field(default_factory=list)
    target_modules: list[str] = Field(default_factory=list)
    api_changes: list[str] = Field(default_factory=list)
    data_model_changes: list[str] = Field(default_factory=list)
    migration_needs: list[str] = Field(default_factory=list)
    rollback_notes: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = "medium"


class TestStrategyResult(BaseModel):
    unit_tests: list[str] = Field(default_factory=list)
    integration_tests: list[str] = Field(default_factory=list)
    regression_targets: list[str] = Field(default_factory=list)
    edge_cases: list[str] = Field(default_factory=list)
    execution_order: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = "medium"


class ReviewResult(BaseModel):
    missing_evidence: list[str] = Field(default_factory=list)
    hidden_dependencies: list[str] = Field(default_factory=list)
    regression_risks: list[str] = Field(default_factory=list)
    security_flags: list[str] = Field(default_factory=list)
    performance_flags: list[str] = Field(default_factory=list)
    compatibility_flags: list[str] = Field(default_factory=list)
    readiness_verdict: str = "ready"
    confidence: ConfidenceLevel = "medium"
