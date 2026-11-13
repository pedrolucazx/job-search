#!/usr/bin/env python3
"""fact_check.py — every number in the compiled CV must exist in the profile.

Absolute rule #1 (never invent data) as code instead of only as a prompt, the
idea behind career-ops' cv-payload-facts gate. Numbers are where an invented
fact hides best: "5 years", "90% coverage", "12 developers". Reads the PDF text
(what the recruiter sees) and checks each quantity, a number plus its unit
(years, %, developers, lines, agents...), against the quantities written in
profile/candidate.yaml, with Portuguese and English units folded together.
A bare number is not checked: the profile is full of versions and dates, so
"5" alone always matches something and would prove nothing.

Usage:
  python3 scripts/fact_check.py <cv.pdf | cv.txt> [--profile profile/candidate.yaml]
Exit 1 and lists the numbers that aren't in the profile.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# unit as written (PT or EN) -> canonical unit
UNITS = {
    "%": "%", "anos": "years", "ano": "years", "years": "years", "year": "years",
    # Team size: "equipe de 4 devs" and "time de 4 pessoas" are the same fact.
    "meses": "months", "months": "months", "devs": "people", "dev": "people",
    "desenvolvedores": "people", "developers": "people", "pessoas": "people",
    "people": "people", "linhas": "lines", "lines": "lines", "agentes": "agents",
    "agents": "agents", "commits": "commits", "projetos": "projects", "projects": "projects",
    "clientes": "clients", "clients": "clients", "teams": "teams",
    "equipes": "teams", "usuarios": "users", "usuários": "users", "users": "users", "h": "hours",
    "horas": "hours", "hours": "hours", "engenheiros": "people", "engineers": "people",
}
UNIT_RE = "|".join(sorted((re.escape(u) for u in UNITS), key=len, reverse=True))
# "4+ years", "80%+", "1,000 lines", "~1000 linhas", "1,5 anos", "2 to 3 agents" (the 3).
# Known misses, by design: numbers in words ("four years") and a word between the
# number and the unit ("3 AI agents") — the corpus doesn't write them that way.
QUANTITY = re.compile(r"(?<![\d.,])(\d{1,3}(?:[.,]\d{3})+(?!\d)|\d+(?:[.,]\d+)?)\s*\+?\s*(?:de\s+|of\s+)?("
                      + UNIT_RE + r")(?![a-zà-ú])", re.I)
# YAML form in the profile: "years: 4" under a skill.
YAML_YEARS = re.compile(r"\byears:\s*(\d+)")


def _canonical(number):
    """'1,000' / '1.000' -> '1000' (thousands); '1,5' / '1.5' -> '1.5' (decimal)."""
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", number):
        return re.sub(r"[.,]", "", number)
    return number.replace(",", ".")


def quantities(text):
    found = {(_canonical(n), UNITS[u.lower()]) for n, u in QUANTITY.findall(text)}
    found |= {(n, "years") for n in YAML_YEARS.findall(text)}
    return found


def strip_comments(yaml_text):
    """YAML comments are notes about jobs ("mais de 5 anos" a recruiter asked for), not facts."""
    return "\n".join(re.sub(r"(^|\s)#.*$", "", line) for line in yaml_text.splitlines())


def unsupported(cv_text, profile_text):
    missing = quantities(cv_text) - quantities(strip_comments(profile_text))
    return sorted(f"{n} {u}" for n, u in missing)


def read_cv(path):
    if path.suffix == ".pdf":
        return subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True,
                              text=True, check=True).stdout
    return path.read_text(encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cv")
    ap.add_argument("--profile", default=str(ROOT / "profile" / "candidate.yaml"))
    args = ap.parse_args(argv)
    missing = unsupported(read_cv(Path(args.cv)), Path(args.profile).read_text(encoding="utf-8"))
    if missing:
        print("numbers not found in the profile (invented?): " + ", ".join(missing))
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
