# 현재 구현 분석 및 기능/기술 스펙

작성일: 2026-03-21  
분석 대상: `docs/prd.md`, `docs/system-architecture.md`, `docs/api-spec.md`, `docs/prd-implementation-check.md`, `src/app/**`, `tests/**`

## 1. 결론

현재 저장소는 더 이상 단순 설계 저장소가 아니다. FastAPI 기반 API, manager pattern 워크플로 서비스, 구조화된 응답 계약, SQLite 기반 run/trace/feedback 저장, 로컬 파일 기반 evidence 수집기, 권한/승인 가드레일, 기본 테스트까지 갖춘 실행 가능한 MVP 백엔드다.

다만 제품의 핵심 차별점이 되어야 할 "실제 AI 기반 멀티 에이전트 시스템"은 아직 구현되지 않았다. 현재 specialist agent 는 LLM 호출이 아니라 규칙 기반의 결정론적 함수이고, repo/docs/issue/CI 연동도 실제 사내 시스템이 아니라 현재 워크스페이스와 로컬 파일을 읽는 개발용 커넥터다. 따라서 현재 상태를 정확히 규정하면:

- 제품 계약과 실행 흐름은 상당 부분 구체화되었다.
- 운영형 AI 플랫폼으로서의 핵심 구현은 아직 남아 있다.
- 재작성 시 문서/계약/테스트는 재사용 가치가 높지만, 런타임 핵심부는 새로 설계하는 편이 맞다.

## 2. 검증 요약

- 문서, 코드, 테스트를 함께 대조했다.
- 로컬 샘플 요청으로 `POST /v1/workflows/plan` 을 직접 실행해 실제 응답을 확인했다.
- 테스트는 `uv run --with pytest python -m pytest -q -s` 로 실행했고 `6 passed in 0.16s` 를 확인했다.

## 3. 완성도 평가

| 영역 | 상태 | 판단 |
| --- | --- | --- |
| API 표면 | 높음 | `plan`, `review`, `test-plan`, `run 조회`, `trace 조회`, `feedback` 가 모두 구현되어 있다. |
| 워크플로 오케스트레이션 | 높음 | manager pattern, 단계별 trace, review-last 흐름이 구현되어 있다. |
| 구조화된 계약 | 높음 | 요청/응답 및 agent step 결과가 Pydantic 스키마로 고정되어 있다. |
| evidence 수집 | 중간 | repo/docs 검색은 동작하지만 현재 워크스페이스 중심이다. issue/CI 는 로컬 파일 기반이다. |
| 보안/가드레일 | 중간 | scope enforcement, rate limiting, approval gate, 민감정보 마스킹은 있다. 실제 SSO/RBAC 는 없다. |
| 영속화/감사 | 중간 이상 | SQLite run/trace/feedback 저장과 trace export 가 있다. 운영용 스토어/메트릭 체계는 아니다. |
| AI 런타임 | 낮음 | openai-agents 실연동, 모델 호출, prompt 실행, tool-using agent runtime 이 없다. |
| 외부 시스템 통합 | 낮음 | 실제 Git/docs/wiki/issue/CI 시스템과 연결되지 않는다. |
| 운영 준비도 | 낮음~중간 | 로컬 MVP 백엔드로는 충분하지만 worker, queue, metrics, production auth, secret 관리가 없다. |

## 4. 현재 구현된 기능 스펙

### 4.1 사용자 인터페이스

현재 제품 표면은 HTTP API 다. Web UI, IDE extension, CLI UX 는 아직 없다.

제공 엔드포인트:

| 엔드포인트 | 기능 | 상태 |
| --- | --- | --- |
| `POST /v1/workflows/plan` | 개발 요청 분석, 영향 범위/구현 계획/테스트/리스크 생성 | 구현 |
| `POST /v1/workflows/review` | 변경안 또는 PR 초안 리뷰 | 구현 |
| `POST /v1/workflows/test-plan` | 테스트 전략 생성 | 구현 |
| `GET /v1/workflows/{run_id}` | run 조회 | 구현 |
| `GET /v1/workflows/{run_id}/trace` | trace 조회 | 구현 |
| `POST /v1/feedback` | 피드백 저장 | 구현 |
| `GET /health` | 헬스체크 | 구현 |

