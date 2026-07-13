---
description: Compila os CVs do dia, roda ATS check e arquiva (sem tocar no tracker)
agent: build
model: opencode/north-mini-code-free
---

Leia `workflows/compile.md` e execute os passos descritos ali para a data em
`$ARGUMENTS` (ou hoje, se omitida). O email/telefone do ATS check vêm de
`profile/candidate.yaml` via `scripts/validate_profile.py` — não hardcoded.
