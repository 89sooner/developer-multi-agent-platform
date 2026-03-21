# PRD v1: AI 기반 개발 워크플로 플랫폼 재작성

## 0. 문서 정보

- 문서 상태: draft v1.0
- 작성일: 2026-03-21
- 문서 목적: 현재 프로토타입을 참고하되, 실제 AI 중심 제품으로 처음부터 다시 구현하기 위한 제품 요구사항을 정의한다.
- 대상 독자: Product, Platform, AI Engineering, Security, DevEx, QA

## 1. 제품 요약

본 제품은 사내 개발자가 기능 구현, 버그 수정, 리팩터링, PR 리뷰, 테스트 설계 단계에서 자연어와 코드 맥락을 입력하면, 실제 저장소와 관련 시스템을 탐색하고 근거 기반의 구현 계획, 테스트 전략, 리뷰 의견을 생성하는 AI 기반 개발 워크플로 플랫폼이다.

제품의 핵심은 "코드를 직접 바꾸는 자율 에이전트"가 아니라, 개발자가 더 빠르고 정확하게 결정을 내리도록 돕는 "증거 기반 개발 의사결정 시스템"이다. 기본 산출물은 항상 계획, 근거, 리스크, 불확실성을 함께 제공해야 한다.

## 2. 문제 정의

현재 개발 단계에서 반복적으로 발생하는 문제는 아래와 같다.

- 요구사항을 구현 가능한 작업으로 재해석하는 데 시간이 많이 든다.
- 영향 범위를 파악하려면 코드, 문서, 이슈, CI 로그를 각각 따로 찾아야 한다.
- 테스트 포인트와 회귀 리스크가 개인 경험에 과도하게 의존한다.
- PR 리뷰 전 단계의 품질이 팀과 개발자마다 크게 흔들린다.
- AI 도구를 써도 근거 출처, 신뢰도, 승인 경계가 불명확해 실무 적용이 어렵다.

## 3. 제품 목표

### 3.1 핵심 목표

- 개발 요청을 1회 입력으로 계획, 테스트, 리뷰 관점까지 구조화한다.
- 코드/문서/이슈/CI 를 근거로 연결한 evidence-first 응답을 제공한다.
- 구현 전에 회귀 위험과 open question 을 드러내 의사결정 품질을 높인다.
- 승인 가능한 경계 안에서만 AI 를 활용하도록 정책과 추적 체계를 내장한다.
- 팀별 표준을 skill, policy, template 형태로 재사용 가능하게 만든다.

### 3.2 성공 상태

- 개발자는 하나의 요청으로 영향 범위, 수정 순서, 테스트 체크리스트, 리스크를 함께 받는다.
- 모든 응답에는 출처와 confidence 가 포함된다.
- low-confidence 응답은 명확히 표시되고, 추가로 필요한 정보가 제안된다.
- 결과물은 리뷰어와 작성자가 바로 협업에 사용할 수 있는 수준으로 구조화된다.

## 4. 비목표

초기 범위에서 아래 항목은 제외한다.

- 승인 없는 코드 커밋, PR 생성, 머지
- 운영 환경 직접 변경
- 운영 DB 직접 실행
- 저장소 전체를 대상으로 한 완전 자율 리팩터링
- 사람 검토 없이 배포 가능한 코드 생성

## 5. 제품 원칙

### 5.1 Evidence First

모든 핵심 주장에는 코드, 문서, 이슈, CI 중 하나 이상의 근거가 붙어야 한다. 근거가 약하면 confidence 를 낮추고 open question 을 남긴다.

### 5.2 Manager Pattern

중앙 orchestrator 가 실행 순서, 정책, 응답 형식, 승인 경계를 소유한다. specialist agent 는 독립 역할만 담당하고 직접 대화 소유권을 갖지 않는다.

### 5.3 Structured Outputs

모든 agent 와 tool 은 스키마 검증 가능한 구조화된 결과를 반환해야 한다. 자유 텍스트는 최종 사용자 응답에만 허용한다.

### 5.4 Human Approval First

읽기와 쓰기를 분리한다. 외부 시스템에 쓰기 작업이 필요한 기능은 명시적 승인과 감사 로그 없이는 실행할 수 없다.

