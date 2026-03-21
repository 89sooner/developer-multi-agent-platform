# Ralph용 PRD v1: AI 기반 개발 워크플로 플랫폼

## 0. 문서 정보

- 문서 상태: draft v1.0
- 작성일: 2026-03-22
- 기반 문서: `docs/prd-ai-rewrite-v1.md`
- 목적: Ralph 가 바로 구현 계획과 작업 분해로 전환할 수 있도록 phase, epic, user story, acceptance criteria 를 명시한다.

## 1. 이 문서의 전제

저장소 안에는 Ralph 전용 스키마나 템플릿이 없다. 따라서 본 문서는 "구현 에이전트 또는 개발팀 handoff 용 실행 PRD" 로 정의한다.

이 문서는 상위 PRD 의 방향성을 유지하되, 아래 항목을 명시적으로 고정한다.

- MVP primary surface: REST API
- MVP 요청 단위: single repo, single branch
- MVP 권한 범위: read-only connector + 승인 없는 write 금지
- First usable release: plan workflow
- review/test-plan/async 는 다음 phase 로 분리
- UI/IDE extension 은 MVP 필수 아님

## 2. 제품 정의

본 제품은 개발자가 자연어 요청과 저장소 맥락을 입력하면, 실제 코드/문서/이슈/CI 근거를 수집하고 구현 계획, 테스트 전략, 리뷰 의견을 구조화된 결과로 제공하는 AI 기반 개발 워크플로 플랫폼이다.

핵심 원칙:

- evidence-first
- manager pattern
- structured outputs
- read/write 분리
- traceability by default

## 3. 목표와 비목표

### 3.1 목표

- 개발자가 단일 요청으로 영향 범위, 구현 계획, 테스트 포인트, 리스크를 얻는다.
- 모든 주요 응답은 근거와 confidence 를 포함한다.
- low-confidence 응답은 명확한 경고와 open questions 를 포함한다.
- 운영자는 run/trace/feedback 을 통해 품질과 실패 원인을 추적할 수 있다.

### 3.2 비목표

- 승인 없는 patch 적용, PR 생성, 머지
- multi-repo orchestration
- 운영 환경 직접 변경
- 코드 자동 반영형 자율 에이전트

## 4. 명시적 제품 결정

### 4.1 사용자 표면

- Phase 1~2 primary surface 는 REST API 다.
- 내부 web UI/IDE extension 은 Phase 4 이후 범위다.

### 4.2 요청 범위

- 한 번의 run 은 하나의 `repo_id` 와 하나의 `branch` 에 한정한다.
- multi-repo context aggregation 은 지원하지 않는다.

### 4.3 실행 모델

- Phase 1 은 sync plan workflow 만 필수다.
- Phase 2 부터 async run 과 상태 조회를 정식 지원한다.
- 동기 응답 SLA 를 넘길 가능성이 있으면 async 전환 가능해야 한다.

### 4.4 권한 모델

- MVP 는 read-only connector 만 허용한다.
- write intent 는 기록할 수 있지만 실행은 하지 않는다.
- approval workflow 와 write action 은 post-MVP phase 에서 구현한다.

### 4.5 언어

- Phase 1 은 한국어/영어 응답을 지원한다.
- 입력 언어와 요청 언어가 다를 경우 `options.language` 가 우선한다.

## 5. 사용자와 핵심 JTBD

### Persona A. 개발자

Job:

- 구현 전에 영향 범위와 변경 순서를 빠르게 파악하고 싶다.
- 작업 전에 테스트 누락과 위험을 줄이고 싶다.

### Persona B. 리뷰어/Tech Lead

Job:

- PR 초안의 위험과 누락 테스트를 빨리 확인하고 싶다.
- 근거가 약한 응답을 구별하고 싶다.

### Persona C. 운영자/플랫폼 엔지니어

Job:

- connector, 모델, workflow 실패를 추적하고 싶다.
- 어떤 run 이 왜 실패했는지 빠르게 알고 싶다.

## 6. 범위 요약

