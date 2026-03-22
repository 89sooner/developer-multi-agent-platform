# Ralph용 Frontend Phase 0/1 구현 Backlog

작성일: 2026-03-22  
기준 문서: `docs/frontend-prd-ralph-v1.md`, `docs/frontend-ia-implementation-plan-v1.md`

## 1. 목적

이 문서는 `docs/frontend-prd-ralph-v1.md` 의 Phase 0, Phase 1 범위를 Ralph 가 바로 실행 가능한 frontend issue backlog 로 분해한 문서다.

목표:

- 프론트엔드 MVP 의 foundation 과 first usable release 구현 순서를 고정한다.
- 각 issue 가 route, component, state, API contract, 테스트 기준을 함께 갖도록 만든다.
- Phase 0 완료 전 Phase 1 이 섞이지 않도록 dependency 를 명확히 둔다.
- direct-entry, degraded success, structured error handling 같은 비가시적 핵심 요구를 backlog 단계에서 누락하지 않는다.

## 2. Backlog 운영 규칙

### 2.1 이슈 ID 규칙

- `FRLP-P0-0X`: Frontend Phase 0 issue
- `FRLP-P1-0X`: Frontend Phase 1 issue

### 2.2 상태 규칙

- `todo`
- `in_progress`
- `blocked`
- `review`
- `done`

### 2.3 우선순위 규칙

- `Must`: phase exit criteria 와 first usable release 에 직접 연결되는 필수 이슈
- `Should`: phase 안에서 강하게 권장되지만 직접 게이트는 아닌 이슈

### 2.4 크기 규칙

- `S`: 0.5~1일
- `M`: 1~3일
- `L`: 3~5일

### 2.5 공통 Definition of Done

모든 issue 는 아래를 만족해야 `done` 으로 본다.

- 코드가 저장소에 반영되어 있다.
- 관련 unit/component/integration test 가 추가되거나 갱신되어 있다.
- route direct-entry 또는 refresh 영향이 있으면 해당 동작이 테스트된다.
- structured error 또는 degraded state 영향이 있으면 최소 1개 이상 상태 테스트가 존재한다.
- 문서화된 contract 와 실제 UI state 가 어긋나지 않는다.

## 3. Critical Path

### Phase 0 Critical Path

1. `FRLP-P0-01` App shell and routing foundation
2. `FRLP-P0-02` Typed API client and structured error normalization
3. `FRLP-P0-03` Session-scoped bearer token handling
4. `FRLP-P0-04` Shared UI state primitives and screen scaffolds
5. `FRLP-P0-05` Frontend test harness and contract fixtures

### Phase 1 Critical Path

1. `FRLP-P1-01` Plan workflow form happy path
2. `FRLP-P1-02` Plan form validation and policy-error recovery
3. `FRLP-P1-03` Run detail route and nested result mapping
4. `FRLP-P1-04` Plan result rendering and evidence inspection
5. `FRLP-P1-05` Degraded success and structured error UX
6. `FRLP-P1-06` Raw payload + metadata inspection hardening
7. `FRLP-P1-07` Phase 1 golden path and release verification

## 4. Phase 0 Backlog

### FRLP-P0-01 App Shell and Route Foundation

- Phase: `Phase 0`
- Priority: `Must`
- Size: `M`
- Depends on: 없음

Goal:

- 모든 이후 화면이 올라갈 수 있는 최소 앱 shell 과 route 구조를 만든다.

Scope:

- app root
- route registration
- primary navigation
- top bar
- direct-entry-capable route shells

Out of Scope:

- workflow-specific rich rendering
- health data fetch

Deliverables:

- app shell layout
- `/workflows/new`, `/runs/:runId`, `/runs/:runId/trace`, `/health` route scaffolds
- desktop/mobile navigation behavior

Acceptance Criteria:

- 앱은 최소 `/workflows/new`, `/runs/:runId`, `/runs/:runId/trace`, `/health` route 를 가진다.
- top bar 와 primary navigation 이 모든 route 에서 일관되게 보인다.
- 모바일에서는 navigation 이 collapse 가능한 drawer 또는 동등 UX 로 동작한다.
- direct URL entry 시 placeholder 가 아니라 실제 route shell 이 렌더링된다.

### FRLP-P0-02 Typed API Client and Structured Error Normalization

- Phase: `Phase 0`
- Priority: `Must`
- Size: `M`
- Depends on: `FRLP-P0-01`

Goal:

- backend contracts 를 타입 안전하게 호출하고 모든 에러를 공통 shape 로 다룰 수 있게 한다.

