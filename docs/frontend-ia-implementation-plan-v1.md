# Frontend IA, Wireframes, and Implementation Plan v1

## 0. Document Info

- Status: draft v1.0
- Date: 2026-03-22
- Source docs: `docs/frontend-prd-v1.md`, `docs/openapi.yaml`, `docs/api-spec.md`, `docs/current-state-functional-technical-spec.md`
- Purpose: define screen-level information architecture, wireframe structure, component architecture, and implementation slices for the current backend-backed frontend MVP.

## 1. Product Frame

This frontend is an operator console for the current workflow backend. It is not a chatbot, IDE extension, collaboration suite, or admin analytics portal. It exists to make the current backend usable through structured screens instead of raw JSON and manual API calls.

Primary product promise:

- submit workflow requests
- inspect completed results
- inspect evidence and trace metadata
- understand degraded vs failed states
- submit lightweight feedback
- check system health

## 2. Scope Guardrails

Supported backend capabilities:

- `POST /v1/workflows/plan`
- `POST /v1/workflows/review`
- `POST /v1/workflows/test-plan`
- `GET /v1/workflows/{run_id}`
- `GET /v1/workflows/{run_id}/trace`
- `POST /v1/feedback`
- `GET /health`

Unsupported or deferred capabilities:

- run history listing/search
- async queue state, progress polling, cancel/retry orchestration
- streaming model output
- real write execution for `write_actions`
- enterprise login/SSO UI
- external system browsers for repo/docs/issues/CI
- collaboration features

## 3. IA Overview

## 3.1 Primary navigation

Top-level areas:

1. `New Workflow`
2. `Run Detail`
3. `Trace`
4. `Health`

Support area:

- `Feedback` inline in `Run Detail`

## 3.2 Route map

- `/` -> redirect to `/workflows/new`
- `/workflows/new?mode=plan|review|test-plan`
- `/runs/:runId`
- `/runs/:runId/trace`
- `/health`

## 3.3 Route rules

- `Run Detail` and `Trace` are direct-entry routes and must support opening from pasted `run_id`-based URLs.
- `Test Plan` mode should optionally accept prefilled state from the most recent plan result in memory.
- App state should not assume a server-side run index exists.

## 4. End-to-End Flow Map

## 4.1 Primary golden flow

1. User enters bearer token.
2. User opens `New Workflow` in `Plan` mode.
3. User submits `repo_id`, `branch`, `task_text`, and options.
4. Backend returns `PlanResponse` with `run_id` and `trace_id`.
5. UI routes to `Run Detail`.
6. User inspects summary, risks, evidence, warnings, and metadata.
7. User opens `Trace` to inspect execution details.
8. User returns to `Run Detail` and submits feedback.

## 4.2 Secondary flow: review

1. User switches mode to `Review`.
2. User provides at least one of `diff_text`, `changed_files`, or `pr_url`.
3. Backend returns `ReviewResponse`.
4. UI renders findings, missing tests, readiness verdict, evidence, and warnings.

## 4.3 Secondary flow: test-plan

1. User comes from an existing plan result or enters structured arrays manually.
2. UI sends `implementation_plan[]` and `impacted_areas[]`.
3. Backend returns `TestPlanResponse`.
4. UI renders unit/integration/regression/edge-case outputs.

## 4.4 Direct lookup flow

1. User navigates directly to `/runs/:runId`.
2. UI fetches run detail.
3. User optionally navigates to `/runs/:runId/trace`.

## 4.5 Health flow

1. User opens `/health`.
2. UI renders overall backend status and connector cards.

## 5. App Shell Wireframe

## 5.1 Desktop layout

- Top bar
  - product name
  - bearer token entry trigger
  - request language control
  - current environment badge
- Left nav
  - New Workflow
  - Health
  - last viewed run shortcut if available
- Main content area
  - route-specific screen content
- Global utility region
  - request error banner
  - degraded-state banner

## 5.2 Mobile layout

- Top app bar
- collapsible navigation drawer
- single-column content flow
- sticky primary action area on forms

## 5.3 Persistent utility surfaces

- auth token modal or slide-over
- global API error banner
- request metadata toast for copied `run_id` or `trace_id`

## 6. Screen Specs

## 6.1 Screen: New Workflow

### Purpose

Single entry point for workflow creation.

### Primary user jobs

- submit a planning request
- submit a review request
- generate a test plan from structured implementation inputs

### Layout zones

1. page header
2. mode switcher
3. request form body
4. advanced context section
5. request options section
6. validation or API error section
7. sticky submit bar

### Wireframe structure

- Header
  - title: `New Workflow`
  - helper text describing synchronous execution
- Mode tabs
  - Plan
  - Review
  - Test Plan
- Core fields panel
  - `repo_id`
  - `branch`
  - `task_text` or structured array inputs depending on mode
- Advanced context accordion
  - `issue_ids`
  - `pr_url`
  - `changed_files`
  - `diff_text` for review
- Options panel
  - `include_tests`
  - `language`
  - `write_actions`
  - `approval_token`
