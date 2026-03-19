---
name: implementation-planner
description: turn grounded repository context into a concrete implementation plan. use when a request asks for impacted modules, change order, api changes, migrations, rollback notes, or implementation risks.
---

Build an implementation plan from grounded evidence.

Return:
- change_plan
- target_modules
- api_changes
- data_model_changes
- migration_needs
- rollback_notes
- risks
- confidence

Do not write production code in this skill.
Mark assumptions explicitly.
Include rollback notes when changes affect persistence, public APIs, or asynchronous workflows.
