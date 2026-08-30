---
paths: []          # omit `paths` entirely to load unconditionally every session
---

# SDD Workflow Rules

- Never modify files in src/ or frontend/src/ while in Requirements or Design phase.
- Each phase file (requirements.md, design.md, tasks.md) must be explicitly
  approved by the user before the next phase command may run.
- tasks.md must reference specific files/functions from design.md — no vague tasks.
- If requirements.md doesn't exist yet, spec-design and spec-tasks must refuse and
  point the user to /spec-requirements first.