### 4.2 입력 계약

실제 구현 기준 주요 요청 필드는 아래와 같다.

#### PlanRequest / ReviewRequest

- `request_type`: optional, `feature | bugfix | refactor | review | test_plan`
- `repo_id`
- `branch`
- `task_text`
- `artifacts.issue_ids`
- `artifacts.pr_url`
- `artifacts.changed_files`
- `options.include_tests`
- `options.language`
- `options.write_actions`
- `options.approval_token`
- `diff_text` 는 review 요청에서만 추가 가능

실무적으로 중요한 해석:

- `request_type` 는 필수가 아니라 힌트다.
- 실제 분류는 `task_text` 기반 키워드 스코어링과 `request_type` 힌트를 함께 쓴다.
- `write_actions` 는 실제 write 를 수행하지 않지만, 요청 의도를 선언하는 정책 입력으로 쓰인다.

#### TestPlanRequest

- `repo_id`
- `branch`
- `implementation_plan`
- `impacted_areas`

### 4.3 출력 계약

현재 구현된 대표 출력은 아래와 같다.

#### plan 응답

- `summary`
- `impacted_areas`
- `implementation_plan`
- `tests`
- `risks`
- `open_questions`
- `evidence`
- `confidence`
- 공통 메타데이터: `run_id`, `trace_id`, `primary_intent`, `secondary_intents`, `selected_agents`, `model_version`, `skill_versions`, `warnings`

#### review 응답

- `summary`
- `review_findings`
- `missing_tests`
- `risks`
- `readiness_verdict`
- `evidence`
- 공통 메타데이터

#### test-plan 응답

- `unit_tests`
- `integration_tests`
- `regression_targets`
- `edge_cases`
- `execution_order`
- 공통 메타데이터

### 4.4 실제 동작하는 워크플로

#### plan 워크플로

1. 인증과 repo scope 검증을 수행한다.
2. 승인 토큰이 필요한 write action 인지 검사한다.
3. orchestrator 가 요청 intent 를 분류하고 selected agent 집합을 결정한다.
4. requirements agent 가 자연어 요청을 정규화한다.
5. repo context agent 가 repo/docs/issues/CI evidence 를 수집한다.
6. implementation agent 가 change plan 과 risks 를 생성한다.
7. 선택적으로 test strategy agent 가 테스트 시나리오를 생성한다.
8. review agent 가 누락 근거, 숨은 의존성, 회귀 리스크를 점검한다.
9. summary 단계가 최종 응답을 조립한다.
10. run, trace 를 저장하고 결과를 반환한다.

#### review 워크플로

1. intent 는 강제로 `review` 로 고정된다.
2. repo context 수집
3. test strategy 생성
4. review 생성
5. summary 조립
6. run/trace 저장

#### test-plan 워크플로

1. 독립 `test_plan` run 을 만든다.
2. synthetic request 를 내부적으로 구성한다.
3. test strategy agent 만 실행한다.
4. summary 조립 후 저장한다.

### 4.5 evidence 수집 스펙

현재 evidence 수집은 "실제 사내 시스템 연동"이 아니라 "로컬 워크스페이스/파일 기반 evidence normalization" 으로 구현되어 있다.

#### repo search

- 검색 대상: `src/`, `tests/`, 그리고 changed_files 로 지정된 실제 파일
- 방식: 키워드 추출 후 파일 경로/본문 매칭 점수화
- 반환: 상위 6개 evidence

#### docs search

- 검색 대상: `docs/`, `README.md`, `prompts/`, `skills/`
- 방식: 키워드 기반 파일 점수화
- 반환: 상위 6개 evidence

#### issue lookup

- 검색 대상: `data/issues/`, `.runtime/issues/`
- 입력: `issue_ids`
- 방식: 동일 이름 파일을 읽어 evidence 로 변환

#### CI lookup

- 검색 대상: `data/ci/<repo_id>/`, `.runtime/ci/<repo_id>/`
- 입력: `repo_id`, `branch`
- 방식: `<branch>.json|md`, `latest.json|md` 우선순위 조회

#### evidence 공통 처리

