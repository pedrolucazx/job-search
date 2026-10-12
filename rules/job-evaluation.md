# job-evaluation.md — Fit Evaluation Framework (generic)

## Evaluation Criteria

For each job requirement, classify as:
- **FULL**: fully met (skill present in the profile at an adequate level)
- **PARTIAL**: partially met (has a base, but lacks depth/years)
- **ABSENT**: not met (a real gap — not in the profile)

## Score Calculation

```
Score = (FULL * 1.0 + PARTIAL * 0.5 + ABSENT * 0.0) / TOTAL * 100
```

## The 60% Rule

Only show jobs with score ≥ 60% in the `/daily` table. Below that the gap is
too large — a customized CV isn't worth the effort.

## Analysis Dimensions (suggested weights, adjustable per track)

1. Technical stack (40% weight) — compare profile `skills` vs. requirements
2. Domain experience (25% weight) — `professional_experience` /
   `personal_projects` relevant to the job's sector
3. Job level vs. `preferences.seniority_by_stack` (15% weight)
4. Location/flexibility (10% weight) — only counts if it passed the deal
   breakers below
5. Alignment with `preferences.target_roles` / `target_industries` (10% weight)

**Entry-level candidates** (empty `professional_experience` and
`personal_projects` — see `rules/cv-rules.md` → Entry-Level Candidates):
dimension 2 has nothing to measure and would unfairly cap every score at
75%. Redistribute its 25% into dimension 1 (stack, now 65%) when the job
itself is an internship/trainee/entry-level posting — those postings don't
expect prior domain experience either. For a mid/senior posting, keep the
weights as-is: a real domain-experience gap against a job that expects it
is a real gap, not something to paper over.

## Gap Table (mandatory format)

| Requirement | Status | Note |
|---|---|---|
| <job skill> | FULL / PARTIAL / ABSENT | context (years, project where it showed up, or reason for the gap) |

## Deal Breakers

Exclude the job **from the whole table**, not just flag it — see
`profile/candidate.yaml → preferences.deal_breakers`. Each item there is a
hard, candidate-specific exclusion condition (e.g. work arrangement, absence
of something mandatory for the candidate). Treat each `deal_breaker` as a
literal rule: if the job matches it, it's out of the table, no exception —
even if the rest of the fit is excellent.

If `preferences.deal_breakers` includes something about work arrangement
(remote/hybrid/on-site), **always confirm by reading the full job
description before applying the exclusion** — search tags (`--remote
remote` etc.) aren't reliable, platforms have mislabeled jobs before.

### Work Arrangement: Silent Full Descriptions (flag, don't exclude)

LinkedIn's public/guest job pages (what this repo's scraper reads) don't
expose the "✓ Remoto" workplace-type badge shown in the logged-in app UI —
confirmed empirically 2026-07-15: neither the `jobs-guest` detail endpoint
nor the public `/jobs/view/<id>` page carry a `workplaceType`,
`jobLocationType`, or JSON-LD `JobPosting` field in any posting checked.
Getting that badge would need an authenticated LinkedIn session (Voyager
API or a logged-in Playwright session) — not worth the risk of the
candidate's real account getting banned over a job-fit heuristic.

So when the full description (WebFetch/Playwright) has **no**
work-arrangement language anywhere — no "remoto"/"híbrido"/"presencial"/
"home office", positive or negative — that's inconclusive, not a deal-breaker
match. Don't exclude on silence:

1. Generate the CV normally if the real score otherwise clears 60%.
2. Add a note to the gap table / report: "modelo de trabalho não confirmado
   no texto do anúncio — conferir o badge Remoto/Híbrido/Presencial na
   página do LinkedIn antes de aplicar."

Only exclude on an **explicit** signal in the full description — "modelo
híbrido", "presencial em <cidade>", a fixed office address with no remote
language nearby, etc. Silence isn't evidence either way.

## Education Completion Requirement (flag, don't exclude)

If the JD mentions a degree requirement (e.g. "ensino superior", "upper
education degree", "tecnólogo completo") and the candidate's `education`
doesn't have a matching `status: "completed"` entry for it, **this is not a
deal breaker** — don't drop the job from the table. Add a note to the gap
table instead (e.g. `| Ensino superior completo | partial/absent | job
lists it, candidate's degree is in progress |`).

The reason it's a note and not an exclusion: some platforms genuinely don't
enforce it (soft requirement, common in BR postings), while others (Gupy
especially) ask it as a **hidden eliminatory screening question** in the
application form itself — invisible when just reading the posting's text —
and auto-reject on the spot before a human ever sees the CV (confirmed
2026-07-13 with Pecege). There's no way to know which case it is from the
job description alone, so let the candidate decide per job instead of
guessing wrong in either direction.

## Seniority Mismatch

If `preferences.seniority_by_stack` exists and the job asks for a level
**above** the ceiling declared for that stack, treat it as a deal breaker when
`preferences.deal_breakers` says so — exclude the job from the table entirely,
the same as any other deal breaker. It's detectable straight from the title
(Sênior, Senior, Sr, Especialista, Specialist, Staff, Lead, Principal, Master,
and roman numerals above the candidate's level), so apply it at step 1 of
`workflows/daily.md`, before any full-description fetch.

A level **below** the ceiling (e.g. a Júnior posting for a Pleno candidate) is
not a deal breaker — flag it in the gap notes and let the candidate decide.

Where the posting spans a range that includes an accepted level ("Pleno /
Sênior", "PL/SR"), it passes: the candidate is eligible for the lower end.

## Two Evaluation Stages

### 1. `/daily` — heuristic pre-screening (no full fetch)

Score here is estimated from title + search tags, without reading the job's
full description (avoids burning scraping/token budget on an obvious job).
**Not final** — don't apply deal breakers definitively here, only as a
coarse initial filter.

### 2. `/apply-batch` — real evaluation (with full description)

1. Fetch the full description.
2. **Check deal breakers first**, with the full description in hand. If it
   matches any: stop here, don't generate a CV, mark as excluded in the
   report with the reason.
3. Extract must-have and nice-to-have requirements.
4. Compare against `profile/candidate.yaml` (skills,
   professional_experience, personal_projects).
5. Produce the full gap table + real score.
6. **If real score < 60%**: stop here, don't generate a CV — the `/daily`
   score was just an estimate; the real one decides whether writing the CV
   is worth the effort.

## Fetching the Full Description

- Default: WebFetch.
- If a specific domain blocks WebFetch/curl (e.g. an SPA behind WAF/bot
  protection), use a real browser via MCP (e.g. Playwright) as a fallback —
  document the problematic domain in a project note so you don't
  rediscover the same block later.
