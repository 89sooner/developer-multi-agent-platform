# PRD 구현 점검

작성일: 2026-03-20

## 1. 총평

현재 저장소는 PRD를 바로 개발 시작할 수 있도록 문서, 프롬프트, Skill 초안, FastAPI 스캐폴드를 갖춘 상태다. 다만 PRD가 요구하는 핵심 MVP를 기준으로 보면 실제 구현 상태는 "부분 구현"이며, 특히 중앙 오케스트레이션, specialist agent 실행, 실제 connector 연동, 권한/승인, 영속 저장, tracing은 아직 스텁 또는 설계 단계에 머물러 있다.

판정:

- 문서 정합성: 보완 완료
- API 스캐폴드: 구현됨
- PRD MVP 런타임: 부분 구현
- PRD Phase 2/3 범위: 대부분 미구현

## 2. 항목별 점검 결과

| 항목 | 상태 | 근거 |
| --- | --- | --- |
| `POST /v1/workflows/plan`, `review`, `test-plan`, `GET run`, `GET trace`, `POST feedback` 엔드포인트 | 구현 | `src/app/api/routes/workflows.py`, `src/app/api/routes/feedback.py` |
| 요청/응답 Pydantic 계약과 evidence 스키마 | 구현 | `src/app/contracts/requests.py`, `src/app/contracts/responses.py` |
| run/trace/feedback 저장소 개념 | 부분 구현 | `src/app/storage/repositories.py` 에 인메모리 저장소만 존재 |
| Workflow Service에서 run_id/trace_id 발급 | 구현 | `src/app/services/workflow_service.py` |
| Repo/docs/issue/CI evidence 수집 흐름 | 부분 구현 | tool 함수가 존재하지만 모두 stub 반환 |
| Review 결과 생성 | 부분 구현 | 실제 분석 없이 고정된 findings를 반환 |
| Test plan 생성 API | 구현 | 별도 엔드포인트는 존재하나 계획 워크플로 내부 자동 호출은 없음 |
| Workflow Orchestrator manager pattern | 미구현 | 실제 agent 실행 없이 프롬프트 텍스트만 로드 |
| Specialist agent structured output chaining | 미구현 | 단계별 JSON 계약 검증/연결 로직 없음 |
| Requirements Agent 실사용 | 미구현 | 프롬프트 로더만 있고 서비스 흐름에 연결되지 않음 |
| Summary Composer 실사용 | 미구현 | 전용 컴포넌트 없음 |
| 요청 자동 분류 | 미구현 | 클라이언트가 `request_type`를 직접 넣어야 함 |
| primary/secondary intent 분리 | 미구현 | 관련 모델/로직 없음 |
| reviewer 단계 강제 마지막 실행 | 부분 구현 | trace step은 그렇게 기록하지만 실제 실행 제어는 없음 |
| skill_version/model_version 기록 | 미구현 | run 결과에 저장되지 않음 |
| user_id/repo_scope 감사 정보 저장 | 미구현 | 저장 필드 없음 |
| SSO/RBAC/rate limiting | 미구현 | API 계층에 인증/권한 처리 없음 |
| human approval gate | 미구현 | 승인 토큰/승인 단계 관련 코드 없음 |
| persistent run/trace store | 미구현 | DB 연동 없음 |
| 실제 tracing/export | 미구현 | synthetic trace payload만 저장 |
| graceful degradation/fallback 메시지 | 부분 구현 | 실패 처리 분기 없이 정상 응답만 가정 |
| 테스트 커버리지 | 미흡 | `tests/test_health.py` 1건만 존재 |

## 3. PRD 관점 상세 판단

### 3.1 MVP Phase 1

- Workflow Orchestrator: 미구현
- Repo Context Agent: 부분 구현
- Implementation Agent: 부분 구현
- Review Agent: 부분 구현
- plan/review API: 구현
- run/trace 저장: 부분 구현

해석:

MVP Phase 1의 외형은 존재하지만, 실제 "멀티 에이전트 서비스"라고 부를 수 있는 실행 런타임은 아직 구현되지 않았다.

### 3.2 기능 요구사항

- 요청 분류: 미구현
- 컨텍스트 수집: 부분 구현
- 구현 계획 생성: 부분 구현
- 테스트 계획 생성: 부분 구현
- 리뷰 생성: 부분 구현
- 최종 응답 형식 고정: 구현

### 3.3 비기능 요구사항

- 성능 목표: 검증 불가
- 단계별 실패 추적: 부분 구현
- 보안/권한 제어: 미구현
- 감사 가능성: 부분 구현

## 4. 코드에서 확인한 주요 갭

### 4.1 실제 agent runtime 부재

`src/app/agents/*.py` 는 모두 프롬프트 파일을 읽는 helper 수준이다. 오케스트레이터가 specialist agent를 선택하거나 structured output으로 다음 단계에 넘기는 실행기가 없다.

### 4.2 서비스 응답이 고정값 중심

`src/app/services/workflow_service.py` 는 evidence 일부만 tool 함수에서 가져오고, summary, impacted_areas, implementation_plan, risks 등은 요청 맥락과 무관한 고정 텍스트로 채운다.

### 4.3 tool 계층이 stub

`src/app/tools/repo_search.py`, `docs_search.py`, `issue_lookup.py`, `ci_lookup.py` 는 실제 외부 시스템 연결 없이 예시 evidence만 반환한다.

### 4.4 저장/트레이싱이 영속적이지 않음

`src/app/storage/repositories.py` 는 인메모리 dict 기반이며, 프로세스 재시작 시 데이터가 사라진다. trace도 span 단위가 아니라 요약 step만 저장한다.

### 4.5 운영 가드레일 누락

PRD의 승인 포인트, 권한 상속, SSO/RBAC, 민감정보 마스킹, skill/model 버전 기록이 현재 API/서비스에 반영되어 있지 않다.

## 5. 실행 검증 메모

현재 환경에서 자동 검증도 제한이 있었다.

- `pytest -q` 실행 시 `fastapi` 미설치 환경으로 수집 실패
- `python -m pytest -q` 실행 시 `pytest` 미설치
- `fastapi.testclient` 기반 스모크 실행 시 `httpx` 미설치로 실패

해석:

프로젝트의 `pyproject.toml` 에 필요한 의존성은 선언되어 있으나, 현재 작업 환경에는 해당 패키지가 모두 설치되어 있지 않았다. 따라서 동적 검증보다는 정적 코드 점검 중심으로 판정했다.

## 6. 우선순위 제안

1. `WorkflowService` 에 실제 orchestrator 런타임을 도입해 request classification, agent selection, step chaining을 구현한다.
2. stub tool을 실제 repo/docs/issue/CI connector로 교체하고 evidence confidence 정책을 넣는다.
3. run/trace/feedback 저장소를 Postgres 등 영속 계층으로 교체하고 `skill_version`, `model_version`, `user_id`, `repo_scope` 를 저장한다.
4. approval gate, 인증/권한, 민감정보 마스킹을 policy layer로 추가한다.
5. plan/review/test-plan API에 대한 통합 테스트를 작성하고 실행 환경 의존성을 고정한다.

## 7. 최종 판정

현재 프로젝트는 "PRD를 설명하는 설계 저장소 + 초기 서버 골격" 으로는 적절하지만, "PRD대로 구현된 서비스" 로 보기는 어렵다. 특히 MVP 핵심인 manager pattern 기반 멀티 에이전트 실행, 실제 근거 수집, 운영 가드레일, 감사 가능한 저장 계층이 아직 비어 있다.
