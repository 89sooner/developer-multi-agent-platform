# Frontend PRD v1

Date: 2026-03-22  
Scope basis: `src/app/**`, `tests/**`, `docs/openapi.yaml`, `docs/api-spec.md`, `docs/current-state-functional-technical-spec.md`

## 1. Product Summary

This frontend is an operator console for the current backend MVP. It does not attempt to present a full autonomous AI platform, IDE extension, or collaboration suite. Its job is to let a developer or reviewer submit workflow requests, inspect results, understand trace/evidence, react to degraded states, and send feedback.

The frontend must be grounded in what the backend actually supports today:

- synchronous workflow submission
- completed run detail retrieval by `run_id`
- trace retrieval by `run_id`
- feedback submission
- health and connector status inspection
- structured error handling with `request_id`

## 2. Problem Statement

The backend already exposes valuable workflow APIs, but there is no UI to make them accessible for day-to-day engineering use. Users currently need to know the API contracts and manually inspect JSON responses. This slows adoption, hides backend capabilities like evidence and trace metadata, and makes degraded states difficult to interpret.

The frontend should turn the current API surface into a clear, inspectable workflow experience without overstating unfinished capabilities such as true AI runtime execution, external system connectors, or enterprise SSO.

## 3. Goals

### 3.1 Primary goals

- Let users submit `plan`, `review`, and `test-plan` workflows without hand-writing JSON.
- Present workflow outputs in structured UI sections instead of raw payloads only.
- Make run metadata, evidence, warnings, and trace information easy to inspect.
- Surface backend failures and degraded-success cases in a way users can act on.
- Let users submit simple post-run feedback.

### 3.2 Success criteria

- A user can submit a plan request and understand the returned implementation plan, tests, risks, and evidence without opening API docs.
- A user can inspect a run and trace using only the returned `run_id`.
- A user can distinguish between hard failure and degraded success.
- A user can recover from common auth/policy/request errors through UI guidance.

## 4. Non-goals

The first frontend must explicitly exclude the following:

- real-time streaming tokens or step-by-step live execution
- async background job management, queues, cancel/retry orchestration
- run history search/list pages backed by server-side query APIs
- actual code write execution for `write_actions`
- external repo, docs, issue, or CI browsing beyond returned evidence payloads
- true AI-chat style conversation UX
- enterprise SSO login flow or role management UI
- collaboration features such as comments, mentions, shared workspaces, or approvals dashboard

## 5. Current Backend Constraints

These constraints shape the frontend scope and UX.

### 5.1 Request execution model

- All workflow APIs execute synchronously in-process.
- The frontend should expect a blocking request/response pattern, not polling for queued jobs.
- After a successful submit, the backend already returns a full result plus `run_id` and `trace_id`.

### 5.2 Retrieval model

- The backend supports `GET /v1/workflows/{run_id}` and `GET /v1/workflows/{run_id}/trace`.
- The backend does not support listing all runs or searching past runs.
- The UI should center around “submit workflow -> inspect returned run” rather than “browse history.”

### 5.3 Auth and policy model

- Workflow APIs require a bearer token.
- Repo scope violations return `403 FORBIDDEN`.
- Some requests with `write_actions` require `approval_token` and return `409 CONFLICT` when missing.
- Missing auth returns `401 UNAUTHORIZED`.
- Validation errors return `422 VALIDATION_ERROR`.

### 5.4 Degraded mode

- Some backend failures still produce `200 OK` results with low confidence and warning messages.
- The frontend must treat warnings and confidence as first-class state, not cosmetic metadata.

### 5.5 Health model

- `/health` returns overall status plus connector-level status.
- `degraded` or `unconfigured` connector states do not always mean the product is down.

## 6. Target Users

### 6.1 Primary user: developer

Needs to understand implementation scope, change plan, test impact, and evidence for a coding task.

### 6.2 Secondary user: reviewer / tech lead

Needs to review a proposed change, inspect risk findings, and verify whether evidence and trace support the recommendation.

### 6.3 Tertiary user: platform operator

Needs to check system health, connector availability, and trace metadata when debugging issues.

## 7. MVP Information Architecture

The frontend MVP should have four top-level areas and one inline support module.

1. `New Workflow`
2. `Run Detail`
3. `Trace`
4. `Health`
5. `Feedback` (inline inside Run Detail)

This architecture matches the backend because workflow submission and run inspection are the real product surface today.

## 8. Core Screens and Flows

## 8.1 New Workflow Screen

### Purpose

Single entry point for all workflow creation.

### Modes

- Plan
- Review
- Test Plan

### Shared fields

- `repo_id`
- `branch`
- `options.language`

### Plan mode fields

- `request_type` optional
- `task_text`
- `artifacts.issue_ids`
- `artifacts.pr_url`
- `artifacts.changed_files`
- `options.include_tests`
- `options.write_actions`
- `options.approval_token`

### Review mode fields

- all plan-like fields above except `request_type` can be hidden or optional
- `diff_text` optional
- `artifacts.changed_files`
- `artifacts.pr_url`

