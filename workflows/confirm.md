# workflows/confirm.md — Confirming Sent Applications

**The only step that writes to the tracker.** Neither `apply-batch.md` nor
`compile.md` touch it — only after the dev confirms it was actually sent
does a record get created (an API call, a spent CSV row, or a local file).

The real backend is read from `profile/candidate.yaml → tracker.backend`:

```bash
python3 scripts/validate_profile.py --get tracker.backend
```

## Input

A list of indices from the `workflows/daily.md` table presented in this
session (e.g. `2,5,7`), or company names directly if the table is no longer
in the session's context.

## Why there's always a local record, regardless of backend

`workflows/daily.md`'s dedup check (step 2) relies on
`documents/applications/<company>_<role>/` existing locally — this has to
work **even when `tracker.backend: none`**, otherwise a job with `CV? = No`
(no `.tex`, so `compile.md` never archives anything for it) would leave
**zero trace anywhere** and resurface in every future `/daily` run. So:

- Step 1 below always creates/updates the local folder, for every job,
  regardless of backend.
- Step 2 below additionally registers in an external tracker (csv/notion) —
  this is extra, not the source of dedup truth.

This also means local dedup keeps working as a safety net even if a
misconfigured Notion MCP or a moved CSV file breaks the external backend.

## Step 1 — Local record (always, every backend)

### If the job had `CV? = Yes` (went through `apply-batch.md`)

1. Check locally whether `documents/applications/<company>_<role>/metadata.json`
   exists — this proves `compile.md` already ran and archived it.
2. If it doesn't exist: warn, register nothing — ask to run
   `workflows/compile.md` first.
3. If it exists: update `<folder>/outcome.md` — set **Status: Applied** and
   **Resolution date: today** (it currently says "waiting for send
   confirmation", from `compile.md`).

### If the job had `CV? = No` (application via an already-registered profile)

1. Use the data already collected in this session's `/daily` (no CV, no
   local file yet — `compile.md` never touched this job).
2. Create `documents/applications/<company>_<role>/outcome.md` from
   scratch:

   ```markdown
   # Outcome: <Company> — <Role>

   **URL:** <url>
   **Status:** Applied (no CV — applied via existing platform profile)
   **Application date:** <today>
   **Resolution date:** —

   ## Interview stages reached
   - [ ] Phone screen
   - [ ] Technical interview
   - [ ] System design
   - [ ] Final round
   - [ ] Offer received

   ## Notes
   ```

## Step 2 — External tracker (additional, per backend)

### `tracker.backend: csv` (default, zero dependency)

```bash
CSV_PATH="$(python3 scripts/validate_profile.py --get tracker.csv.path)"
python3 scripts/track_append.py --check-duplicate --path "$CSV_PATH" --empresa "<company>" --cargo "" --data ""
# if it exited with code 0 (doesn't exist), register for real:
python3 scripts/track_append.py \
  --path "$CSV_PATH" \
  --empresa "<company>" --cargo "<role>" --url "<url>" \
  --status "Applied" --data "$(date +%Y-%m-%d)" --fonte "<source>" \
  --nivel "<level>" --stack "<comma-separated stack>" \
  --gaps "<skills with status != full, comma-separated>" \
  --versao-cv "<name of the .tex used, empty if no CV>" \
  --feedback "<gap notes>"
```

### `tracker.backend: notion` (personal config — the profile owner's own MCP)

Requires the agent to have the Notion MCP configured (not present in every
environment — that's why it isn't the default). Read
`profile/candidate.yaml → tracker.notion.*`:

- `data_source_id` = `tracker.notion.data_source_id`
- Fields: Company, Role, Link = url, Status = "Applied", Source, Level,
  Date = today.
- **Stack/Technologies**: only the `stack` items that match
  `tracker.notion.stack_tags` (that workspace's fixed vocabulary) — anything
  left over goes in the Feedback text, never try to write outside the
  vocabulary.
- **Identified gaps**: same rule, filtering by `tracker.notion.gap_tags`.
- Before creating, search (`notion-search` or equivalent) by company to
  avoid duplicates.

### `tracker.backend: none`

Nothing to do here — Step 1's local record already happened and is the
only bookkeeping this backend gets. This is what makes `none` safe to use:
no external service, but `/daily` still won't resurface the job.

## Report

```
✓ Company X → CV compiled, registered → Applied (local + csv/notion)
✓ Company Y → no CV, registered → Applied (local + csv/notion)
✗ Company Z → documents/applications/.../ doesn't exist, run workflows/compile.md first
2 confirmed, 1 pending.
```
