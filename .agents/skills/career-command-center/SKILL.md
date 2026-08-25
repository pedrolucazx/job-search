---
name: career-command-center
description: >
  Use for this repo's job-search workflow commands: daily, /daily,
  apply-batch, /apply-batch, compile-today, /compile-today, confirm,
  /confirm, interview-prep, /interview-prep. Thin adapter only; candidate
  data lives in profile/candidate.yaml, rules live in rules/, and executable
  workflows live in workflows/.
---

# Career Command Center

Use this skill for command-style job-search requests in this repository.
Short Codex aliases also exist: `$daily`, `$apply-batch`, `$compile-today`,
`$confirm`, and `$interview-prep`.

Before executing any workflow:

1. Read `AGENTS.md`.
2. Run `python3 scripts/validate_profile.py`; if it fails, stop and ask for
   the profile fix.
3. Read the matching workflow:
   - daily or `/daily`: `workflows/daily.md`
   - apply-batch or `/apply-batch`: `workflows/apply-batch.md`
   - compile-today or `/compile-today`: `workflows/compile.md`
   - confirm or `/confirm`: `workflows/confirm.md`
   - interview-prep or `/interview-prep`: `workflows/interview-prep.md`
4. Execute that workflow using `profile/candidate.yaml` and the referenced
   rules.

Never submit a job application, fill out an application form, or act past the
manual handoff described in the workflow.
