# Ralph용 Phase 0/1 구현 Backlog

작성일: 2026-03-22  
기준 문서: `docs/prd-ralph-v1.md`

## 1. 목적

이 문서는 `docs/prd-ralph-v1.md` 의 Phase 0, Phase 1 범위를 Ralph 가 바로 실행 가능한 issue backlog 로 분해한 문서다.

목표:

- 구현 순서를 흔들리지 않게 고정한다.
- 각 issue 가 독립적으로 완료 조건을 가진다.
- acceptance criteria 를 바로 개발/테스트 기준으로 사용할 수 있게 만든다.
- Phase 0 완료 전 Phase 1 범위가 무분별하게 섞이지 않도록 dependency 를 명확히 둔다.

## 2. Backlog 운영 규칙

### 2.1 이슈 ID 규칙

- `RLP-P0-0X`: Phase 0 issue
- `RLP-P1-0X`: Phase 1 issue

### 2.2 상태 규칙

- `todo`
- `in_progress`
- `blocked`
- `review`
- `done`

### 2.3 우선순위 규칙

- `Must`: phase exit criteria 에 직접 연결되는 필수 이슈
- `Should`: phase 안에서 강하게 권장되지만, phase exit 의 직접 게이트는 아닌 이슈

### 2.4 크기 규칙

- `S`: 0.5~1일
- `M`: 1~3일
- `L`: 3~5일

### 2.5 공통 Definition of Done

모든 issue 는 아래를 만족해야 `done` 으로 본다.

- 코드가 저장소에 반영되어 있다.
- 관련 contract test 또는 unit/integration test 가 추가되거나 갱신되어 있다.
- OpenAPI 또는 문서가 바뀐 경우 문서도 함께 반영되어 있다.
- 실패/권한/경계 조건이 최소 1개 이상 테스트되어 있다.
- 로그/trace 에 필요한 메타데이터가 누락되지 않는다.

## 3. Critical Path

### Phase 0 Critical Path

1. `RLP-P0-01` Core contracts
2. `RLP-P0-02` Run/trace persistence
3. `RLP-P0-03` Auth + repo scope
4. `RLP-P0-04` Connector interfaces
5. `RLP-P0-05` Orchestrator execution skeleton
6. `RLP-P0-06` Contract/security/persistence tests

### Phase 1 Critical Path

1. `RLP-P1-01` Plan endpoint happy path
2. `RLP-P1-02` Requirements normalization
3. `RLP-P1-03` Repo/docs read connectors
4. `RLP-P1-04` Implementation planner
5. `RLP-P1-05` Summary composer + confidence policy
6. `RLP-P1-06` Feedback + retrieval hardening
7. `RLP-P1-07` Golden scenario + release verification

## 4. Phase 0 Backlog

### RLP-P0-01 Core Workflow Contracts

- Phase: `Phase 0`
- Priority: `Must`
- Size: `M`
- Depends on: 없음

Goal:

- workflow API 와 내부 step contract 의 기준선을 고정한다.

Scope:

- request/response envelope 정의
- 공통 error model 정의
- run status enum 정의
- trace step schema 정의
- evidence schema 정의

Out of Scope:

- plan/review/test-plan 실제 품질 구현

Deliverables:

- Pydantic models
- OpenAPI schema
- error code table
- contract fixture examples

Acceptance Criteria:

- `plan`, `review`, `test-plan`, `get run`, `get trace`, `feedback` 의 schema 가 버전된 OpenAPI 로 문서화된다.
- `run_id`, `trace_id`, `status`, `confidence` 의 공통 필드가 정의된다.
- error response 는 최소 `code`, `message`, `request_id` 또는 동등 필드를 가진다.
- schema validation 실패 시 4xx 로 일관되게 반환된다.

### RLP-P0-02 Run/Trace/Feedback Persistence Foundation

- Phase: `Phase 0`
- Priority: `Must`
- Size: `L`
- Depends on: `RLP-P0-01`

Goal:

- workflow run 의 수명주기와 추적 데이터를 저장할 수 있게 한다.

Scope:

- run store
- trace store
- feedback store
- state transition helpers
- persistence repository abstraction

Out of Scope:

- 운영 대시보드
- admin search UI

Deliverables:

- persistence schema
- repository/service layer
- run status transition rules
- migration/init script

Acceptance Criteria:

- run 상태 `queued`, `running`, `completed`, `failed`, `canceled` 를 저장할 수 있다.
- trace 는 step, tool call, error summary, version metadata 를 저장할 수 있다.
- feedback 는 `run_id` 기준으로 저장된다.
- 존재하지 않는 run 에 대한 trace/feedback 저장은 명시적 오류를 반환한다.

### RLP-P0-03 Authentication and Repo Scope Enforcement

- Phase: `Phase 0`
- Priority: `Must`
- Size: `M`
- Depends on: `RLP-P0-01`

