import type { PlanRequest, ReviewRequest, TestPlanRequest } from "./contracts/requests";
import type { PlanResponse, ReviewResponse, RunDetailResponse, TestPlanResponse, TraceResponse } from "./contracts/responses";
import { fetchJson, type RequestContext } from "./http";

export function createPlan(payload: PlanRequest, context?: RequestContext) {
  return fetchJson<PlanResponse>("/v1/workflows/plan", { method: "POST", body: JSON.stringify(payload) }, context);
}

export function createReview(payload: ReviewRequest, context?: RequestContext) {
  return fetchJson<ReviewResponse>("/v1/workflows/review", { method: "POST", body: JSON.stringify(payload) }, context);
}

export function createTestPlan(payload: TestPlanRequest, context?: RequestContext) {
  return fetchJson<TestPlanResponse>("/v1/workflows/test-plan", { method: "POST", body: JSON.stringify(payload) }, context);
}

export function getRun(runId: string, context?: RequestContext) {
  return fetchJson<RunDetailResponse>(`/v1/workflows/${runId}`, undefined, context);
}

export function getTrace(runId: string, context?: RequestContext) {
  return fetchJson<TraceResponse>(`/v1/workflows/${runId}/trace`, undefined, context);
}