- Footer action bar
  - Submit
  - Reset

### Primary components

- `WorkflowModeSwitcher`
- `PlanRequestForm`
- `ReviewRequestForm`
- `TestPlanRequestForm`
- `ArtifactRefsPanel`
- `RequestOptionsPanel`
- `FormValidationSummary`
- `SubmitActionBar`

### Validation rules

- `repo_id` required for all modes
- `branch` required for all modes
- `task_text` required for plan and review
- `implementation_plan[]` and `impacted_areas[]` required for test-plan
- review mode requires at least one of `diff_text`, `changed_files`, or `pr_url`
- if `write_actions` is non-empty, UI should encourage `approval_token` before submit

### State variants

- pristine
- editing
- client validation error
- request loading
- submit success redirecting
- API error

### Data mapping note

- form-level output language should map to request payload `options.language`
- optional `X-User-Language` may be used as a default request header, but this screen does not imply full app localization support

### Test scenarios

- submit valid plan
- block invalid review with missing context
- submit test-plan from prefilled plan output
- preserve form values on `409 CONFLICT`
- surface structured `422` validation errors

## 6.2 Screen: Run Detail

### Purpose

Primary inspection surface for all completed workflow outputs.

### Data source of truth

- immediate submit success may temporarily use the POST response for transition speed
- route entry, refresh, and long-lived rendering must use `GET /v1/workflows/{run_id}` as the source of truth
- screen rendering must combine top-level `RunDetailResponse` metadata with nested `RunDetailResponse.result`
- result-section branching must be based on `request_type` and the shape of `result`

### Layout zones

1. run header
2. status and warning strip
3. result content region
4. evidence region
5. metadata region
6. raw payload drawer
7. feedback region

### Wireframe structure

- Header row
  - page title
  - `run_id`
  - actions: copy run id, open trace
- Status strip
  - completion status
  - confidence badge
  - warnings summary
- Main body two-column desktop layout
  - left: overview and result panels
  - right: evidence and metadata cards
- Collapsible raw payload drawer
- Inline feedback form at bottom

### Primary components

- `RunHeader`
- `RunStatusStrip`
- `RunOverviewCard`
- `PlanResultPanel`
- `ReviewResultPanel`
- `TestPlanResultPanel`
- `EvidenceList`
- `WarningsBanner`
- `MetadataPanel`
- `RawJsonDrawer`
- `FeedbackForm`

### State variants

- loading
- successful plan result
- successful review result
- successful test-plan result
- degraded success
- `404 NOT_FOUND`
- `403 FORBIDDEN`

### Test scenarios

- render plan result sections
- render review result sections
- render test-plan result sections
- show degraded banner when warnings + low confidence exist
- open raw payload drawer and preserve JSON formatting
- fetch and render correctly on direct URL entry without relying on submit-memory state
- reload `/runs/:runId` and preserve correct rendering from fetched nested result payload

## 6.3 Screen: Trace

### Purpose

Show execution trust and debugging detail.

### Layout zones

1. trace header
2. trace summary metadata
3. step timeline
4. tool call table
5. error summary panel

### Wireframe structure

- Header
  - title
  - `trace_id`
  - back to run action
- Summary bar
  - exported time
  - model/prompt/skill version summary
- Timeline section
  - one row/card per step
- Tool call table
  - grouped or sorted by step
- Error summary card

### Primary components

- `TraceHeader`
- `TraceSummaryBar`
- `TraceTimeline`
- `TraceStepCard`
- `ToolCallTable`
- `ErrorSummaryCard`

### State variants

- loading
- trace with tool calls
- trace without tool calls
- failed trace with error summary
- `404 NOT_FOUND`

### Test scenarios

- render ordered steps
- render tool call table rows
- show error summary when provided
- render metadata from trace payload
- fetch and render correctly on direct URL entry or browser reload

## 6.4 Screen: Health

### Purpose

Operational readiness view.

### Layout zones

1. page header
2. overall status summary
3. connector card grid
4. explanatory note for degraded/unconfigured states

### Primary components

- `HealthHeader`
- `OverallStatusCard`
- `HealthStatusGrid`
- `ConnectorHealthCard`
- `StatusLegend`

### State variants

- loading
- overall ok
- overall degraded
- connector unconfigured mix
- API error

### Test scenarios

- show repo/docs connector states
- explain unconfigured issue/ci connectors
- distinguish degraded from failure messaging

## 7. Component Architecture

## 7.1 App shell and infrastructure

- `AppShell`
- `PrimaryNav`
- `TopBar`
- `AuthTokenDialog`
- `ApiErrorBanner`
- `AppRouter`

## 7.2 Shared form primitives

- `TextField`
- `TextareaField`
- `TokenField`
- `TagInputList`
- `EditableStringList`
- `ToggleField`
- `SelectField`
- `FormSection`

## 7.3 Workflow creation components

- `WorkflowModeSwitcher`
- `PlanRequestForm`
- `ReviewRequestForm`
- `TestPlanRequestForm`
- `ArtifactRefsPanel`
- `RequestOptionsPanel`
- `SubmitActionBar`