Goal:

- 인증된 사용자만 접근하고, 사용자 scope 밖 저장소 조회를 차단한다.

Scope:

- user context extraction
- role/repo scope model
- endpoint auth dependency
- repo scope policy enforcement
- access denial audit log

Out of Scope:

- doc/issue 세부 scope matrix 고도화
- approval workflow

Deliverables:

- auth middleware or dependency
- user context object
- policy functions
- audit log hook

Acceptance Criteria:

- 모든 workflow endpoint 는 인증 없으면 401 을 반환한다.
- `repo_id` 가 사용자 scope 밖이면 403 을 반환한다.
- 인증 성공 시 user context 는 최소 `user_id`, `roles`, `repo_scopes`, `request_id` 를 포함한다.
- scope violation 은 로그 또는 감사 레코드로 남는다.

### RLP-P0-04 Connector Interface and Evidence Normalization

- Phase: `Phase 0`
- Priority: `Must`
- Size: `L`
- Depends on: `RLP-P0-01`

Goal:

- repo/docs/issue/ci 커넥터를 교체 가능하게 만드는 공통 interface 를 정의한다.

Scope:

- connector protocol/interface
- evidence normalization
- connector timeout/error contract
- connector health model
- read-only connector rule

Out of Scope:

- 실제 조직 시스템 연동 세부 구현

Deliverables:

- connector base interface
- standardized evidence object
- connector result/error types
- health response schema

Acceptance Criteria:

- repo/docs/issue/ci connector 가 동일 evidence 구조를 반환할 수 있다.
- connector 실패는 typed error 또는 동등 개념으로 표현된다.
- timeout/empty result/auth failure 를 구분할 수 있다.
- connector health 상태를 조회할 수 있는 내부 모델이 존재한다.

### RLP-P0-05 Orchestrator Execution Skeleton

- Phase: `Phase 0`
- Priority: `Must`
- Size: `L`
- Depends on: `RLP-P0-01`, `RLP-P0-02`, `RLP-P0-04`

Goal:

- specialist step 을 순차 실행하고 trace 로 기록하는 최소 런타임을 만든다.

Scope:

- orchestrator service
- step execution wrapper
- structured step result validation
- degraded mode fallback contract
- model/skill/prompt version recording hook

Out of Scope:

- high-quality plan logic
- async worker

Deliverables:

- workflow execution service
- step runner abstraction
- trace instrumentation
- fallback strategy

Acceptance Criteria:

- orchestrator 는 요청 하나를 step sequence 로 실행할 수 있다.
- 각 step 은 시작/종료 시각, 상태, latency, confidence 를 trace 에 남긴다.
- step schema validation 실패 시 retry 또는 fallback 규칙을 적용할 수 있다.
- run 완료 시 final result 와 trace 가 함께 저장된다.

### RLP-P0-06 Foundation Test Suite and Exit Gate

- Phase: `Phase 0`
- Priority: `Must`
- Size: `M`
- Depends on: `RLP-P0-01`, `RLP-P0-02`, `RLP-P0-03`, `RLP-P0-04`, `RLP-P0-05`

Goal:

- Phase 0 종료를 판단할 수 있는 최소 테스트/문서 게이트를 만든다.

Scope:

- contract tests
- auth/scope tests
- persistence tests
- degraded mode tests
- OpenAPI verification

Out of Scope:

- plan quality golden scenarios

Deliverables:

- automated tests
- phase exit checklist
- sample payloads

Acceptance Criteria:

- 주요 endpoint contract tests 가 통과한다.
- 401/403/404 계열 권한 및 조회 테스트가 통과한다.
- run/trace 저장 및 재조회 테스트가 통과한다.
- degraded mode 동작을 검증하는 최소 1개 테스트가 존재한다.

## 5. Phase 1 Backlog

### RLP-P1-01 Plan Workflow API Happy Path

- Phase: `Phase 1`
- Priority: `Must`
- Size: `M`
- Depends on: `RLP-P0-06`

Goal:

- 사용자가 `plan` 요청을 보내고 기본 구조의 응답을 받는 end-to-end happy path 를 만든다.

Scope:

- `POST /v1/workflows/plan`
- sync execution path
- request classification
- selected agent metadata
- result persistence

Out of Scope:

- advanced ranking
- async execution

Deliverables:

- plan endpoint
- classification logic
- response mapping

Acceptance Criteria:

- `repo_id`, `branch`, `task_text` 만으로 plan 요청을 처리할 수 있다.
- 응답에는 `summary`, `impacted_areas`, `implementation_plan`, `risks`, `open_questions`, `evidence`, `confidence` 가 포함된다.
- 응답에는 `primary_intent`, `secondary_intents`, `selected_agents` 가 포함된다.
- run 과 trace 를 조회하면 해당 plan 요청의 결과를 다시 확인할 수 있다.

