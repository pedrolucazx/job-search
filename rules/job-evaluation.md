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

## Seniority Mismatch

If `preferences.seniority_by_stack` exists and the job asks for a different
level than declared for that stack: not a deal breaker (doesn't exclude by
itself), but flag it clearly in the table/gap notes — the candidate decides
whether to apply anyway.

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