## 7.4 Result inspection components

- `RunHeader`
- `RunStatusStrip`
- `RunOverviewCard`
- `PlanResultPanel`
- `ReviewFindingList`
- `TestPlanResultPanel`
- `EvidenceList`
- `MetadataPanel`
- `RawJsonDrawer`

## 7.5 Trace and operational components

- `TraceTimeline`
- `TraceStepCard`
- `ToolCallTable`
- `HealthStatusGrid`
- `ConnectorHealthCard`

## 7.6 Feedback components

- `FeedbackForm`
- `FeedbackSuccessNotice`

## 8. Data Contracts and State Model

## 8.1 Global state

- bearer token (session-scoped)
- request language default
- latest run reference

## 8.2 Route state

- active workflow mode
- form draft for current mode
- fetched run detail
- fetched trace detail
- health snapshot

## 8.3 State rules

- current run detail and trace are fetched independently
- trace route must not depend on in-memory run result to function
- feedback submission success only affects feedback local state, not run payload refetch
- direct route entry must work from fetched API payloads alone
- local draft persistence is not baseline MVP state; it belongs to usability hardening

## 8.4 Error model

All endpoint errors should parse into a unified client shape:

- `code`
- `message`
- `request_id`
- `detail`
- `http_status`

## 9. UX State Matrix

| Situation | UI treatment | Keep current content? |
| --- | --- | --- |
| form loading | disable submit + spinner | yes |
| `401` | auth banner + token prompt | yes |
| `403` | scoped access message | yes |
| `404` | not found empty state | no |
| `409` | approval guidance banner | yes |
| `422` | field and summary validation display | yes |
| `429` | retry guidance banner | yes |
| `500` | generic failure with request id | yes |
| degraded `200` | amber warning banner + warnings list | yes |
| empty evidence | neutral empty-state note | yes |

## 10. Implementation Slices

## Slice 0 - Shell and client foundation

Includes:

- app shell
- route structure
- bearer token handling
- typed API client
- global structured error parser
- frontend test harness

Done when:

- app can render routes and call `/health`
- global error handling works for structured API errors

## Slice 1 - Plan workflow form

Includes:

- plan mode form
- client validation
- submit flow
- redirect to run detail

Done when:

- a valid plan request can be sent from the UI and navigates to the resulting run

## Slice 2 - Plan run detail inspection

Includes:

- plan result rendering
- evidence list
- warnings and degraded success treatment
- raw payload display

Done when:

- users can understand the full plan result without reading raw JSON only

## Slice 3 - Review workflow

Includes:

- review form
- review-specific validation rule
- review result rendering

Done when:

- users can submit review context and inspect verdict/findings

## Slice 4 - Test-plan workflow

Includes:

- test-plan form
- prefill from latest plan result
- result rendering

Done when:

- users can generate and inspect a structured test plan

## Slice 5 - Trace inspection

Includes:

- trace route
- timeline
- tool call table
- metadata and error summary

Done when:

- users can inspect execution details for a returned run

## Slice 6 - Health and feedback

Includes:

- health route
- connector status cards
- inline feedback submission on run detail

Done when:

- users can inspect system health and submit feedback from a run view

## Slice 7 - Usability hardening

Includes:

- local draft persistence
- copy/share run id
- trace search
- evidence filtering

Done when:

- primary workflows are faster to resume and inspect

## 11. TDD Strategy

For every screen-level feature, define tests in this order:

1. contract mapping test
2. validation/state unit test
3. component rendering test
4. integration test with mocked API response
5. golden-path end-to-end test

Required golden scenarios:

- plan happy path
- review happy path
- test-plan from plan-prefill path
- degraded success plan path
- `401` and `403` protected workflow path
- health degraded/unconfigured path

## 12. Traceability Matrix

| Screen | Primary components | API | Core states | Planned slice |
| --- | --- | --- | --- | --- |
| New Workflow | `WorkflowModeSwitcher`, request forms, options panel | `POST /v1/workflows/*` | pristine, editing, loading, validation error, API error | 1, 3, 4 |
| Run Detail | header, result panels, evidence list, metadata, raw payloads, feedback | `GET /v1/workflows/{run_id}`, `POST /v1/feedback` | loading, success, degraded, 403, 404 | 2, 6 |
| Trace | timeline, step card, tool call table | `GET /v1/workflows/{run_id}/trace` | loading, success, empty tool calls, 404 | 5 |
| Health | status grid, connector cards | `GET /health` | loading, ok, degraded, API error | 0, 6 |

## 13. Deferred Items

- run list/history page
- enterprise login experience
- server-driven recent runs
- multi-run comparison
- collaboration tools
- external connector browsing
- live progress streaming

## 14. Handoff Rule for Ralph

Ralph should use this document as the execution decomposition layer below `docs/frontend-prd-v1.md` and above the phased Ralph PRD.

Execution rule:

1. do not implement screens outside the listed routes first
2. complete each slice with tests before starting the next slice
3. do not invent unsupported backend state
4. treat degraded-success UX as a required feature, not a polish item
