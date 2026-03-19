---
name: review-gate
description: review a proposed change plan or draft implementation summary for missing evidence, regressions, hidden dependencies, compatibility concerns, and readiness. use before returning a final developer recommendation.
---

Review the proposed output before it is returned to a developer.

Return:
- missing_evidence
- hidden_dependencies
- regression_risks
- security_flags
- performance_flags
- compatibility_flags
- readiness_verdict
- confidence

Reject unsupported claims.
Prioritize the most severe issues first.
If no critical issues are found, say so clearly.
