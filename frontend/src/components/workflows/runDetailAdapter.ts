import type { Evidence, RunDetailResponse } from "../../api/contracts/responses";

interface PlanResultShape {
  summary: string;
  impacted_areas: string[];
  implementation_plan: string[];
  tests: string[];
  risks: string[];
  open_questions: string[];
  evidence: Evidence[];
  warnings?: string[];
  confidence?: string;
}

interface ReviewResultShape {
  summary: string;
  review_findings: Array<{
    category: string;
    severity: string;
    message: string;
    evidence: Evidence[];
  }>;
  missing_tests: string[];
  risks: string[];
  readiness_verdict: "ready" | "needs_changes" | "blocked";
  evidence: Evidence[];
  warnings?: string[];
  confidence?: string;
}

interface TestPlanResultShape {
  unit_tests: string[];
  integration_tests: string[];
  regression_targets: string[];
  edge_cases: string[];
  execution_order: string[];
  warnings?: string[];
  confidence?: string;
}

function asStringArray(value: unknown) {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

export function isPlanLikeRunDetail(run: RunDetailResponse) {
  const result = run.result as unknown as PlanResultShape;
  return typeof result.summary === "string" && Array.isArray(result.implementation_plan);
}

export function isReviewLikeRunDetail(run: RunDetailResponse) {
  const result = run.result as unknown as ReviewResultShape;
  return Array.isArray(result.review_findings) && typeof result.readiness_verdict === "string";
}

export function isTestPlanLikeRunDetail(run: RunDetailResponse) {
  const result = run.result as unknown as TestPlanResultShape;
  return Array.isArray(result.unit_tests) && Array.isArray(result.execution_order);
}

export function adaptPlanRunDetail(run: RunDetailResponse) {
  const result = run.result as unknown as PlanResultShape;
  return {
    summary: result.summary ?? "",
    impactedAreas: asStringArray(result.impacted_areas),
    implementationPlan: asStringArray(result.implementation_plan),
    tests: asStringArray(result.tests),
    risks: asStringArray(result.risks),
    openQuestions: asStringArray(result.open_questions),
    evidence: Array.isArray(result.evidence) ? result.evidence : [],
    warnings: asStringArray(result.warnings),
    confidence: typeof result.confidence === "string" ? result.confidence : undefined
  };
}

export function adaptReviewRunDetail(run: RunDetailResponse) {
  const result = run.result as unknown as ReviewResultShape;
  return {
    summary: result.summary ?? "",
    findings: Array.isArray(result.review_findings) ? result.review_findings : [],
    missingTests: asStringArray(result.missing_tests),
    risks: asStringArray(result.risks),
    readinessVerdict: result.readiness_verdict ?? "needs_changes",
    evidence: Array.isArray(result.evidence) ? result.evidence : [],
    warnings: asStringArray(result.warnings),
    confidence: typeof result.confidence === "string" ? result.confidence : undefined
  };
}

export function adaptTestPlanRunDetail(run: RunDetailResponse) {
  const result = run.result as unknown as TestPlanResultShape;
  return {
    unitTests: asStringArray(result.unit_tests),
    integrationTests: asStringArray(result.integration_tests),
    regressionTargets: asStringArray(result.regression_targets),
    edgeCases: asStringArray(result.edge_cases),
    executionOrder: asStringArray(result.execution_order),
    warnings: asStringArray(result.warnings),
    confidence: typeof result.confidence === "string" ? result.confidence : undefined
  };
}
