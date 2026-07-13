#!/usr/bin/env python3
"""check_roteiro.py — mechanical structural check for /interview-prep output.

Validates a generated roteiro.md against the template contract defined in
rules/interview-roteiro.md, and cross-checks its gap coverage against the
job's metadata.json. Deterministic string/regex checks only — no LLM tokens
spent, same philosophy as scripts/compile-all.sh's ATS check (see
rules/README.md -> "Robustness for free/weaker models").

This does NOT verify tone, honesty, or translation quality (that needs
human/LLM judgment) — only that the required structure is present and that
every identified gap is at least mentioned in the compatibility analysis.

Usage:
  python3 scripts/check_roteiro.py documents/applications/<company>_<role>/
"""
import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "## 1. Roteiro PT-BR",
    "## 2. Roteiro EN",
    "## 3. Pontos-chave",
    "## 4. Perguntas",
    "## 5. Checklist",
    "## 6. Análise crítica",
]

REQUIRED_SUBHEADINGS_SECTION_6 = [
    "Requisitos obrigatórios atendidos",
    "Diferenciais atendidos",
    "Atende parcialmente",
    "Não atende",
    "Veredicto honesto",
]

MIN_RECRUITER_QUESTIONS = 4
MIN_CHECKLIST_ITEMS = 8

# An unfilled ALL-CAPS bracket placeholder left over from the template (e.g.
# "[EMPRESA]", "[PONTO 1]") — deliberately does NOT match a real markdown
# checkbox ("- [ ]" / "- [x]"), which is lowercase/empty inside the brackets.
PLACEHOLDER_RE = re.compile(r"\[[A-ZÀ-Ú][A-ZÀ-Ú0-9\s/\-]*\]")


def check(roteiro_text: str, metadata: dict) -> list[str]:
    errors = []

    if not roteiro_text.lstrip().startswith("# Roteiro de Apresentação"):
        errors.append("missing H1 title '# Roteiro de Apresentação — ...'")

    last_pos = -1
    for section in REQUIRED_SECTIONS:
        pos = roteiro_text.find(section)
        if pos == -1:
            errors.append(f"missing required section: {section!r}")
        elif pos < last_pos:
            errors.append(f"section out of order: {section!r} appears before an earlier section")
        else:
            last_pos = pos

    placeholders = PLACEHOLDER_RE.findall(roteiro_text)
    if placeholders:
        errors.append(f"unfilled template placeholder(s) left in output: {placeholders}")

    section_4_start = roteiro_text.find("## 4. Perguntas")
    section_5_start = roteiro_text.find("## 5. Checklist")
    if section_4_start != -1 and section_5_start != -1:
        section_4_text = roteiro_text[section_4_start:section_5_start]
        n_questions = len(re.findall(r"^-\s+", section_4_text, re.MULTILINE))
        if n_questions < MIN_RECRUITER_QUESTIONS:
            errors.append(
                f"only {n_questions} recruiter question(s) found, need >= {MIN_RECRUITER_QUESTIONS}"
            )

    section_6_start = roteiro_text.find("## 6. Análise crítica")
    if section_5_start != -1 and section_6_start != -1:
        section_5_text = roteiro_text[section_5_start:section_6_start]
        n_checklist = len(re.findall(r"^-\s+\[ \]", section_5_text, re.MULTILINE))
        if n_checklist < MIN_CHECKLIST_ITEMS:
            errors.append(
                f"only {n_checklist} checklist item(s) found, need >= {MIN_CHECKLIST_ITEMS}"
            )

    section_6_text = roteiro_text[section_6_start:] if section_6_start != -1 else ""
    for subheading in REQUIRED_SUBHEADINGS_SECTION_6:
        if subheading not in section_6_text:
            errors.append(f"section 6 is missing required subheading: {subheading!r}")

    for gap in metadata.get("gaps", []):
        skill = gap.get("skill", "")
        if skill and skill.lower() not in section_6_text.lower():
            errors.append(
                f"gap {skill!r} (status={gap.get('status')}) from metadata.json is not "
                "mentioned anywhere in section 6 — every non-full gap must be addressed honestly"
            )

    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", help="documents/applications/<company>_<role>/ directory")
    args = parser.parse_args()

    folder = Path(args.folder)
    roteiro_path = folder / "roteiro.md"
    metadata_path = folder / "metadata.json"

    if not roteiro_path.exists():
        print(f"ERROR: {roteiro_path} does not exist — run /interview-prep first.", file=sys.stderr)
        sys.exit(1)
    if not metadata_path.exists():
        print(f"ERROR: {metadata_path} does not exist.", file=sys.stderr)
        sys.exit(1)

    roteiro_text = roteiro_path.read_text(encoding="utf-8")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    errors = check(roteiro_text, metadata)
    if errors:
        print(f"❌ {len(errors)} problem(s) in {roteiro_path}:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"✅ {roteiro_path} passes the structural check ({len(metadata.get('gaps', []))} gap(s) all addressed).")


if __name__ == "__main__":
    main()
