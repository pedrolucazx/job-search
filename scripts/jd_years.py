#!/usr/bin/env python3
"""jd_years.py — how many years of experience does this job description ask for?

From career-ops' jd-years.mjs: titles don't say it, the body does, and plain
rules read it with no LLM. It matters most on Gupy, where an eliminatory
question on time of experience rejects on the spot and the JD is the only
warning (Deliver IT 2026-10-01: rejected for asking 5+ years; DB 2026-09-01:
"há quanto tempo atua com Java?").

A number only counts when "experiência"/"experience" is next to it, so "20
anos de mercado" or "plano de 5 anos" never become a requirement, and not when
it describes the company ("empresa com 10 anos de experiência no mercado") or
is an upper bound ("até 5 anos"). For a range ("3 a 5 anos", "entre 3 e 5")
the lower end is the requirement. A requirement in a "diferencial/desejável"
sentence is soft: it is reported but never makes the verdict "above". The
verdict compares the highest hard requirement with the candidate's years (the
largest `years` among profile skills, i.e. total professional time).

Usage:
  python3 scripts/jd_years.py jd.txt            # or - for stdin
  python3 scripts/jd_years.py jd.txt --candidate-years 4
Prints {"required": N|null, "verdict": "within|above|unknown", "evidence": [...]}.
Exit 0 always; the caller decides what "above" means for the source.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORDS = {"um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "três": 3, "quatro": 4, "cinco": 5,
         "seis": 6, "sete": 7, "oito": 8, "dez": 10, "one": 1, "two": 2, "three": 3, "four": 4,
         "five": 5, "six": 6, "seven": 7, "eight": 8, "ten": 10}
NUM = r"(\d{1,2}|" + "|".join(WORDS) + r")"
YEARS = r"(?:anos?|years?|yrs?)"
EXPERIENCE = r"(?:experi[eê]ncia|experience|atua[cç][aã]o|working)"
RANGE = r"(?:\s*(?:a|à|-|–|e|to|ou)\s*" + NUM + r")?"
PATTERNS = [
    # "5+ anos de experiência", "3 a 5 anos de experiência", "5 years of experience"
    re.compile(NUM + r"\s*\+?" + RANGE + r"\s*" + YEARS +
               r"\s*(?:\+\s*)?(?:de|of|em|in|com|with)?\s*(?:\w+\s+){0,3}?" + EXPERIENCE, re.I),
    # "experiência de pelo menos 5 anos", "experiência entre 3 e 5 anos", "mínimo de 4 anos de atuação"
    re.compile(EXPERIENCE + r"[^.;\n]{0,40}?" + NUM + r"\s*\+?" + RANGE + r"\s*" + YEARS, re.I),
]
UPPER_BOUND = re.compile(r"(?:at[eé]|up to|no m[aá]ximo|at most)\s*$", re.I)
COMPANY_CONTEXT = re.compile(r"\b(?:empresa|somos|companhia|company|fundad[ao]|founded|no mercado|"
                             r"in the market|no brasil|in brazil|de mercado|h[aá]\s+\d+\s+anos)\b", re.I)
SOFT = re.compile(r"diferencial|desej[aá]vel|nice to have|\bplus\b|preferencial|preferred|bonus", re.I)


def _value(token):
    token = token.lower()
    return int(token) if token.isdigit() else WORDS.get(token)


def _sentence(text, start, end):
    left = max(text.rfind(".", 0, start), text.rfind("\n", 0, start), text.rfind(";", 0, start)) + 1
    right = min([i for i in (text.find(".", end), text.find("\n", end), text.find(";", end)) if i != -1] or [len(text)])
    return text[left:right]


def find_requirements(text):
    """[(years, phrase, soft)] for every experience requirement in the text."""
    text = text or ""
    found = []
    for pattern in PATTERNS:
        for match in pattern.finditer(text):
            numbers = [_value(g) for g in match.groups() if g]
            if not numbers or not 0 < numbers[0] <= 15:
                continue
            if UPPER_BOUND.search(text[max(0, match.start() - 12):match.start()]) or \
               UPPER_BOUND.search(text[match.start():match.start() + match.group(0).find(match.group(1))]):
                continue  # "até 5 anos" is a cap, not a requirement
            sentence = _sentence(text, match.start(), match.end())
            if COMPANY_CONTEXT.search(sentence) and not re.search(r"\bvoc[eê]\b|\byou\b|candidat", sentence, re.I):
                continue  # the company's age, not the candidate's
            found.append((numbers[0], " ".join(match.group(0).split()), bool(SOFT.search(sentence))))
    return found


def required_years(text):
    """(highest hard minimum requirement or None, the phrases it came from)."""
    hard = [(n, phrase) for n, phrase, soft in find_requirements(text) if not soft]
    if not hard:
        return None, []
    top = max(n for n, _ in hard)
    return top, sorted({phrase for n, phrase in hard if n == top})


def candidate_years(profile=ROOT / "profile" / "candidate.yaml"):
    text = Path(profile).read_text(encoding="utf-8")
    years = [int(y) for y in re.findall(r"^\s*years:\s*(\d+)", text, re.M)]
    return max(years) if years else None


def verdict(text, candidate):
    need, evidence = required_years(text)
    soft = sorted({n for n, _, is_soft in find_requirements(text) if is_soft})
    base = {"required": need, "candidate": candidate, "soft_required": soft, "evidence": evidence}
    if need is None or candidate is None:
        return {**base, "verdict": "unknown"}
    return {**base, "verdict": "above" if need > candidate else "within"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("jd", help="file with the job description, or - for stdin")
    ap.add_argument("--candidate-years", type=int, help="default: largest skills[].years in the profile")
    args = ap.parse_args(argv)
    text = sys.stdin.read() if args.jd == "-" else Path(args.jd).read_text(encoding="utf-8")
    years = args.candidate_years if args.candidate_years is not None else candidate_years()
    print(json.dumps(verdict(text, years), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
