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

**Detecting jobs with no CV needed**: if the destination platform uses an
already-registered profile instead of a PDF (e.g. certain ATS platforms —
this varies by market/country, adjust per profile), mark the job as
"no CV" — generating a `.tex` for these is wasted effort.

## 2. Check for duplicates

Depends on the active profile's `tracker.backend`:

- **notion**: search by company via the Notion MCP
  (`tracker.notion.database_id`). Remove jobs whose company is already
  registered, any status.
- **csv**: read `tracker.csv.path` (e.g. `documents/applications.csv`) and
  remove jobs whose company already appears there.
- **none**: only check locally (`documents/applications/*/` and
  `daily/*/*.json` from the last few days) — no external tracker to query.

For any backend, also check locally (`documents/applications/*/` and
`daily/*/*.json`) — this covers an in-progress application that hasn't been
confirmed in the tracker yet.

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