Scope:

- typed request/response adapters
- common fetch wrapper
- structured error parser
- protected/public endpoint split

Out of Scope:

- screen-specific error copy polish

Deliverables:

- API client module
- error normalization module
- contract fixture mocks

Acceptance Criteria:

- workflow submit, run detail, trace, feedback, health 호출 함수를 공통 client 에서 제공한다.
- 에러 응답은 최소 `http_status`, `code`, `message`, `request_id`, `detail` 로 파싱된다.
- `401`, `403`, `404`, `409`, `422`, `429`, `500` 을 구분 가능한 shape 로 반환한다.
- health 와 protected endpoint 가 같은 error parser 를 공유한다.

### FRLP-P0-03 Session Bearer Token Handling

- Phase: `Phase 0`
- Priority: `Must`
- Size: `S`
- Depends on: `FRLP-P0-02`

Goal:

- 사용자가 session 범위에서 token 을 입력하고 protected request 에 자동 적용할 수 있게 한다.

Scope:

- token input UI
- session-scoped token state
- protected request authorization header injection
- token reset/edit flow

Out of Scope:

- enterprise login
- long-lived credential storage

Deliverables:

- token dialog or equivalent UI
- auth state store
- authorization header binding

Acceptance Criteria:

- 사용자는 session 범위에서 bearer token 을 입력/수정/삭제할 수 있다.
- protected request 는 token 이 있으면 `Authorization: Bearer <token>` 을 보낸다.
- token 없이 protected endpoint 호출 시 `401` 회복 UX 가 가능하다.
- token 은 장기 insecure storage 에 강제 저장되지 않는다.

### FRLP-P0-04 Shared Screen State Primitives and Global Status UX

- Phase: `Phase 0`
- Priority: `Must`
- Size: `M`
- Depends on: `FRLP-P0-01`, `FRLP-P0-02`

Goal:

- 모든 이후 화면이 공통 loading/error/degraded status 를 일관되게 사용할 수 있도록 한다.

Scope:

- loading primitives
- API error banner
- degraded warning banner
- empty state primitives
- request-id display helpers

Out of Scope:

- plan-specific result layouts

Deliverables:

- `ApiErrorBanner`
- `WarningsBanner`
- loading and empty-state components
- common screen state helpers

Acceptance Criteria:

- 공통 UI 는 loading, empty, structured error, degraded-success state 를 표현할 수 있다.
- `request_id` 가 있는 에러는 공통 배너에서 노출 가능하다.
- degraded `200` state 는 에러와 구분된 시각 treatment 를 가진다.
- 공통 상태 컴포넌트는 최소 한 개 이상의 route shell 에 통합된다.

### FRLP-P0-05 Frontend Test Harness and Contract Fixtures

- Phase: `Phase 0`
- Priority: `Must`
- Size: `M`
- Depends on: `FRLP-P0-01`, `FRLP-P0-02`, `FRLP-P0-03`, `FRLP-P0-04`

Goal:

- 이후 story 들을 acceptance criteria 기준으로 검증할 수 있는 테스트 기반을 만든다.

Scope:

- test runner/config
- route render helpers
- mocked API layer
- contract fixture examples
- golden route-entry harness

Out of Scope:

- plan-specific detailed fixtures beyond foundation coverage

Deliverables:

- frontend test harness
- API mock fixtures
- route direct-entry test utilities

Acceptance Criteria:

- route/component/integration 테스트를 실행할 수 있다.
- mocked backend contract fixture 로 health 와 protected request 흐름을 검증할 수 있다.
- direct-entry route 테스트 유틸리티가 존재한다.
- foundation regression 을 막는 최소 smoke suite 가 존재한다.

## 5. Phase 1 Backlog

### FRLP-P1-01 Plan Workflow Form Happy Path

- Phase: `Phase 1`
- Priority: `Must`
- Size: `M`
- Depends on: `FRLP-P0-05`

Goal:

- 사용자가 JSON 없이 plan 요청을 보낼 수 있는 first usable entry flow 를 만든다.

Scope:

- plan mode form
- `repo_id`, `branch`, `task_text` core fields
- optional artifact and options inputs
- submit loading and success transition

Out of Scope:

- review/test-plan mode

Deliverables:

- `PlanRequestForm`
- `ArtifactRefsPanel`
- `RequestOptionsPanel`
- submit action wiring

Acceptance Criteria:

