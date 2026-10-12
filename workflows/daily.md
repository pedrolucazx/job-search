# workflows/daily.md — Morning Routine

Kicks off the day's applications: scrape → gap score → table → dev's
choice. Generic — search queries come from the active profile, never
hardcoded here.

## 0. Load the profile

```bash
python3 scripts/validate_profile.py
```

If it errors, stop and ask the dev to fix `profile/candidate.yaml` before
continuing. Read `preferences.target_roles`, `track`, and `skills` from the
profile — they're the basis for step 1's search queries.

## 1. Scrape (configurable sources)

Search CLIs available in this repo today: `.agents/skills/linkedin-search/`
and `.agents/skills/freehire-search/` (both bun, zero API cost). Build two
query axes from the active profile — don't use a fixed query list:

- `ROLE_QUERY`: `preferences.target_roles` OR-joined into one quoted string
  (e.g. `"Backend Developer Pleno" OR "Software Engineer" OR "Fullstack
  Developer"`). One combined call surfaces more distinct postings per page
  than one call per role, which mostly re-hits the same top-of-feed jobs.
- `SKILL_QUERY`: the 3-4 highest-`years`/`level` skills across
  `skills.<category>`, OR-joined the same way (e.g. `"Node.js" OR "NestJS"
  OR "TypeScript"`). Catches postings whose title doesn't literally match a
  target role but whose stack is a tight fit — this is what actually
  drives the fit score in step 3, so it raises match accuracy, not just
  volume.

```bash
QUERIES=("$ROLE_QUERY" "$SKILL_QUERY")

for q in "${QUERIES[@]}"; do
  # LinkedIn's page size is fixed at 10 server-side, so pull 4 pages
  # (40 results/query) instead of just page 1.
  for page in 1 2 3 4; do
    bun run .agents/skills/linkedin-search/cli/src/cli.ts search \
      -q "$q" -l "Brazil" --remote remote --jobage 14 --page "$page" --format json
  done
  # freehire's --limit IS the real API page size, so ask for 40 in one call
  # instead of looping pages.
  bun run .agents/skills/freehire-search/cli/src/cli.ts search \
    -q "$q" --country BR --remote remote --jobage 14 --limit 40 \
    --seniority junior,middle --format json
done
```

⚠️ This is ~9 calls/source per run (2 query axes × 4 LinkedIn pages + 1
freehire call, vs. ~3 calls/source before) — still personal-use volume, but
if LinkedIn starts responding with 429s, drop to 3 pages before dropping a
query axis (the skill axis is what raises match accuracy, not the page
count).

⚠️ This filters by the search tag, it's not a guarantee — reconfirm the real
work arrangement in step 2.5 of `apply-batch.md` (see
`rules/job-evaluation.md` → Deal Breakers). Never rely solely on this tag to
apply `preferences.deal_breakers` definitively.

Deduplicate by company + role across sources. Keep each job's source
(`linkedin`/`freehire`/other) to use later in the tracker, if the backend is
Notion (`tracker.notion.stack_tags` etc.).

**Filtering blocked companies**: drop any job whose company matches
`preferences.blocked_companies` (case-insensitive), before anything else —
no fit score calculated, no full description fetched. This is a company-level
hard exclusion decided by the dev (e.g. a recruiter with a suspicious volume
of near-identical postings, a mandatory intro-video gate, or just a bad
personal experience) — different from `preferences.deal_breakers`, which is
about a specific job's content, not the company posting it. Don't mention
these jobs in the ranked table at all, not even as "excluded" — they're
silently dropped at this stage.

**Filtering blocked sources**: drop any job whose URL host matches an entry in
`preferences.blocked_sources` (substring match on the host, case-insensitive),
at the same stage and with the same silence as `blocked_companies` — not
mentioned in the table at all. This blocks a *destination platform*, not an
employer: the same company stays eligible through another source, so match on
the URL, never on the company name. Note that aggregators rewrite links, so one
posting can surface twice under different hosts — dedup by company + role
happens first, and the surviving copy is the one whose host gets checked; if
the copy that survives dedup is the blocked one, prefer keeping the copy from
an allowed host instead of dropping the job entirely.