### 5.5 Measurable AI Quality

좋은 답변 여부를 감으로 판단하지 않는다. citation coverage, usefulness, low-confidence 비율, reviewer override 비율 같은 지표를 측정한다.

## 6. 대상 사용자

### 6.1 1차 사용자

- 백엔드 개발자
- 프론트엔드 개발자
- 플랫폼 엔지니어
- QA/SDET
- Tech Lead

### 6.2 핵심 사용 시나리오

- 새 기능 구현 전 영향 범위와 구현 순서 파악
- 버그 수정 전 관련 코드와 재현/회귀 포인트 탐색
- 리팩터링 전 경계, 단계적 전환, 롤백 계획 수립
- PR 제출 전 사전 리뷰와 누락 테스트 확인
- 구현 계획 기반 테스트 전략 생성

## 7. MVP 범위

### 7.1 포함 범위

- plan workflow
- review workflow
- test-plan workflow
- 실제 repo connector 연동
- 실제 docs/wiki connector 연동
- issue/PR/CI 읽기 연동
- evidence/citation/confidence 기반 응답
- run/trace/feedback 저장
- 인증, repo scope enforcement, approval gate
- API 우선 제공, 최소 1개 사용자 표면 제공

### 7.2 차기 범위

- patch draft 생성
- PR description 생성
- CI 실패 자동 분석
- 보안 리뷰 specialist
- 아키텍처 변경 시뮬레이션
- IDE extension 고도화

## 8. 사용자 경험 요구사항

### 8.1 입력 경험

사용자는 아래 정보 중 일부만 제공해도 요청을 시작할 수 있어야 한다.

- 자연어 task text
- repo
- branch
- issue id 또는 PR URL
- changed files 또는 diff
- 원하는 응답 언어

제품은 입력이 불완전해도 가능한 범위에서 분석을 시작하되, 부족한 정보는 open question 으로 반환해야 한다.

### 8.2 출력 경험

모든 plan/review 응답은 아래 섹션을 안정적으로 포함해야 한다.

- summary
- impacted areas
- implementation plan 또는 review findings
- tests 또는 missing tests
- risks
- open questions
- evidence
- confidence

### 8.3 인터랙션 모델

- 짧은 요청은 동기 응답 가능해야 한다.
- 긴 요청은 비동기 실행과 상태 조회를 지원해야 한다.
- 사용자는 run 이 어떤 단계까지 진행되었는지 확인할 수 있어야 한다.
- 사용자는 결과에 대해 feedback 을 남길 수 있어야 한다.

## 9. 기능 요구사항

### FR-1. 요청 수집 및 분류

시스템은 요청을 `feature`, `bugfix`, `refactor`, `review`, `test_plan` 중 하나 이상으로 분류해야 한다.

수용 기준:

- 요청 유형은 사용자가 명시하지 않아도 추론 가능해야 한다.
- primary intent 와 secondary intent 를 분리해 저장해야 한다.
- 분류 confidence 와 분류 warning 을 남겨야 한다.

### FR-2. 요구사항 정규화

시스템은 자연어 요청을 개발 가능한 단위로 재구성해야 한다.

수용 기준:

- feature summary 생성
- acceptance criteria 생성
- assumptions 생성
- non-goals 생성
- impacted areas 초기 가설 생성

### FR-3. 코드베이스 컨텍스트 수집

시스템은 대상 저장소에서 관련 코드와 유사 구현을 탐색해야 한다.

수용 기준:

- 관련 파일 후보 제시
- 유사 구현 예시 제시
- 계층 간 의존성 요약
- changed files 가 있으면 우선 반영
- evidence 객체로 결과를 정규화

### FR-4. 외부 아티팩트 수집

시스템은 문서, 이슈, PR, CI 결과를 읽어 분석 근거에 포함해야 한다.

수용 기준:

- docs/wiki connector 지원
- issue/PR connector 지원
- CI/test result connector 지원
- connector 실패 시 partial result + warning 처리

### FR-5. 구현 계획 생성

시스템은 수집된 근거를 바탕으로 구현 계획을 생성해야 한다.

수용 기준:

- target modules
- ordered change plan
- API changes
- data model changes
- migration needs
- rollback notes
- implementation risks

