# Ralph용 Frontend PRD v1: Operator Console for Workflow Backend

## 0. 문서 정보

- 문서 상태: draft v1.0
- 작성일: 2026-03-22
- 기반 문서: `docs/frontend-prd-v1.md`, `docs/frontend-ia-implementation-plan-v1.md`
- 목적: Ralph 가 프론트엔드 MVP 를 phase, epic, user story, acceptance criteria 단위로 바로 구현 계획에 옮길 수 있도록 고정한다.

## 1. 이 문서의 전제

이 문서는 현재 저장소의 백엔드 기능을 전제로 한 프론트엔드 실행 PRD 다. 따라서 이 문서는 제품 비전을 넓히는 문서가 아니라, 현재 API 기반 MVP 를 안전하게 UI 로 노출하는 문서다.

이 문서는 다음 결정을 고정한다.

- 첫 프론트엔드는 operator console 이다.
- primary surface 는 workflow submission + run inspection 이다.
- run history, async jobs, streaming, enterprise login 은 현 phase 에서 제외한다.
- 백엔드가 없는 기능은 프론트에서 암시하지 않는다.

## 2. 제품 정의

본 프론트엔드는 개발자, 리뷰어, 운영자가 현재 workflow backend 를 브라우저에서 사용할 수 있게 만드는 UI 계층이다. 사용자는 plan/review/test-plan 요청을 제출하고, 결과와 evidence 와 trace 를 inspect 하며, degraded mode 와 오류를 이해하고, run 에 대한 feedback 을 남길 수 있어야 한다.

핵심 원칙:

- backend-truth-first
- inspectability by default
- evidence-visible outputs
- degraded-state clarity
- no fake capability surface

## 3. 목표와 비목표

### 3.1 목표

- 사용자가 JSON 을 직접 작성하지 않고 workflow 요청을 제출할 수 있다.
- 사용자가 `run_id` 와 `trace_id` 기반으로 결과를 신뢰 가능하게 inspect 할 수 있다.
- degraded success 와 hard failure 를 명확히 구분할 수 있다.
- 운영자는 health 와 trace 로 현재 환경 상태를 이해할 수 있다.
- feedback submission 으로 결과 유용성을 남길 수 있다.

### 3.2 비목표

- 채팅형 AI assistant UI
- 실제 patch 적용 또는 PR 생성 UI
- live progress streaming
- run list/search dashboard
- 외부 system browser
- enterprise SSO 및 권한 관리 화면
- multi-user collaboration workspace

## 4. 명시적 제품 결정

### 4.1 사용자 표면

- MVP primary surface 는 web operator console 이다.
- 화면 구조는 `New Workflow`, `Run Detail`, `Trace`, `Health` 로 제한한다.
- `Feedback` 은 별도 top-level 화면이 아니라 `Run Detail` 내부 모듈이다.

### 4.2 실행 모델

- workflow submit 은 sync request/response 로 동작한다.
- 성공 submit 직후 사용자는 즉시 `Run Detail` 로 이동한다.
- async progress UI 는 backend 확장 전에는 만들지 않는다.

### 4.3 조회 모델

- 프론트는 `run_id` 기반 조회를 기본으로 한다.
- run history, 검색, 필터링은 phase 밖이다.
- `Run Detail` 은 top-level metadata 와 nested `RunDetailResponse.result` 를 함께 렌더링하는 모델을 사용한다.
- submit 직후 POST 응답은 즉시 전환 최적화로만 사용할 수 있고, direct entry 와 refresh 시에는 `GET /v1/workflows/{run_id}` 가 source of truth 다.

### 4.4 인증 모델

- MVP 는 bearer token 수동 입력 기반이다.
- token 부재/권한 부족/approval conflict 를 UI 에서 명확히 구분한다.

### 4.5 결과 표현 모델

- evidence, warnings, confidence, metadata 는 숨겨진 debug 정보가 아니라 핵심 UX 다.
- degraded `200` 은 에러가 아니라 제한된 성공으로 표현한다.

## 5. 사용자와 JTBD

### Persona A. 개발자

Job:

- 자연어 요청에서 구현 계획과 테스트 포인트를 빠르게 얻고 싶다.
- evidence 와 warnings 를 보고 결과를 믿어도 되는지 판단하고 싶다.

### Persona B. 리뷰어 / Tech Lead

Job:

- review 결과를 구조적으로 읽고 readiness 와 missing tests 를 빠르게 확인하고 싶다.
- trace 와 evidence 를 보고 weak reasoning 을 구분하고 싶다.

