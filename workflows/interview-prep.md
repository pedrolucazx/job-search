# workflows/interview-prep.md — Interview Presentation Script

Generates the HR/behavioral "Roteiro de Entrevista" (presentation script +
critical fit analysis) for a job the candidate already applied to. Not
technical-round prep — see `rules/interview-prep.md` for that.

## Input

A company name, or a full/partial folder name from `documents/applications/`
(e.g. `verity-fullstack` to disambiguate), or an index from a session that
already ran `/apply-batch`/`/confirm` for it.

## 1. Resolve the application folder

List every folder under `documents/applications/` whose name starts with
the given company (case-insensitive, e.g. `dexian` matches
`dexian_fullstack_developer_react_node_aws`).

- **Zero matches**: stop, warn the dev, and point to
  `workflows/apply-batch.md` + `workflows/compile.md` — this command only
  works for a job that already has a compiled, archived CV (same gate style
  as `workflows/confirm.md`'s missing-metadata check).
- **Exactly one match, but not yet confirmed**: check the matched folder's
  `outcome.md`. If it doesn't exist, or its `Status` is still
  `waiting for send confirmation` (the placeholder `compile.md` writes) —
  stop and point to `workflows/confirm.md`. Prepping an interview script
  only makes sense once the candidate actually confirmed the application
  was sent; don't generate one off a CV that only got compiled, not
  confirmed.
- **Exactly one match, already confirmed**: use it.
- **More than one match** (the candidate applied to more than one role at
  the same company — e.g. two different postings from the same employer):
  first drop any match that isn't confirmed yet (same `outcome.md`/`Status`
  check as above) — an unconfirmed application isn't a valid option to prep
  for. Of what's left: zero → treat as the zero-matches case above; one →
  use it; more than one → do **not** guess, list the matching folders with
  their `cargo` (read from each `metadata.json`) and ask the dev which one
  they mean, e.g.:
  ```
  Mais de uma vaga confirmada na Verity:
  1. verity_fullstack_developer_senior_remoto — Fullstack Developer Sênior - REMOTO
  2. verity_node_backend_developer_senior — Node.js Backend Developer Sênior
  Qual delas? (responda com o número ou o nome completo da pasta)
  ```
  Once picked, use that specific folder for every step below.

## 2. Read the sources of truth

- `documents/applications/<company>_<role>/cv_draft.tex` — the source of
  truth for what was actually highlighted to this specific employer (not
  the raw profile — the CV may have been trimmed to fit 1 page).
- `documents/applications/<company>_<role>/metadata.json` — `score`,
  `gaps[]`, `stack[]`, `nivel`, `requisitos_full/partial/absent`, `url`.
- `profile/candidate.yaml` — `personal`, `education`, `languages`,
  `soft_skills`, `professional_experience` (including `duration_note` /
  `period`), `personal_projects`, `preferences.target_industries` /
  `target_roles`.

## 3. Refresh job and company context

If the full job description text isn't already in the session's context,
re-fetch it — reuse `rules/job-evaluation.md` → "Fetching the Full
Description" (WebFetch by default, Playwright MCP fallback for
WAF-blocked domains) rather than re-implementing fetch logic.

Do light company research (site, LinkedIn, main product) for the checklist
item and the FUTURO/FUTURE section — every company-specific claim used in
the script must come from this research or the posting itself (see
`rules/interview-roteiro.md` → "Verify-Before-Use" rule). Never assume a
generic fact about the company.

## 4. Generate the roteiro

Follow `rules/interview-roteiro.md` in full: the 6-section template
contract, the Present→Past→Future timing rule, the conversational tone
rule, the English B1-B2 framing rule, the honesty rule for gaps (risk level
+ concrete action per `partial`/`absent` item in `metadata.json.gaps[]`),
the minimum-4-questions rule, and the data-sourcing sub-rules (years of
experience, motivation sentence, most-relevant-project selection reusing
`rules/cv-rules.md` → "Content Selection by Stack Overlap").

## 5. Save the output

Write to `documents/applications/<company>_<role>/roteiro.md`.

## 6. Update the local outcome record

Append one line to `documents/applications/<company>_<role>/outcome.md`'s
`## Notes` section (create the `## Notes` heading if the file somehow lacks
one), e.g.:

```
Roteiro de entrevista gerado em <date> — ver roteiro.md
```

Never touch `Status`, `Resolution date`, or the "Interview stages reached"
checkboxes in `outcome.md` — those remain exclusively owned by
`workflows/confirm.md`.

## 7. Report

```
✓ Company X — roteiro.md gerado em documents/applications/<pasta>/
  Compatibilidade ~NN% — N gaps sinalizados com risco/ação.
✗ Company Y — folder/cv_draft.tex not found, run apply-batch + compile first.
✗ Company Z — found but not confirmed yet (Status: waiting for send
  confirmation) — run workflows/confirm.md first.
```