### FR-6. 테스트 전략 생성

시스템은 구현 계획 또는 review 요청을 기반으로 테스트 전략을 생성해야 한다.

수용 기준:

- unit tests
- integration tests
- regression targets
- edge cases
- execution order

### FR-7. 사전 리뷰 생성

시스템은 변경안 또는 PR 초안을 검토하고 준비 상태를 판정해야 한다.

수용 기준:

- missing evidence
- hidden dependencies
- regression risks
- security/performance/compatibility flags
- readiness verdict
- missing tests

### FR-8. 최종 응답 조립

시스템은 specialist 결과를 병합해 일관된 최종 응답을 생성해야 한다.

수용 기준:

- 필수 섹션 누락 금지
- evidence 없는 주장은 warning 또는 low confidence 처리
- 사용자 언어 또는 요청 언어를 따름

### FR-9. run 수명주기 관리

시스템은 모든 요청을 run 단위로 관리해야 한다.

수용 기준:

- run_id, trace_id 발급
- queued/running/completed/failed 상태 저장
- 동기/비동기 실행 모두 지원
- 재조회 API 제공

### FR-10. trace 및 감사

시스템은 각 단계와 tool 호출을 추적 가능하게 남겨야 한다.

수용 기준:

- step 시작/종료 시각
- step latency
- tool call summary
- model/skill/prompt version
- error summary
- user_id, repo scope, request metadata

### FR-11. 보안 및 승인 경계

시스템은 사용자 권한을 넘는 접근이나 승인 없는 쓰기를 허용하면 안 된다.

수용 기준:

- SSO 기반 사용자 식별
- repo/doc/issue scope enforcement
- write action 별 approval workflow
- 민감정보 마스킹
- privilege escalation 차단

### FR-12. feedback 수집

시스템은 결과에 대한 유용성 피드백을 저장해야 한다.

수용 기준:

- rating
- useful 여부
- comment
- run 연결
- 후속 품질 분석에 활용 가능한 형태로 저장

### FR-13. skill/policy 관리

시스템은 팀별 규칙과 프롬프트 자산을 버전 관리 가능한 형태로 운영해야 한다.

수용 기준:

- role 별 skill 매핑
- version 기록
- 정책 변경 이력
- rollout 단위 분리 가능

### FR-14. 관리자 및 운영 기능

시스템은 운영자가 품질과 안정성을 관리할 수 있어야 한다.

수용 기준:

- connector 상태 확인
- 모델/skill 버전 확인
- low-confidence 비율과 오류율 조회
- 재실행 또는 triage 에 필요한 run 검색

## 10. AI/에이전트 요구사항

### 10.1 에이전트 구성

필수 agent:

- Workflow Orchestrator
- Requirements Agent
- Repo Context Agent
- Implementation Agent
- Test Strategy Agent
- Review Agent
- Summary Composer

### 10.2 실행 규칙

- orchestrator 는 항상 최종 응답 품질을 책임진다.
- review 단계는 plan/review workflow 에서 항상 summary 직전에 실행된다.
- 외부 시스템 접근은 tool connector 계층만 사용한다.
- agent 결과는 스키마 검증에 실패하면 재시도 또는 fallback 해야 한다.

### 10.3 AI 품질 규칙

- 근거 없는 파일명, 모듈명, 영향 범위 단정 금지
- evidence 가 약하면 confidence 하향
- uncertainty 는 open question 으로 노출
- 사용자에게는 reasoning 전문이 아니라 결과와 근거를 제공

### 10.4 모델 전략

- 모델 공급자에 종속되지 않는 추상화 계층을 둔다.
- structured output 지원 모델을 기본 전제로 한다.
- 단계별 latency budget 과 cost budget 을 둔다.
- 장애 시 축약 응답 또는 deterministic fallback 을 허용한다.

## 11. 기술 요구사항

### 11.1 권장 아키텍처

- API 서비스
- Workflow orchestration 서비스
- Background worker
- Tool connector 계층
- Policy/validation 계층
- Run store
- Trace/evaluation store
- Feedback store
- Skill/prompt registry

### 11.2 저장소 요구사항

- run, trace, feedback 은 분리 저장
- 운영형 DB 사용
- trace export 와 장기 보관 지원
- 요청/응답 payload versioning 지원