| Phase | 이름 | 목표 | 사용자 가치 |
| --- | --- | --- | --- |
| Phase 0 | Foundation | 계약, 보안, 저장, connector 추상화 확정 | 개발 가능한 기반 확보 |
| Phase 1 | Plan MVP | evidence 기반 구현 계획 제공 | 첫 실사용 가능 릴리스 |
| Phase 2 | Review + Test + Async | review/test-plan/비동기 실행 제공 | 개발/리뷰 워크플로 확장 |
| Phase 3 | Ops + Quality | 운영 관측, 평가, 버전 관리 | 운영 안정성과 품질 개선 |
| Phase 4 | Controlled Write Assist | 승인 기반 write assistance | 고도화 |

## 7. 공통 기능 요구사항

모든 phase 에 공통으로 적용되는 규칙:

- 모든 successful run 은 `run_id`, `trace_id`, `status` 를 가져야 한다.
- 모든 major response 는 `confidence` 를 가져야 한다.
- evidence 가 비어 있으면 `low` confidence 와 `open_questions` 가 강제되어야 한다.
- repo scope 밖 접근은 차단되어야 한다.
- tool 접근은 connector 계층만 통해야 한다.
- agent step 결과는 schema validation 을 통과해야 한다.

## 8. Phase 0: Foundation

### 8.1 목표

제품의 실행 기반을 먼저 고정한다. 이 phase 는 사용자에게 큰 기능 가치를 주는 단계가 아니라, 이후 phase 가 흔들리지 않도록 계약과 운영 기본선을 만드는 단계다.

### 8.2 In Scope

- API contract 확정
- auth + repo scope enforcement
- run/trace/feedback persistence
- connector interface 와 health 모델
- 기본 orchestrator runtime 틀
- error model 과 response envelope 정의

### 8.3 Out of Scope

- 실제 plan/review 결과 품질 고도화
- UI/IDE
- write action

### 8.4 Epic

#### Epic P0-A. Core Platform Contracts

#### US-0.1 API 계약 확정

As a client developer, I want a stable versioned workflow API so that I can integrate without guessing payload shapes.

Acceptance Criteria:

- `POST /v1/workflows/plan`, `review`, `test-plan`, `GET run`, `GET trace`, `POST feedback` 계약이 OpenAPI 로 정의된다.
- 각 endpoint 는 요청/응답 schema validation 을 수행한다.
- 공통 에러 코드 목록과 상태 코드를 문서화한다.
- contract test 가 주요 endpoint 에 대해 존재한다.

#### US-0.2 run/trace 상태 모델 확정

As a platform engineer, I want a fixed run state model so that sync/async workflow 를 일관되게 운영할 수 있다.

Acceptance Criteria:

- run 상태는 최소 `queued`, `running`, `completed`, `failed`, `canceled` 를 지원한다.
- trace 는 step, tool call, error summary, version metadata 를 저장한다.
- run 과 trace 는 같은 `run_id` 기준으로 조회 가능하다.
- trace 조회 권한은 run 조회 권한과 동일하게 적용된다.

#### Epic P0-B. Security and Connector Boundaries

#### US-0.3 SSO 및 repo scope enforcement

As a security engineer, I want authenticated and scoped access so that users cannot query unauthorized repositories.

Acceptance Criteria:

- 모든 workflow endpoint 는 인증을 요구한다.
- 사용자 context 는 최소 `user_id`, `roles`, `repo_scopes` 를 가진다.
- `repo_id` 가 scope 밖이면 403 을 반환한다.
- scope violation 은 감사 로그에 남는다.

#### US-0.4 connector 추상화와 health

As an integration engineer, I want a standard connector layer so that repo/docs/issue/CI integration can be swapped independently.

Acceptance Criteria:

- repo/docs/issue/ci connector interface 가 공통 evidence 객체를 반환한다.
- connector timeout 정책이 정의된다.
- connector failure 는 workflow 전체 crash 대신 단계 실패로 처리할 수 있다.
- 운영자는 connector health 상태를 확인할 수 있다.

### 8.5 Phase Exit Criteria

