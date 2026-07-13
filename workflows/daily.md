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
and `.agents/skills/freehire-search/` (both bun, zero API cost). Build
queries from `preferences.target_roles` and the highest-level skills in
`skills.<category>` of the active profile — don't use a fixed query list.

```bash
for q in "${QUERIES[@]}"; do
  bun run .agents/skills/linkedin-search/cli/src/cli.ts search \
    -q "$q" -l "Brazil" --remote remote --jobage 7 --format json
  bun run .agents/skills/freehire-search/cli/src/cli.ts search \
    -q "$q" --country BR --remote remote --jobage 7 --format json
done
```

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

**Detecting jobs with no CV needed**: if the destination platform uses an
already-registered profile instead of a PDF (e.g. certain ATS platforms —
this varies by market/country, adjust per profile), mark the job as
"no CV" — generating a `.tex` for these is wasted effort.

## 2. Check for duplicates

Always check locally first, **regardless of `tracker.backend`**:
`documents/applications/<company>_<role>/` (any job ever confirmed via
`workflows/confirm.md`, with or without a CV — see that file for why this
exists even for `tracker.backend: none`) and `daily/*/*.json` from the last
few days (catches an application in progress this week that hasn't been
confirmed yet). This local check alone is enough to never resurface a
confirmed job, even with no external tracker configured.

Additionally, if an external tracker is configured, check it too (catches
applications confirmed on another machine, or history from before this
local checkout existed):

- **notion**: search by company via the Notion MCP
  (`tracker.notion.database_id`). Remove jobs whose company is already
  registered, any status.
- **csv**: read `tracker.csv.path` (e.g. `documents/applications.csv`) and
  remove jobs whose company already appears there.
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