**Filtering gender-restricted postings**: drop any job whose title signals it's
restricted to a gender the candidate doesn't fit (e.g. "vaga para mulheres",
"women only", "woman in tech") — see `preferences.deal_breakers` in
`profile/candidate.yaml`. Unlike the work-arrangement deal breaker, this one
is detectable straight from the title/tag, no full-description fetch needed,
so apply it here at step 1, same as `blocked_companies`: don't mention these
jobs in the ranked table at all, not even as "excluded".

**Filtering seniority above the candidate's ceiling**: drop any job whose title
declares a level above the ceiling in `preferences.seniority_by_stack` —
Sênior, Senior, Sr, Especialista, Specialist, Staff, Lead, Tech Lead,
Principal, Master, Architect, and roman numerals above the candidate's level.
See `preferences.deal_breakers` in `profile/candidate.yaml` and
`rules/job-evaluation.md` → Seniority Mismatch. Like the gender filter, this is
readable straight from the title, so it belongs here at step 1, not at the
`apply-batch` gate: on 2026-10-11 a batch of 35 produced 12 CVs of which 10
were Sênior/Especialista, all discarded unread. A title spanning a range that
includes an accepted level ("Pleno / Sênior", "PL/SR") passes. Don't mention
the dropped ones in the ranked table at all.

Where the source supports a seniority facet, filter at the API instead of
post-filtering: freehire takes `--seniority junior,middle`. LinkedIn has **no**
seniority flag on search (the field only comes back on `detail`, and it's
usually `Not Applicable`), so there the title match above is the only filter.

**Detecting jobs with no CV needed**: if the destination platform uses an
already-registered profile instead of a PDF (e.g. certain ATS platforms —
this varies by market/country, adjust per profile), mark the job as
"no CV" — generating a `.tex` for these is wasted effort.

## 2. Check for duplicates

Always check locally first, **regardless of `tracker.backend`**. Resolve the
application's folder with the identity module rather than building the path by
hand — it exits 0 and prints the folder if the job was ever archived, exits 1
if it wasn't, and still finds folders whose name predates the module:

```bash
python3 scripts/application_id.py --find "<company>" "<role>"
```

That covers any job ever confirmed via `workflows/confirm.md`, with or without
a CV (see that file for why this exists even for `tracker.backend: none`).
Also check `daily/*/*.json` from the last few days (catches an application in
progress this week that hasn't been confirmed yet). This local check alone is
enough to never resurface a confirmed job, even with no external tracker
configured.

Additionally, if an external tracker is configured, check it too (catches
applications confirmed on another machine, or history from before this
local checkout existed):

- **notion**: search by company via the Notion MCP
  (`tracker.notion.database_id`). Remove jobs where **both** company and
  role match an existing entry (any status) — matching by company alone
  would silently and permanently hide a genuinely different role at a
  company you've touched before (e.g. a second, better-fitting posting from
  an employer that already rejected you for a different role).
- **csv**: read `tracker.csv.path` (e.g. `documents/applications.csv`) and
  remove jobs where both company and role already appear there
  (`scripts/track_append.py --check-duplicate` takes `--cargo` for exactly
  this — passing an empty `--cargo` degrades back to the old,
  too-broad company-only match).
- **none**: nothing extra to check — the local check above is the whole
  story for this backend.

## 3. Calculate fit score

Use `rules/job-evaluation.md` (heuristic pre-screening, no full fetch)
comparing the job's title + skills against `profile/candidate.yaml`.

## 4. Present the ranked table

Always include the URL (it's the link the dev will use to submit manually
later — this system never applies on its own). Only jobs with score ≥ 60%:

```
#  │ Company   │ Role            │ URL              │ Score │ Gaps    │ CV?
───┼───────────┼─────────────────┼──────────────────┼───────┼─────────┼──────
1  │ Company X │ Mid-level BE    │ ...              │ 82%   │ AWS     │ Yes
```

## 5. Ask

> "Which numbers do you want to apply to today? (e.g. 1,2,3,4,8,10,20) or
> 'skip'."

## 6. Route by type

- **`CV? = Yes`** → `workflows/apply-batch.md` with those indices.
- **`CV? = No`** → apply manually on the platform; then
  `workflows/confirm.md` with those indices to register in the tracker.