### Persona C. 운영자 / 플랫폼 엔지니어

Job:

- connector 상태와 trace 를 보고 현재 환경 제한과 실패 원인을 알고 싶다.

## 6. 범위 요약

| Phase | 이름 | 목표 | 사용자 가치 |
| --- | --- | --- | --- |
| Phase 0 | Frontend Foundation | shell, routing, auth token, API client, error model | 안전한 UI 기반 확보 |
| Phase 1 | Plan Workflow FUR | plan submit + run detail inspection | 첫 실사용 가능 릴리스 |
| Phase 2 | Review + Test Plan | review/test-plan workflow 확장 | 개발/리뷰 워크플로 확장 |
| Phase 3 | Trace + Health + Feedback | inspectability 와 운영 가시성 강화 | trust/ops usability 확보 |
| Phase 4 | Usability Hardening | drafts, trace search, evidence filtering, shareable identifiers | 반복 사용성 강화 |

## 7. 공통 프론트엔드 요구사항

모든 phase 에 공통으로 적용되는 규칙:

- 모든 protected request 는 bearer token 을 보낼 수 있어야 한다.
- 모든 structured API error 는 `code`, `message`, `request_id`, `detail` 로 파싱된다.
- degraded success 는 명시적 warning UI 를 가진다.
- unsupported backend capability 를 암시하는 client-only state 를 만들지 않는다.
- screen 과 component 는 current API contracts 에 직접 매핑되어야 한다.

## 8. Phase 0: Frontend Foundation

### 8.1 목표

프론트엔드가 현재 backend contracts 를 안전하게 호출하고 공통 상태를 처리할 수 있는 기반을 만든다.

### 8.2 In Scope

- app shell
- route structure
- bearer token input
- typed API client
- structured error parser
- shared loading/error primitives
- test harness

### 8.3 Out of Scope

- workflow-specific rich rendering
- run result interpretation
- trace visualization

### 8.4 Epic

#### Epic F0-A. App Shell and Networking Foundation

#### US-F0.1 라우팅과 앱 쉘 구성

As a user, I want a stable app shell and route structure so that I can move between workflow creation, run detail, trace, and health consistently.

Acceptance Criteria:

- 앱은 최소 `/workflows/new`, `/runs/:runId`, `/runs/:runId/trace`, `/health` route 를 가진다.
- top bar 와 primary navigation 이 모든 route 에서 일관되게 보인다.
- 모바일에서는 navigation 이 collapse 가능한 drawer 또는 동등 UX 로 동작한다.
- route 진입 시 unsupported page 나 placeholder 가 아닌 실제 shell state 가 렌더링된다.

#### US-F0.2 bearer token 입력과 protected request 처리

As a user, I want to provide a bearer token once per session so that I can call protected workflow APIs without manually editing headers.

Acceptance Criteria:

- 사용자는 session 범위에서 bearer token 을 입력/수정/삭제할 수 있다.
- protected API request 는 token 이 있으면 `Authorization: Bearer <token>` 을 보낸다.
- token 없이 protected endpoint 호출 시 `401` 응답을 적절히 안내한다.
- token 값은 장기 저장소에 강제 영속화되지 않는다.

#### US-F0.3 structured error parsing 공통화

As a frontend engineer, I want all API errors normalized into one client shape so that every screen can handle backend failures consistently.

Acceptance Criteria:

- 에러 응답은 최소 `http_status`, `code`, `message`, `request_id`, `detail` 로 파싱된다.
- `401`, `403`, `404`, `409`, `422`, `429`, `500` 가 구분된 UI copy 를 가진다.
- form screen 은 `422` detail 을 field-level 또는 summary-level validation 으로 표시할 수 있다.
- 에러 파서는 health 와 workflow endpoint 에 공통 사용된다.

### 8.5 Phase Exit Criteria

- shell 과 route 구조가 동작한다.
- bearer token 입력과 protected request 처리가 가능하다.
- structured error 파싱이 공통 모듈로 동작한다.
- foundation component/integration tests 가 준비된다.

## 9. Phase 1: Plan Workflow First Usable Release

### 9.1 목표

개발자가 plan 요청을 제출하고 결과를 inspect 할 수 있는 first usable release 를 만든다.

### 9.2 In Scope

- plan request form
- request options panel
- submit loading state
- run detail overview
- plan result rendering
- evidence rendering
- degraded success banner
- raw payload inspection

### 9.3 Out of Scope

- review/test-plan form
- trace 전용 화면
- health 화면

### 9.4 Epic

