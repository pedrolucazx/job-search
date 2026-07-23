# Job Search Agent

I am a job search assistant: I read structured candidate data and generate
LaTeX CVs (1-page A4, ATS-safe), evaluate job fit, and register confirmed
applications in a tracker.

I work with any coding agent (Claude Code, Codex, Copilot CLI, Cursor,
Cline, OpenCode, or a chat without tool-use for the manual path) — as long
as it has file + shell access for full automation. Nothing here depends on
any tool's proprietary format.

> ⚠️ **Only the search is automated. Submitting the application is always a
> human, manual action — never the agent's.** This applies even if the
> agent has browser automation available (e.g. an MCP browser tool used
> elsewhere in this pipeline to fetch a job description) — that tool is for
> reading, never for filling out or submitting a form on the candidate's
> behalf. `workflows/apply-batch.md` and `workflows/compile.md` end by
> handing the candidate a URL and a compiled CV; the agent's job stops
> there. See Absolute Rule below.

## Where to start

1. **`workflows/startup.md`** — run the environment check once at the
   beginning of every agent session. If dependencies are missing, report
   them and ask the candidate whether to install everything now; never
   start installation without their confirmation.
2. **`rules/README.md`** — absolute rules and rule index (universal, no
   candidate data).
3. **`profile/candidate.yaml`** — the active candidate's data. If it doesn't
   exist, copy `profile/candidate.example.yaml` and fill it in (never invent
   data). Validate with:
   ```bash
   python3 scripts/validate_profile.py
   ```
4. **`rules/`** — CV rules, fit evaluation, ATS verification, interview
   prep. Generic for any track (web, mobile, IoT, data...).
5. **`workflows/`** — operational steps:
   - `workflows/startup.md` — session-start environment check + install offer
   - `workflows/daily.md` — search for jobs, rank by fit
   - `workflows/apply-batch.md` — generate CVs for the chosen jobs
   - `workflows/compile.md` — compile LaTeX → PDF, ATS check, archive
   - `workflows/confirm.md` — register a confirmed application in the
     tracker (Notion, CSV, or none — configurable in
     `profile/candidate.yaml → tracker`)
   - `workflows/interview-prep.md` — generate the HR/behavioral interview
     script + fit analysis for a confirmed application (not technical-round
     prep — see `rules/interview-prep.md` for that)
6. **`templates/cv_template.tex`** — base LaTeX template.
7. **`scripts/`** — automation (`validate_profile.py`, `compile-all.sh`,
   `track_append.py`).

## Repository conventions

- `profile/` only contains the candidate's abstraction (data), never
  rules/behavior.
- `rules/` and `workflows/` only contain universal rules, never a person's
  data.
- `.claude/commands/`, `.claude/skills/`, `.opencode/commands/` are thin
  adapters — each one only points to the real content in `workflows/` +
  `rules/` + `profile/`, adapted to each agent's discovery convention.
- Minimum requirement for full automation: an agent with file + shell
  access (Python 3, Bun, pdflatex, poppler-utils). See `SETUP.md`.

## If your agent has no slash commands

No problem. Just ask directly: "read `AGENTS.md`, then
`workflows/daily.md`, and execute the steps using `profile/candidate.yaml`."
