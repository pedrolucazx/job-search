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
Scrape (LinkedIn + freehire) → dedup in Notion → gap score → ranked table.
You pick the numbers.

```
/apply-batch 1,2,3,8
```
Generates `documents/cv/main_<company>_<role>.tex` + `daily/<date>/<company>_<role>.json` for each chosen job
(role in the name avoids overwriting when there's more than one job at the same company).
Accepts an index from the table or a pasted URL directly (a job found outside `/daily`).

Exit Claude Code (`exit` / Ctrl+D) once the `.tex` files are ready.

### Step 2 — OpenCode (`opencode` at the repo root)

```
/compile-today
```
Reads `daily/<date>/*.json` → `pdflatex` on each `.tex` (via `scripts/compile-all.sh`) →
ATS check → registers in Notion via MCP → archives into `documents/applications/`.

Implemented in `.opencode/commands/compile-today.md`, already with
`north-mini-code-free` pinned in the frontmatter — no need to pick a model by hand.

> ⚠️ **Setup pending**: `pdflatex` isn't installed in this environment
> (`sudo apt install texlive-latex-base texlive-latex-recommended texlive-fonts-recommended`,
> see `SETUP.md`). Without it, `/compile-today`'s Step 1 won't run. Haven't yet
> tested the compilation end-to-end — only validated that reading `cv_tex` from
> the JSON works correctly.

---

## 2. Available free models (OpenCode Zen)

| Model | What's known |
|---|---|
| `opencode/big-pickle` | A "stealth" model (code name, provider doesn't reveal which one it is). No size/speed signal in the name. |
| `opencode/deepseek-v4-flash-free` | DeepSeek line, "flash" variant (optimized for speed/cost). **Your current default on OpenCode.** |
| `opencode/mimo-v2.5-free` | MiMo line (Xiaomi) — historically this line focuses on reasoning/math relative to its size. |
| `opencode/north-mini-code-free` | "mini" + "code" in the name — signals a small/fast model tuned for code and tool-calling. 256K context per third-party aggregators. |

⚠️ **This is name-based heuristic, not benchmark**: OpenCode Zen's official
documentation doesn't publish a capability comparison between these 4 — it only
confirms they're free for a limited time (usage data may be retained to improve
the model, avoid pasting sensitive information). Adjust the table below as you
observe in practice.

---

## 3. Which model to use for which task

| Task (inside `/compile-today`) | Suggested model | Why |
|---|---|---|
| Run `pdflatex`, `pdftotext`, parse JSON, call the Notion MCP | `north-mini-code-free` | Mechanical tool-calling/bash, little judgment needed — "code" in the name is the strongest signal we have. |
| Interpret a LaTeX compile error (overfull hbox, missing package) and propose a fix | `mimo-v2.5-free` | Needs real reasoning about the root cause, not just following steps. |
| Final daily report / `/status` | `deepseek-v4-flash-free` | Your current default — summarizing text is light work, no need to switch. |
| Fallback — if the three above get stuck or give a bad answer on a tricky job | `big-pickle` | Reserve option with no clear signal in the name; free, so it costs nothing to try before falling back to Claude. |

Switching models mid-OpenCode-session: `/models` in the TUI, or pin it per
command (Section 4).

---

## 4. Pinning the model per command (avoids picking manually every time)

OpenCode's custom commands live in `.opencode/commands/*.md`, just like
`.claude/commands/`. The frontmatter accepts `model:`:

```markdown
---
description: Compiles today's CVs, runs the ATS check, and registers in Notion
agent: build
model: opencode/north-mini-code-free
---

Read daily/<date>/*.json and for each one: compile the .tex with pdflatex,
run pdftotext -layout for the ATS check, and register the application in Notion via MCP.
```

This way `/compile-today` always opens with `north-mini-code-free` without you
needing to select it on the spot. Smaller commands (`/ats-check`,
`/register-notion`, `/status`, `/compile-last`) are left for when they're
actually used — the same reasoning that held back `/interview-prep` until it
became a real need (see `.opencode/commands/interview-prep.md`, now
implemented with `mimo-v2.5-free` — that task requires fine judgment about
tone/honesty on gaps, not mechanical tool-calling, which is why it doesn't use
`north-mini-code-free`).
