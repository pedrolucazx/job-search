# Rules — Index and Absolute Rules

Universal instructions for any agent/LLM operating this repository. Contains
no candidate data — that lives in `profile/candidate.yaml` (see `AGENTS.md`
at the repo root for where to start).

## Index

| File | Content |
|---|---|
| `cv-rules.md` | CV generation rules: content selection, verbs, formatting, soft skills |
| `job-evaluation.md` | Fit score framework, gap table, deal breakers |
| `ats-verification.md` | Compilation pipeline and ATS verification |
| `interview-prep.md` | Interview prep based on registered applications |

## Absolute Rules (apply to any candidate)

1. **NEVER invent data** — a metric, project, technology, or experience
   outside what's in `profile/candidate.yaml`. If information is missing,
   ask or leave it out — never fill in something plausible.
2. **Education** and **Languages** sections are LOCKED — copy exactly as
   they appear in `profile/candidate.yaml → education / languages`, never
   rewrite or summarize.
3. The CV must fit in **exactly 1 A4 page**.
4. Gap analysis always as a `full` / `partial` / `absent` table (see
   `job-evaluation.md`).
5. Soft skills are always bilingual, format `"Language A (Language B)"` — see
   `profile/candidate.yaml → soft_skills`.
6. **NEVER** use two columns, tables, charts, icons, or images in the CV's
   LaTeX (ATS can't parse them).
7. All candidate data comes from `profile/candidate.yaml` — never hardcoded
   here in `rules/` or in `workflows/`.
8. Fit score and CV content selection work by **overlap between declared
   skills and job requirements** — never by a fixed niche vocabulary (the
   engine doesn't assume "fintech" or any other domain; that's each dev's
   own `preferences.target_industries`).

## Robustness for free/weaker models

If the agent running this is a free or weaker model:
- Prefer this folder's **deterministic gates** (e.g. the 100%-remote rule,
  the 60%-score rule) over nuanced judgment whenever possible.
- When producing structured output (metadata JSON, gap table), if the
  result isn't well-formed, retry once before reporting an error.
- Minimum requirement: the agent needs file + shell access (read
  `profile/`, run `scripts/validate_profile.py`, compile LaTeX). A raw chat
  without tool-use only works for the manual path (pasting the YAML into
  the prompt).
