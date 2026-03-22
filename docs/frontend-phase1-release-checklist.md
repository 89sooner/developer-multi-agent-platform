# Frontend Phase 1 Release Checklist

Date: 2026-03-22

## Scope

This checklist documents the first usable release gate for the plan-first frontend experience.

## Release Gate

- [x] `New Workflow` renders a real plan form instead of a placeholder shell.
- [x] Required fields (`repo_id`, `branch`, `task_text`) block invalid submission.
- [x] Optional artifact and request option inputs are available.
- [x] Successful `POST /v1/workflows/plan` transitions to `Run Detail`.
- [x] `409`, `422`, `401`, and `403` paths preserve the current draft and expose `request_id` when present.
- [x] `Run Detail` uses `GET /v1/workflows/{run_id}` as the source of truth for direct entry and refresh-safe rendering.
- [x] Plan result sections render `summary`, `impacted_areas`, `implementation_plan`, `tests`, `risks`, and `open_questions`.
- [x] Evidence cards render `source_type`, `locator`, `snippet`, `confidence`, and `timestamp`.
- [x] Degraded `200` responses remain visible and are clearly marked with warnings + low confidence.
- [x] Raw request/result payloads are available through a secondary inspectability surface.
- [x] Metadata exposes `run_id`, `trace_id`, `model_version`, `skill_versions`, `prompt_versions`, `user_id`, and `repo_scope`.
- [x] Frontend route tests cover submit happy path, direct entry, auth/policy errors, degraded mode, and inspectability.

## Validation Commands

- [x] `npm --prefix frontend test`
- [x] `npm --prefix frontend run build`
- [x] `lsp_diagnostics` clean for changed `frontend/src/**/*.ts` and `frontend/src/**/*.tsx`
