# 🎯 Job Search — Multi-Agent Job Application System

<p align="center">
  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python">
  <img src="https://img.shields.io/badge/Bun-%23000000.svg?style=for-the-badge&logo=bun&logoColor=white" alt="Bun">
  <img src="https://img.shields.io/badge/bash_script-%23121011.svg?style=for-the-badge&logo=gnu-bash&logoColor=white" alt="Bash">
  <img src="https://img.shields.io/badge/latex-%23008080.svg?style=for-the-badge&logo=latex&logoColor=white" alt="LaTeX">
  <img src="https://img.shields.io/github/license/pedrolucazx/job-search?style=for-the-badge" alt="MIT license">
</p>

<p align="center"><em>A job search framework that runs on your own machine, with any coding agent.</em></p>

Searches for jobs, evaluates fit, generates a LaTeX CV (1-page A4, ATS-safe),
and tracks applications — all driven by **your** profile in YAML. No
candidate data lives in the engine: swap the profile and the same pipeline
works for any track (backend, frontend, mobile, IoT, data...) and any coding
agent with file + shell access (Claude Code, Codex, OpenCode, Cursor, Cline,
or even a plain chat without tool-use for the manual path).

> This repo is a working instance for one person's job search. The generic
> engine (`AGENTS.md`, `rules/`, `workflows/`, `profile/`) is in English so
> any dev can reuse it. The day-to-day command files (`CLAUDE.md`,
> `.claude/commands/`, `.opencode/commands/`) stay in Portuguese — that's
> the maintainer's own daily-use language, and it doesn't affect how the
> pipeline works for you.

## How it works

```
 /daily              /apply-batch <n>        /compile-today          /confirm <n>
    │                      │                       │                      │
    ▼                      ▼                       ▼                      ▼
 Search jobs          Generate LaTeX CV      Compile → PDF          Register in
 (LinkedIn+freehire)  for chosen job         ATS check, archive     tracker (Notion/
 Rank by fit          (gate: deal-breaker                            CSV/none)
                       + score ≥60%)
```

Every step reads `profile/candidate.yaml` (your data) + `rules/` (universal
CV/fit/ATS rules) — nothing hardcoded in the engine. See [AGENTS.md](AGENTS.md)
for the full architecture.

## Prerequisites

- A coding agent with file + shell access (Claude Code, Codex, OpenCode...)
- Python 3 + PyYAML — check with `python3 -c "import yaml"`
- [Bun](https://bun.sh) — for the job search CLIs
- LaTeX (`pdflatex`) + `pdftotext` (poppler-utils) — to compile and ATS-check

Detailed install steps: [SETUP.md](SETUP.md).

## Getting started

```bash
# 1. Your profile (never invent data — leave blank what you don't know)
cp profile/candidate.example.yaml profile/candidate.yaml
# fill in profile/candidate.yaml with your real data
python3 scripts/validate_profile.py

# 2. Job search CLIs
cd .agents/skills/linkedin-search/cli && bun install && cd ../../../..
cd .agents/skills/freehire-search/cli && bun install && cd ../../../..
```

Then, inside your coding agent:

```
/daily              → search jobs, rank by fit score
/apply-batch 1,2,3  → generate CVs for the jobs you picked
/compile-today      → compile, run ATS check, archive
/confirm 1,2,3      → register the sent application in the tracker
```

## Commands

| Command | What it does |
|---|---|
| `/daily` | Scrape LinkedIn + freehire, deduplicate, rank by fit score |
| `/apply-batch <indices\|url>` | Generate a `.tex` CV for chosen jobs — blocks on deal-breaker or score < 60% before spending effort |
| `/compile-today` | Compile `.tex` → PDF, run ATS check, archive — **never touches the tracker** |
| `/confirm <indices>` | Only command that registers "Applied" in the tracker |

## Architecture

| Folder | Content |
|---|---|
| `profile/` | Your data (`candidate.yaml`, gitignored) — start from `candidate.example.yaml` |
| `rules/` | Universal rules: CV, fit score, ATS, interview — no one's personal data |
| `workflows/` | Operational steps for each command above |
| `templates/` | Generic LaTeX template (placeholders resolved from the profile) |
| `scripts/` | Profile validation, batch compilation, CSV tracker |
| `.agents/skills/` | Job search CLIs (LinkedIn, freehire) |

Full detail, including why each folder exists: [AGENTS.md](AGENTS.md).

## Tests

```bash
python3 -m unittest discover -s tests
```

Covers `scripts/validate_profile.py` and `scripts/track_append.py` (stdlib
`unittest`, zero extra dependency), plus a guard that
`profile/candidate.example.yaml` always passes validation.

## Troubleshooting

| Symptom | Where to look |
|---|---|
| `/daily` finds no jobs | LinkedIn may have blocked scraping — try freehire only, or paste the URL directly into `/apply-batch` |
| CV came out longer than 1 page | `/compile-today` already blocks this on its own (won't register, won't archive, shows up in the report) — trim content following `rules/cv-rules.md` and rerun `/compile-today` |
| `/compile-today` failed to compile | The pdflatex log shows up in the report — usually an unescaped special character |
| A job showed up before | `/daily` filters against the tracker **and** local files (`documents/applications/`, `daily/*/*.json`) to catch an in-progress application that hasn't been confirmed yet |
| Forgot to run `/confirm` | No problem — the CV is already compiled and archived locally, the tracker just stays out of date until you run `/confirm <number>`; doesn't have to be the same day |

## Other documents

- [AGENTS.md](AGENTS.md) — full architecture, agent/LLM-agnostic
- [SETUP.md](SETUP.md) — installing dependencies
- [OPENCODE.md](OPENCODE.md) — OpenCode's free models and which to use for each task
- [documents/README.md](documents/README.md) — how the applications folder is organized (local, gitignored)

## Credits

The job search CLIs (`.agents/skills/linkedin-search/`, `.agents/skills/freehire-search/`)
were adapted from parts of [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) (not a fork).
