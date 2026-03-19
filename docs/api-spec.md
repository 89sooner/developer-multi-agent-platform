# API 스펙 초안

## 1. 개요

본 API는 사내 개발자용 멀티 에이전트 워크플로를 호출하기 위한 HTTP 인터페이스다. MVP에서는 분석과 리뷰 중심으로 제공한다.

기본 규칙:
- 모든 응답은 `run_id`를 포함한다
- 상태 조회는 `GET /v1/workflows/{run_id}`로 수행한다
- 동기 실행이 길어지는 경우 추후 `202 Accepted` 비동기 처리로 확장한다
- 모든 요청은 인증이 필요하다

## 2. 공통 헤더

- `Authorization: Bearer <token>`
- `Content-Type: application/json`
- `X-Request-Id: optional`
- `X-User-Language: optional, default=ko`

## 3. 공통 응답 형태

```json
{
  "run_id": "run_01",
  "status": "completed",
  "trace_id": "trace_01",
  "request_type": "feature",
  "confidence": "medium"
}
```

## 4. 엔드포인트

### 4.1 POST /v1/workflows/plan

용도:
- feature / bugfix / refactor 요청에 대한 영향 범위 및 구현 계획 생성

요청 필드:
- request_type
- repo_id
- branch
- task_text
- artifacts
- options

응답 필드:
- summary
- impacted_areas
- implementation_plan
- tests
- risks
- open_questions
- evidence
- confidence

### 4.2 POST /v1/workflows/review

용도:
- PR 초안 또는 변경안에 대한 사전 리뷰

추가 요청 필드:
- pr_url
- diff_text
- changed_files

응답 필드:
- summary
- review_findings
- missing_tests
- risks
- readiness_verdict
- evidence

### 4.3 POST /v1/workflows/test-plan

용도:
- 구현 계획 기반 테스트 전략 생성

추가 요청 필드:
- implementation_plan
- impacted_areas

응답 필드:
- unit_tests
- integration_tests
- regression_targets
- edge_cases
- execution_order

### 4.4 GET /v1/workflows/{run_id}

용도:
- 실행 상태 및 최종 결과 조회

응답 필드:
- run_id
- status
- request
- result
- created_at
- completed_at
- trace_id

### 4.5 GET /v1/workflows/{run_id}/trace

용도:
- trace 요약 조회

응답 필드:
- trace_id
- spans
- step_summaries
- tool_calls
- error_summary

### 4.6 POST /v1/feedback

용도:
- 결과에 대한 사용자 피드백 저장

요청 필드:
- run_id
- rating
- useful
- comment

응답 필드:
- feedback_id
- stored

## 5. 요청 예시

### 5.1 plan 요청

```json
{
  "request_type": "feature",
  "repo_id": "user-service",
  "branch": "feature/timezone-profile",
  "task_text": "사용자 프로필 수정 API에 timezone 필드를 추가하려고 해. 영향 범위와 구현 계획을 정리해줘.",
  "artifacts": {
    "issue_ids": ["DEV-123"],
    "pr_url": null
  },
  "options": {
    "include_tests": true,
    "language": "ko"
  }
}
```

### 5.2 plan 응답

```json
{
  "run_id": "run_01",
  "status": "completed",
  "trace_id": "trace_01",
  "request_type": "feature",
  "summary": "프로필 저장 경로, 검증 로직, 응답 스키마에 영향이 있다.",
  "impacted_areas": [
    "profile controller",
    "profile service",
    "request/response schema"
  ],
  "implementation_plan": [
    "DTO에 timezone 필드 추가",
    "유효한 timezone 검증 추가",
    "저장 로직 반영",
    "응답 스키마와 문서 수정"
  ],
  "tests": [
    "유효 timezone 저장 성공",
    "잘못된 timezone 저장 실패",
    "기존 API 호환성 유지"
  ],
  "risks": [
    "기존 클라이언트와의 역호환성",
    "기본 timezone 정책 누락"
  ],
  "open_questions": [
    "기본값 정책을 서버가 강제할지 여부"
  ],
  "evidence": [
    {
      "source_type": "repo",
      "locator": "src/profile/service.ts",
      "confidence": "high"
    }
  ],
  "confidence": "medium"
}
```

## 6. 에러 코드 초안

- `400_BAD_REQUEST`
- `401_UNAUTHORIZED`
- `403_SCOPE_VIOLATION`
- `404_RUN_NOT_FOUND`
- `408_CONNECTOR_TIMEOUT`
- `409_APPROVAL_REQUIRED`
- `422_SCHEMA_VALIDATION_FAILED`
- `429_RATE_LIMITED`
- `500_INTERNAL_ERROR`
- `503_MODEL_UNAVAILABLE`

## 7. 버전 전략

- base path는 `/v1`
- breaking change가 발생하면 `/v2`
- schema field 추가는 backward compatible로 본다

## 8. 인증/권한 정책

- 사용자 권한 범위 밖의 repo/doc/issue 접근 금지
- write action은 approval token이 있어야 한다
- 관리자 권한 우회는 금지한다