### RLP-P1-02 Requirements Normalization Step

- Phase: `Phase 1`
- Priority: `Must`
- Size: `M`
- Depends on: `RLP-P1-01`

Goal:

- 자연어 요청을 구현 가능한 요구사항 단위로 정규화한다.

Scope:

- feature summary
- assumptions
- acceptance criteria
- non-goals
- impacted areas hypothesis

Out of Scope:

- review/test-plan 전용 normalization

Deliverables:

- requirements step implementation
- structured output schema
- fallback behavior

Acceptance Criteria:

- requirements step 은 `feature_summary`, `assumptions`, `acceptance_criteria`, `non_goals`, `impacted_areas` 를 생성한다.
- step 실패 시 workflow 전체가 500 으로 끝나지 않고 fallback warning 이 남는다.
- requirements 결과는 최종 impacted areas 계산에 반영된다.
- requirements step 결과는 trace 에 기록된다.

### RLP-P1-03 Repo and Docs Read Connectors

- Phase: `Phase 1`
- Priority: `Must`
- Size: `L`
- Depends on: `RLP-P0-04`, `RLP-P1-02`

Goal:

- plan 응답의 근거가 되는 repo/docs evidence 를 실제 read connector 로 수집한다.

Scope:

- repo read connector
- docs/wiki read connector
- changed files prioritization
- evidence ranking
- snippet masking

Out of Scope:

- issue/PR/CI 정식 read

Deliverables:

- repo connector implementation
- docs connector implementation
- evidence ranking/scoring
- masking integration

Acceptance Criteria:

- repo connector 는 관련 파일 후보를 evidence 로 반환한다.
- docs connector 는 관련 문서 후보를 evidence 로 반환한다.
- `changed_files` 가 제공되면 ranking 에 우선 반영된다.
- evidence 는 최소 `source_type`, `locator`, `confidence` 를 포함한다.

### RLP-P1-04 Implementation Planner Step

- Phase: `Phase 1`
- Priority: `Must`
- Size: `M`
- Depends on: `RLP-P1-02`, `RLP-P1-03`

Goal:

- 수집된 근거를 바탕으로 실행 가능한 구현 계획을 만든다.

Scope:

- target modules
- ordered change plan
- risks
- API/data model change hints
- rollback notes

Out of Scope:

- patch generation

Deliverables:

- implementation planner step
- structured result schema
- fallback behavior

Acceptance Criteria:

- implementation step 은 최소 `target_modules`, `change_plan`, `risks` 를 생성한다.
- 공개 계약 변경 가능성이 있으면 API/data model change 힌트를 포함할 수 있다.
- 근거가 약하면 implementation confidence 는 자동 하향된다.
- step 결과는 trace 와 final response composition 에 사용된다.

### RLP-P1-05 Summary Composer and Confidence Policy

- Phase: `Phase 1`
- Priority: `Must`
- Size: `M`
- Depends on: `RLP-P1-02`, `RLP-P1-03`, `RLP-P1-04`

Goal:

- 여러 step 결과를 하나의 신뢰 가능한 최종 plan 응답으로 조립한다.

Scope:

- summary composition
- impacted areas merge
- confidence collapse policy
- warnings and open questions policy
- evidence-required output rule

Out of Scope:

- review/test-plan composition

Deliverables:

- summary composer
- confidence policy module
- open questions generation rule

Acceptance Criteria:

- final response 는 필수 섹션 누락 없이 조립된다.
- evidence 가 0개인 성공 응답은 반드시 `confidence=low` 다.
- weak evidence 상황에서는 `warnings` 와 `open_questions` 가 함께 포함된다.
- summary 는 degraded mode 여부를 사용자에게 드러낼 수 있다.

### RLP-P1-06 Feedback API and Retrieval Hardening

- Phase: `Phase 1`
- Priority: `Should`
- Size: `S`
- Depends on: `RLP-P1-01`

Goal:

- plan 결과에 대한 피드백과 재조회 흐름을 마무리한다.

Scope:

- feedback endpoint integration
- run detail retrieval validation
- trace retrieval validation
- authorization hardening

Out of Scope:

- admin search

Deliverables:

- feedback service integration
- retrieval permission tests

Acceptance Criteria:

- 사용자는 자신의 run 에 대해 feedback 을 남길 수 있다.
- 타 사용자 run 에 대한 feedback 시도는 차단된다.
- run/trace 조회 응답은 plan 실행 결과와 연결된다.
- retrieval 관련 404/403 테스트가 존재한다.

### RLP-P1-07 Golden Scenarios and Phase 1 Release Gate

- Phase: `Phase 1`
- Priority: `Must`
- Size: `M`
- Depends on: `RLP-P1-05`, `RLP-P1-06`

Goal:

- plan MVP 의 출시 여부를 판단할 수 있는 품질 게이트를 만든다.

Scope:

- golden scenario set
- success rate measurement
- low-confidence coverage checks
- latency measurement
- release checklist

Out of Scope:

- offline evaluation platform 전체

Deliverables:

- golden scenario fixtures
- automated verification script or test suite
- Phase 1 release checklist

Acceptance Criteria:

- golden scenario 기준 plan workflow 성공률을 계산할 수 있다.
- evidence 포함률과 low-confidence 표시 누락 여부를 검증할 수 있다.
- sync plan p95 latency 를 측정할 수 있다.
- release checklist 가 문서화되어 있다.

## 6. 권장 구현 순서

### Sprint Slice A

- `RLP-P0-01`
- `RLP-P0-02`
- `RLP-P0-03`

Outcome:

- 계약, 저장, 인증이 고정된다.

### Sprint Slice B

- `RLP-P0-04`
- `RLP-P0-05`
- `RLP-P0-06`

Outcome:

- connector 경계와 orchestrator skeleton 이 완성된다.

### Sprint Slice C

- `RLP-P1-01`
- `RLP-P1-02`
- `RLP-P1-03`

Outcome:

- evidence 가 붙는 plan happy path 가 동작한다.

### Sprint Slice D

- `RLP-P1-04`
- `RLP-P1-05`
- `RLP-P1-06`
- `RLP-P1-07`

Outcome:

- plan MVP 의 품질 게이트와 release 기준이 완성된다.

## 7. Phase 0/1 Exit Checklist

### Phase 0 Exit Checklist

- [ ] OpenAPI 가 Phase 0 기준 계약을 반영한다.
- [ ] 인증과 repo scope enforcement 가 동작한다.
- [ ] run/trace/feedback 저장이 동작한다.
- [ ] connector interface 와 degraded mode 룰이 구현되어 있다.
- [ ] foundation test suite 가 통과한다.

### Phase 1 Exit Checklist

- [ ] `POST /v1/workflows/plan` happy path 가 동작한다.
- [ ] requirements, repo/docs evidence, implementation, summary 가 연결된다.
- [ ] evidence 없는 성공 응답은 low-confidence 로 처리된다.
- [ ] feedback 저장과 run/trace 재조회가 동작한다.
- [ ] golden scenario 와 latency 측정이 준비되어 있다.

## 8. Ralph 실행 규칙

Ralph 는 이 backlog 를 사용할 때 아래 원칙을 따른다.

1. 여러 issue 를 병렬 진행하더라도 write scope 가 겹치지 않게 분리한다.
2. `Must` issue 를 끝내기 전 `Should` issue 로 확장하지 않는다.
3. Phase 0 완료 전에는 Phase 1 구현을 병합하지 않는다.
4. acceptance criteria 를 테스트로 증명할 수 없는 issue 는 완료 처리하지 않는다.
5. Phase 1 범위에서 issue/PR/CI 정식 연동이나 write assist 로 범위를 늘리지 않는다.

## 9. Local vs Blocked 분해 기준 (2026-03-22)

Phase 0/1 잔여 대형 항목은 아래처럼 쪼개서 운영한다.

- `local`: 현재 저장소/테스트만으로 완료 가능한 작업 (provider/connector seam, config selector, contract fixture).
- `blocked-external`: 외부 IdP, 조직 시스템 API, 서비스 계정/credential, endpoint contract 가 필요해 로컬에서 완료 불가한 작업.

현재 상태 요약:

- Auth: 로컬 bearer-claims 기본 provider + provider selector 는 `local` 완료, 실제 IdP adapter 는 `blocked-external`.
- Auth: repo scope violation 은 warning log/audit event 로 남기며, 실제 외부 IdP claim contract 연결만 `blocked-external`.
- Connector: workspace repo/docs connector seam + registry 연결은 `local` 완료, 외부 repo/docs/issue/ci adapter 는 `blocked-external`.

로컬 subtasks 상태:

- `RLP-P0-04.7`: connector timeout/auth-failure/empty-result 를 구분하는 typed error contract 와 fixture 추가 완료.
- `RLP-P0-03.6`: 미래 IdP provider 가 참조할 claim key (`user_id`, `repo_scopes`, `roles`) 와 issuer/audience env key 고정 완료.
- 현재 남은 next focus 는 모두 `blocked-external` 이며, 외부 IdP/조직 시스템 계약 없이는 진행하지 않는다.

남은 항목 처리 규칙:

- `prd.json` 상위 상태가 `blocked` 이면, 로컬 실행 가능한 subtasks 는 모두 종료되었고 외부 의존성만 남았다는 뜻이다.
- `driver.note` 는 Ralph 실행 방식 설명이고, `blockers` 는 앞으로 진행을 막는 현재 의존성만 남긴다.
