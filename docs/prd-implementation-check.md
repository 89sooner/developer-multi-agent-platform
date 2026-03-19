# PRD 구현 점검

작성일: 2026-03-20
갱신일: 2026-03-20

## 1. 총평

현재 저장소는 문서 중심 설계 저장소에서 한 단계 더 나아가, manager pattern 기반 워크플로 런타임, 구조화된 specialist agent 결과 연결, SQLite 기반 run/trace 영속화, 인증/권한/승인 게이트, trace export, API 테스트까지 포함하는 실행 가능한 MVP 백엔드 골격으로 보강되었다.

단, 아래 해석은 유지한다.

- 외부 Git/docs/issue/CI 시스템은 아직 실제 사내 SaaS/온프렘 커넥터가 아니라 local/workspace 기반 connector 로 동작한다.
- 인증은 실제 SSO 연동이 아니라 SSO claim 형태를 흉내 낸 개발용 bearer claim parser 로 구현되어 있다.
- agent runtime 은 openai-agents 실모델 호출이 아니라 구조화된 deterministic runtime 으로 구현되어 있다.

판정:

- 문서 정합성: 구현 상태 기준으로 갱신 필요 항목만 남음
- API 스캐폴드: 구현됨
- PRD MVP 런타임: 구현됨
- PRD Phase 2/3 범위: 일부 선반영, 다수는 차기 과제

## 2. 항목별 점검 결과

| 항목 | 상태 | 근거 |
| --- | --- | --- |
| `POST /v1/workflows/plan`, `review`, `test-plan`, `GET run`, `GET trace`, `POST feedback` 엔드포인트 | 구현 | `src/app/api/routes/workflows.py`, `src/app/api/routes/feedback.py` |
| 요청/응답 Pydantic 계약과 evidence 스키마 | 구현 | `src/app/contracts/requests.py`, `src/app/contracts/responses.py` |
| run/trace/feedback 저장소 개념 | 구현 | `src/app/storage/repositories.py` 의 SQLite 영속 저장소 |
| Workflow Service에서 run_id/trace_id 발급 | 구현 | `src/app/services/workflow_service.py` |
| Repo/docs/issue/CI evidence 수집 흐름 | 구현 | `src/app/tools/*.py` 에 local/workspace 기반 connector 구현 |
| Review 결과 생성 | 구현 | `src/app/agents/review.py`, `src/app/agents/summary.py` |
| Test plan 생성 API | 구현 | `src/app/services/workflow_service.py`, `src/app/agents/test_strategy.py` |
| Workflow Orchestrator manager pattern | 구현 | `src/app/agents/orchestrator.py`, `src/app/services/workflow_service.py` |
| Specialist agent structured output chaining | 구현 | `src/app/contracts/agent_results.py` 기반 step 결과 연결 |
| Requirements Agent 실사용 | 구현 | `src/app/agents/requirements.py`, plan workflow 에 연결 |
| Summary Composer 실사용 | 구현 | `src/app/agents/summary.py` |
| 요청 자동 분류 | 구현 | `src/app/agents/orchestrator.py` |
| primary/secondary intent 분리 | 구현 | `IntentClassification`, API 응답/저장소에 반영 |
| reviewer 단계 강제 마지막 실행 | 구현 | plan/review trace 에서 `review -> summary` 순서 강제 |
| skill_version/model_version 기록 | 구현 | response 와 run store 에 저장 |
| user_id/repo_scope 감사 정보 저장 | 구현 | `RunDetailResponse`, SQLite runs table |
| SSO/RBAC/rate limiting | 구현 | `src/app/core/auth.py`, `src/app/core/rate_limit.py` |
| human approval gate | 구현 | `write_actions` + `approval_token` 검증 |
| persistent run/trace store | 구현 | `.runtime/workflows.sqlite3`, `.runtime/traces/*.json` |
| 실제 tracing/export | 구현 | step/tool call timestamp 저장 + trace export 파일 |
| graceful degradation/fallback 메시지 | 구현 | workflow step fallback 과 warning 누적 |
| 테스트 커버리지 | 구현 | `tests/test_workflows.py`, `tests/test_health.py` |

