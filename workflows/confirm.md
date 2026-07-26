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
in the session's context. If a bare company name matches more than one
pending job — more than one `daily/<date>/*.json` from today, or more than
one `documents/applications/<company>_*/` folder still awaiting
confirmation (the candidate applied to two different roles at the same
employer) — list the matches (company + role) and ask which one before
registering anything. Never guess which one the dev means.

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

1. Resolve the folder — don't build the path by hand, or a job that was
   archived under a slightly different name will look like it was never
   compiled:

   ```bash
   python3 scripts/application_id.py --find "<company>" "<role>"
   ```

2. Exit code 1 (nothing printed): warn, register nothing — ask to run
   `workflows/compile.md` first.
3. Folder printed: update `<folder>/outcome.md` — set **Status: Applied** and
   **Resolution date: today** (it currently says "waiting for send
   confirmation", from `compile.md`).

### If the job had `CV? = No` (application via an already-registered profile)

1. Use the data already collected in this session's `/daily` (no CV, no
   local file yet — `compile.md` never touched this job).
2. Get the canonical slug
   (`python3 scripts/application_id.py "<company>" "<role>"`) and create
   `documents/applications/<slug>/outcome.md` from scratch — same name the
   compile step would have used, so a later `/daily` finds it:

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

Company, role, url, source, level, stack, gaps and the CV version all come
from the folder's `metadata.json` via `--from`; the script fills `data` with
today and `status` with `Applied`. Don't retype any of them by hand, or the
tracker row will drift from the record the dashboard reads.

**Exactly two commands, and the second one runs at most once** — it appends a
row, so running it twice gives you two identical rows.

```bash
CSV_PATH="$(python3 scripts/validate_profile.py --get tracker.csv.path)"
FOLDER="documents/applications/<slug>"   # the folder Step 1 resolved
python3 scripts/track_append.py --check-duplicate --path "$CSV_PATH" --from "$FOLDER"
# check-duplicate matches on company AND role, never company alone: two
# different roles at the same employer are two different applications. --from
# takes both from metadata.json, so the check can't be silently disabled by a
# missing --cargo. If it exited with code 0 (doesn't exist), register for real.
# Add --feedback "<note>" to this same command only for something
# metadata.json can't know — never as a second invocation.
python3 scripts/track_append.py --path "$CSV_PATH" --from "$FOLDER"
```

For a `CV? = No` job there is no `metadata.json`, so `--from` has nothing to
read: pass `--empresa`, `--cargo` and `--data` explicitly (plus whatever else
this session's `/daily` collected).

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
- Before creating, search (`notion-search` or equivalent) by company **and**
  role to avoid duplicates — matching by company alone would wrongly flag a
  different role at the same employer as already registered.

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
