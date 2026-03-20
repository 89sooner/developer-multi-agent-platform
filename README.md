# developer-multi-agent-platform

사내 개발자가 개발 단계에서 자연어로 요청하면, 코드/문서/이슈/CI 맥락을 수집하고 구현 계획, 테스트 포인트, 리뷰 의견까지 생성하는 멀티 에이전트 서비스의 설계 저장소다.

이 저장소는 다음 내용을 바로 시작할 수 있게 포함한다.

- PRD
- 시스템 아키텍처 상세 설계서
- agent별 prompt 초안
- skill 초안
- OpenAPI 기반 API 스펙 초안
- MVP 개발 일정안
- FastAPI 기반 서버 스캐폴드
- JSON/Pydantic 계약 초안
- 기본 디렉터리 구조와 실행 예시

## 권장 스택

- Python 3.11+
- FastAPI
- Pydantic
- openai-agents
- Uvicorn
- uv

## 저장소 구조

```text
developer-multi-agent-platform/
├── docs/
│   ├── prd.md
│   ├── system-architecture.md
│   ├── agent-skill-drafts.md
│   ├── api-spec.md
│   ├── mvp-schedule.md
│   └── openapi.yaml
├── prompts/
│   ├── orchestrator.md
│   ├── repo_context.md
│   ├── implementation.md
│   ├── review.md
│   ├── requirements.md
│   └── test_strategy.md
├── skills/
│   ├── workflow-orchestrator/
│   ├── repo-context-finder/
│   ├── implementation-planner/
│   ├── review-gate/
│   ├── requirements-planner/
│   └── test-strategy-generator/
├── src/app/
│   ├── api/
│   ├── agents/
│   ├── contracts/
│   ├── core/
│   ├── services/
│   ├── storage/
│   └── tools/
├── tests/
├── .env.example
├── .gitignore
├── Makefile
├── pyproject.toml
└── Dockerfile
```

## 빠른 시작

### 1. 환경 변수 준비

```bash
cp .env.example .env
```

### 2. 가상환경 및 패키지 설치

```bash
uv sync --dev
```

`pyproject.toml` 은 Python `>=3.11`을 요구하고, `.python-version`은 `3.11`로 고정되어 있다.
`uv`를 사용하면 로컬에 Python 3.10만 있더라도 필요한 버전을 자동으로 준비할 수 있다.

### 3. 서버 실행

```bash
make dev
```

또는

```bash
uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 테스트 실행

```bash
make test
```

## Python 버전 이슈 트러블슈팅

Python 3.10에서 아래와 같은 오류가 발생할 수 있다.

```text
ImportError: cannot import name 'UTC' from 'datetime'
```

이 프로젝트는 Python 3.11 이상의 `datetime.UTC`를 사용한다. 다음 순서로 해결한다.

```bash
uv python install 3.11
uv sync --dev
make dev
```

## 현재 상태

- 문서와 골격 코드는 준비되어 있다
- 실제 repo/doc/issue/CI 커넥터는 stub 상태다
- openai-agents 연동부는 구조 중심으로 잡혀 있으며, 배포 전 실제 계정/모델/권한 정책에 맞게 보강이 필요하다

## 다음 작업 우선순위

1. repo search tool 구현
2. run store와 trace store 연결
3. orchestrator + specialist agent 실제 연동
4. review 단계와 approval workflow 추가
5. IDE extension 또는 internal web UI 연결
