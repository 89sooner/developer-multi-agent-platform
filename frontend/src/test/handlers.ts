import { http, HttpResponse } from "msw";

import {
  conflictErrorFixture,
  forbiddenErrorFixture,
  healthFixture,
  notFoundErrorFixture,
  reviewRunDetailFixture,
  reviewValidationErrorFixture,
  runDetailFixture,
  testPlanRunDetailFixture,
  testPlanValidationErrorFixture,
  traceFixture,
  unauthorizedErrorFixture,
  validationErrorFixture
} from "./fixtures/contracts";

export const handlers = [
  http.get("/health", () => HttpResponse.json(healthFixture)),
  http.post("/v1/workflows/plan", async ({ request }) => {
    const auth = request.headers.get("Authorization");
    if (!auth) {
      return HttpResponse.json(unauthorizedErrorFixture, { status: 401 });
    }

    const payload = (await request.json()) as Record<string, unknown>;
    const taskText = typeof payload.task_text === "string" ? payload.task_text : "";
    const options = (payload.options ?? {}) as Record<string, unknown>;
    const writeActions = Array.isArray(options.write_actions) ? options.write_actions : [];
    const approvalToken = typeof options.approval_token === "string" ? options.approval_token : null;

    if (!taskText.trim()) {
      return HttpResponse.json(validationErrorFixture, { status: 422 });
    }

    if (taskText.includes("trigger validation")) {
      return HttpResponse.json(validationErrorFixture, { status: 422 });
    }

    if (writeActions.length > 0 && !approvalToken) {
      return HttpResponse.json(conflictErrorFixture, { status: 409 });
    }

    if (typeof payload.repo_id === "string" && payload.repo_id === "other-repo") {
      return HttpResponse.json(forbiddenErrorFixture, { status: 403 });
    }

    if (taskText.includes("delay")) {
      await new Promise((resolve) => setTimeout(resolve, 40));
    }

    return HttpResponse.json({
      run_id: "run_123",
      status: "completed",
      trace_id: "trace_123",
      request_type: "feature",
      primary_intent: "feature",
      secondary_intents: ["review"],
      selected_agents: ["workflow-orchestrator", "requirements-planner", "review-gate"],
      model_version: "gpt-5.4",
      skill_versions: { "summary-composer": "builtin-v1" },
      prompt_versions: { "summary-composer": "builtin-v1" },
      warnings: ["repo_context 단계가 실패해 degraded mode 로 응답했다: connector timeout"],
      confidence: "low",
      summary: "Create a plan-first operator console release.",
      impacted_areas: ["frontend/src/routes/WorkflowsNewRoute.tsx"],
      implementation_plan: ["Build the plan form", "Render run detail"],
      tests: ["npm --prefix frontend test"],
      risks: ["Validation UI drift"],
      open_questions: ["Should write-action guidance be inline?"],
      evidence: [
        {
          source_type: "repo",
          locator: "frontend/src/routes/WorkflowsNewRoute.tsx",
          snippet: "Plan request route",
          confidence: "medium"
        }
      ]
    });
  }),
  http.post("/v1/workflows/review", async ({ request }) => {
    const auth = request.headers.get("Authorization");
    if (!auth) {
      return HttpResponse.json(unauthorizedErrorFixture, { status: 401 });
    }

    const payload = (await request.json()) as Record<string, unknown>;
    const taskText = typeof payload.task_text === "string" ? payload.task_text : "";
    const diffText = typeof payload.diff_text === "string" ? payload.diff_text : "";
    const artifacts = (payload.artifacts ?? {}) as Record<string, unknown>;
    const changedFiles = Array.isArray(artifacts.changed_files) ? artifacts.changed_files : [];
    const prUrl = typeof artifacts.pr_url === "string" ? artifacts.pr_url : "";
    const options = (payload.options ?? {}) as Record<string, unknown>;
    const writeActions = Array.isArray(options.write_actions) ? options.write_actions : [];
    const approvalToken = typeof options.approval_token === "string" ? options.approval_token : null;

    if (!taskText.trim() || (!diffText.trim() && changedFiles.length === 0 && !prUrl.trim())) {
      return HttpResponse.json(reviewValidationErrorFixture, { status: 422 });
    }
    if (writeActions.length > 0 && !approvalToken) {
      return HttpResponse.json(conflictErrorFixture, { status: 409 });
    }
    if (typeof payload.repo_id === "string" && payload.repo_id === "other-repo") {
      return HttpResponse.json(forbiddenErrorFixture, { status: 403 });
    }

    return HttpResponse.json({
      run_id: "run_review_123",
      status: "completed",
      trace_id: "trace_review_123",
      request_type: "review",
      primary_intent: "review",
      secondary_intents: ["risk-analysis"],
      selected_agents: ["review-gate", "workflow-orchestrator"],
      model_version: "gpt-5.4",
      skill_versions: { reviewer: "builtin-v1" },
      prompt_versions: { reviewer: "builtin-v1" },
      warnings: ["review connector degraded to local context"],
      confidence: "low",
      summary: "Review the plan workflow release before merge.",
      review_findings: reviewRunDetailFixture.result.review_findings,
      missing_tests: reviewRunDetailFixture.result.missing_tests,
      risks: reviewRunDetailFixture.result.risks,
      readiness_verdict: "needs_changes",
      evidence: reviewRunDetailFixture.result.evidence
    });
  }),
  http.post("/v1/workflows/test-plan", async ({ request }) => {
    const auth = request.headers.get("Authorization");
    if (!auth) {
      return HttpResponse.json(unauthorizedErrorFixture, { status: 401 });
    }

    const payload = (await request.json()) as Record<string, unknown>;
    const implementationPlan = Array.isArray(payload.implementation_plan) ? payload.implementation_plan : [];
    const impactedAreas = Array.isArray(payload.impacted_areas) ? payload.impacted_areas : [];

    if (implementationPlan.length === 0 || impactedAreas.length === 0) {
      return HttpResponse.json(testPlanValidationErrorFixture, { status: 422 });
    }

    return HttpResponse.json({
      run_id: "run_test_plan_123",
      status: "completed",
      trace_id: "trace_test_plan_123",
      request_type: "test_plan",
      primary_intent: "test_plan",
      secondary_intents: ["quality-gate"],
      selected_agents: ["test-strategy-generator", "workflow-orchestrator"],
      model_version: "gpt-5.4",
      skill_versions: { tester: "builtin-v1" },
      prompt_versions: { tester: "builtin-v1" },
      warnings: ["test plan generated from partial context"],
      confidence: "low",
      unit_tests: testPlanRunDetailFixture.result.unit_tests,
      integration_tests: testPlanRunDetailFixture.result.integration_tests,
      regression_targets: testPlanRunDetailFixture.result.regression_targets,
      edge_cases: testPlanRunDetailFixture.result.edge_cases,
      execution_order: testPlanRunDetailFixture.result.execution_order
    });
  }),
  http.get("/v1/workflows/:runId", ({ params, request }) => {
    const auth = request.headers.get("Authorization");
    if (!auth) {
      return HttpResponse.json(unauthorizedErrorFixture, { status: 401 });
    }
    if (params.runId === "missing") {
      return HttpResponse.json(notFoundErrorFixture, { status: 404 });
    }
    if (params.runId === "forbidden") {
      return HttpResponse.json(forbiddenErrorFixture, { status: 403 });
    }
    if (params.runId === "run_review_123") {
      return HttpResponse.json(reviewRunDetailFixture);
    }
    if (params.runId === "run_test_plan_123") {
      return HttpResponse.json(testPlanRunDetailFixture);
    }
    return HttpResponse.json({ ...runDetailFixture, run_id: params.runId });
  }),
  http.get("/v1/workflows/:runId/trace", ({ params, request }) => {
    const auth = request.headers.get("Authorization");
    if (!auth) {
      return HttpResponse.json(unauthorizedErrorFixture, { status: 401 });
    }
    if (params.runId === "missing") {
      return HttpResponse.json({ ...notFoundErrorFixture, message: "trace not found" }, { status: 404 });
    }
    return HttpResponse.json(traceFixture);
  })
];
