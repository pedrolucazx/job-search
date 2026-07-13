# ats-verification.md — ATS Verification (generic)

Describes what the compilation step (`workflows/compile.md`) does. It's
mechanical — doesn't depend on LLM judgment, runs via script/shell on any
agent.

## Compilation Pipeline

1. `pdflatex -interaction=nonstopmode` on the generated `.tex`.
2. Check page count: exactly 1 A4 page. Anything other than 1 = failure,
   don't archive — treat like a compilation error.
3. `pdftotext -layout` on the PDF → extract the text layer.
4. Check parseability:
   - Email and phone (`profile/candidate.yaml → personal.email/phone`)
     appear as literal text, not as an icon glyph.
   - No `(cid:*)` or replacement characters in the extracted text.
   - Correct reading order (no two-column contamination).
5. Keyword coverage: compare the job's skills/stack (status `full`/`partial`)
   against the text layer — they should appear. Skills marked `absent` in
   the gap table **must not appear in the CV** — if they do, that's a sign
   of invented data; block and fix before archiving.
6. Compilation error: report the log, try one obvious fix (unescaped
   character, overfull hbox) and recompile once; if it fails again, mark as
   an error in the report and don't proceed for that job.

## Synonym False Positive

If the ATS check flags "skill missing" but the CV used a real synonym (e.g.
the job/JSON says "CI/CD" but the CV wrote "GitHub Actions"), that's not
blocking — use judgment before halting compilation over this. But "absent
gap appears in the CV" is **always** blocking.
