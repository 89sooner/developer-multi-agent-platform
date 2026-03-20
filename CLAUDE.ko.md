# CLAUDE.ko.md

이 파일은 Claude Code (claude.ai/code)가 이 저장소에서 작업할 때 참고하는 가이드입니다.

## 프로젝트 개요

사내 개발자를 위한 멀티 에이전트 워크플로 서비스입니다. 개발자가 기능 구현, 버그 수정, 리팩터링, PR 리뷰를 자연어로 요청하면 서비스는:
1. 코드, 문서, 이슈, CI 시스템에서 컨텍스트 수집
2. 근거와 함께 구현 계획 생성
3. 테스트 전략과 리뷰 의견 작성
4. 신뢰도(confidence) 레벨과 함께 구조화된 응답 반환

아키텍처는 openai-agents의 **manager pattern**을 따릅니다: 중앙 Workflow Orchestrator가 대화를 소유하고 전문 에이전트들을 호출합니다 (handoff 방식 사용 안 함).

## 개발 명령어

```bash
# 개발 서버 (핫 리로드)
make dev
# 또는: uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 실행
make run

# 테스트 실행
make test
# 또는: pytest -q

# 린트/포맷
make lint   # ruff로 코드 검사
make fmt    # ruff로 코드 포맷팅
```

## 아키텍처 개요

### 에이전트 레이어 (`src/app/agents/`)

- **`orchestrator.py`**: 요청 분류 (feature/bugfix/refactor/review/test_plan), 호출할 전문 에이전트 결정, `INTENT_KEYWORDS`의 키워드 매칭으로 의도 신뢰도 점수 계산
- **`repo_context.py`**: repo, 문서, 이슈에서 근거 검색. `src/app/tools/`의 도구 호출
- **`implementation.py`**: 변경 계획, 대상 모듈, API 변경, 롤백 노트 생성
- **`test_strategy.py`**: 테스트 시나리오 생성 (단위/통합/회귀/에지 케이스)
- **`review.py`**: 결과 검토: 누락 근거, 숨겨진 의존성, 위험 요소
- **`requirements.py`**: 자연어 요구사항을 acceptance criteria로 정규화
- **`summary.py`**: 최종 `PlanResponse`, `ReviewResponse`, `TestPlanResponse` 객체 조합

모든 전문 에이전트는 **구조화된 출력** (`contracts/agent_results.py`의 Pydantic 모델)을 사용합니다.

### 도구 레이어 (`src/app/tools/`)

외부 시스템에서 균일한 evidence 객체 제공. 현재 스텁 상태:
- `repo_search.py`: Git/코드 검색
- `docs_search.py`: 문서/위키 검색
- `issue_lookup.py`: 이슈 트래커 쿼리
- `ci_lookup.py`: CI/테스트 결과 쿼리

모든 도구는 표준화된 `Evidence` 객체를 반환합니다 (`contracts/responses.py` 경유).

### 서비스 레이어 (`src/app/services/`)

- **`workflow_service.py`**: 핵심 조정. `_execute_step()`를 통한 에이전트 순서 오케스트레이션, 폴백 처리, 트레이싱. 메서드: `create_plan()`, `create_review()`, `create_test_plan()`, `get_run()`, `get_trace()`, `create_feedback()`.
- **`skill_registry.py`**: 에이전트 이름을 스킬 버전에 매핑 (카나리 롤아웃용).

### 스토리지 (`src/app/storage/`)

`repositories.py`가 세 개 테이블로 `SQLiteStore` 구현:
- `runs`: 워크플로 실행 (상태, 타임스탬프, 에이전트, 모델)
- `traces`: 에이전트/도구 호출 이력
- `feedback`: 사용자 평가와 수정

파일은 `.runtime/traces/{run_id}.json`로 내보내기.

### 코어 (`src/app/core/`)

