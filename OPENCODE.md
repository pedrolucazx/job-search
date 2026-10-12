# OpenCode — Daily Sequence and Free Models

Guide for using OpenCode (free AI, via OpenCode Zen) as the pipeline's second actor.
Goal: Claude Code (paid) does the work that requires fine judgment; OpenCode (free)
does the mechanical work. Saves Claude Code Pro tokens even with RTK.

---

## 1. Full daily sequence

### Step 1 — Claude Code (`claude` at the repo root)

```
/daily
```
Scrape (LinkedIn + freehire) → dedup (local first, then the configured tracker)
→ gap score → ranked table. You pick the numbers.

```
/apply-batch 1,2,3,8
```
Generates `documents/cv/main_<slug>.tex` + `daily/<date>/<slug>.json` for each chosen job,
where `<slug>` comes from `scripts/application_id.py` (company + role, so two roles at the
same company can't overwrite each other).
Accepts an index from the table or a pasted URL directly (a job found outside `/daily`).

Exit Claude Code (`exit` / Ctrl+D) once the `.tex` files are ready.

### Step 2 — OpenCode (`opencode` at the repo root)

```
/compile-today
```
Reads `daily/<date>/*.json` → `pdflatex` on each `.tex` (via `scripts/compile-all.sh`) →
ATS check → archives into `documents/applications/`.

**It never touches the tracker.** Registering an application is `/confirm`'s job
alone, after you confirm the CV was actually sent — see `workflows/compile.md`.

Implemented in `.opencode/commands/compile-today.md`. It pins no model: the
`north-mini-code-free` it used to pin is gone from OpenCode Zen (see the table
below), so it runs on whatever your OpenCode default is, same as `/daily`,
`/apply-batch` and `/confirm`. Only `/interview-prep` still pins one
(`mimo-v2.5-free`).

> ⚠️ **Setup pending**: `pdflatex` isn't installed in this environment
> (`sudo apt install texlive-latex-base texlive-latex-recommended texlive-fonts-recommended`,
> see `SETUP.md`). Without it, `/compile-today`'s Step 1 won't run. Haven't yet
> tested the compilation end-to-end — only validated that reading `cv_tex` from
> the JSON works correctly.

---

## 2. Available models (OpenCode Zen)

Last verified: 2026-09-01 via `opencode models`.

### Free tier (OpenCode-branded)

| Model | Status | What's known |
|---|---|---|
| `opencode/big-pickle` | ✅ Available | Stealth model — provider doesn't reveal which one. No size/speed signal. |
| `opencode/mimo-v2.5-free` | ✅ Available | MiMo line (Xiaomi) — reasoning/math focus. **Pinned by `/interview-prep`.** |
| `opencode/deepseek-v4-flash-free` | ❌ Not available | Removed from current version. |
| `opencode/north-mini-code-free` | ❌ Not available | Removed from current version. |

### Paid / usage-metered (also on the account)

Google, NVIDIA, and OpenAI models are also listed (e.g. `google/gemini-3.5-flash`, `nvidia/deepseek-ai/deepseek-v4-flash`, `openai/gpt-5.5`). These are **not free-tier** — usage counts against quota or bills.

⚠️ **Heuristic, not benchmark**: OpenCode doesn't publish capability comparisons. Adjust based on observation.

---

## 3. Which model to use for which task

| Task (inside `/compile-today`) | Suggested model | Why |
|---|---|---|
| Run `pdflatex`, `pdftotext`, parse JSON, call the Notion MCP | `mimo-v2.5-free` | Only free option available for tool-calling. |
| Interpret a LaTeX compile error (overfull hbox, missing package) and propose a fix | `mimo-v2.5-free` | Needs reasoning about root cause. |
| Final daily report / `/status` | `mimo-v2.5-free` | Only free option — summarizing is light work. |
| Fallback | `big-pickle` | Second free option if mimo struggles. |

> ⚠️ Only 2 free models remain: `mimo-v2.5-free` and `big-pickle`. If neither
> works for a task, fall back to Claude (this session's model).

Switching models mid-OpenCode-session: `/models` in the TUI, or pin it per
command (Section 4).

---

## 4. Pinning the model per command (avoids picking manually every time)

OpenCode's custom commands live in `.opencode/commands/*.md`, just like
`.claude/commands/`. The frontmatter accepts `model:`:

```markdown
---
description: Generates the interview script (presentation + fit analysis) for an already-confirmed job
agent: build
model: opencode/mimo-v2.5-free
---

Read workflows/interview-prep.md and execute the steps described there.
```

This way `/interview-prep` always opens with `mimo-v2.5-free` without you
needing to select it on the spot. It's the only command that pins one today:
leave `model:` out and the command runs on your OpenCode default, which is
what `/compile-today`, `/daily`, `/apply-batch` and `/confirm` do. Pin a model
only when a command genuinely needs that one, otherwise the pin rots the way
`north-mini-code-free` did when it left the free tier.

> ⚠️ Only 2 free models available: `mimo-v2.5-free` and `big-pickle`.
