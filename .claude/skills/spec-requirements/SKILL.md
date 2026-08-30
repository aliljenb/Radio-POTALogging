---
name: spec-requirements
description: SDD - Generate requirements.md for a new feature or bugfix.md for a bug, following the project's SDD template.
argument-hint: [feature-name]
disable-model-invocation: true      # only run when the user explicitly types /spec-requirements
allowed-tools: Read Write Glob Grep # no Bash/Edit — this phase never touches code
---

If not already existing, generate `specs/$1/requirements.md` using the template at `skills/spec-requirements/template.md`

## Before writing or editing anything

If any part of the scope is unclear, ambiguous, or could reasonably be
interpreted more than one way — target users/roles, feature boundaries,
edge cases, priority/must-have vs nice-to-have, measurable thresholds for
acceptance criteria, etc. — stop and ask control questions before drafting
or changing requirements.md.

- Ask one question at a time, or a small batch of tightly related ones.
- Each question must offer 2-4 concrete, mutually exclusive multiple-choice
  options (plus the user can always answer "Other" with free text).
- Use the `AskUserQuestion` tool so the options are clickable. Only fall
  back to a lettered list (A/B/C/D) in chat if that tool isn't available.
- Do not proceed to writing or editing requirements.md until blocking
  ambiguities are resolved. Minor, non-blocking assumptions can just be
  stated inline in the requirement instead of asked about.

Read the file `specs/$1/requirements.md` and help me create or refine the project requirements.

Follow these guidelines:
- Use the format: "As a **[user type]**, I want to **[goal]**, so that **[benefit]**"
- Include acceptance criteria for each requirement
- Group requirements logically
- Ensure requirements are testable and measurable

Update `specs/$1/requirements.md` with the refined requirements.