Frontend rule: require at least one of `diff_text`, `changed_files`, or `pr_url` in the UI, even if the backend technically accepts weaker context.

### Test Plan mode fields

- `repo_id`
- `branch`
- `implementation_plan[]`
- `impacted_areas[]`

Frontend rule: this mode should support prefilling from a prior plan result.

### Submission behavior

- Disable submit while request is in flight.
- Generate and send `X-Request-Id` client-side when possible.
- Treat request payload `options.language` as the primary output-language control; `X-User-Language` is only an optional request default.
- Preserve the raw response payload in client state for debugging.
- On success, immediately route to `Run Detail` using returned `run_id`.

## 8.2 Run Detail Screen

### Purpose

Primary inspection surface for completed workflow results.

### Data source of truth

- immediate submit transitions may use the POST response temporarily
- direct entry and browser refresh must fetch `GET /v1/workflows/{run_id}`
- screen rendering must combine top-level run metadata with nested `RunDetailResponse.result`

### Sections

#### A. Overview

- `summary`
- `primary_intent`
- `secondary_intents`
- `selected_agents`
- `confidence`
- `warnings`
- `status`
- `created_at`
- `completed_at`

#### B. Results

Render different blocks based on run type.

For plan runs:

- `impacted_areas`
- `implementation_plan`
- `tests`
- `risks`
- `open_questions`

For review runs:

- `review_findings`
- `missing_tests`
- `risks`
- `readiness_verdict`

For test-plan runs:

- `unit_tests`
- `integration_tests`
- `regression_targets`
- `edge_cases`
- `execution_order`

#### C. Evidence

Each evidence card should show:

- `source_type`
- `locator`
- `snippet` if present
- `confidence`
- `timestamp` if present

#### D. Metadata

- `run_id`
- `trace_id`
- `model_version`
- `skill_versions`
- `prompt_versions`
- `user_id`
- `repo_scope`

#### E. Raw Payloads

- original request payload
- final result payload

This is important because the product is still technical and users may need exact contract inspection.

## 8.3 Trace Screen

### Purpose

Show backend execution details for debugging and trust.

### Required elements

- ordered `steps`
- per-step `status`
- `started_at`, `ended_at`, `latency_ms`
- `tool_calls` count
- `confidence`
- `input_ref` and `output_ref`
- `error_message`
- trace-level `metadata`
- `exported_at`
- `error_summary`

### Tool call list

For each tool call:

- `tool_name`
- `status`
- `duration_ms`
- `input_summary`
- `output_count`
- `error_message`

### UX guidance

- Use a stepper or vertical timeline, not a tree visualization.
- `spans` should not be visualized as a separate hierarchy because they currently mirror `steps`.

## 8.4 Health Screen

### Purpose

Operational visibility.

### Required elements

- overall `status`
- backend `version`
- connector cards for `repo`, `docs`, `issue`, and `ci`
- connector `status`
- connector `detail`

### UX guidance

- `degraded` means limited capability, not necessarily outage.
- `unconfigured` for issue/ci should read as “not connected in this environment,” not “broken.”

## 8.5 Feedback Module

### Placement

Inline on the Run Detail screen after results are shown.

### Fields

- `rating` 1-5
- `useful` boolean
- `comment` optional

### Behavior

- Submit to `POST /v1/feedback`
- Show success confirmation only
- No feedback history, editing, or management UI in MVP

## 9. UX State Requirements

## 9.1 Loading states

- form submit loading
- run detail loading
- trace loading
- health loading

## 9.2 Empty states

- no evidence returned
- no warnings
- no trace tool calls
- no connector detail text

## 9.3 Error states

### `401 UNAUTHORIZED`

- show token/auth requirement
- display `request_id`
- offer retry after entering/updating bearer token

### `403 FORBIDDEN`

- explain repo scope restriction
- display `request_id`
- show attempted `repo_id` when available

### `404 NOT_FOUND`

- used for run/trace/feedback target not found
- show a direct action to go back to workflow submission

### `409 CONFLICT`

- explain approval token requirement for write actions
- preserve current form state

### `422 VALIDATION_ERROR`

- map field-level issues back into the form
- also provide raw validation details for advanced users

### `429 RATE_LIMITED`

- show generic retry guidance
- do not rely on `Retry-After` header being present

### `500 INTERNAL_ERROR`

- show generic failure banner with `request_id`

## 9.4 Degraded success state

This is the most important non-obvious state.

The frontend must show a dedicated warning treatment when all are true:

- HTTP status is `200`
- response contains warning messages
- confidence is low or reduced

Suggested UI treatment:

- yellow or amber banner
- message: “Result completed with limited backend context”
- expandable warning list
- keep result visible, do not replace it with an error state

## 10. API to Screen Mapping

| Screen | Endpoint | Method | Primary Output |
| --- | --- | --- | --- |
| New Workflow - Plan | `/v1/workflows/plan` | POST | `PlanResponse` |
| New Workflow - Review | `/v1/workflows/review` | POST | `ReviewResponse` |
| New Workflow - Test Plan | `/v1/workflows/test-plan` | POST | `TestPlanResponse` |
| Run Detail | `/v1/workflows/{run_id}` | GET | `RunDetailResponse` |
| Trace | `/v1/workflows/{run_id}/trace` | GET | `TraceResponse` |
| Feedback | `/v1/feedback` | POST | `FeedbackResponse` |
| Health | `/health` | GET | `HealthResponse` |

