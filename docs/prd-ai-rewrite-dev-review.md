# `prd-ai-rewrite-v1.md` 개발 명확성 검토

작성일: 2026-03-22  
검토 대상: `docs/prd-ai-rewrite-v1.md`

## 1. 총평

`docs/prd-ai-rewrite-v1.md` 는 제품 방향, 원칙, 핵심 기능, 기술 방향을 설명하는 상위 PRD 로서는 충분히 좋다. 특히 evidence-first, manager pattern, structured output, approval-first 같은 핵심 원칙은 명확하고 일관적이다.

반면 개발 착수용 문서로 바로 넘기기에는 아직 부족하다. 가장 큰 문제는 "무엇을 언제 어떤 순서로 어느 수준까지 만들 것인가"가 명시적으로 고정되어 있지 않다는 점이다. 기능 요구사항은 있지만, 구현 phase, story 단위 범위, 테스트 가능한 acceptance criteria, release gate 가 없다.

판정:

- 전략 PRD 로서: 적합
- 구현 착수용 PRD 로서: 보완 필요
- 바로 개발 가능한 수준: 부분적

## 2. 강점

- 제품 문제와 목표가 명확하다.
- MVP 와 차기 범위를 구분했다.
- 에이전트 구조와 보안 원칙이 비교적 명확하다.
- API 와 데이터 개념이 크게 흔들리지 않는다.
- 성공 지표와 리스크 항목이 포함되어 있다.

## 3. 개발 관점의 주요 부족점

### 3.1 MVP 릴리스 단위가 모호함

현재 문서는 MVP 범위를 정의하지만, 실제로 어떤 기능 묶음을 "첫 출시"로 볼지 확정하지 않는다.

예:

- API 만으로 출시하는지
- API + 최소 내부 UI 를 같이 내는지
- sync-only 로 내는지
- async 상태 조회까지 MVP 에 넣는지

개발팀 입장에서는 이 결정이 없으면 구현 우선순위와 시스템 구조가 흔들린다.

### 3.2 phase 와 의존 관계가 제품 요구사항 수준으로 고정되지 않음

문서 말미에 `Phase 1/2/3` 가 있지만, 이것이 제품 요구사항인지 단순 제안인지 경계가 약하다. 또한 phase 별 진입 조건과 종료 기준이 없다.

필요한 보완:

- phase 목표
- in scope / out of scope
- 선행 의존성
- phase exit criteria

### 3.3 user story 수준으로 분해되지 않음

현재 기능 요구사항은 FR 단위다. 개발 백로그로 직접 전환하려면 사용자 관점 story 로 다시 쪼개야 한다.

예:

- "개발자는 자연어 요청으로 plan 을 받고 싶다"
- "리뷰어는 diff 기반 readiness verdict 를 받고 싶다"
- "운영자는 connector 실패를 모니터링하고 싶다"

현재 문서는 이 수준까지는 내려오지 않는다.

### 3.4 acceptance criteria 가 테스트 가능 수준으로 충분히 구체적이지 않음

현재 수용 기준은 방향성은 맞지만, 구현 검증 기준으로 쓰기엔 추상적이다.

예:

- "docs/wiki connector 지원"은 어떤 인증 방식과 실패 동작까지 포함하는지 불명확하다.
- "structured output 지원 모델"은 schema validation 실패 시 retry 횟수나 fallback 조건이 없다.
- "low-confidence 응답 비율 20% 이하"는 어떤 데이터셋 기준인지 없다.

### 3.5 사용자 표면과 운영 모드가 확정되지 않음

`API 우선 제공, 최소 1개 사용자 표면 제공`은 너무 넓다. 개발 PRD 에서는 아래 중 하나로 고정해야 한다.

- MVP 의 primary surface 는 REST API
- UI/IDE 는 차기
- 또는 반대로 최소 web UI 가 MVP 필수

이 결정이 없으면 인증 흐름, 상태 조회, 피드백 UX 가 달라진다.

### 3.6 비동기 실행 상태 모델이 부족함

문서에 동기/비동기 실행이 모두 언급되지만, run 상태 모델과 전환 규칙이 구체적이지 않다.

필요한 보완:

- 언제 async 로 전환하는지
- 상태값 정의
- polling/events 방식
- cancel 가능 여부

### 3.7 connector 범위와 읽기/쓰기 경계가 구체적이지 않음

repo/docs/issue/CI 연동이 필요하다는 점은 명확하지만, MVP 에서 어떤 읽기 범위를 보장하는지와 어떤 쓰기 범위가 금지되는지 상세하지 않다.

필요한 보완:

- MVP 는 single-repo read-only 인지
- PR diff 는 URL 기반 조회인지 raw diff 업로드도 허용하는지
- CI 는 latest build 만 보는지, run history 도 필요한지

### 3.8 auth / RBAC / approval state machine 이 부족함

보안 원칙은 적절하지만 개발용 명세로는 아래가 더 필요하다.

- 지원 role 목록
- repo scope / doc scope / issue scope 적용 위치
- approval record 의 상태
- approval token 혹은 approval object 계약

### 3.9 운영 메트릭의 정의가 부족함

메트릭 항목은 제시됐지만 측정 기준이 없다.

예:

- citation coverage 계산 기준
- critical false citation 정의
- usefulness 점수 산정 방식

운영 대시보드와 평가 자동화를 만들려면 정의가 먼저 필요하다.

### 3.10 데이터 보존과 감사 정책이 빠져 있음

운영 제품 기준으로는 다음이 부족하다.

- run/trace/feedback retention
- 민감정보 저장 금지 범위
- trace export 보관 정책
- 관리자 조회 감사 로그

## 4. 개발을 위해 명시적으로 고정해야 하는 결정

Ralph용 PRD 에서는 아래를 명시적으로 고정하는 것이 맞다.

1. MVP primary surface 는 REST API 로 한정한다.
2. MVP 요청 단위는 single repo / single branch 로 제한한다.
3. Phase 1 은 read-only plan workflow 를 first usable release 로 정의한다.
4. Review, test-plan, async execution 은 Phase 2 로 분리한다.
5. 승인 기반 write action 은 post-MVP phase 로 분리한다.
6. 모든 성공 응답은 evidence 를 포함하거나 low-confidence + open questions 를 강제한다.
7. 비동기 상태 모델과 phase exit criteria 를 제품 요구사항으로 고정한다.

## 5. 검토 결과 반영 방향

위 부족점을 보완한 Ralph용 PRD 는 다음 구조를 가져야 한다.

- phase 별 목표/범위/제외 범위
- epic 및 user story
- story 별 acceptance criteria
- phase exit criteria
- 명시적 제품 결정과 운영 제약
- API/보안/관측/평가에 대한 구현 가능한 기준

## 6. 최종 판단

현재 `prd-ai-rewrite-v1.md` 는 버릴 문서가 아니다. 오히려 상위 전략 PRD 로는 충분히 쓸 만하다. 다만 개발팀이나 구현 에이전트가 바로 실행에 옮기려면, 제품 결정을 더 좁히고 phase 와 story 를 고정한 하위 PRD 가 반드시 하나 더 필요하다.

그 하위 문서가 `Ralph용 PRD` 다.
