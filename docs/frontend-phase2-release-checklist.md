# Frontend Phase 2 Release Checklist

Date: 2026-03-22

## Scope

This checklist documents the release gate for the review and test-plan expansion on top of the completed Phase 1 plan-first frontend.

## Release Gate

- [x] `/workflows/new?mode=review` renders a dedicated review form.
- [x] Review mode blocks submit unless at least one of `diff_text`, `changed_files`, or `pr_url` is present.
- [x] Successful review submission transitions to a review-shaped run detail screen.
- [x] Review run detail renders `review_findings`, `missing_tests`, `risks`, `readiness_verdict`, evidence, metadata, and degraded-state warnings.
- [x] `/workflows/new?mode=test-plan` renders a dedicated test-plan form using only backend-supported fields.
- [x] Test-plan mode supports both manual entry and plan-result prefill from the Phase 1 plan run detail.
- [x] Successful test-plan submission transitions to a test-plan run detail screen.
- [x] Test-plan run detail renders `unit_tests`, `integration_tests`, `regression_targets`, `edge_cases`, and `execution_order`.
- [x] Shared run detail inspectability remains available for review/test-plan via metadata and raw payload drawer.
- [x] Shared release-gate tests cover plan regression, review happy path, and test-plan prefill path.
- [x] Repo hygiene updates are in place for frontend-generated artifacts via `.gitignore`.

## Validation Commands

- [x] `npm --prefix frontend test`
- [x] `npm --prefix frontend run build`
- [x] `lsp_diagnostics frontend/src/routes/WorkflowsNewRoute.tsx`
- [x] `lsp_diagnostics frontend/src/routes/RunDetailRoute.tsx`
- [x] `lsp_diagnostics frontend/src/components/workflows/runDetailAdapter.ts`
- [x] `lsp_diagnostics frontend/src/test/workflows-new-route.test.tsx`
- [x] `lsp_diagnostics frontend/src/test/run-route.test.tsx`
- [x] `lsp_diagnostics frontend/src/test/workflow-release-gate.test.tsx`
