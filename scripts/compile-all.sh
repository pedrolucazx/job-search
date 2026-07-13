#!/bin/bash
# compile-all.sh — Batch-compiles today's .tex files (mechanical, no judgment)
# Usage: ./scripts/compile-all.sh [date]
# If date is omitted, uses today's date
# Reads the "cv_tex" field from each daily/<date>/<company>.json — never guesses the filename.
# ATS check happens here via grep (mechanical, no LLM tokens spent): confirms
# literal email/phone, keyword coverage for full+partial stack/gaps, and
# absence of absent-gap keywords (a sign of invented data in the CV). The
# extracted text is deleted at the end — only the PASS/FAIL result matters to the caller.

set -euo pipefail

DATA_DIR="${1:-$(date +%Y-%m-%d)}"
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CV_DIR="$BASE_DIR/documents/cv"

# Email/phone come from the active profile, never hardcoded here (see AGENTS.md)
EMAIL="$(python3 "$BASE_DIR/scripts/validate_profile.py" --get personal.email)"
PHONE="$(python3 "$BASE_DIR/scripts/validate_profile.py" --get personal.phone)"
DAILY_DIR="$BASE_DIR/daily/$DATA_DIR"
COMPILED=0
ERRORS=0

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
        grep -qi -- "$skill" "$txt_file" && ATS_FAILS+=("absent gap APPEARS in the CV (invented data?): $skill")
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
echo "  Compiled: $COMPILED | Errors: $ERRORS"
echo "══════════════════════════════════════════"
