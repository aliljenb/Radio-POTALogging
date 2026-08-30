---
name: spec-new
description: SDD - Set up a new feature spec folder from the templates
argument-hint: [feature-name]
disable-model-invocation: true
allowed-tools: Bash(mkdir:*) Bash(cp:*) Read Write Edit
---
Scaffold a new spec for the feature: **$ARGUMENTS**

1. Validate that $ARGUMENTS is a single kebab-case name (lowercase letters,
   digits, and hyphens only, no spaces). If not, suggest a corrected name and stop.
2. If `specs/$ARGUMENTS/` already exists, report it and stop (do not overwrite).
3. Create `specs/$ARGUMENTS/` and copy the three templates into it:
   - `${CLAUDE_PROJECT_DIR}/.claude/skills/spec-requirements/template.md` → `specs/$ARGUMENTS/requirements.md`
   - `${CLAUDE_PROJECT_DIR}/.claude/skills/spec-design/template.md` → `specs/$ARGUMENTS/design.md`
   - `${CLAUDE_PROJECT_DIR}/.claude/skills/spec-tasks/template.md` → `specs/$ARGUMENTS/tasks.md`
4. Create an empty `specs/$ARGUMENTS/prompts.txt` file.
5. In each copied file, replace `[feature-name]` with $ARGUMENTS.
6. Confirm the folder is ready and tell the user the next step is
   `/spec-requirements $ARGUMENTS`.

Do NOT fill in any content yet — that is the next phase.