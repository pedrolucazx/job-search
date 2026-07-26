#!/bin/bash
# compile-all.sh — Batch-compiles today's .tex files AND archives them (mechanical, no judgment)
# Usage: ./scripts/compile-all.sh [date]
# If date is omitted, uses today's date
# Reads the "cv_tex" field from each daily/<date>/<company>.json — never guesses the filename.
# ATS check happens here via grep (mechanical, no LLM tokens spent): confirms
# literal email/phone, keyword coverage for full+partial stack/gaps, and
# absence of absent-gap keywords (a sign of invented data in the CV). The
# extracted text is deleted at the end — only the PASS/FAIL result matters to the caller.
#
# Archiving (move to documents/applications/<company>_<role>/, create
# outcome.md) happens here too, for any job that compiled to exactly 1 page
# and has no blocking ATS issue. This used to be a manual step for whichever
# agent ran this script — folded into the script itself because a weaker
# model reliably ran the compile step and then stopped, skipping archiving
# (see rules/README.md "Robustness for free/weaker models").

set -euo pipefail

DATA_DIR="${1:-$(date +%Y-%m-%d)}"
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CV_DIR="$BASE_DIR/documents/cv"
APPLICATIONS_DIR="$BASE_DIR/documents/applications"

# Email/phone/name come from the active profile, never hardcoded here (see AGENTS.md)
EMAIL="$(python3 "$BASE_DIR/scripts/validate_profile.py" --get personal.email)"
PHONE="$(python3 "$BASE_DIR/scripts/validate_profile.py" --get personal.phone)"
CANDIDATE="$(python3 "$BASE_DIR/scripts/validate_profile.py" --get personal.name)"
# The archived PDF is what the recruiter receives, so it carries the candidate's
# name, not the company's. The intermediate .tex/.pdf in documents/cv/ still use
# the per-application slug — they all share one directory until archiving.
CV_FILENAME="$(python3 "$BASE_DIR/scripts/application_id.py" --filename "$CANDIDATE")_CV.pdf"
DAILY_DIR="$BASE_DIR/daily/$DATA_DIR"
COMPILED=0
ERRORS=0
ARCHIVED=0
NEEDS_REVIEW=0

# One implementation of the company+role identity, shared with the agent and the
# dashboard — see scripts/application_id.py
slugify() {
  python3 "$BASE_DIR/scripts/application_id.py" "$@"
}

echo "╔══════════════════════════════════════════╗"
echo "║     Batch Compilation — $DATA_DIR"
echo "╚══════════════════════════════════════════╝"

if [ ! -d "$DAILY_DIR" ]; then
  echo "❌ No metadata found for $DATA_DIR"
  exit 1
fi

