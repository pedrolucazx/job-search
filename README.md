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

## 5-minute checklist (new here? start here)

If you've never used this kind of agent-driven repo before, follow these in
order — nothing else to read first:

- [ ] Clone this repo (or use "Use this template" on GitHub)
- [ ] Run `python3 scripts/check_setup.py` — it tells you exactly what's
      missing (Bun, LaTeX, PyYAML...) and how to install each one. Rerun it
      until everything shows ✅.
- [ ] `cp profile/candidate.example.yaml profile/candidate.yaml`
- [ ] Open `profile/candidate.yaml` and replace every value with your own
      real data (name, email, skills, experience — see
      `profile/candidate.schema.yaml` if a field is unclear). Never leave
      the example's placeholder data in there — see the warning below,
      the pipeline will refuse to run if you do.
- [ ] Run `python3 scripts/validate_profile.py` — fix anything it flags
- [ ] Install the search CLIs (step 2 in "Getting started" below)
- [ ] Open your coding agent (Claude Code, Codex, OpenCode...) in this
      folder and type `/daily`

That's it — the agent takes it from there and tells you what to do next at
every step.

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
- LaTeX (`pdflatex`) + `pdftotext`/`pdfinfo` (poppler-utils) — to compile and ATS-check
- `jq` — reads fields out of the metadata JSON during compilation

Run `python3 scripts/check_setup.py` to check all of these at once — it
tells you exactly what's missing and how to install it. Detailed manual
install steps: [SETUP.md](SETUP.md).

## Getting started

```bash
# 0. Check your environment first — tells you exactly what's missing
python3 scripts/check_setup.py
```

```bash
# 1. Your profile (never invent data — leave blank what you don't know)
cp profile/candidate.example.yaml profile/candidate.yaml
# fill in profile/candidate.yaml with your real data — name, email, everything
python3 scripts/validate_profile.py
```

⚠️ **`validate_profile.py` will refuse to pass if you forgot to replace the
example's placeholder name/email/handles** — this is not a style suggestion,
it's a hard block. If you just copy the template and run the pipeline
without editing it, you'll get a clear error telling you exactly what's
still unedited, instead of silently generating a CV with someone else's
contact info.

```bash
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

Covers `scripts/validate_profile.py`, `scripts/track_append.py`, and
`scripts/check_setup.py` (stdlib `unittest`, zero extra dependency), plus a
guard that `profile/candidate.example.yaml` always passes validation.

## Troubleshooting

### Setup / environment

| Symptom | Where to look |
|---|---|
| Not sure what's wrong with your setup | Run `python3 scripts/check_setup.py` first — it checks everything at once and tells you exactly what's missing |
| `bash: bun: command not found` | Bun isn't installed — `curl -fsSL https://bun.sh/install \| bash`, then open a new terminal (or `source` your shell config) so it's on your PATH |
| `pdflatex: command not found` | LaTeX isn't installed — see [SETUP.md](SETUP.md); on Debian/Ubuntu you need `texlive-latex-extra` specifically, not just `texlive-latex-base` (the template uses `titlesec`, which isn't in the base set) |
| `ModuleNotFoundError: No module named 'yaml'` | PyYAML isn't installed — `pip install pyyaml` (or `pip3 install pyyaml` depending on your system) |
| `jq: command not found` | `sudo apt install jq` (or `brew install jq` on macOS) — used to read fields out of the metadata JSON during compilation |
| Your coding agent doesn't recognize `/daily` as a command | Not every agent has slash-command support. Just say it in plain language instead: "read AGENTS.md, then workflows/daily.md, and run the steps using profile/candidate.yaml" |
| Not sure what to put in `tracker.backend` | Use `csv` unless you specifically already use Notion and know your database ID — `csv` needs nothing installed and works out of the box |

### Day-to-day usage

| Symptom | Where to look |
|---|---|
| `python3 scripts/validate_profile.py` fails right after copying the example | That's expected the first time — it's telling you which placeholder fields (name, email, handles) you still need to replace with your real data. Fix each line it lists, then run it again |
| `/daily` finds no jobs | LinkedIn may have blocked scraping — try freehire only, or paste the URL directly into `/apply-batch` |
| CV came out longer than 1 page | `/compile-today` already blocks this on its own (won't register, won't archive, shows up in the report) — trim content following `rules/cv-rules.md` and rerun `/compile-today` |
| `/compile-today` failed to compile | The pdflatex log shows up in the report — usually an unescaped special character |
| A job showed up before | `/daily` filters against the tracker **and** local files (`documents/applications/`, `daily/*/*.json`) to catch an in-progress application that hasn't been confirmed yet — this works even with `tracker.backend: none`, see `workflows/confirm.md` |
| Forgot to run `/confirm` | No problem — the CV is already compiled and archived locally, the tracker just stays out of date until you run `/confirm <number>`; doesn't have to be the same day |

## Other documents

- [AGENTS.md](AGENTS.md) — full architecture, agent/LLM-agnostic
- [SETUP.md](SETUP.md) — installing dependencies
- [OPENCODE.md](OPENCODE.md) — OpenCode's free models and which to use for each task
- [documents/README.md](documents/README.md) — how the applications folder is organized (local, gitignored)

## Credits

The job search CLIs (`.agents/skills/linkedin-search/`, `.agents/skills/freehire-search/`)
were adapted from parts of [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search)
(not a fork) — including the choice of running them on Bun.