## 3. PRD 관점 상세 판단

### 3.1 MVP Phase 1

- Workflow Orchestrator: 구현
- Repo Context Agent: 구현
- Implementation Agent: 구현
- Review Agent: 구현
- plan/review API: 구현
- run/trace 저장: 구현

해석:

이제 MVP Phase 1 은 “문서와 모형” 수준이 아니라 실제로 실행 가능한 개발용 백엔드 런타임으로 볼 수 있다.

### 3.2 기능 요구사항

- 요청 분류: 구현
- 컨텍스트 수집: 구현
- 구현 계획 생성: 구현
- 테스트 계획 생성: 구현
- 리뷰 생성: 구현
- 최종 응답 형식 고정: 구현

### 3.3 비기능 요구사항

- 성능 목표: 아직 정량 검증 전
- 단계별 실패 추적: 구현
- 보안/권한 제어: 구현
- 감사 가능성: 구현

## 4. 코드에서 확인한 주요 갭

초기 점검에서 지적했던 큰 갭은 대부분 해소되었다.

### 4.1 실제 agent runtime 부재

해소됨.

- `src/app/services/workflow_service.py` 에서 오케스트레이터가 specialist agent 를 manager pattern 으로 호출한다.
- `src/app/contracts/agent_results.py` 로 단계 간 structured output 계약을 강제한다.

### 4.2 서비스 응답이 고정값 중심

해소됨.

- 응답은 분류 결과, repo evidence, implementation/test/review 결과를 합성해서 생성된다.
- `src/app/agents/summary.py` 가 최종 응답 객체를 구성한다.

### 4.3 tool 계층이 stub

해소됨.

- repo/doc 검색은 실제 workspace 파일 검색을 수행한다.
- issue/ci 는 local file-backed connector 로 대체되었다.

### 4.4 저장/트레이싱이 영속적이지 않음

해소됨.

- run/trace/feedback 은 SQLite 에 저장된다.
- trace 는 JSON export 파일로도 남는다.

### 4.5 운영 가드레일 누락

대부분 해소됨.

- repo scope enforcement
- approval gate
- 민감정보 마스킹
- model/skill version 기록
- rate limiting

남은 과제:

- 실제 사내 SSO/IdP 연동
- 외부 Git/docs/issue/CI 실커넥터 연동
- 실모델 기반 openai-agents runtime 연결

## 5. 실행 검증 메모

실행 검증은 완료했다.

- `python -m compileall src/app tests` 통과
- 서비스 객체 direct smoke test 통과
- `pytest -q` 통과

결과:

- 총 6개 테스트 통과
- 인증, scope enforcement, approval gate, auto classification, run/trace persistence, rate limiting 을 검증했다

## 6. 우선순위 제안

1. local connector 를 실제 사내 Git/docs/issue/CI connector 로 교체한다.
2. 개발용 bearer claim parser 를 실제 SSO/IdP 연동으로 대체한다.
3. deterministic agent runtime 을 openai-agents 기반 런타임으로 연결한다.
4. p95 latency, tool success rate, low confidence rate 를 메트릭으로 수집한다.
5. IDE extension 또는 internal UI 와 연결한다.

## 7. 최종 판정

현재 프로젝트는 더 이상 “PRD를 설명하는 설계 저장소 + 초기 서버 골격” 수준이 아니다. PRD의 MVP 핵심이었던 manager pattern 기반 멀티 에이전트 흐름, structured output chaining, review-last orchestration, approval gate, 감사 가능한 run/trace 저장 계층은 구현되었다.

다만 production-ready 판정까지는 아직 남은 일이 있다. 특히 외부 시스템 실연동, 실제 SSO, 실모델 기반 agent runtime, 운영 메트릭 수집은 차기 작업으로 보는 것이 정확하다.