- 모든 evidence 는 표준 객체로 정규화된다.
- 민감정보 패턴은 snippet 수준에서 마스킹된다.
- evidence 수와 uncertainty 수를 기반으로 confidence 를 계산한다.

### 4.6 저장 및 조회 스펙

현재 영속 계층은 SQLite 단일 스토어다.

저장 테이블:

- `runs`
- `traces`
- `feedback`

저장 항목:

- run 메타데이터
- 원본 request payload
- 최종 result payload
- primary/secondary intent
- selected agents
- user_id, repo_scope
- model_version, skill_versions
- trace payload
- feedback payload

추가 동작:

- trace 는 DB 저장과 별도로 `.runtime/traces/<run_id>.json` 으로 export 된다.

### 4.7 인증/권한/정책 스펙

현재 보안 관련 실제 동작은 다음과 같다.

- 인증: `Authorization: Bearer sub=...;repos=...;roles=...` 형태의 개발용 claim parser
- repo scope enforcement: 사용자 repo scope 밖의 `repo_id` 는 403
- role 저장: `admin` role 은 run/trace/feedback 타 사용자 조회에 사용 가능
- rate limiting: 사용자별 메모리 버킷 기반
- approval gate: `write_actions` 가 있으면 `approval_token` 필요
- masking: evidence snippet 에 secret pattern redaction 적용

### 4.8 장애 대응 스펙

각 단계는 예외 발생 시 전체 요청을 즉시 실패시키지 않고 fallback 결과를 생성한다.

- requirements 실패 시 low-confidence requirements fallback
- repo context 실패 시 빈 evidence + uncertainty fallback
- implementation 실패 시 generic change plan fallback
- test strategy 실패 시 빈 test fallback
- review 실패 시 blocked verdict fallback

이 동작으로 degraded mode 응답이 가능하다.

### 4.9 품질 보증 스펙

현재 테스트가 커버하는 범위:

- health endpoint
- plan workflow 결과 생성
- run/trace persistence
- primary intent / selected agent / skill version 메타데이터
- repo scope violation
- approval gate
- review workflow
- rate limiting

## 5. 현재 기술 스펙

### 5.1 기술 스택

- 언어: Python 3.11+
- API 프레임워크: FastAPI
- 스키마/계약: Pydantic v2
- 실행: 단일 프로세스 in-process 서비스
- 저장소: SQLite
- 테스트: pytest + httpx ASGI transport
- 의존성 선언상 AI 라이브러리: `openai-agents`

### 5.2 실제 런타임 아키텍처

현재 런타임은 아래 계층으로 구성된다.

1. API 라우터
2. auth/rate limit/policy
3. workflow service
4. orchestrator + specialist agents
5. tool layer
6. SQLite store + trace exporter

중요한 구현 특성:

- worker 프로세스가 없다.
- async queue 가 없다.
- 모든 워크플로는 요청 스레드 안에서 동기적으로 끝난다.
- agent 간 직접 통신은 없고 workflow service 가 순서를 통제한다.

### 5.3 agent 실행 방식

현재 agent 는 LLM 호출 기반이 아니라 Python 함수 기반 결정론적 로직이다.

실제 의미:

- structured output 은 존재하지만 model output validation 이 아니다.
- prompt 파일과 skill 자산은 버전 계산 또는 참고 자산으로만 존재한다.
- specialist agent 결과는 규칙, 키워드, evidence 수, 경로 추론으로 생성된다.

### 5.4 trace 구조

trace 에는 다음이 저장된다.

- step 이름
- step 순서
- 상태
- 시작/종료 시각
- latency
- tool call 수
- confidence
- input/output ref
- error_message
- tool call 레코드

현재 제한:

- 진짜 span tree 는 없다.
- `spans` 는 `steps` 를 그대로 재사용한다.
- token usage, model latency, prompt version 실행 정보는 없다.

### 5.5 skill/version 처리

현재 skill registry 는 동적 실행기가 아니라 버전 해시 계산기 역할에 가깝다.

- selected agent 이름 기준으로 skill version 을 계산한다.
- 각 skill 의 `SKILL.md`, `agents/openai.yaml` 파일을 hash 해 version 을 만든다.
- `summary-composer` 는 builtin 값이다.