## 11. Functional Requirements

## 11.1 Workflow submission

- The system must support plan submission.
- The system must support review submission.
- The system must support test-plan submission.
- The UI must preserve the last successful response in memory for immediate transition to Run Detail.

## 11.2 Run inspection

- The UI must render workflow-type-specific result sections.
- The UI must expose warnings and confidence clearly.
- The UI must expose evidence in human-readable cards.
- The UI must expose raw JSON for advanced inspection.
- The UI must support direct URL entry and browser refresh from `GET /v1/workflows/{run_id}` without relying on in-memory submit state.

## 11.3 Trace inspection

- The UI must render ordered steps.
- The UI must render per-step timing and status.
- The UI must render tool call records.
- The UI must render metadata including prompt/skill/model versions.

## 11.4 Feedback

- The UI must allow one feedback submission for a viewed run.
- The UI should disable repeat submission within the same client session after success.

## 11.5 Health

- The UI must show overall system status.
- The UI must show connector-level status and detail.

## 12. Technical Requirements for Frontend Implementation

These are framework-agnostic requirements.

## 12.1 Client architecture

- Prefer a single-page application or server-rendered app with client-side data fetches.
- Keep state model simple: auth token, active form state, current run, current trace, health snapshot.
- Build typed API clients directly from current request/response contracts.

## 12.2 Networking

- Send `Authorization: Bearer <token>` for protected endpoints.
- Support optional `X-Request-Id` and `X-User-Language` headers.
- Centralize structured error parsing using `code`, `message`, `request_id`, and `detail`.

## 12.3 Data modeling

- Create frontend types for all contracts in `src/app/contracts/requests.py` and `src/app/contracts/responses.py`.
- Do not invent client-only fields that imply unsupported backend state such as queue position, percent complete, or live token count.

## 12.4 Security and privacy

- Do not store bearer tokens in long-lived insecure storage by default.
- Avoid logging raw request payloads with secrets in client telemetry.
- Treat returned evidence snippets as already partially masked, but still render them carefully.

## 13. Suggested Component Breakdown

- `WorkflowModeSwitcher`
- `PlanRequestForm`
- `ReviewRequestForm`
- `TestPlanRequestForm`
- `RequestOptionsPanel`
- `RunOverviewCard`
- `PlanResultPanel`
- `ReviewResultPanel`
- `TestPlanResultPanel`
- `EvidenceList`
- `WarningsBanner`
- `TraceTimeline`
- `ToolCallTable`
- `FeedbackForm`
- `HealthStatusGrid`
- `ApiErrorBanner`
- `RawJsonDrawer`

## 14. Release Phasing

## Phase A - MVP

- New Workflow screen
- Run Detail screen
- Trace screen
- Health screen
- Feedback module
- bearer token input and request header management

## Phase B - usability hardening

- prefill Test Plan from Plan result
- copy/share `run_id`
- local draft persistence
- better evidence filtering and trace search

## Phase C - after backend expansion

- run history page if backend adds listing/search
- SSO login if backend adds enterprise auth
- external integrations browser if connectors become real
- live execution/streaming if backend becomes async

## 15. Acceptance Criteria

### Workflow submission

- A user can submit a valid plan request and see the returned summary, plan, tests, risks, questions, and evidence.
- A user can submit a valid review request and see findings, missing tests, risks, and readiness verdict.
- A user can submit a valid test-plan request and see unit/integration/regression/edge-case outputs.

### Run and trace

- A user can open a returned `run_id` and inspect metadata plus raw request/result.
- A user can open the corresponding trace and inspect steps and tool calls.

### Error and degraded UX

- A `401`, `403`, `409`, `422`, `429`, and `500` response each produce distinct UI guidance.
- A degraded `200` response with warnings remains viewable and is clearly marked as limited-confidence output.

### Operational view

- A user can read connector health without needing backend logs.

## 16. Explicitly Deferred Requirements

The PRD should stay honest about these gaps:

- There is no server-side run history listing.
- There is no job progress polling model.
- There is no real external repo/docs/issues/CI system navigation.
- There is no actual write execution despite `write_actions` being part of request options.
- There is no enterprise login UI yet.
- There is no conversational AI assistant surface in the backend today.

## 17. Source of Truth

This PRD is grounded primarily in:

- `src/app/api/routes/workflows.py`
- `src/app/api/routes/feedback.py`
- `src/app/contracts/requests.py`
- `src/app/contracts/responses.py`
- `src/app/services/workflow_service.py`
- `src/app/main.py`
- `src/app/tools/health.py`
- `tests/test_workflows.py`
- `tests/test_health.py`
- `docs/openapi.yaml`
- `docs/api-spec.md`
- `docs/current-state-functional-technical-spec.md`
