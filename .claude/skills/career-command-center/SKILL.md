---
name: career-command-center
version: 2.0.0
description: >
  Thin pointer into the generic job-hunt engine. Candidate data lives in
  profile/candidate.yaml, universal rules in rules/, workflows in
  workflows/. Use this skill on ALL application commands.
context: fork
allowed-tools:
  - Bash(bun run .agents/skills/linkedin-search/*)
  - Bash(bun run .agents/skills/freehire-search/*)
  - Bash(python3 scripts/*)
  - WebFetch
  - WebSearch
  - Read
  - Write
  - Edit
  - mcp__claude_ai_Notion__notion-search
  - mcp__claude_ai_Notion__notion-create-pages
  - mcp__claude_ai_Notion__notion-update-page
---

# Career Command Center

Central skill that orchestrates the job search. Contains no candidate data
or behavior rules — it's just the trigger for Claude Code to load:

1. `profile/candidate.yaml` — the active candidate's data
2. `rules/README.md` (and the rest of `rules/`) — universal rules
3. `workflows/` — operational steps for each command

See `AGENTS.md` at the repo root for the full architecture description.