- OpenAPI 와 contract tests 가 준비되어 있다.
- 인증 및 repo scope enforcement 가 동작한다.
- run/trace/feedback 저장과 조회가 가능하다.
- connector interface 와 degraded mode 처리 규칙이 문서와 코드에 반영되어 있다.

## 9. Phase 1: Plan MVP

### 9.1 목표

개발자가 자연어 요청 하나로 evidence 기반 구현 계획을 받을 수 있는 첫 실사용 릴리스를 만든다.

### 9.2 In Scope

- sync `plan` workflow
- requirements normalization
- repo/docs read connector
- evidence 기반 impacted areas
- implementation plan 생성
- review-last summary
- feedback 저장

### 9.3 Out of Scope

- async execution
- issue/CI 정식 연동
- review endpoint 정식 품질 보장
- patch draft

### 9.4 Epic

#### Epic P1-A. Developer Planning Workflow

#### US-1.1 자연어 개발 요청으로 plan 생성

As a developer, I want to submit a natural-language request for one repo and branch so that I receive an actionable implementation plan.

Acceptance Criteria:

- 사용자는 `repo_id`, `branch`, `task_text` 로 plan 요청을 보낼 수 있다.
- 요청 시 optional 하게 `issue_ids`, `changed_files`, `language` 를 함께 보낼 수 있다.
- 시스템은 `primary_intent`, `secondary_intents`, `selected_agents` 를 계산해 응답에 포함한다.
- 성공 응답은 `summary`, `impacted_areas`, `implementation_plan`, `risks`, `open_questions`, `evidence`, `confidence` 를 포함한다.

#### US-1.2 요구사항 정규화와 영향 범위 제시

As a developer, I want the system to normalize my request into implementation-ready requirements so that ambiguous tasks become concrete.

Acceptance Criteria:

- 시스템은 `feature_summary`, `acceptance_criteria`, `assumptions`, `non_goals` 를 내부 step 결과로 생성한다.
- 최종 응답의 `impacted_areas` 는 requirements 결과와 repo evidence 를 반영한다.
- requirements step 이 실패하면 degraded result 와 warning 을 남긴다.
- impact 를 특정할 근거가 약하면 `confidence=low` 또는 `open_questions` 가 포함된다.

#### US-1.3 evidence 기반 구현 계획 제공

As a developer, I want implementation steps tied to evidence so that I can trust and execute the plan.

Acceptance Criteria:

- repo/docs connector 는 관련 파일 및 문서를 evidence 로 반환한다.
- implementation plan 은 최소 `target modules`, `ordered change plan`, `risks` 를 생성한다.
- evidence 가 0개이면 plan 은 high confidence 로 반환될 수 없다.
- response 의 evidence 항목은 `source_type`, `locator`, `confidence` 를 포함한다.

#### Epic P1-B. Trust and Feedback

#### US-1.4 low-confidence 및 불확실성 노출

As a tech lead, I want low-confidence plans to clearly disclose uncertainty so that developers do not over-trust weak answers.

Acceptance Criteria:

- evidence 부족 또는 connector 실패 시 warning 이 응답에 포함된다.
- `open_questions` 는 비어 있더라도 weak evidence 상황에서는 최소 1개 이상 생성된다.
- `confidence` 는 `low | medium | high` 중 하나로 제한된다.
- summary 는 low-confidence 상황을 명시적으로 드러낸다.

#### US-1.5 피드백 저장

As a developer, I want to rate the usefulness of a plan so that the product team can improve answer quality.

Acceptance Criteria:

- 사용자는 `run_id`, `rating`, `useful`, `comment` 로 feedback 을 저장할 수 있다.
- feedback 는 존재하는 run 에만 연결 가능하다.
- 권한 없는 사용자는 타 사용자 run 에 feedback 을 남길 수 없다.
- feedback 저장 성공 시 `feedback_id` 가 반환된다.

### 9.5 Phase Exit Criteria

