#!/usr/bin/env python3
"""application_id.py — canonical identity for one application.

An application is identified by company + role, never by company alone (see
workflows/daily.md's dedup step and scripts/track_append.py
--check-duplicate). This module is the only place that turns that pair into a
filesystem name, so the agent, compile-all.sh and the dashboard can't disagree
about what a given application is called.

Usage:
  python3 scripts/application_id.py "Acme Health" "AI Engineer II (Remote)"
      acme_health_ai_engineer_ii_remote
  python3 scripts/application_id.py "Acme Health"
      acme_health
  python3 scripts/application_id.py --find "Acme Health" "AI Engineer II (Remote)"
      documents/applications/acme_health_ai_engineer_ii_remote
      (prints nothing and exits 1 if no folder matches)
  python3 scripts/application_id.py --filename "Ana Souza"
      Ana_Souza
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPLICATIONS = ROOT / "documents" / "applications"


def _ascii(text):
    normalized = unicodedata.normalize("NFKD", str(text or ""))
    return normalized.encode("ascii", "ignore").decode("ascii")


def slug(*parts):
    pieces = (re.sub(r"[^a-zA-Z0-9]+", "_", _ascii(part)).strip("_").lower() for part in parts)
    return "_".join(piece for piece in pieces if piece)


def filename(text):
    return re.sub(r"[^A-Za-z0-9]+", "_", _ascii(text)).strip("_")


def find(company, role, applications_dir=None):
    base = Path(applications_dir) if applications_dir else APPLICATIONS
    exact = base / slug(company, role)
    if exact.is_dir():
        return exact

    wanted = (str(company).strip().lower(), str(role).strip().lower())
    for metadata_path in sorted(base.glob("*/metadata.json")):
        try:
            record = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        found = (str(record.get("empresa", "")).strip().lower(),
                 str(record.get("cargo", "")).strip().lower())
        if found == wanted:
            return metadata_path.parent
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description="Canonical identity for one application.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--find", action="store_true",
                      help="print the existing application folder for company+role; exit 1 if there is none")
    mode.add_argument("--filename", action="store_true",
                      help="ASCII filename form keeping capitalisation, for the delivered PDF")
    parser.add_argument("parts", nargs="+", metavar="TEXT")
    args = parser.parse_args(argv)

    if args.filename:
        print(filename(" ".join(args.parts)))
        return 0

    if args.find:
        if len(args.parts) != 2:
            parser.error("--find takes exactly two arguments: company and role")
        folder = find(args.parts[0], args.parts[1])
        if folder is None:
            return 1
        print(folder.relative_to(ROOT))
        return 0

    print(slug(*args.parts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
