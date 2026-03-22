import { useMemo, useState } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";

import type { PlanRequest, ReviewRequest, TestPlanRequest } from "../api/contracts/requests";
import { createPlan, createReview, createTestPlan } from "../api/workflows";
import type { ClientError } from "../api/errors";
import { ApiErrorBanner } from "../components/state/ApiErrorBanner";
import { ValidationSummary } from "../components/workflows/ValidationSummary";
import { PlanRequestForm } from "../components/workflows/PlanRequestForm";
import { ReviewRequestForm } from "../components/workflows/ReviewRequestForm";
import { TestPlanRequestForm } from "../components/workflows/TestPlanRequestForm";
import { WorkflowModeSwitcher, type WorkflowMode } from "../components/workflows/WorkflowModeSwitcher";
import { useSession } from "../session/SessionProvider";

const INITIAL_PLAN_REQUEST: PlanRequest = {
  repo_id: "developer-multi-agent-platform",
  branch: "main",
  task_text: "",
  artifacts: {
    issue_ids: [],
    pr_url: null,
    changed_files: []
  },
  options: {
    include_tests: true,
    language: "ko",
    write_actions: [],
    approval_token: null
  }
};

const INITIAL_REVIEW_REQUEST: ReviewRequest = {
  repo_id: "developer-multi-agent-platform",
  branch: "main",
  task_text: "",
  diff_text: null,
  artifacts: {
    issue_ids: [],
    pr_url: null,
    changed_files: []
  },
  options: {
    include_tests: true,
    language: "ko",
    write_actions: [],
    approval_token: null
  }
};

const INITIAL_TEST_PLAN_REQUEST: TestPlanRequest = {
  repo_id: "developer-multi-agent-platform",
  branch: "main",
  implementation_plan: [],
  impacted_areas: []
};

function toClientError(error: unknown): ClientError | null {
  if (error && typeof error === "object" && "clientError" in error) {
    return (error as { clientError: ClientError }).clientError;
  }
  return null;
}

function validationMessages(value: PlanRequest) {
  const messages: string[] = [];
  if (!value.repo_id.trim()) {
    messages.push("Repository ID is required.");
  }
  if (!value.branch.trim()) {
    messages.push("Branch is required.");
  }
  if (!value.task_text.trim()) {
    messages.push("Task text is required.");
  }
  return messages;
}

function reviewValidationMessages(value: ReviewRequest) {
  const messages = validationMessages(value);
  const hasContext = Boolean(value.diff_text?.trim()) || value.artifacts.changed_files.length > 0 || Boolean(value.artifacts.pr_url?.trim());
  if (!hasContext) {
    messages.push("Review mode requires at least one of diff text, changed files, or PR URL.");
  }
  return messages;
}

function testPlanValidationMessages(value: TestPlanRequest) {
  const messages: string[] = [];
  if (!value.repo_id.trim()) {
    messages.push("Repository ID is required.");
  }
  if (!value.branch.trim()) {
    messages.push("Branch is required.");
  }
  if (value.implementation_plan.length === 0) {
    messages.push("At least one implementation-plan item is required.");
  }
  if (value.impacted_areas.length === 0) {
    messages.push("At least one impacted-area item is required.");
  }
  return messages;
}

function detailMessages(detail: unknown) {
  if (!Array.isArray(detail)) {
    return [] as string[];
  }

  return detail
    .map((entry) => {
      if (!entry || typeof entry !== "object") {
        return null;
      }
      const maybeLoc = "loc" in entry ? entry.loc : undefined;
      const maybeMsg = "msg" in entry ? entry.msg : undefined;
      const field = Array.isArray(maybeLoc) ? maybeLoc.filter((item): item is string => typeof item === "string").join(".") : "request";
      return typeof maybeMsg === "string" ? `${field}: ${maybeMsg}` : null;
    })
    .filter((message): message is string => Boolean(message));
}

