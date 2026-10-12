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

## Professional Summary (Resumo Profissional)

Never a single generic sentence that just restates the Skills section in
prose (e.g. "Desenvolvedor backend com experiência em X, Y, Z, testes e
CI/CD" — that's filler, not evidence). Write 3-5 sentences:

1. Years of experience + the 2-3 stack items the job cares about most (same
   ranking as "Content Selection by Stack Overlap" below).
2. At least one sentence naming a real, concrete system from
   `professional_experience[].projects[]` relevant to the job (the actual
   project/client name, e.g. "FHEMIG", "Celcoin (BaaS)", "SES-RS") — a named
   system is what makes the summary read as evidence instead of a skills
   list. Never invent one; if no project overlaps the job's stack, name the
   most senior/complex one available instead of skipping this sentence.
3. A closing sentence on how the candidate works (autonomy, code quality,
   collaboration), toned to the job's seniority (see "Selection by Job
   Seniority" below).

## AI-Assisted Development Workflow (when the job asks for it)

If the job posting mentions AI-assisted development as a skill or
requirement (Claude Code, Copilot, Cursor, "AI-driven development",
"prompt engineering as part of the SDLC", etc.), cite
`profile/candidate.yaml → ai_development_workflow` in the Resumo
Profissional or Experience Bullets — in addition to, never instead of, the
`Inside My Mind` personal project (`personal_projects[P5/P6]`) when that
project overlaps the job's stack. The workflow field describes how the
candidate actually works with AI day to day; the project is a shipped
artifact — the two are complementary evidence, not a substitute for each
other. Never invent a tool/agent name beyond what's literally in that field.

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

The verbs above are listed in dictionary form; conjugate them in the first
person in the CV itself (Liderei, Defini, Garanti, Implementei, Desenvolvi,
Colaborei) — see "Experience Bullets" below.

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

- **Always first person, never third person.** The candidate is the one
  speaking: "Migrei a produção para AWS", "Implementei o backend",
  "Construí componentes" — never "Migrou", "Implementou", "Construiu". A
  third-person bullet reads like someone else describing the candidate,
  which is not what a CV is. This applies to every narrative line in the
  document, not just the experience bullets: the Resumo Profissional and the
  project descriptions follow the same rule. In English CVs the verb is the
  bare past tense with the subject dropped, as is standard there ("Migrated
  production to AWS"), which is already first person — the failure mode to
  watch for is Portuguese third-person conjugation.
- **No em dashes (travessoes) anywhere in the document.** Use a comma, a
  colon, a period or parentheses instead. This covers prose dashes in the
  summary and bullets, the `---` separator between a project name and its
  link, and any em dash carried over from a name in
  `profile/candidate.yaml` (e.g. "Inside My Mind — API" is rendered
  "Inside My Mind: API"; changing a separator is formatting, not editing the
  fact). En dashes in date ranges ("Nov 2021 – Fev 2026") are date
  formatting, not prose dashes, and stay.
- Project descriptions are bullets too, not noun phrases — "Construí a API
  em Fastify" rather than "API em Fastify". A noun phrase hides who did the
  work.
- 4 to 6 bullets per experience, starting with the most relevant to the job.
- Vary the verb — never repeat the same verb in consecutive bullets.
- Base bullets on `professional_experience[].responsibilities`, and weave in
  named systems from `professional_experience[].projects[]` where relevant
  to the job's stack (the real project/client name, e.g. "Celcoin (BaaS)",
  "FHEMIG", "SES-RS") — don't invent a responsibility or project detail that
  isn't listed there, but don't flatten a bullet into only the generic
  responsibility line either; a named system grounds the claim as evidence
  instead of a skills list restated in prose.
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
- If you redefine `\section` in a compact preamble instead of using the
  template, the definition MUST start with `\par` (e.g.
  `\renewcommand{\section}[1]{\par\vspace{4pt}...}`). Without it the heading
  glues onto the previous paragraph and every section runs inline.

## CV Language

Default: bilingual section headers (Portuguese / English), body in
Portuguese — matches the base template.

If the job posting's own description body is written in English (not just
an English job title on an otherwise Portuguese posting — check the actual
body text), generate the CV fully in English instead: English-only section
headers, translated summary/skills/bullets/project descriptions. Education
and Languages stay factually locked (same institutions, dates, levels) but
their labels/descriptions are translated too, for consistency with an
all-English document — translating for the target audience isn't the kind
of paraphrasing the lock rule guards against; inventing or softening a fact
is. Institution proper names are never translated.
Soft skills stay bilingual per profile, but lead with the CV's primary
language (English first, Portuguese in parentheses, when the CV is in
English).

## Mandatory Checklist Before Delivering

1. No invented data — every bullet/project/skill traceable to
   `profile/candidate.yaml`.
1.5. Every narrative line in the first person, with no third-person verb
   ("Desenvolveu", "Migrou", "Implementou") anywhere in the summary,
   experience bullets or project descriptions, and zero em dashes in the
   compiled PDF (`pdftotext <pdf> - | grep -c "—"` must print 0).
2. Institution/project/technology names spelled exactly as in the profile
   (check for typos).
3. Repository links as real hyperlinks, only for items with `link` filled
   in the profile.
4. Education and Languages identical to the profile, no paraphrasing.
5. Document fits on 1 A4 page.
6. Email and phone appear as literal text in the final PDF (not as an icon
   glyph — verified in `ats-verification.md`).
