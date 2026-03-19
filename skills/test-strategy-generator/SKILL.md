---
name: test-strategy-generator
description: generate structured test strategies for a proposed implementation plan. use when a request needs unit tests, integration tests, regression targets, edge cases, or recommended test execution order.
---

Generate a practical test strategy for the plan.

Return:
- unit_tests
- integration_tests
- regression_targets
- edge_cases
- execution_order
- confidence

Separate test types clearly.
Include only tests that match the plan and risks.
