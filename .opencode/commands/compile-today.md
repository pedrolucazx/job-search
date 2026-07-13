---
description: Compiles today's CVs, runs the ATS check, and archives (doesn't touch the tracker)
agent: build
model: opencode/north-mini-code-free
---

Read `workflows/compile.md` and execute the steps described there for the
date in `$ARGUMENTS` (or today, if omitted). The ATS check's email/phone
come from `profile/candidate.yaml` via `scripts/validate_profile.py` — never
hardcoded.