#### Epic F1-A. Plan Request Submission

#### US-F1.1 자연어 plan 요청 제출

As a developer, I want to submit a plan request without hand-writing JSON so that I can get an actionable implementation plan quickly.

Acceptance Criteria:

- 사용자는 `repo_id`, `branch`, `task_text` 를 입력해 plan 요청을 보낼 수 있다.
- 사용자는 optional 하게 `issue_ids`, `pr_url`, `changed_files`, `include_tests`, `language`, `write_actions`, `approval_token` 을 입력할 수 있다.
- submit 중에는 중복 제출이 방지된다.
- 성공 시 UI 는 반환된 `run_id` 기반으로 `Run Detail` 화면으로 이동한다.

#### US-F1.2 approval conflict 와 validation error 처리

As a developer, I want invalid or policy-blocked requests explained clearly so that I can fix inputs without losing work.

Acceptance Criteria:

- `409 CONFLICT` 가 오면 approval token 요구사항을 설명한다.
- `422 VALIDATION_ERROR` 가 오면 잘못된 필드를 수정할 수 있게 표시한다.
- 현재 form 입력값은 오류 발생 후에도 유지된다.
- `request_id` 가 있으면 화면에 노출된다.

#### Epic F1-B. Plan Result Inspection

#### US-F1.3 plan 결과 구조화 렌더링

As a developer, I want plan results rendered in semantic sections so that I can act on them immediately.

Acceptance Criteria:

- `summary`, `impacted_areas`, `implementation_plan`, `tests`, `risks`, `open_questions` 가 별도 섹션으로 렌더링된다.
- `primary_intent`, `secondary_intents`, `selected_agents`, `status`, `confidence` 가 overview 에 노출된다.
- `run_id`, `trace_id`, `model_version`, `skill_versions`, `prompt_versions`, `user_id`, `repo_scope` 가 metadata 로 inspect 가능하다.
- raw request/result payload 를 접을 수 있는 drawer 또는 동등 UI 가 존재한다.
- 브라우저 refresh 또는 direct URL entry 시에도 `GET /v1/workflows/{run_id}` payload 만으로 같은 화면을 복원할 수 있다.
- 화면 구현은 flattened submit response 가 아니라 `RunDetailResponse.result` 기반 result-section branching 을 사용한다.

#### US-F1.4 evidence 와 degraded success 노출

As a tech lead, I want weak or limited plan results to disclose evidence quality and warnings so that I do not over-trust them.

Acceptance Criteria:

- evidence 는 `source_type`, `locator`, `snippet`, `confidence`, `timestamp` 를 표시할 수 있다.
- warning 이 있고 confidence 가 낮거나 약화된 경우 degraded banner 를 보여준다.
- degraded banner 는 결과를 숨기지 않고 함께 노출된다.
- evidence 가 비어 있어도 empty state 를 보여주며 페이지가 깨지지 않는다.

### 9.5 Phase Exit Criteria

- plan form submit 이 동작한다.
- 성공 시 run detail 로 이동해 결과를 읽을 수 있다.
- validation/policy/degraded states 가 구분된다.
- plan happy path 와 degraded path 테스트가 존재한다.

## 10. Phase 2: Review + Test Plan Expansion

### 10.1 목표

개발/리뷰 워크플로에 필요한 review 와 test-plan 화면을 추가한다.

### 10.2 In Scope

- review mode form
- review-specific validation
- review result rendering
- test-plan form
- plan-result 기반 prefill
- test-plan result rendering

### 10.3 Out of Scope

- review/test-plan beyond current backend contracts
- cross-run comparison

### 10.4 Epic

#### Epic F2-A. Review Workflow

#### US-F2.1 review context 입력 규칙 적용

As a reviewer, I want the UI to require enough review context so that I do not send weak review requests by accident.

Acceptance Criteria:

- review mode 에서는 `diff_text`, `changed_files`, `pr_url` 중 하나 이상이 있어야 submit 가능하다.
- 사용자는 `task_text`, `repo_id`, `branch` 와 함께 review context 를 입력할 수 있다.
- invalid review state 는 client-side validation 으로 막힌다.
- submit 성공 시 review 결과 run detail 로 이동한다.

#### US-F2.2 review 결과와 readiness verdict 렌더링

As a reviewer, I want review findings and readiness verdict shown clearly so that I can decide next action quickly.

Acceptance Criteria:

