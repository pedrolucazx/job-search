# workflows/apply-batch.md — Batch Application

Generates `.tex` CVs for N jobs selected from the `workflows/daily.md`
table. Generic — reads `profile/candidate.yaml` + `rules/`, never hardcoded
data.

## Input

- A list of numeric indices (e.g. `1,2,3,4,8,10,20`) from this session's
  `/daily` table, OR a URL pasted directly (manual flow).

## Flow per job

### 1. Fetch the posting

If already collected during the scrape with the full description, use it
directly. Otherwise, WebFetch the URL (see `rules/job-evaluation.md` →
Fetching the Full Description for the fallback on problematic domains).

### 2. Extract requirements

List must-have and nice-to-have requirements for the job.

### 2.5 Gate — deal breakers and real score

Use `rules/job-evaluation.md`, with the full description in hand:

1. Check `profile/candidate.yaml → preferences.deal_breakers` against the
   full description (not the search tag). If it matches any: **don't
   generate a CV**, mark as excluded in the report with the reason.
2. Calculate the real score (full gap table). If < 60%: **don't generate a
   CV**, mark as excluded with the score and the main reason for the drop.
3. Only proceed to step 3 if it passed both.

### 3. Generate the CV

Read `rules/cv-rules.md` + `profile/candidate.yaml` +
`templates/cv_template.tex`.

Produce `documents/cv/main_<sanitized_company>.tex` with:
- [ ] Summary personalized for the job
- [ ] Skills ordered by overlap with the job's stack
- [ ] 4-6 experience bullets, most relevant first
- [ ] Projects selected by stack overlap (see `rules/cv-rules.md`)
- [ ] Education and Languages — copied exactly from `profile/candidate.yaml`
- [ ] Soft skills — exactly the profile's, bilingual format
- [ ] Exactly 1 A4 page
- [ ] No data outside the profile

### 4. Save metadata

Create `daily/<date>/<sanitized_company>.json` — canonical schema, field
names can't change (`workflows/compile.md` depends on them):

```json
{
  "empresa": "Company Name",
  "cargo": "Job title",
  "url": "https://...",
  "data": "YYYY-MM-DD",
  "cv_tex": "documents/cv/main_company.tex",
  "score": 82,
  "gaps": [
    {"skill": "AWS", "status": "absent", "nota": "Identified gap"},
    {"skill": "Kafka", "status": "partial", "nota": "Concepts, no hands-on practice"}
  ],
  "stack": ["Node.js", "TypeScript", "PostgreSQL"],
  "nivel": "Mid-level",
  "fonte": "LinkedIn",
  "requisitos_full": 7,
  "requisitos_partial": 2,
  "requisitos_absent": 1,
  "total_requisitos": 10
}
```

### 5. Partial report

- Passed the gate: `✓ Company — CV generated — <url>`
- Excluded at the gate: `✗ Company — excluded, real score 33% (reason)` —
  no `.tex` generated, no effort wasted on a CV that shouldn't have gotten
  this far.

At the end: "X CVs generated, Y excluded. Run `workflows/compile.md` for
the generated ones."