- **`config.py`**: `pydantic-settings`를 통한 설정, `.env`에서 로드
- **`auth.py`**: `user_id`, `repo_scopes`, `roles`가 포함된 `UserContext`
- **`policy.py`**: 가드레일: `enforce_repo_scope()`, `require_approval()`
- **`tracing.py`**: 에이전트 스텝의 상태, 신뢰도, 에러를 추적하는 `TraceRecorder`
- **`rate_limit.py`**: 요청 스로틀링

### API (`src/app/api/`)

`router.py` 포함 엔드포인트:
- `/v1/workflows/plan` (POST)
- `/v1/workflows/review` (POST)
- `/v1/workflows/test-plan` (POST)
- `/v1/workflows/{run_id}` (GET)
- `/v1/workflows/{run_id}/trace` (GET)
- `/v1/feedback` (POST)

모든 라우트는 `UserContext`로 검증하고 repo scope 강제 적용.

### 컨트랙트 (`src/app/contracts/`)

- **`requests.py`**: `PlanRequest`, `ReviewRequest`, `TestPlanRequest`, `FeedbackRequest`
- **`responses.py`**: API용 응답 DTO
- **`agent_results.py`**: 각 에이전트의 구조화된 출력 (예: `RepoContextResult`, `ImplementationResult`, `ReviewResult`)

### 스킬 디렉토리 (`skills/`)

각 스킬 포함 내용:
- `SKILL.md`: 스킬 정의와 목적
- `agents/openai.yaml`: openai-agents 설정
- `references/`: 지원 문서, 패턴, 체크리스트

스킬은 전문 에이전트와 1:1 매핑. 프롬프트 템플릿은 `prompts/`에 위치.

## 핵심 디자인 패턴

### 워크플로 실행

1. `WorkflowService._run_orchestrator()`가 `run_id`, `trace_id`를 생성하고 의도 분류
2. `_start_run()`이 초기 run 상태 저장
3. 각 에이전트 스텝은 `_execute_step()`으로 실행되며 폴백 처리
4. `TraceRecorder`가 스텝별 타이밍, 신뢰도, 에러 캡처
5. `_finish_run()`이 run 상태 업데이트하고 trace 내보내기

### 에이전트 선택 규칙 (`orchestrator.py` 기준)

- feature/bugfix/refactor → requirements-planner + repo-context-finder + implementation-planner [+ include_tests 시 test-strategy-generator] + review-gate + summary-composer
- review → repo-context-finder + test-strategy-generator + review-gate + summary-composer
- test_plan → test-strategy-generator + summary-composer

### 신뢰도 레벨

순서: `low < medium < high`. `collapse_confidence()`로 축소. 낮은 신뢰도는 최종 응답에서 경고 트리거.

### 폴백 동작

각 에이전트는 `WorkflowService`의 `_fallback_*()` 메서드를 가지며, `confidence="low"`로 저하된 결과와 설명 메시지를 반환.

## 현재 구현 상태

- **완료**: FastAPI 스캐폴드, 에이전트 컨트랙트, SQLite 스토리지, 오케스트레이터 로직, 정책 레이어, 트레이싱
- **스텁**: 모든 도구 (`repo_search`, `docs_search`, `issue_lookup`, `ci_lookup`)가 더미 evidence 반환
- **대기 중**: 실제 openai-agents 연동, 실제 Git/문서/CI 커넥터

## 다음 우선순위 (README 기준)

1. 실제 Git/코드 검색으로 `repo_search_tool` 구현
2. 모든 에이전트에 `run_store`와 `trace_store` 연결
3. 오케스트레이터 + 전문 에이전트를 openai-agents 런타임으로 연결
4. 리뷰 단계와 승인 워크플로 추가
5. IDE 익스텐션 또는 내부 웹 UI 연동

## 중요 제약

- 쓰기 작업은 명시적 `approval_token` 필요 (`require_approval()` 강제)
- Repo scope는 tool 레이어에서 `UserContext.repo_scopes`로 강제
- Evidence는 필수 포함: `source_type`, `source_id`, `locator`, `snippet`, `timestamp`, `confidence`
- 모든 구조화된 출력은 Pydantic으로 검증
- 한국어(`ko`)가 기본 응답 언어