- `review_findings`, `missing_tests`, `risks`, `readiness_verdict`, `evidence` 를 렌더링한다.
- verdict 는 시각적으로 구분된다 (`ready`, `needs_changes`, `blocked`).
- review 결과도 warnings/confidence/degraded handling 규칙을 공유한다.
- evidence 와 metadata 섹션은 plan 결과와 동일한 패턴으로 inspect 가능하다.

#### Epic F2-B. Test Plan Workflow

#### US-F2.3 plan 결과에서 test-plan prefill

As a developer, I want to reuse an existing plan result when creating a test plan so that I do not re-enter structured arrays manually.

Acceptance Criteria:

- 직전 plan result 가 메모리에 있으면 `implementation_plan` 과 `impacted_areas` 를 prefill 할 수 있다.
- 사용자는 prefilled 배열을 편집할 수 있다.
- prefill 데이터가 없어도 수동 입력으로 submit 가능하다.
- prefill 은 unsupported server-side history 를 전제로 하지 않는다.

#### US-F2.4 test-plan 결과 구조화 렌더링

As a developer, I want a dedicated test-plan result view so that I can turn plan output into QA action items.

Acceptance Criteria:

- `unit_tests`, `integration_tests`, `regression_targets`, `edge_cases`, `execution_order` 를 섹션으로 렌더링한다.
- test-plan response 는 run detail 구조 안에서 일관되게 표현된다.
- raw payload 와 metadata inspect 경로를 유지한다.
- degraded state 처리 규칙을 공유한다.

### 10.5 Phase Exit Criteria

- review form 과 result rendering 이 동작한다.
- test-plan prefill 과 수동 입력이 모두 동작한다.
- review/test-plan 전용 validation 과 result tests 가 존재한다.

## 11. Phase 3: Trace + Health + Feedback

### 11.1 목표

운영 가시성과 inspectability 를 강화한다.

### 11.2 In Scope

- trace route
- timeline / tool call rendering
- health route
- connector status cards
- inline feedback submission

### 11.3 Out of Scope

- admin analytics dashboard
- feedback history page

### 11.4 Epic

#### Epic F3-A. Trace Inspection

#### US-F3.1 실행 step 과 tool call inspect

As a user, I want to inspect ordered execution steps and tool calls so that I can understand what the system did and where it degraded or failed.

Acceptance Criteria:

- trace 화면은 ordered step list 를 렌더링한다.
- 각 step 은 `status`, `started_at`, `ended_at`, `latency_ms`, `tool_calls`, `confidence`, `input_ref`, `output_ref`, `error_message` 를 표시할 수 있다.
- tool call table 은 `tool_name`, `status`, `duration_ms`, `input_summary`, `output_count`, `error_message` 를 렌더링한다.
- `error_summary` 와 trace-level `metadata` 를 함께 보여준다.
- direct URL entry 또는 refresh 시에도 `GET /v1/workflows/{run_id}/trace` 만으로 화면을 복원할 수 있다.

#### Epic F3-B. Health Visibility

#### US-F3.2 connector health 상태 시각화

As an operator, I want to see overall health and connector-specific status so that I understand whether the environment is fully usable or limited.

Acceptance Criteria:

- health 화면은 overall `status` 와 backend `version` 을 보여준다.
- connector 카드가 `repo`, `docs`, `issue`, `ci` 상태를 렌더링한다.
- `degraded` 와 `unconfigured` 는 서로 다른 설명을 가진다.
- health API 실패 시 별도 error state 를 보여준다.

#### Epic F3-C. Feedback Capture

#### US-F3.3 run 기반 feedback 제출

As a user, I want to submit simple usefulness feedback after reading a result so that the team can improve quality.

Acceptance Criteria:

- `Run Detail` 화면에서 `rating`, `useful`, `comment` 를 입력할 수 있다.
- submit 성공 시 confirmation state 를 보여준다.
- 같은 client session 안에서 중복 submit 을 방지할 수 있다.
- feedback UI 는 별도 top-level route 없이 동작한다.

### 11.5 Phase Exit Criteria

- trace inspect flow 가 동작한다.
- health 화면이 connector 상태를 설명한다.
- feedback submit 이 run detail 안에서 완료된다.
- trace/health/feedback 관련 integration tests 가 존재한다.

## 12. Phase 4: Usability Hardening

### 12.1 목표

새 backend capability 추가 없이 반복 사용성과 inspect efficiency 를 높인다.

### 12.2 In Scope

- local draft persistence
- copy/share `run_id`
- evidence filtering
- trace search
- empty/error/help copy polishing

### 12.3 Out of Scope

- backend search/list features
- multi-user collaboration

### 12.4 Epic