- golden scenario 기준 plan workflow 성공률 90% 이상
- successful plan response 의 evidence 포함률 100%
- low-evidence 응답의 low-confidence 표시 누락 0건
- sync plan p95 latency 15초 이하
- feedback 저장과 run/trace 조회가 가능하다

## 10. Phase 2: Review + Test + Async

### 10.1 목표

개발과 리뷰 단계에서 필요한 review/test-plan/long-running execution 을 추가해 실제 팀 워크플로에 가까운 제품으로 확장한다.

### 10.2 In Scope

- `review` workflow
- `test-plan` workflow
- issue/PR/CI read connector
- async run
- step progress/status 조회
- degraded mode 강화

### 10.3 Out of Scope

- 승인 기반 write action
- UI/IDE extension 정식 출시

### 10.4 Epic

#### Epic P2-A. Review and Test Workflows

#### US-2.1 diff/changed files 기반 사전 리뷰

As a reviewer, I want to submit a PR URL, diff, or changed files so that I receive readiness verdict and missing tests before merge.

Acceptance Criteria:

- review 요청은 `pr_url`, `diff_text`, `changed_files` 중 하나 이상을 받을 수 있다.
- 성공 응답은 `review_findings`, `missing_tests`, `risks`, `readiness_verdict`, `evidence`, `confidence` 를 포함한다.
- 변경 범위를 특정할 수 없으면 `readiness_verdict=blocked` 또는 동등한 degraded verdict 를 반환한다.
- review workflow 는 summary 직전에 review step 을 반드시 수행한다.

#### US-2.2 구현 계획 기반 테스트 전략 생성

As a developer, I want a dedicated test-plan endpoint so that I can generate test coverage guidance even before implementation.

Acceptance Criteria:

- `test-plan` 요청은 `implementation_plan`, `impacted_areas`, `repo_id`, `branch` 를 입력으로 받는다.
- 응답은 `unit_tests`, `integration_tests`, `regression_targets`, `edge_cases`, `execution_order` 를 포함한다.
- test-plan workflow 는 review 입력 없이 독립 실행 가능하다.
- test-plan 결과는 별도 run 으로 저장된다.

#### Epic P2-B. Async Execution and Resilience

#### US-2.3 장기 실행 요청의 비동기 처리

As a user, I want long-running workflows to continue asynchronously so that I can retrieve results later instead of waiting for timeouts.

Acceptance Criteria:

- 시스템은 정책에 따라 sync 또는 async 실행을 선택할 수 있다.
- async 요청은 `queued` 또는 `running` 상태와 `run_id` 를 즉시 반환한다.
- 사용자는 `GET /v1/workflows/{run_id}` 로 상태를 조회할 수 있다.
- 상태 전이는 `queued -> running -> completed|failed|canceled` 를 따른다.

#### US-2.4 단계별 진행 상황과 trace 조회

As a user, I want to inspect step progress and trace details so that I can understand what the system has done and where it failed.

Acceptance Criteria:

- trace 응답은 step 목록, tool call 목록, error summary 를 포함한다.
- 각 step 은 `status`, `started_at`, `ended_at`, `latency`, `confidence` 를 가진다.
- 실패한 step 이 있으면 error summary 가 비어 있지 않아야 한다.
- trace 조회는 run 접근 권한과 동일한 권한 규칙을 따른다.

#### US-2.5 connector 실패 시 partial result 반환

As a developer, I want partial results when one connector fails so that the workflow is still useful under degraded conditions.

Acceptance Criteria:

- repo/docs/issue/ci connector 실패는 해당 step warning 으로 누적된다.
- 단일 connector 실패가 전체 run 500 으로 직결되지 않는다.
- partial result 에는 실패한 connector 종류가 warning 또는 open question 으로 남는다.
- evidence 가 일부만 있어도 가능한 범위에서 응답 조립을 계속한다.

### 10.5 Phase Exit Criteria

- review 와 test-plan workflow 가 golden scenario 에서 성공한다.
- async run 생성과 상태 조회가 동작한다.
- connector partial failure 시 degraded response 가 반환된다.
- review response 의 `readiness_verdict` 누락률 0건
- trace 에 step/tool call 메타데이터가 저장된다

