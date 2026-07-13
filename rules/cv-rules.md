# cv-rules.md — CV Generation Rules (generic, any track)

See `README.md` for the Absolute Rules. This file covers the logic for
selecting and formatting CV content. Never contains candidate data —
everything here reads `profile/candidate.yaml`.

## Content Selection by Stack Overlap

There's no fixed table of "which project to highlight for which stack" —
that would be niche-specific, and the goal is to work the same for backend,
frontend, mobile, IoT, data, etc. Instead:

1. Extract the job's required stack (must-have + nice-to-have).
2. For each item in `professional_experience[].projects[]` and each item in
   `personal_projects[]`, compute the overlap between that item's `stack`
   and the job's stack.
3. Sort by overlap, descending. Pick the projects/experiences with the
   highest overlap to highlight first in the CV — low-overlap ones get cut
   if the 1-page limit gets tight.
4. An item with `include_only_if` only gets included if the textual
   condition matches the job (e.g. a Ruby project only shows up if the job
   mentions Ruby).
5. A `personal_projects` item without a filled-in `link`: cite it without a
   hyperlink, never invent a repository URL.

## Entry-Level Candidates (No Experience Yet)

If `professional_experience` and `personal_projects` are both empty, that's
not an incomplete profile — it's a legitimate student/intern/trainee
candidate. Build the CV around what actually exists instead:

- Lead with **Education** — expand `education[].description` if it lists
  relevant coursework, a capstone/class project, or a bootcamp track. Still
  never invent detail beyond what's in the profile.
- **Skills** section carries more weight than usual — list everything in
  `skills.<category>` even at `basic` level; for this candidate that's the
  main evidence of capability, not a supplement to experience bullets.
- Summary section should be honest about seniority ("Computer Science
  student seeking an internship in backend development", not "Software
  Engineer with X years").
- Never fabricate a "Projects" or "Experience" section to fill space — an
  intern/trainee CV that's mostly Education + Skills + Languages is normal
  and expected, not a defect to paper over.

## Selection by Job Seniority

Tone and verbs change based on the seniority declared in the job posting vs.
the candidate's seniority (`preferences.seniority_by_stack`, if filled in):

| Job level | Tone | Preferred verbs |
|---|---|---|
| Senior/Staff/Specialist | Autonomy, ownership, architectural decisions | Led, Defined, Ensured, Architected |
| Mid-level | Technical autonomy, driving work | Led, Defined, Ensured, Implemented |
| Junior | Fundamentals, delivery, learning | Developed, Implemented, Collaborated |

If `preferences.seniority_by_stack` flags a mismatch (the job asks for a
level above what the candidate declared for that stack), report it in the
evaluation — it doesn't block CV generation by itself, but the agent should
flag it in the report.

## Soft Skills

Always bilingual, format `"Language A (Language B)"`. Use exactly the 6 (or
however many there are) from `profile/candidate.yaml → soft_skills`. If the
job uses an equivalent term for one of them, you can swap the label while
keeping the bilingual pair — never add a 7th.

## Experience Bullets

Format: **ACTION VERB + TECHNICAL CONTEXT + RESULT/SCOPE**.

- 4 to 6 bullets per experience, starting with the most relevant to the job.
- Vary the verb — never repeat the same verb in consecutive bullets.
- Base bullets on `professional_experience[].responsibilities` — don't
  invent a responsibility that isn't listed there.
- If the profile distinguishes tools by context (e.g. one ORM used at work
  and another in personal projects), respect that distinction — don't
  transplant a personal-project tool into a professional-experience bullet
  or vice versa.

**Example of a correct bullet**: specific verb + real technology from the
profile + concrete scope/result. Never generic like "Built robust and
secure APIs" (that says nothing verifiable).

## Experience Duration

Never round experience time beyond 1 year (e.g. if `duration_note` says
"4+ years", write "4 years" or "4+ years", never "5 years").

## Template and Formatting

- LaTeX article class, A4, 1 page, sans-serif font (Helvetica or
  equivalent), a single accent color for section headings.
- See `templates/cv_template.tex` as the base — it already has the
  placeholders.
- Section titles in UPPERCASE, no two columns/tables/icons/images (Absolute
  Rule #6).

## Mandatory Checklist Before Delivering

1. No invented data — every bullet/project/skill traceable to
   `profile/candidate.yaml`.
2. Institution/project/technology names spelled exactly as in the profile
   (check for typos).
3. Repository links as real hyperlinks, only for items with `link` filled
   in the profile.
4. Education and Languages identical to the profile, no paraphrasing.
5. Document fits on 1 A4 page.
6. Email and phone appear as literal text in the final PDF (not as an icon
   glyph — verified in `ats-verification.md`).