#### Epic F4-A. Workflow Continuity

#### US-F4.1 local draft persistence

As a user, I want unfinished workflow input preserved locally so that I can recover from refresh or accidental navigation.

Acceptance Criteria:

- form draft 는 mode 별로 로컬에 저장될 수 있다.
- submit 성공 또는 explicit reset 시 draft 를 비울 수 있다.
- 토큰과 민감값은 보수적으로 저장하거나 제외한다.
- draft persistence 는 route 전환 후에도 복원 가능하다.

#### Epic F4-B. Faster Inspection

#### US-F4.2 evidence filtering 과 trace search

As a user, I want to narrow down evidence and trace content quickly so that large responses remain readable.

Acceptance Criteria:

- evidence 는 최소 source type 또는 text 기준 필터링이 가능하다.
- trace 화면은 step/tool call 수준 검색 또는 필터를 지원한다.
- 필터 적용은 현재 페이지 메모리 상태 안에서 동작한다.
- 필터가 없어도 기본 화면 readability 가 유지된다.

#### US-F4.3 copy/share run identifier

As a user, I want to copy a run or trace identifier quickly so that I can hand off investigation or bookmark the result.

Acceptance Criteria:

- `run_id` 와 `trace_id` copy action 이 존재한다.
- copy 성공 피드백이 UI 에 표시된다.
- deep link route 로 다시 열 수 있다.
- server-side recent-runs feature 없이도 재진입 가능하다.

### 12.5 Phase Exit Criteria

- drafts, filtering, and identifier sharing improve primary workflows without new backend dependencies.
- usability-hardening tests 가 존재한다.

## 13. 비기능 요구사항

### 13.1 성능

- primary route 전환은 불필요한 full-page reload 없이 동작해야 한다.
- 결과 화면은 중간 크기 JSON payload 에서도 readable 해야 한다.

### 13.2 신뢰성

- degraded `200` 를 실패처럼 잘못 표기하면 안 된다.
- route direct entry 시 필요한 fetch 만으로 동작해야 한다.
- protected request 에서 token 누락 시 UX 가 즉시 복구 가능해야 한다.

### 13.3 보안

- bearer token 은 장기 insecure storage 에 기본 저장하지 않는다.
- raw payload rendering 시 민감정보를 추가 로그로 남기지 않는다.

### 13.4 감사/추적성

- `run_id`, `trace_id`, `request_id` 는 UI 에서 inspect/copy 가능해야 한다.
- model/prompt/skill version metadata 는 숨기지 않는다.

## 14. 성공 지표

### 14.1 Phase 1

- 사용자가 plan submit 부터 result inspection 까지 완료할 수 있다.
- degraded result 와 hard error 를 혼동하지 않는다.

### 14.2 Phase 2

- review 와 test-plan flow 가 각각 독립적으로 완료 가능하다.
- prefill 로 test-plan 작성 시간이 단축된다.

### 14.3 Phase 3

- 운영자/리뷰어가 trace 와 health 로 현재 상태를 설명할 수 있다.
- feedback submit 성공률이 안정적으로 유지된다.

### 14.4 Phase 4

- draft 복원, filtering, identifier sharing 으로 반복 사용 효율이 개선된다.

## 15. 의존성과 가정

- backend contracts 는 현재 문서 기준으로 유지된다.
- `run_id` 와 `trace_id` 기반 fetch 는 안정적으로 동작한다.
- frontend 는 framework-agnostic 하되 typed client 구성이 가능하다.

## 16. 남은 오픈 질문

1. bearer token 입력 UX 를 modal, inline top bar, settings panel 중 무엇으로 둘 것인가.
2. local draft persistence 범위를 memory only 로 둘지 session storage 까지 허용할지.
3. evidence filtering 기본 기준을 source type 우선으로 둘지 free-text 우선으로 둘지.
4. 추후 backend 가 run listing 을 추가하면 navigation 구조를 어떻게 확장할지.

## 17. Ralph 실행 지침

Ralph 는 이 문서를 구현 입력으로 사용할 때 다음 순서를 따른다.

1. Phase 0 foundation 없이 workflow-specific UI 부터 시작하지 않는다.
2. Phase 1 을 first usable release 로 고정하고 plan flow 를 먼저 완성한다.
3. 각 story 는 대응되는 component/integration/E2E test 로 증명 가능해야 한다.
4. unsupported backend capability 를 보완하려고 client-only fake state 를 추가하지 않는다.
5. degraded-state clarity 와 inspectability 를 시각 polish 보다 우선한다.
