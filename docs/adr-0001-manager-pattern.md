# ADR 0001: manager pattern 채택

## 상태
accepted

## 결정
개발 단계 멀티 에이전트 MVP는 manager pattern을 사용한다.

## 이유
- 중앙에서 출력 형식과 정책을 통제하기 쉽다
- 권한, trace, approval workflow를 한 곳에서 관리할 수 있다
- specialist agent를 tool처럼 조합하기 쉽다

## 결과
- handoff는 MVP 기본값이 아니다
- orchestrator가 최종 응답 품질을 책임진다
- specialist agent는 구조화된 출력만 반환한다
