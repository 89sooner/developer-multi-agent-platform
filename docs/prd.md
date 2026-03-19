# PRD: 사내 개발자용 개발단계 멀티 에이전트 서비스

## 0. 문서 정보

- 문서 상태: draft v0.1
- 작성일: 2026-03-19
- 대상 독자: Product, DevEx, Platform, AI Infra, Security
- 문서 목적: MVP 범위, 역할 분리, API/백엔드 구조, 운영 기준을 정의한다

## 1. 제품 요약

본 서비스는 사내 개발자가 기능 개발, 버그 수정, 리팩터링, PR 준비 단계에서 자연어로 요청하면, 코드와 문서 맥락을 수집하고 변경 계획, 테스트 포인트, 리뷰 의견까지 순차적으로 생성하는 내부 개발 지원 서비스다.

기본 설계는 역할별 Skill과 중앙 오케스트레이터 기반의 멀티 에이전트 구조다. 실행 흐름은 manager pattern을 기준으로 하며, 중앙 오케스트레이터가 전체 대화를 소유하고 specialist agent를 도구처럼 호출한다.

## 2. 배경 및 문제 정의

현재 개발 단계에서 반복적으로 발생하는 비효율은 아래와 같다.

- 요구사항을 개발 가능한 작업으로 해석하는 데 시간이 많이 든다
- 변경 영향 범위를 찾기 위해 여러 저장소, 문서, 이슈를 오가야 한다
- 구현 전 테스트 포인트와 리스크를 빠뜨리기 쉽다
- PR 초안이나 구현 계획이 사람마다 품질 편차가 크다
- 개발자, 리뷰어, QA가 같은 정보를 서로 다른 형식으로 재정리한다

이 서비스는 위 문제를 요청 분해, 근거 수집, 구현 계획, 테스트 계획, 리뷰의 표준 워크플로로 해결한다.

## 3. 목표

### 3.1 제품 목표

- 개발자가 변경 영향 범위를 파악하는 시간을 줄인다
- 구현 계획 초안 작성 시간을 줄인다
- 테스트 누락과 리뷰 누락을 줄인다
- 근거 기반의 일관된 개발 산출물을 만든다
- 사내 개발 표준과 아키텍처 규칙을 Skill로 재사용 가능하게 만든다

### 3.2 성공 상태

- 개발자는 하나의 입력만으로 영향 범위, 구현 순서, 테스트 체크리스트, 주요 리스크를 한 번에 받는다
- 결과물에는 항상 근거와 불확실성이 함께 표시된다
- 동일한 유형의 요청에 대해 팀 간 산출물 형식이 크게 흔들리지 않는다

## 4. 비목표

MVP 범위에서 아래 항목은 제외한다.

- 코드 자동 커밋
- 자동 머지
- 운영 환경 직접 변경
- 운영 데이터베이스 직접 실행
- 승인 없는 PR 생성 또는 댓글 작성
- 전 저장소를 대상으로 한 완전 자율 리팩터링

## 5. 제품 원칙

### 5.1 중앙 오케스트레이션 우선

MVP에서는 handoff가 아니라 manager pattern을 사용한다. 개발 단계 서비스는 최종 응답 형식과 정책을 중앙에서 강제해야 하므로 manager가 기본 선택이다.

### 5.2 Skill은 역할 단위로 분리

역할별 Skill을 따로 둔다. Skill은 각 전문 에이전트의 작업 표준을 담당하고, 실행 흐름은 오케스트레이터가 담당한다.

### 5.3 모든 단계는 구조화된 출력으로 연결

각 서브에이전트는 자유 텍스트가 아니라 스키마 검증 가능한 JSON을 반환한다.

### 5.4 근거 없는 단정 금지

- 파일명, 모듈명, 영향 범위를 추정으로만 단정하지 않는다
- 검색 근거가 약하면 confidence를 낮춰 반환한다
- 불확실한 항목은 open_questions에 남긴다

### 5.5 사람 승인 우선

- 계획 제안과 실제 변경 수행은 분리한다
- 외부 시스템에 쓰기 작업이 필요한 경우 반드시 승인 단계를 둔다

## 6. 대상 사용자

### 6.1 1차 사용자

- 백엔드 개발자
- 프론트엔드 개발자
- 플랫폼 엔지니어
- QA/SDET
- 기술 리드

### 6.2 핵심 사용 상황

- 새 기능 구현 전 영향 범위 분석
- 버그 수정 전 관련 코드/문서 탐색
- 리팩터링 전 변경 계획 수립
- PR 제출 전 사전 리뷰
- 테스트 시나리오 초안 작성

