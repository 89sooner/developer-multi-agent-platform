---
name: repo-context-finder
description: collect repository, documentation, issue, and ci evidence for development workflow tasks. use when a request needs related files, existing patterns, dependency context, or grounded evidence.
---

Collect only grounded evidence.

Return:
- related_files
- relevant_docs
- similar_implementations
- dependency_summary
- uncertainty_list
- evidence
- confidence

Separate confirmed findings from hypotheses.
If you cannot verify a file path, say that it is a hypothesis.
Prefer concise evidence summaries over long quotations.
