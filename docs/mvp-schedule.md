# MVP 개발 일정안

## 1. 가정

- 팀 구성: 1 PM, 1 Tech Lead, 2 Backend, 1 Frontend or Internal UI, 1 QA/SDET
- 개발 기간: 6주
- 목표: 영향 범위 분석, 구현 계획 생성, PR 사전 리뷰까지 제공하는 내부 MVP 출시

## 2. 마일스톤 요약

| 주차 | 목표 | 주요 산출물 |
|---|---|---|
| 1주차 | 요구사항 확정, 계약 정의 | PRD 확정, API 계약, 디렉터리 구조 |
| 2주차 | API/런타임 골격 | FastAPI skeleton, contracts, run store stub |
| 3주차 | repo-context + implementation | tool stubs, context agent, implementation agent |
| 4주차 | review + trace | review agent, trace/logging, partial failure handling |
| 5주차 | E2E 통합 | end-to-end demo, quality checks, sample prompts |
| 6주차 | 내부 시범 운영 | pilot rollout, feedback loop, backlog 정리 |

## 3. 주차별 상세

### 1주차

목표:
- 문제 정의 고정
- 핵심 workflow와 output schema 확정
- repo/doc/issue/CI 대상 시스템 결정

작업:
- PRD 승인
- system architecture 확정
- OpenAPI 초안 작성
- agent output schema 정의
- security review 시작

완료 기준:
- 문서 승인 완료
- MVP 범위 고정
- 우선 연결 시스템 목록 확정

### 2주차

목표:
- 실행 가능한 API skeleton 구축

작업:
- FastAPI app bootstrap
- `/v1/workflows/plan`, `/review`, `/test-plan` route 생성
- contracts / validators 생성
- run store in-memory 구현
- trace correlation ID 적용

완료 기준:
- local environment 실행 가능
- request/response validation 동작
- health check 및 smoke test 통과

### 3주차

목표:
- repo-context와 implementation 흐름 연결

작업:
- repo/docs/issue connector stub 구현
- Repo Context Agent prompt 적용
- Implementation Agent prompt 적용
- evidence 표준 객체 구현
- 결과 병합 로직 초안 완성

완료 기준:
- feature/bugfix/refactor plan 요청에 대한 stubbed E2E 동작
- evidence와 confidence 반환

### 4주차

목표:
- 리뷰와 관측 체계 추가

작업:
- Review Agent 적용
- low confidence 정책 반영
- error handling / degraded mode 구현
- trace export 설계
- feedback endpoint 추가

완료 기준:
- review workflow 동작
- step-level logging 확인 가능
- 실패 시 부분 결과 반환

### 5주차

목표:
- 품질 향상과 시나리오 검증

작업:
- test-plan endpoint 보강
- sample repo 시나리오 테스트
- prompt/skill revisions
- security / compatibility checklist 반영
- UI 또는 CLI demo 경로 준비

완료 기준:
- 대표 시나리오 3개 이상 성공
- human review로 치명적 오류 없음

### 6주차

목표:
- 내부 파일럿과 개선 backlog 정리

작업:
- limited pilot rollout
- 사용자 피드백 수집
- model / prompt tuning
- backlog prioritization
- GA 전 확장안 정리

완료 기준:
- 파일럿 사용자 확보
- 상위 개선 과제 목록화
- post-MVP roadmap 작성

## 4. 인력 배치 제안

### PM
- PRD, rollout, feedback loop

### Tech Lead
- architecture, prompt/skill review, quality gate

### Backend 1
- API, run store, contracts

### Backend 2
- agent runtime, tool layer, integrations

### Frontend/Internal UI
- internal web UI 또는 IDE extension prototype

### QA/SDET
- scenario tests, regression test set, acceptance criteria 검증

## 5. 주요 리스크와 대응

### 연결 시스템 불확실성
대응:
- 1주차에 대상 시스템 확정
- stub interface를 먼저 고정

### prompt 불안정성
대응:
- 구조화된 output 강제
- review agent를 필수 단계로 적용

### connector latency
대응:
- timeout 정책
- partial result 허용
- sync/async 분리 설계

### 권한 이슈
대응:
- 최소 권한
- scope enforcement
- write action 비활성 기본값

## 6. 출시 기준

- plan workflow 성공률 90% 이상
- 대표 시나리오 3개 이상 내부 승인
- low confidence 표시 누락 없음
- feedback 저장 가능
- trace와 run 조회 가능