- 사용자는 `repo_id`, `branch`, `task_text` 를 입력해 plan 요청을 보낼 수 있다.
- optional 하게 `issue_ids`, `pr_url`, `changed_files`, `include_tests`, `language`, `write_actions`, `approval_token` 을 입력할 수 있다.
- submit 중에는 중복 제출이 방지된다.
- 성공 시 반환된 `run_id` 기반으로 `Run Detail` 화면으로 이동한다.

### FRLP-P1-02 Plan Validation and Policy Error Recovery

- Phase: `Phase 1`
- Priority: `Must`
- Size: `S`
- Depends on: `FRLP-P1-01`

Goal:

- validation/policy/auth 오류가 발생해도 사용자가 입력을 잃지 않고 복구할 수 있게 한다.

Scope:

- field validation summary
- `409` approval conflict handling
- `422` validation detail handling
- `401` token recovery
- `403` scope explanation

Out of Scope:

- advanced retry policies

Deliverables:

- validation summary UI
- policy/auth error recovery copy
- preserved form state behavior

Acceptance Criteria:

- `409 CONFLICT` 가 오면 approval token 요구사항을 설명한다.
- `422 VALIDATION_ERROR` 가 오면 잘못된 필드를 수정할 수 있게 표시한다.
- `401` 과 `403` 에 대해 분리된 회복/안내 UX 가 존재한다.
- 오류 발생 후에도 현재 form 입력값은 유지된다.
- structured error 에 `request_id` 가 존재하면 화면에서 inspect 가능하다.

### FRLP-P1-03 Run Detail Route and Nested Result Mapping

- Phase: `Phase 1`
- Priority: `Must`
- Size: `M`
- Depends on: `FRLP-P1-01`

Goal:

- run detail 을 direct entry 와 refresh 에서도 안정적으로 복원 가능한 형태로 만든다.

Scope:

- `/runs/:runId` fetch
- top-level metadata mapping
- nested `RunDetailResponse.result` mapping
- request-type-based result branching

Out of Scope:

- trace 화면

Deliverables:

- run detail data adapter
- route loader/fetch logic
- plan/review/test-plan branching helpers

Acceptance Criteria:

- `GET /v1/workflows/{run_id}` payload 만으로 `Run Detail` 을 렌더링할 수 있다.
- 화면 구현은 top-level metadata 와 nested `result` 를 함께 사용한다.
- 브라우저 refresh 와 direct URL entry 시에도 같은 화면을 복원할 수 있다.
- submit 직후 POST response 는 immediate transition optimization 으로만 사용되고 source of truth 로 가정되지 않는다.

### FRLP-P1-04 Plan Result Rendering and Evidence Inspection

- Phase: `Phase 1`
- Priority: `Must`
- Size: `M`
- Depends on: `FRLP-P1-03`

Goal:

- plan 결과를 의미 있는 섹션으로 나눠 바로 실행 가능한 정보로 보여준다.

Scope:

- overview section
- result sections
- evidence cards
- metadata panel

Out of Scope:

- raw payload drawer

Deliverables:

- `RunOverviewCard`
- `PlanResultPanel`
- `EvidenceList`
- `MetadataPanel`

Acceptance Criteria:

- `summary`, `impacted_areas`, `implementation_plan`, `tests`, `risks`, `open_questions` 가 별도 섹션으로 렌더링된다.
- `primary_intent`, `secondary_intents`, `selected_agents`, `status`, `confidence` 가 overview 에 노출된다.
- evidence 는 `source_type`, `locator`, `snippet`, `confidence`, `timestamp` 를 표시할 수 있다.
- evidence 가 비어 있어도 empty state 를 보여주며 페이지가 깨지지 않는다.

### FRLP-P1-05 Degraded Success and Structured Error UX

- Phase: `Phase 1`
- Priority: `Must`
- Size: `S`
- Depends on: `FRLP-P1-03`, `FRLP-P1-04`

Goal:

- 성공이지만 제한된 결과와 실제 실패를 명확히 구분한다.

Scope:

- degraded banner
- warnings list
- route-level structured error treatment
- request-id visibility

Out of Scope:

- trace-specific failure visualization

Deliverables:

- degraded success banner behavior
- run-detail error-state composition

Acceptance Criteria:

- warning 이 있고 confidence 가 낮거나 약화된 경우 degraded banner 를 보여준다.
- degraded banner 는 결과를 숨기지 않고 함께 노출된다.
- `/runs/:runId` direct-entry 또는 refresh 에서 `401` 이 발생하면 token recovery UX 를 제공한다.
- `404` 와 `403` 는 run detail 에서 distinct state 로 보인다.
- `request_id` 가 존재하는 에러는 화면에서 inspect 가능하다.

