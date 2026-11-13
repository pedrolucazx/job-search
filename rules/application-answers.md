# application-answers.md — Answering application forms

Idea from career-ops' application-answers: the same questions come back on
almost every form (salary, work model, start date, years per stack, English),
and answering them fresh each time produces inconsistent answers that cost
processes. A pretension of R$ 4.000 PJ on one form, a different number on the
next, "1 year of Java" on a Gupy eliminatory question while the profile says
4 — each one a self-inflicted rejection.

## Rule

1. **Facts come from `profile/candidate.yaml → application_answers`**, copied
   verbatim (trim only to fit a character limit, never change the number or
   the meaning). Years per stack come from `years_by_stack`; a stack not
   listed there is answered from `skills.<category>[].years`.
2. **Nothing is invented.** A question the profile can't answer (notice
   period, a specific domain like capital markets or Renda Fixa) is answered
   honestly as "não tenho experiência com X" — never stretched — or, if it is
   a preference/fact about the candidate, asked to the candidate first.
3. **Eliminatory questions are answered with the truth from the profile**, even
   when the truth eliminates. Rejected for a real gap is better than hired on
   a claim the technical round exposes.
4. **Open questions** ("why this company", "describe your experience with X")
   are written per job from `professional_experience` and the JD, first person,
   no em dashes, within the field's character limit (count it).
5. **Save what was sent**: every form answered goes to
   `documents/applications/<slug>/form-answers.md` (question, answer), so a
   later interview can be prepared against exactly what the candidate claimed.

## Changing an answer

Edit `application_answers` in the profile, not the form. A new number there
changes every future form at once, which is the point.
