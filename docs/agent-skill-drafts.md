# agent별 prompt / skill 초안

## 1. 설계 원칙

- runtime prompt와 skill은 분리한다
- prompt는 agent 실행용 지시문이다
- skill은 재사용 가능한 작업 표준과 참조 자료를 묶는다
- prompt는 서비스 런타임에 사용하고, skill은 ChatGPT/Codex/운영 도구에 재사용한다
- 출력은 항상 구조화된 계약을 따른다

## 2. agent 목록

- Workflow Orchestrator
- Repo Context Agent
- Implementation Agent
- Review Agent
- Requirements Agent
- Test Strategy Agent

## 3. 파일 위치

### Prompt 파일

- `prompts/orchestrator.md`
- `prompts/repo_context.md`
- `prompts/implementation.md`
- `prompts/review.md`
- `prompts/requirements.md`
- `prompts/test_strategy.md`

### Skill 파일

- `skills/workflow-orchestrator/`
- `skills/repo-context-finder/`
- `skills/implementation-planner/`
- `skills/review-gate/`
- `skills/requirements-planner/`
- `skills/test-strategy-generator/`

## 4. agent별 역할과 출력 계약

### 4.1 Workflow Orchestrator

역할:
- 요청 분류
- specialist agent 호출 순서 결정
- 최종 응답 조립

필수 출력:
- request_type
- selected_agents
- execution_plan
- final_response

### 4.2 Repo Context Agent

역할:
- 관련 파일, 문서, 이슈, CI 맥락 수집
- 유사 구현과 의존성 요약

필수 출력:
- related_files
- relevant_docs
- similar_implementations
- dependency_summary
- uncertainty_list
- evidence

### 4.3 Implementation Agent

역할:
- 구체적인 변경 계획 작성

필수 출력:
- change_plan
- target_modules
- api_changes
- data_model_changes
- migration_needs
- rollback_notes
- risks

### 4.4 Review Agent

역할:
- 누락과 리스크 검토

필수 출력:
- missing_evidence
- hidden_dependencies
- regression_risks
- security_flags
- performance_flags
- compatibility_flags
- readiness_verdict

### 4.5 Requirements Agent

역할:
- 자연어 요구를 개발 가능한 작업으로 변환

필수 출력:
- feature_summary
- assumptions
- acceptance_criteria
- non_goals
- impacted_areas

### 4.6 Test Strategy Agent

역할:
- 테스트 전략 생성

필수 출력:
- unit_tests
- integration_tests
- regression_targets
- edge_cases
- execution_order

## 5. Prompt 작성 규칙

- 근거 없는 추정 금지
- evidence가 약하면 confidence를 낮춘다
- 불확실한 사항은 open_questions에 남긴다
- 응답 언어는 사용자 언어를 따른다
- JSON 외 자유 텍스트를 반환하지 않는다

## 6. Skill 작성 규칙

- frontmatter의 name, description은 lowercase 유지
- description에는 언제 사용해야 하는지 포함
- body에는 절차와 금지 규칙, 참조 리소스를 적는다
- scripts, references, assets는 필요한 경우만 둔다

## 7. 개선 포인트

- skill 버전 분리
- 팀별 architecture references 분리
- repo별 coding patterns 별도 문서화
- review checklist와 security baseline 강화
