# 🎯 Job Search — Job-Hunt Workspace

This repository is your job-hunt command center.
Claude Code (Opus) generates CVs with surgical precision; OpenCode handles compilation, ATS checks, and tracker registration.

Full architecture (agent/LLM-agnostic): see `AGENTS.md`.

## Absolute Rules
1. NEVER invent data, metrics, projects, or technologies outside `profile/candidate.yaml`
2. Education and Languages sections are LOCKED — copy exactly as they are
3. The CV must be EXACTLY 1 A4 page
4. Gap analysis always with a full/partial/absent table
5. Soft skills always bilingual "Português (English)", per `profile/candidate.yaml`
6. NEVER use two columns, tables, charts, icons, or images in the LaTeX

(Full, annotated list in `rules/README.md`.)

## Available Commands
| Command | What it does | Runs on |
|---|---|---|
| `/daily` | Scrapes LinkedIn + freehire, ranks jobs, presents a table | Claude Code |
| `/apply-batch 1,2,3,8` | Generates .tex CVs for N selected jobs (index or pasted URL) | Claude Code |
| `/compile-today` | Compiles .tex → .pdf → ATS check → archives (doesn't touch the tracker) | OpenCode |
| `/confirm 1,2,3` | Only command that registers "Applied" in the configured tracker (see `profile/candidate.yaml → tracker`) | Claude Code |
| `/interview-prep <company>` | Generates a presentation script + critical fit analysis for an already-confirmed job (doesn't cover the technical round) | Claude Code / OpenCode |

## Where the rules and data live (read before running commands)
- `profile/candidate.yaml` — the active candidate's canonical data (gitignored; copy from `profile/candidate.example.yaml`)
- `rules/` — universal rules for CV, fit evaluation, ATS, interview
- `workflows/` — operational steps for each command above

## Output Format (Claude Code → OpenCode bridge)
Claude Code generates:
- `documents/cv/main_<company>_<role>.tex` — CV in LaTeX (role in the name avoids overwriting when there's more than one job at the same company)
- `daily/<date>/<company>_<role>.json` — Application metadata

OpenCode reads and processes it.