### FRLP-P1-06 Raw Payload and Metadata Inspection Hardening

- Phase: `Phase 1`
- Priority: `Must`
- Size: `S`
- Depends on: `FRLP-P1-03`, `FRLP-P1-04`

Goal:

- 기술 사용자가 request/result 와 version metadata 를 더 깊게 inspect 할 수 있게 한다.

Scope:

- raw payload drawer
- version metadata display
- `run_id` / `trace_id` visibility

Out of Scope:

- copy/share polish

Deliverables:

- `RawJsonDrawer`
- extended metadata view

Acceptance Criteria:

- raw request/result payload 를 접을 수 있는 drawer 또는 동등 UI 가 존재한다.
- `run_id`, `trace_id`, `model_version`, `skill_versions`, `prompt_versions`, `user_id`, `repo_scope` 를 inspect 할 수 있다.
- raw payload 는 결과 화면 readability 를 해치지 않는 보조 surface 로 배치된다.
- drawer 상태와 표시 내용에 대한 component test 가 존재한다.

### FRLP-P1-07 Phase 1 Golden Path and Release Verification

- Phase: `Phase 1`
- Priority: `Must`
- Size: `M`
- Depends on: `FRLP-P1-02`, `FRLP-P1-03`, `FRLP-P1-04`, `FRLP-P1-05`, `FRLP-P1-06`

Goal:

- plan frontend FUR 의 출시 여부를 판단할 수 있는 품질 게이트를 만든다.

Scope:

- plan happy path integration
- direct-entry/reload verification
- degraded success verification
- auth/policy error verification
- release checklist

Out of Scope:

- review/test-plan flow verification

Deliverables:

- golden scenario tests
- release checklist
- phase verification notes

Acceptance Criteria:

- plan happy path 가 submit 부터 run detail inspection 까지 동작한다.
- direct URL entry 와 refresh 가 `Run Detail` 에서 복원된다.
- direct URL entry 와 refresh 상황의 `401` recovery 가 검증된다.
- degraded result 와 hard error 가 혼동되지 않음을 테스트로 검증한다.
- raw payload 와 metadata inspectability 가 release gate 에 포함된다.
- Phase 1 release checklist 가 문서화된다.

## 6. 권장 구현 순서

### Sprint Slice A

- `FRLP-P0-01`
- `FRLP-P0-02`
- `FRLP-P0-03`

Outcome:

- shell, routing, API client, token handling이 고정된다.

### Sprint Slice B

- `FRLP-P0-04`
- `FRLP-P0-05`

Outcome:

- 공통 상태 표현과 테스트 기반이 준비된다.

### Sprint Slice C

- `FRLP-P1-01`
- `FRLP-P1-02`
- `FRLP-P1-03`

Outcome:

- submit 에서 run detail direct-entry-safe data flow 까지 연결된다.

### Sprint Slice D

- `FRLP-P1-04`
- `FRLP-P1-05`
- `FRLP-P1-06`
- `FRLP-P1-07`

Outcome:

- plan FUR 의 결과 inspectability 와 release gate 가 완성된다.

## 7. Phase 0/1 Exit Checklist

### Phase 0 Exit Checklist

- [ ] app shell 과 route 구조가 준비되어 있다.
- [ ] bearer token 입력과 protected request 처리가 동작한다.
- [ ] structured error parser 가 공통 모듈로 동작한다.
- [ ] foundation test harness 와 route-entry fixtures 가 존재한다.

### Phase 1 Exit Checklist

- [ ] plan form submit 이 동작한다.
- [ ] plan 결과가 semantic sections 로 렌더링된다.
- [ ] `Run Detail` 이 `GET /v1/workflows/{run_id}` 기반 direct-entry/reload 를 지원한다.
- [ ] degraded success 와 hard error 가 구분된다.
- [ ] golden path 와 release checklist 가 준비되어 있다.

## 8. Ralph 실행 규칙

Ralph 는 이 backlog 를 사용할 때 아래 원칙을 따른다.

1. Phase 0 완료 전에는 plan-specific rendering issue 를 병합하지 않는다.
2. direct-entry/reload 를 baseline requirement 로 보고 late polish 로 미루지 않는다.
3. degraded success UX 는 feature completeness 조건으로 본다.
4. client-only fake state 로 backend gap 을 덮지 않는다.
5. Phase 1 완료 전 review/test-plan/trace/health/feedback 구현으로 범위를 넓히지 않는다.
