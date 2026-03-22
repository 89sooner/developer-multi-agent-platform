import type { HealthResponse, RunDetailResponse, TraceResponse } from "../../api/contracts/responses";

export const healthFixture: HealthResponse = {
  status: "degraded",
  version: "0.1.0",
  connectors: {
    repo: { status: "ok", detail: "workspace repo connector online" },
    docs: { status: "degraded", detail: "fallback docs connector" },
    issue: { status: "unconfigured", detail: "no issue connector" },
    ci: { status: "unconfigured", detail: "no ci connector" }
  }
};

export const runDetailFixture: RunDetailResponse = {
  run_id: "run_123",
  status: "completed",
  created_at: "2026-03-22T10:00:00Z",
  completed_at: "2026-03-22T10:00:03Z",
  request_type: "feature",
  primary_intent: "plan",
  secondary_intents: ["review"],
  selected_agents: ["workflow-orchestrator", "requirements-planner"],
  user_id: "alice",
  repo_scope: ["developer-multi-agent-platform"],
  model_version: "gpt-5.4",
  skill_versions: { orchestrator: "v1" },
  prompt_versions: { requirements: "v1" },
  request: {
    repo_id: "developer-multi-agent-platform",
    branch: "main",
    task_text: "phase 0 shell"
  },
  result: {
    warnings: ["repo context step returned limited evidence"],
    confidence: "low",
    summary: "Phase 1 shell baseline",
    impacted_areas: ["frontend/src/routes/WorkflowsNewRoute.tsx", "frontend/src/routes/RunDetailRoute.tsx"],
    implementation_plan: ["Create the plan form", "Render semantic result sections", "Add release-gate tests"],
    tests: ["npm --prefix frontend test", "npm --prefix frontend run build"],
    risks: ["Nested result mapping can drift from backend schema"],
    open_questions: ["Should approval-token guidance be inline or modal?"],
    evidence: [
      {
        source_type: "repo",
        locator: "frontend/src/routes/RunDetailRoute.tsx",
        snippet: "Render plan result sections and metadata.",
        confidence: "medium",
        timestamp: "2026-03-22T10:00:02Z"
      }
    ]
  },
  trace_id: "trace_123"
};

export const traceFixture: TraceResponse = {
  trace_id: "trace_123",
  steps: [
    {
      step_name: "requirements",
      step_order: 1,
      status: "completed",
      started_at: "2026-03-22T10:00:00Z",
      ended_at: "2026-03-22T10:00:01Z",
      latency_ms: 320,
      tool_calls: 2,
      confidence: "medium",
      input_ref: "input://requirements",
      output_ref: "output://requirements"
    }
  ],
  spans: [],
  tool_calls: [
    {
      step_name: "requirements",
      tool_name: "repo_search",
      status: "completed",
      started_at: "2026-03-22T10:00:00Z",
      ended_at: "2026-03-22T10:00:01Z",
      duration_ms: 220,
      input_summary: "search changed files",
      output_count: 3
    }
  ],
  metadata: {
    model_version: "gpt-5.4"
  },
  exported_at: "2026-03-22T10:00:03Z",
  error_summary: null
};

export const reviewRunDetailFixture: RunDetailResponse = {
  ...runDetailFixture,
  run_id: "run_review_123",
  request_type: "review",
  primary_intent: "review",
  result: {
    summary: "Review the plan workflow release before merge.",
    review_findings: [
      {
        category: "coverage",
        severity: "medium",
        message: "Add a route-level 404 test for run detail.",
        evidence: [
          {
            source_type: "repo",
            locator: "frontend/src/test/run-route.test.tsx",
            snippet: "Missing 404 coverage",
            confidence: "medium"
          }
        ]
      }
    ],
    missing_tests: ["Add a review mode validation regression test"],
    risks: ["A reviewer can submit weak context without diff evidence"],
    readiness_verdict: "needs_changes",
    evidence: [
      {
        source_type: "repo",
        locator: "frontend/src/routes/WorkflowsNewRoute.tsx",
        snippet: "Review mode route",
        confidence: "high"
      }
    ],
    warnings: ["review connector degraded to local context"],
    confidence: "low"
  }
};

export const testPlanRunDetailFixture: RunDetailResponse = {
  ...runDetailFixture,
  run_id: "run_test_plan_123",
  request_type: "test_plan",
  primary_intent: "test_plan",
  result: {
    unit_tests: ["Validate mode switching helpers", "Parse multiline plan arrays"],
    integration_tests: ["Submit test-plan request and render result"],
    regression_targets: ["Existing plan flow remains intact"],
    edge_cases: ["Missing implementation-plan items", "Prefill absent on direct entry"],
    execution_order: ["Unit tests", "Integration tests", "Manual verification"],
    warnings: ["test plan generated from partial context"],
    confidence: "low"
  }
};

export const unauthorizedErrorFixture = {
  code: "UNAUTHORIZED",
  message: "missing bearer token",
  request_id: "req_auth01"
};

export const forbiddenErrorFixture = {
  code: "FORBIDDEN",
  message: "repo scope violation",
  request_id: "req_forbid01"
};

export const notFoundErrorFixture = {
  code: "NOT_FOUND",
  message: "run not found",
  request_id: "req_missing01"
};

export const validationErrorFixture = {
  code: "VALIDATION_ERROR",
  message: "request validation failed",
  request_id: "req_validation01",
  detail: [
    {
      loc: ["body", "task_text"],
      msg: "Field required"
    }
  ]
};

export const conflictErrorFixture = {
  code: "CONFLICT",
  message: "approval token required for write actions",
  request_id: "req_conflict01"
};

export const reviewValidationErrorFixture = {
  code: "VALIDATION_ERROR",
  message: "review context is incomplete",
  request_id: "req_review_validation01",
  detail: [
    {
      loc: ["body", "review_context"],
      msg: "Provide diff_text, changed_files, or pr_url"
    }
  ]
};

export const testPlanValidationErrorFixture = {
  code: "VALIDATION_ERROR",
  message: "test plan inputs are incomplete",
  request_id: "req_test_plan_validation01",
  detail: [
    {
      loc: ["body", "implementation_plan"],
      msg: "At least one implementation plan item is required"
    }
  ]
};
