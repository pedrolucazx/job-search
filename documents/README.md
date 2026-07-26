# Documents

This folder holds application materials. It's gitignored.

## Structure
- `cv/` — staging area: `apply-batch.md` writes `main_<slug>.tex` here and
  `compile-all.sh` compiles it in place, then moves both out. Empty between runs.
- `applications/<slug>/` — one folder per application, created by
  `compile-all.sh` when a CV compiles to 1 page with no blocking ATS issue.
  `<slug>` comes from `scripts/application_id.py` (company + role).
  - `<Candidate_Name>_CV.pdf` — the file you attach when applying, named after
    the candidate (`profile/candidate.yaml → personal.name`)
  - `cv_draft.tex` — the LaTeX source it was built from
  - `metadata.json` — the day's record: score, gap table, stack, url, slug, and
    `cv_tex` pointing at the archived source
  - `outcome.md` — status and interview stages, format owned by
    `scripts/outcome.py`
- `applications.csv` — the CSV tracker, when `profile.tracker.backend` is `csv`.
  Written only by `/confirm`, via `scripts/track_append.py`.
