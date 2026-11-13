#!/usr/bin/env python3
"""cv_voice.py — the CV speaks in the first person and has no em dashes.

Both are rules in rules/cv-rules.md that were broken before they were rules,
so they are checked on the compiled text, the way career-ops' cv-voice does
for its own style rules. Third person shows up as a Portuguese past-tense verb
opening a bullet or a sentence ("Desenvolveu", "Implementou", "Construiu");
the English CV drops the subject ("Built", "Migrated"), which is already first
person, so it is not checked.

Usage:
  python3 scripts/cv_voice.py <cv.pdf | cv.txt>
Exit 1 and lists the offending fragments.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

EM_DASH = "—"
# Opening a bullet or a sentence: "• Desenvolveu ...", ". Implementou ...".
OPENING = re.compile(r"(?:^|[•●▪\-*]\s+|[.;:]\s+)([A-ZÁÉÍÓÚÂÊÔÃÕ][a-zà-ú]{3,}(?:ou|eu|iu))\b", re.M)
# Past tense, 3rd person singular, that are not verbs or are fine at a sentence start.
NOT_VERBS = {"Meu", "Seu", "Teu", "Ceu", "Museu", "Europeu", "Pneu", "Judeu", "Plebeu", "Liceu",
             "Sou", "Estou", "Vou", "Dou", "Ou", "Eu", "Nou"}


def problems(text):
    found = []
    dashes = text.count(EM_DASH)
    if dashes:
        line = next(l for l in text.splitlines() if EM_DASH in l)
        found.append(f"{dashes} travessão(ões), ex.: \"{' '.join(line.split())[:70]}\"")
    for verb in sorted({m.group(1) for m in OPENING.finditer(text)} - NOT_VERBS):
        found.append(f"terceira pessoa: \"{verb}\" (use a 1ª pessoa, ex.: \"{verb[:-2]}ei\")" if verb.endswith("ou")
                     else f"terceira pessoa: \"{verb}\"")
    return found


def read_cv(path):
    if path.suffix == ".pdf":
        return subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True,
                              text=True, check=True).stdout
    return path.read_text(encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cv")
    args = ap.parse_args(argv)
    found = problems(read_cv(Path(args.cv)))
    if found:
        print("voz do CV: " + "; ".join(found))
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