export function WorkflowsNewRoute() {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { bearerToken, language, setLastRunId } = useSession();
  const [planValue, setPlanValue] = useState<PlanRequest>(INITIAL_PLAN_REQUEST);
  const [reviewValue, setReviewValue] = useState<ReviewRequest>(INITIAL_REVIEW_REQUEST);
  const [testPlanValue, setTestPlanValue] = useState<TestPlanRequest>(() => {
    const state = location.state as { repoId?: string; branch?: string; implementationPlan?: string[]; impactedAreas?: string[] } | null;
    if (!state) {
      return INITIAL_TEST_PLAN_REQUEST;
    }
    return {
      repo_id: state.repoId ?? INITIAL_TEST_PLAN_REQUEST.repo_id,
      branch: state.branch ?? INITIAL_TEST_PLAN_REQUEST.branch,
      implementation_plan: state.implementationPlan ?? [],
      impacted_areas: state.impactedAreas ?? []
    };
  });
  const [error, setError] = useState<ClientError | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const mode = (searchParams.get("mode") as WorkflowMode | null) ?? "plan";

  const validations = useMemo(() => {
    if (mode === "review") {
      return reviewValidationMessages(reviewValue);
    }
    if (mode === "test-plan") {
      return testPlanValidationMessages(testPlanValue);
    }
    return validationMessages(planValue);
  }, [mode, planValue, reviewValue, testPlanValue]);
  const backendValidationMessages = useMemo(() => detailMessages(error?.detail), [error]);
  const hasTestPlanPrefill = testPlanValue.implementation_plan.length > 0 || testPlanValue.impacted_areas.length > 0;

  async function submitCurrentMode() {
    if (validations.length > 0 || submitting) {
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const response =
        mode === "review"
          ? await createReview(
              {
                ...reviewValue,
                options: {
                  ...reviewValue.options,
                  language: reviewValue.options.language || language
                }
              },
              { bearerToken, language: reviewValue.options.language || language, requestId: "fe_review_submit" }
            )
          : mode === "test-plan"
            ? await createTestPlan(testPlanValue, { bearerToken, language, requestId: "fe_test_plan_submit" })
            : await createPlan(
                {
                  ...planValue,
                  options: {
                    ...planValue.options,
                    language: planValue.options.language || language
                  }
                },
                {
                  bearerToken,
                  language: planValue.options.language || language,
                  requestId: "fe_plan_submit"
                }
              );

      setLastRunId(response.run_id);
      navigate(`/runs/${response.run_id}`);
    } catch (candidate) {
      setError(toClientError(candidate));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="route-stack">
      <section className="panel">
        <p className="eyebrow">Phase 2 Route</p>
        <h2>{mode === "review" ? "Review workflow" : mode === "test-plan" ? "Test-plan workflow" : "Plan workflow"}</h2>
        <p>{mode === "review" ? "Submit review context with enough evidence to get a readiness verdict and findings." : mode === "test-plan" ? "Create a structured test plan from manual input or a plan-result prefill." : "Submit a plan request without hand-writing JSON, preserve context on policy errors, and transition straight into the run-detail inspector."}</p>
      </section>
      <WorkflowModeSwitcher
        mode={mode}
        onChange={(nextMode) => {
          setError(null);
          setSearchParams({ mode: nextMode });
        }}
      />
      {error ? (
        <ApiErrorBanner error={error}>
          {error.http_status === 401 ? <p>Open the session token dialog, update the bearer token, and submit again.</p> : null}
          {error.http_status === 403 ? <p>Use a token scoped to the selected repository before retrying.</p> : null}
          {error.http_status === 422 && Array.isArray(error.detail) ? <p>Correct the highlighted payload issues and resubmit.</p> : null}
        </ApiErrorBanner>
      ) : null}
      <ValidationSummary messages={[...validations, ...backendValidationMessages]} />
      {mode === "review" ? (
        <ReviewRequestForm value={reviewValue} onChange={setReviewValue} onSubmit={submitCurrentMode} submitting={submitting} />
      ) : mode === "test-plan" ? (
        <TestPlanRequestForm value={testPlanValue} hasPrefill={hasTestPlanPrefill} onChange={setTestPlanValue} onSubmit={submitCurrentMode} submitting={submitting} />
      ) : (
        <PlanRequestForm value={planValue} onChange={setPlanValue} onSubmit={submitCurrentMode} submitting={submitting} />
      )}
    </div>
  );
}
