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
`north-mini-code-free` it used to pin is gone from OpenCode Zen (see Section 2),
so it runs on your OpenCode default, `console-nvidia/moonshotai/kimi-k3`, same
as `/daily`, `/apply-batch` and `/confirm`. Only `/interview-prep` pins one.

> ⚠️ **Setup pending**: `pdflatex` isn't installed in this environment
> (`sudo apt install texlive-latex-base texlive-latex-recommended texlive-fonts-recommended`,
> see `SETUP.md`). Without it, `/compile-today`'s Step 1 won't run. Haven't yet
> tested the compilation end-to-end — only validated that reading `cv_tex` from
> the JSON works correctly.

---

## 2. Available models (OpenCode Zen)

Last verified: 2026-10-11 via `opencode models`. **130 models across 3
providers**: `console-nvidia` (57), `opencode` (42), `opencode-go` (31). Don't
guess an id, the prefix is part of it and the same model shows up under more
than one: Kimi K3 is listed as `console-nvidia/moonshotai/kimi-k3`,
`opencode/kimi-k3` and `opencode-go/kimi-k3`.

### Current default

`console-nvidia/moonshotai/kimi-k3`, so every command without a `model:` in its
frontmatter runs on it.

### Free tier

Ten ids under `opencode/` end in `-free`:

| Model | Note |
|---|---|
| `opencode/mimo-v2.6-flash-free` | MiMo line (Xiaomi), reasoning/math focus. Replaces the `mimo-v2.5-free` this doc used to recommend. |
| `opencode/nemotron-3-ultra-free` | Nemotron line (NVIDIA), the larger of the two. |
| `opencode/nemotron-3.5-lightning-free` | Nemotron, speed variant. |
| `opencode/ling-3.1-flash-free` | Ling line, flash variant. |
| `opencode/ling-3.0-flash-fin-free` | Ling, finance-tuned. |
| `opencode/longcat-2.5-preview-free` | Preview, expect churn. |
| `opencode/step-5-preview-free` | Preview, expect churn. |
| `opencode/exo-free` | No public signal. |
| `opencode/space-bunny-free` | Stealth name, no public signal. |
| `opencode/muse-spark-1.3-contributor-free` | Contributor tier, may need eligibility. |

`opencode/big-pickle` is still listed and still a stealth name, without a
`-free` suffix.

### Gone since the last check

`opencode/mimo-v2.5-free`, `opencode/north-mini-code-free` and
`opencode/deepseek-v4-flash-free` are no longer in the list. The first two were
pinned in command frontmatter here and had to be replaced.

### Paid / usage-metered

Most of the inventory. The `opencode/` prefix also carries frontier models
(`claude-opus-5-5`, `gpt-6-astra`, `gemini-3.1-pro`), and `console-nvidia`
carries 57 ids including non-chat ones (embeddings, vision, image generation),
which won't work as a command's `model:`.

⚠️ **Heuristic, not benchmark**: OpenCode doesn't publish capability
comparisons, and a `-free` suffix says nothing about whether a model handles
tool-calling well. Adjust based on observation.

---

## 3. Which model to use for which task

`/compile-today` and the other unpinned commands run on the
`console-nvidia/moonshotai/kimi-k3` default, which is fine for the whole
pipeline: shelling out to `pdflatex` and `pdftotext`, parsing the daily JSON,
and calling the Notion MCP are tool-calling plus light reasoning.

Reach for something else only on a specific failure:

| Situation | Try | Why |
|---|---|---|
| Default is rate-limited or down | `opencode/mimo-v2.6-flash-free` | Free, reasoning-oriented, handles tool-calling. |
| That one also fails | `opencode/big-pickle` | Second fallback, still listed. |
| A LaTeX error neither can diagnose | Claude (this session) | Root-cause reasoning over a noisy log. |

Switching mid-session: `/models` in the TUI, or pin it per command (Section 4).

---

## 4. Pinning the model per command (avoids picking manually every time)

OpenCode's custom commands live in `.opencode/commands/*.md`, just like
`.claude/commands/`. The frontmatter accepts `model:`:

```markdown
---
description: Generates the interview script (presentation + fit analysis) for an already-confirmed job
agent: build
model: console-nvidia/moonshotai/kimi-k3
---

Read workflows/interview-prep.md and execute the steps described there.
```

Leave `model:` out and the command runs on the account default, which is what
`/compile-today`, `/daily`, `/apply-batch` and `/confirm` do, and what keeps
them working when an id disappears. **A pin is a liability**: this repo has
already shipped two dead ones, `north-mini-code-free` and `mimo-v2.5-free`,
both pinned while the model was quietly dropped from the list. Pin only when a
command genuinely needs that specific model, and re-run `opencode models` when
one starts failing for no clear reason.