for json_file in "$DAILY_DIR"/*.json; do
  [ -f "$json_file" ] || continue

  empresa=$(basename "$json_file" .json)
  tex_rel=$(jq -r '.cv_tex' "$json_file")
  tex_file="$BASE_DIR/$tex_rel"
  pdf_file="${tex_file%.tex}.pdf"

  if [ ! -f "$tex_file" ]; then
    echo "⚠  $empresa — .tex not found at $tex_rel (cv_tex from the JSON)"
    continue
  fi

  echo ""
  echo "── $empresa ──"

  # Compile
  if pdflatex -interaction=nonstopmode -output-directory="$CV_DIR" "$tex_file" > /tmp/latex_log.txt 2>&1; then
    echo "  ✅ PDF generated: ${pdf_file}"

    # Check page count
    PAGES=$(pdfinfo "$pdf_file" 2>/dev/null | grep Pages | awk '{print $2}')
    if [ "$PAGES" = "1" ]; then
      echo "  ✅ Pages: $PAGES (1 = OK)"
    else
      echo "  ⚠  Pages: $PAGES (expected: 1)"
    fi

    # Mechanical ATS check via grep — leaves no .txt behind, only the verdict
    ATS_BLOCKED=false
    if command -v pdftotext &> /dev/null; then
      txt_file="$CV_DIR/${empresa}_ats.txt"
      pdftotext -layout "$pdf_file" "$txt_file" 2>/dev/null

      ATS_FAILS=()
      grep -qF "$EMAIL" "$txt_file" || ATS_FAILS+=("email missing/not literal")
      grep -qF "$PHONE" "$txt_file" || ATS_FAILS+=("phone missing/not literal")

      while IFS= read -r skill; do
        [ -z "$skill" ] && continue
        grep -qi -- "$skill" "$txt_file" || ATS_FAILS+=("stack missing: $skill")
      done < <(jq -r '.stack[]?' "$json_file")

      while IFS= read -r skill; do
        [ -z "$skill" ] && continue
        grep -qi -- "$skill" "$txt_file" || ATS_FAILS+=("full/partial gap missing: $skill")
      done < <(jq -r '.gaps[]? | select(.status != "absent") | .skill' "$json_file")

      while IFS= read -r skill; do
        [ -z "$skill" ] && continue
        if grep -qi -- "$skill" "$txt_file"; then
          ATS_FAILS+=("absent gap APPEARS in the CV (invented data?): $skill")
          ATS_BLOCKED=true
        fi
      done < <(jq -r '.gaps[]? | select(.status == "absent") | .skill' "$json_file")

      rm -f "$txt_file"

      if [ ${#ATS_FAILS[@]} -eq 0 ]; then
        echo "  ✅ ATS check OK (email, phone, stack and gaps verified)"
      else
        echo "  ⚠  ATS check has issues:"
        printf '     - %s\n' "${ATS_FAILS[@]}"
      fi
    else
      echo "  ⚠  pdftotext not installed — skipping ATS check"
    fi

    COMPILED=$((COMPILED + 1))

    # Archive — only if exactly 1 page and no blocking ATS issue
    if [ "$PAGES" = "1" ] && [ "$ATS_BLOCKED" = false ]; then
      empresa_nome=$(jq -r '.empresa' "$json_file")
      cargo=$(jq -r '.cargo' "$json_file")
      # The slug is decided once, by apply-batch.md via application_id.py, and
      # travels in the record. Older records predate the field — recompute then.
      slug=$(jq -r '.slug // empty' "$json_file")
      [ -n "$slug" ] || slug="$(slugify "$empresa_nome" "$cargo")"
      archive_dir="$APPLICATIONS_DIR/$slug"
      mkdir -p "$archive_dir"
      mv "$pdf_file" "$archive_dir/$CV_FILENAME"
      mv "$tex_file" "$archive_dir/cv_draft.tex"
      # cv_tex pointed at documents/cv/, which the mv above just emptied
      jq --arg p "documents/applications/$slug/cv_draft.tex" --arg s "$slug" \
        '.cv_tex = $p | .slug = $s' "$json_file" > "$archive_dir/metadata.json"
      # outcome.md's format lives in scripts/outcome.py, which reads the
      # metadata.json written just above — never inline the template here again.
      # Never --force: an existing outcome.md may already carry confirm.md's
      # manual "Status: Applied" edit. The existence test lives here so that a
      # real failure below reads as a failure instead of as "already exists".
      if [ -f "$archive_dir/outcome.md" ]; then
        echo "  ⚠  outcome.md already exists — kept as-is"
      else
        python3 "$BASE_DIR/scripts/outcome.py" --write "$archive_dir" > /dev/null \
          || echo "  ❌ outcome.md NOT written (see the error above)"
      fi
      echo "  📦 Archived to documents/applications/$slug/"
      ARCHIVED=$((ARCHIVED + 1))
    else
      echo "  ⚠  Not archived — needs manual review (see issues above)"
      NEEDS_REVIEW=$((NEEDS_REVIEW + 1))
    fi
  else
    echo "  ❌ COMPILE ERROR"
    head -20 /tmp/latex_log.txt | tail -10
    ERRORS=$((ERRORS + 1))
  fi

  # Clean up build artifacts (not _ats.txt, that one stays)
  rm -f "$CV_DIR/$(basename "${tex_file%.tex}").aux" "$CV_DIR/$(basename "${tex_file%.tex}").log" "$CV_DIR/$(basename "${tex_file%.tex}").out"
done

echo ""
echo "══════════════════════════════════════════"
echo "  Compiled: $COMPILED | Archived: $ARCHIVED | Needs review: $NEEDS_REVIEW | Errors: $ERRORS"
echo "══════════════════════════════════════════"