즉, "버전 기록"은 구현되었지만 "실제 skill 로딩 및 실행"은 구현되지 않았다.

## 6. PRD 대비 갭 분석

| 항목 | PRD 기대 상태 | 현재 상태 | 판정 |
| --- | --- | --- | --- |
| manager pattern | 중앙 orchestrator 가 specialist 를 통제 | 구현 | 유지 대상 |
| structured output chaining | 단계 간 JSON 계약 연결 | 구현 | 유지 대상 |
| requirements/repo context/implementation/review/test strategy | specialist 분리 | 구현 | 유지 대상 |
| Summary Composer | 최종 응답 조립 | 구현 | 유지 대상 |
| openai-agents 기반 AI runtime | 실모델 기반 실행 | 미구현 | 재작성 핵심 |
| prompt/skill runtime 사용 | 실제 실행 입력으로 사용 | 미구현 | 재작성 필요 |
| 실제 Git/docs/wiki/issue/CI 연결 | 사내 시스템 연결 | 미구현 | 재작성 핵심 |
| API gateway + worker 분리 | scale 가능한 배포 구조 | 미구현 | 재작성 필요 |
| Postgres run store | 운영형 저장소 | 미구현 | 재작성 필요 |
| tracing sink/OTLP | 중앙 관측 체계 | 미구현 | 재작성 필요 |
| SSO/실제 RBAC | enterprise auth | 미구현 | 재작성 필요 |
| approval workflow | 승인 기반 write action | gate 만 구현, write 미구현 | 부분 구현 |
| async 처리 | 긴 요청 비동기화 | 미구현 | 재작성 필요 |
| UI/IDE extension | 사용자 접점 | 미구현 | 차기 또는 MVP 범위 결정 필요 |
| feedback loop | 저장 후 품질 개선 | 저장만 구현 | 부분 구현 |

## 7. 재작성 시 유지/폐기/대체 권고

### 7.1 유지할 것

- manager pattern 기본 전략
- endpoint 구조와 핵심 응답 계약
- evidence, confidence, warnings, open_questions 중심의 출력 철학
- run/trace/feedback 를 분리 저장하는 개념
- approval gate 와 scope enforcement 정책
- review-last 워크플로
- skill version, model version 을 결과에 남기는 감사 패턴
- 현재 테스트가 표현하는 최소 제품 계약

### 7.2 대체할 것

- 규칙 기반 specialist agent -> 실제 LLM + structured output 단계
- 로컬 파일 검색기 -> 실제 repo/docs/wiki/issue/CI connector
- SQLite 단일 스토어 -> 운영형 DB + object storage + trace sink
- 개발용 bearer claim parser -> 실제 SSO/IdP + RBAC
- in-process sync 실행 -> queue/worker 기반 실행

### 7.3 폐기하거나 참고용으로 격하할 것

- 현재 heuristic response 생성 로직을 제품 핵심으로 보는 해석
- `repo_id`, `branch` 를 받아도 현재 워크스페이스만 검색하는 임시 방식
- prompt/skill 파일이 이미 런타임에 연결돼 있다고 보는 가정

### 7.4 재작성 입력 자산으로 재사용할 것

- `docs/prd.md`, `docs/system-architecture.md`, `docs/api-spec.md`
- `src/app/contracts/*.py`
- `tests/test_workflows.py`, `tests/test_health.py`
- `prompts/*`
- `skills/*`

## 8. 최종 판단

현재 프로젝트는 "개발자용 AI 워크플로 제품"의 실행 가능한 백엔드 프로토타입이다. 제품 계약, 단계 분리, 증거 기반 응답, 저장과 추적, 정책 가드레일은 충분히 구체적이다. 반면 실제 AI 추론, 실제 조직 시스템 연동, 운영 환경 아키텍처는 아직 프로토타입 단계에 머물러 있다.

따라서 AI 로 바닥부터 재작성할 때는 현재 코드를 그대로 확장하기보다, 다음 원칙이 맞다.

1. 현재 계약과 워크플로 개념은 설계 기준으로 유지한다.
2. 현재 런타임 구현은 개발용 참조 구현으로만 본다.
3. AI 실행기, connector 계층, 운영 인프라는 새 제품 기준으로 다시 설계한다.