### 11.3 통합 요구사항

- Git/code search
- docs/wiki
- issue/PR tracker
- CI/test results
- SSO/IdP
- secret manager

### 11.4 성능 요구사항

- plan/review 의 동기 응답은 가능한 경우 15초 이내 목표
- 장기 작업은 비동기 전환
- connector timeout 과 degraded mode 지원
- p95 latency, tool success rate, run completion rate 측정

### 11.5 보안 요구사항

- 최소 권한 원칙
- 감사 가능한 모든 write intent 기록
- 응답과 trace 에서 민감정보 마스킹
- tenant/repo scope 강제
- 관리자 우회 경로 최소화

### 11.6 관측 요구사항

필수 메트릭:

- request count
- run completion rate
- step failure rate
- connector success rate
- p50/p95 latency
- low-confidence rate
- approval required rate
- user usefulness score

### 11.7 테스트 요구사항

- endpoint contract tests
- agent schema validation tests
- connector contract tests
- degraded mode tests
- auth/scope/approval tests
- golden scenario tests
- offline evaluation set 운영

## 12. 데이터 및 API 요구사항

### 12.1 핵심 엔터티

- WorkflowRun
- AgentStepResult
- Evidence
- ToolCall
- Feedback
- ApprovalRecord

### 12.2 기본 API 범위

- `POST /v1/workflows/plan`
- `POST /v1/workflows/review`
- `POST /v1/workflows/test-plan`
- `GET /v1/workflows/{run_id}`
- `GET /v1/workflows/{run_id}/trace`
- `POST /v1/feedback`

필요 시 확장:

- `POST /v1/workflows/{run_id}/approve`
- `POST /v1/workflows/{run_id}/cancel`
- `GET /v1/workflows/{run_id}/events`

## 13. 성공 지표

- plan/review run completion rate 95% 이상
- evidence citation coverage 100%
- critical false citation 0건
- usefulness 평균 4.0/5 이상
- low-confidence 응답 비율 20% 이하
- reviewer 가 "바로 활용 가능"으로 평가한 비율 70% 이상

## 14. 주요 리스크와 대응

### 14.1 근거 품질 불안정

대응:

- connector 품질 우선 확보
- evidence ranking 개선
- citation 검증 로직 추가

### 14.2 모델 응답 변동성

대응:

- structured output 강제
- step별 retry/fallback
- golden scenario regression 운영

### 14.3 권한 및 보안 문제

대응:

- tool 계층에서 scope enforcement 강제
- 민감정보 masking
- 승인 없는 write 차단

### 14.4 사용자 신뢰 부족

대응:

- confidence 와 uncertainty 노출
- trace 와 evidence 투명성 제공
- feedback 기반 개선 루프 운영

## 15. 출시 단계 제안

### Phase 1

- API 우선 MVP
- 실제 repo/docs/issue/CI read connector
- plan/review/test-plan
- run/trace/feedback
- SSO 와 scope enforcement

### Phase 2

- 비동기 worker
- 운영 메트릭/대시보드
- patch draft 와 PR description
- UI/IDE extension 강화

### Phase 3

- 승인 기반 write action
- 보안 리뷰 specialist
- 조직 표준 기반 팀별 skill rollout

## 16. 재작성 원칙

이 PRD 기반 재작성에서는 현재 저장소를 그대로 확장하는 것을 목표로 하지 않는다. 현재 저장소는 아래 용도로 활용한다.

- 제품 계약과 워크플로 개념의 참고 구현
- 초기 API/스키마 초안
- prompt/skill seed asset
- 테스트 시나리오 seed set

반면 아래 항목은 신규 구현을 원칙으로 한다.

- AI runtime
- connector 계층
- 저장/추적 인프라
- 인증/권한 계층
- 비동기 실행 구조

## 17. 최종 정의

이 제품의 MVP 성공은 "AI 가 멋진 문장을 쓰는 것"이 아니라, "개발자가 실제 작업 전 더 빠르고 더 정확하게 결정할 수 있게 만드는 것"으로 정의한다. 따라서 기능 범위, 기술 구조, 평가 체계 모두를 evidence, policy, traceability 중심으로 설계한다.