## 7. 범위

### 7.1 MVP 포함 범위

- 기능 요청을 개발 작업으로 정리
- 관련 코드/문서/이슈 탐색
- 구현 계획 초안 생성
- 테스트 체크리스트 생성
- PR 사전 리뷰 의견 생성
- 근거, 리스크, 오픈 이슈를 포함한 최종 응답 생성

### 7.2 차기 범위

- 코드 패치 초안 생성
- PR 설명문 자동 생성
- CI 실패 로그 원인 분석
- 보안 점검 전용 specialist agent
- 아키텍처 변경 영향 시뮬레이션

## 8. 에이전트 구성

- Workflow Orchestrator
- Requirements Agent
- Repo Context Agent
- Implementation Agent
- Test Strategy Agent
- Review Agent
- Summary Composer

MVP는 아래 4개로 시작한다.

- Workflow Orchestrator
- Repo Context Agent
- Implementation Agent
- Review Agent

## 9. Skill 목록

- workflow-orchestrator
- repo-context-finder
- implementation-planner
- review-gate
- requirements-planner
- test-strategy-generator

## 10. API 및 백엔드 구조

핵심 컴포넌트는 아래와 같다.

- API Gateway
- Workflow Service
- Agent Runtime
- Tool / MCP Proxy
- Skill Registry
- Run Store
- Trace Store
- Feedback Store

주요 엔드포인트는 아래와 같다.

- `POST /v1/workflows/plan`
- `POST /v1/workflows/review`
- `POST /v1/workflows/test-plan`
- `GET /v1/workflows/{run_id}`
- `GET /v1/workflows/{run_id}/trace`
- `POST /v1/feedback`

## 11. MVP 시나리오

### 11.1 새 기능 영향 범위 분석

입력:
- “사용자 프로필 수정 API에 timezone 필드를 추가하려고 한다. 영향 범위와 구현 계획을 정리해줘.”

기대 결과:
- 영향 범위
- 구현 단계
- 테스트 포인트
- 호환성 리스크

### 11.2 버그 수정 계획

입력:
- “특정 조건에서 주문 생성이 중복된다. 어디를 먼저 봐야 하는지와 수정 계획을 정리해줘.”

기대 결과:
- 재현 포인트
- 수정 후보
- 동시성/중복 처리 리스크

### 11.3 PR 사전 리뷰

입력:
- “이 PR 초안의 리스크와 누락 테스트를 확인해줘.”

기대 결과:
- 리스크 목록
- 누락 테스트
- 근거 기반 리뷰 의견

### 11.4 리팩터링 전 검토

입력:
- “이 서비스 레이어를 분리하려고 한다. 변경 전 확인할 의존성과 위험을 정리해줘.”

기대 결과:
- 의존성 목록
- 단계별 실행 순서
- 롤백 고려사항

## 12. 기능 요구사항

- 요청 분류
- 컨텍스트 수집
- 구현 계획 생성
- 테스트 계획 생성
- 리뷰 생성
- 최종 응답 형식 고정

최종 응답 필드:

- summary
- impacted_areas
- implementation_plan
- tests
- risks
- open_questions
- evidence
- confidence

## 13. 비기능 요구사항

- 일반 질의: 첫 응답 5초 이내 시작
- 중간 규모 분석: 30초 이내 완료 목표
- 단계별 실패 원인 추적 가능
- 권한 범위 밖의 repo/doc 접근 금지
- run_id 단위 감사 가능

## 14. 운영 원칙

- 외부 시스템 접근은 tool 또는 MCP proxy를 통해서만 수행
- run마다 trace_id, user_id, repo_scope 저장
- skill_version과 model_version을 결과에 기록
- reviewer 단계는 항상 마지막에 수행
- confidence가 low인 경우 사용자에게 불확실성 명시

## 15. 성공 지표

- 주간 활성 사용자 수
- 사용자 1인당 주간 실행 수
- evidence 포함 응답 비율
- human accept 비율
- 평균 응답 시간
- tool 실패율

## 16. 오픈 이슈

- 사내 Git 저장소와 코드 검색은 어떤 시스템을 기준으로 할 것인가
- 문서 소스는 위키, 노션, 드라이브 중 무엇이 1차 대상인가
- 이슈 시스템은 Jira인지 GitHub Issues인지
- CI 결과와 테스트 로그는 어떤 API로 연결할 것인가
- repo 권한 상속은 어떤 identity provider를 기준으로 할 것인가