## 11. Phase 3: Ops + Quality

### 11.1 목표

제품을 운영 가능한 형태로 만들기 위해 품질 측정, 버전 추적, 운영자 도구를 추가한다.

### 11.2 In Scope

- metrics and dashboards
- run search / admin query
- prompt/skill/model version tracking
- evaluation dataset
- alerting and health reporting

### 11.3 Epic

#### Epic P3-A. Observability

#### US-3.1 운영 메트릭과 알림

As an operator, I want workflow quality and failure metrics so that I can detect regressions quickly.

Acceptance Criteria:

- 최소 `run completion rate`, `step failure rate`, `connector success rate`, `p95 latency`, `low-confidence rate`, `usefulness score` 를 수집한다.
- 주요 임계치 초과 시 alert 를 보낼 수 있다.
- connector 별 성공률을 구분해 볼 수 있다.
- 운영자는 최근 24시간/7일 기준 추이를 확인할 수 있다.

#### US-3.2 run 검색과 운영자 조회

As an operator, I want to search runs by status, repo, user, and time range so that I can triage incidents.

Acceptance Criteria:

- 운영자는 `status`, `repo_id`, `user_id`, `date range` 로 run 을 검색할 수 있다.
- run detail 에 request metadata, selected agents, model/skill version 이 포함된다.
- 관리자 조회 행위는 감사 로그에 남는다.
- 일반 사용자는 자기 run 만 조회 가능하다.

#### Epic P3-B. AI Quality Management

#### US-3.3 skill/prompt/model version 추적

As an AI engineer, I want every run to record model, prompt, and skill versions so that I can correlate regressions with changes.

Acceptance Criteria:

- 모든 run 은 `model_version` 을 기록한다.
- agent step 또는 run 수준에서 `prompt_version` 과 `skill_version` 을 기록한다.
- 배포 후 버전 변경 내역을 조회할 수 있다.
- 동일한 golden scenario 를 다른 버전으로 재실행 가능하다.

#### US-3.4 평가 데이터셋과 회귀 검증

As a tech lead, I want golden scenarios and offline evaluation so that model or prompt changes do not silently degrade quality.

Acceptance Criteria:

- plan/review/test-plan 별 golden scenario 세트가 존재한다.
- 정기 평가에서 citation coverage 와 critical false citation 을 측정한다.
- 평가 실패 시 배포를 차단하거나 경고할 수 있다.
- low-confidence 비율과 usefulness score 도 평가 리포트에 포함된다.

### 11.4 Phase Exit Criteria

- 운영 메트릭과 alert 가 동작한다.
- run search 와 admin audit 가 가능하다.
- version tracking 이 모든 run 에서 누락 없이 기록된다.
- golden scenario regression 리포트를 생성할 수 있다.

## 12. Phase 4: Controlled Write Assist

### 12.1 목표

승인 기반 write assistance 를 추가하되, 읽기 중심 제품의 신뢰성과 감사성을 해치지 않도록 제한적으로 도입한다.

### 12.2 In Scope

- patch draft 생성
- PR description 생성
- approval record 와 execution gate
- write action audit trail

### 12.3 Epic

#### US-4.1 patch draft 생성

As a developer, I want the system to draft a patch proposal after I approve it so that I can accelerate implementation without surrendering control.

Acceptance Criteria:

- patch draft 는 explicit approval 없이는 생성되지 않는다.
- patch draft 는 적용 전 preview 로 제공된다.
- 생성된 patch draft 는 관련 evidence 와 연결된다.
- 시스템은 실제 apply 와 draft generation 을 구분해 기록한다.

#### US-4.2 승인 기반 PR description 생성

As a developer, I want an approved PR description draft so that repetitive documentation work is reduced.

Acceptance Criteria:

- PR description draft 는 existing run 결과를 재사용해 생성할 수 있다.
- 생성 결과는 summary, impacted areas, tests, risks 를 포함한다.
- approval 없이 외부 PR 시스템에 write 하지 않는다.
- write intent 와 approval record 는 trace 에 남는다.

