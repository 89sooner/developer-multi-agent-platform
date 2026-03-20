# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-agent workflow service for internal developers. When a developer provides a natural language request for feature implementation, bug fixes, refactoring, or PR review, the service:
1. Collects context from code, docs, issues, and CI systems
2. Generates implementation plans with evidence
3. Creates test strategies and review notes
4. Returns structured responses with confidence levels

The architecture follows the **manager pattern** from openai-agents: a central Workflow Orchestrator owns the conversation and invokes specialist agents, rather than using handoff.

## Development Commands

```bash
# Development server with hot reload
make dev
# or: uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

# Production run
make run

# Run tests
make test
# or: pytest -q

# Linting
make lint   # Check code with ruff
make fmt    # Format code with ruff
```

## Architecture Overview

### Agent Layer (`src/app/agents/`)

- **`orchestrator.py`**: Classifies requests (feature/bugfix/refactor/review/test_plan), determines which specialist agents to invoke, and scores intent confidence using keyword matching in `INTENT_KEYWORDS`.
- **`repo_context.py`**: Searches repo, docs, issues for evidence. Calls tools from `src/app/tools/`.
- **`implementation.py`**: Generates change plans, target modules, API changes, rollback notes.
- **`test_strategy.py`**: Creates test scenarios (unit/integration/regression/edge cases).
- **`review.py`**: Reviews results for missing evidence, hidden dependencies, and risks.
- **`requirements.py`**: Normalizes natural language requirements into acceptance criteria.
- **`summary.py`**: Composes final `PlanResponse`, `ReviewResponse`, or `TestPlanResponse` objects.

All specialist agents use **structured outputs** (Pydantic models from `contracts/agent_results.py`).

### Tool Layer (`src/app/tools/`)

Provides uniform evidence objects from external systems. Current tools are stubs:
- `repo_search.py`: Git/code search
- `docs_search.py`: Document/wiki search
- `issue_lookup.py`: Issue tracker queries
- `ci_lookup.py`: CI/test result queries

All tools return standardized `Evidence` objects (via `contracts/responses.py`).

### Service Layer (`src/app/services/`)

- **`workflow_service.py`**: Core coordination. Orchestrates the agent sequence via `_execute_step()`, handling fallbacks and tracing. Methods: `create_plan()`, `create_review()`, `create_test_plan()`, `get_run()`, `get_trace()`, `create_feedback()`.
- **`skill_registry.py`**: Maps agent names to skill versions (used for canary rollouts).

### Storage (`src/app/storage/`)

`repositories.py` implements `SQLiteStore` with three tables:
- `runs`: workflow executions (status, timestamps, agents, models)
- `traces`: agent/tool invocation history
- `feedback`: user ratings and corrections

Files exported to `.runtime/traces/{run_id}.json`.

### Core (`src/app/core/`)

- **`config.py`**: Settings via `pydantic-settings`, loaded from `.env`.
- **`auth.py`**: `UserContext` with `user_id`, `repo_scopes`, `roles`.
- **`policy.py`**: Guardrails: `enforce_repo_scope()`, `require_approval()`.
- **`tracing.py`**: `TraceRecorder` tracks agent steps with status, confidence, errors.
- **`rate_limit.py`**: Request throttling.

### API (`src/app/api/`)

`router.py` includes:
- `/v1/workflows/plan` (POST)
- `/v1/workflows/review` (POST)
- `/v1/workflows/test-plan` (POST)
- `/v1/workflows/{run_id}` (GET)
- `/v1/workflows/{run_id}/trace` (GET)
- `/v1/feedback` (POST)

All routes validate via `UserContext` and apply repo scope enforcement.

### Contracts (`src/app/contracts/`)

- **`requests.py`**: `PlanRequest`, `ReviewRequest`, `TestPlanRequest`, `FeedbackRequest`
- **`responses.py`**: Response DTOs for API
- **`agent_results.py`**: Structured outputs for each agent (e.g., `RepoContextResult`, `ImplementationResult`, `ReviewResult`)

### Skills Directory (`skills/`)

Each skill contains:
- `SKILL.md`: Skill definition and purpose
- `agents/openai.yaml`: openai-agents configuration
- `references/`: Supporting docs, patterns, checklists

Skills map 1:1 to specialist agents. Prompt templates live in `prompts/`.

## Key Design Patterns

### Workflow Execution

1. `WorkflowService._run_orchestrator()` creates `run_id`, `trace_id` and classifies intent
2. `_start_run()` persists initial run state
3. Each agent step executes via `_execute_step()` with fallback handling
4. `TraceRecorder` captures timing, confidence, errors per step
5. `_finish_run()` updates run status and exports trace

### Agent Selection Rules (per `orchestrator.py`)

- feature/bugfix/refactor → requirements-planner + repo-context-finder + implementation-planner [+ test-strategy-generator if include_tests] + review-gate + summary-composer
- review → repo-context-finder + test-strategy-generator + review-gate + summary-composer
- test_plan → test-strategy-generator + summary-composer

### Confidence Levels

Order: `low < medium < high`. Collapsed via `collapse_confidence()`. Low confidence triggers warnings in final response.

### Fallback Behavior

Each agent has a `_fallback_*()` method in `WorkflowService` that returns degraded results with `confidence="low"` and explanatory messages.

## Current Implementation Status

- **Complete**: FastAPI skeleton, agent contracts, SQLite storage, orchestrator logic, policy layer, tracing
- **Stub**: All tools (`repo_search`, `docs_search`, `issue_lookup`, `ci_lookup`) return dummy evidence
- **Pending**: Actual openai-agents integration, real Git/docs/CI connectors

## Next Priorities (from README)

1. Implement `repo_search_tool` with actual Git/code search
2. Connect `run_store` and `trace_store` to all agents
3. Wire up orchestrator + specialist agents with openai-agents runtime
4. Add review phase and approval workflow
5. Integrate with IDE extension or internal web UI

## Important Constraints

- Write actions require explicit `approval_token` (enforced by `require_approval()`)
- Repo scope is enforced at tool layer via `UserContext.repo_scopes`
- Evidence must include: `source_type`, `source_id`, `locator`, `snippet`, `timestamp`, `confidence`
- All structured outputs use Pydantic for validation
- Korean (`ko`) is default response language