### 12.4 Phase Exit Criteria

- write assistance 는 approval 없이 실행되지 않는다.
- 모든 write intent 와 실행 결과가 감사 가능하다.
- draft 와 actual write 가 명확히 분리된다.

## 13. API 요구사항

### 13.1 Phase 1 필수 API

- `POST /v1/workflows/plan`
- `GET /v1/workflows/{run_id}`
- `GET /v1/workflows/{run_id}/trace`
- `POST /v1/feedback`

### 13.2 Phase 2 추가 API

- `POST /v1/workflows/review`
- `POST /v1/workflows/test-plan`
- `POST /v1/workflows/{run_id}/cancel` 또는 동등 기능

### 13.3 Phase 4 추가 API

- `POST /v1/workflows/{run_id}/approve`
- `POST /v1/workflows/{run_id}/patch-draft`
- `POST /v1/workflows/{run_id}/pr-description-draft`

## 14. 비기능 요구사항

### 14.1 성능

- Phase 1 sync plan p95 latency: 15초 이하
- Phase 2 review/test-plan sync latency 목표: 20초 이하
- SLA 를 넘길 가능성이 있는 요청은 async 전환 가능해야 한다.

### 14.2 신뢰성

- connector 단일 실패로 전체 run 이 즉시 실패하지 않아야 한다.
- evidence 0건인 성공 응답은 low-confidence 여야 한다.
- critical false citation 은 허용하지 않는다.

### 14.3 보안

- 모든 요청은 인증 필요
- repo scope enforcement 필수
- 민감정보 masking 필수
- approval 없는 write 금지

### 14.4 감사/보존

- run/trace/feedback 저장
- admin 조회 감사 로그 저장
- retention 기간은 운영 정책으로 분리하되 시스템이 설정 가능해야 한다.

## 15. 성공 지표

### 15.1 Phase 1

- plan workflow 성공률 90% 이상
- successful response evidence 포함률 100%
- low-confidence 표시 누락 0건

### 15.2 Phase 2

- review/test-plan 성공률 90% 이상
- degraded mode 동작 검증 100%
- async 상태 조회 오류율 1% 이하

### 15.3 Phase 3

- 운영 대시보드에서 핵심 지표를 확인 가능
- golden scenario regression 이 배포 파이프라인에 연결됨
- version tracking 누락률 0건

## 16. 의존성과 가정

- repo/docs/issue/CI 시스템에 read-only 접근 가능한 인증 수단이 제공된다.
- 조직 내 SSO/IdP 와 repo scope 매핑이 가능하다.
- 모델 공급자는 structured output 을 지원한다.
- 운영 환경에서 run/trace 저장소와 메트릭 수집기가 제공된다.

## 17. 남은 오픈 질문

아래 질문은 구현 전 제품 오너가 확정해야 한다.

1. docs/wiki 의 1차 연결 대상은 무엇인가.
2. issue/PR tracker 의 1차 연결 대상은 무엇인가.
3. CI 는 latest result 만 필요할지, history lookup 도 필요한지.
4. Phase 2 에 최소 web UI 가 필요한지, API-only 로 유지할지.
5. retention 기간의 기본값은 얼마인지.

확정 전 기본 가정:

- docs/wiki 는 조직의 대표 문서 시스템 1종
- issue/PR tracker 는 조직의 기본 코드 협업 시스템 1종
- CI 는 latest read 중심

## 18. Ralph 실행 지침

Ralph 는 이 문서를 구현 입력으로 사용할 때 다음 순서를 따른다.

1. Phase 0 의 계약, 보안, 저장, connector 추상화를 먼저 고정한다.
2. Phase 1 의 `plan` workflow 를 first usable release 로 구현한다.
3. Phase 1 exit criteria 충족 전에는 review/test-plan/write action 으로 범위를 넓히지 않는다.
4. 모든 story 는 acceptance criteria 기준으로 테스트 가능해야 한다.
5. evidence, confidence, traceability 원칙을 기능 편의보다 우선한다.
