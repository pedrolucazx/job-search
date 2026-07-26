#!/usr/bin/env python3
"""track_append.py — CSV tracker (zero-dependency backend).

Used by workflows/confirm.md when profile.tracker.backend == "csv".
Stdlib only (csv module) — no external dependency, runs on any agent with
Python 3 installed.

Note: the CLI flags and CSV columns keep their original field names
(--empresa, --cargo, --fonte, --nivel, --versao-cv...) to match the schema
used across daily/*.json and workflows/confirm.md — see
profile/candidate.schema.yaml for what each one means.

Usage:
  python3 scripts/track_append.py \
    --path documents/applications.csv \
    --from documents/applications/company_x_backend_pleno

  python3 scripts/track_append.py --check-duplicate \
    --path documents/applications.csv \
    --from documents/applications/company_x_backend_pleno

  python3 scripts/track_append.py \
    --path documents/applications.csv \
    --empresa "Company X" --cargo "Mid-level Backend" --url "https://..." \
    --status "Applied" --data "2026-07-27" --fonte "LinkedIn" \
    --nivel "Mid-level" --stack "Node.js,TypeScript" --gaps "AWS,Kafka" \
    --versao-cv "main_company_x.tex" --feedback "gap notes"

Any explicit flag overrides the value derived from --from.
"""
import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

FIELDS = [
    "data", "empresa", "cargo", "url", "status", "fonte", "nivel",
    "stack", "gaps", "versao_cv", "feedback",
]


def derive(folder):
    metadata = Path(folder) / "metadata.json"
    try:
        record = json.loads(metadata.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read {metadata}: {exc}", file=sys.stderr)
        sys.exit(1)
    open_gaps = [g for g in (record.get("gaps") or []) if g.get("status") != "full"]
    return {
        "data": date.today().isoformat(),
        "empresa": record.get("empresa") or "",
        "cargo": record.get("cargo") or "",
        "url": record.get("url") or "",
        "status": "Applied",
        "fonte": record.get("fonte") or "",
        "nivel": record.get("nivel") or "",
        "stack": ",".join(record.get("stack") or []),
        "gaps": ",".join(g.get("skill", "") for g in open_gaps),
        "versao_cv": record.get("cv_tex") or "",
        "feedback": "; ".join(f'{g.get("skill", "")}: {g.get("nota", "")}' for g in open_gaps),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    parser.add_argument("--from", dest="from_folder",
                        help="folder holding a metadata.json to derive every column from")
    parser.add_argument("--empresa")
    parser.add_argument("--cargo")
    parser.add_argument("--url")
    parser.add_argument("--status")
    parser.add_argument("--data")
    parser.add_argument("--fonte")
    parser.add_argument("--nivel")
    parser.add_argument("--stack")
    parser.add_argument("--gaps")
    parser.add_argument("--versao-cv", dest="versao_cv")
    parser.add_argument("--feedback")
    parser.add_argument("--check-duplicate", action="store_true",
                         help="only check whether company+cargo already exists (no write), exit code 1 if it does")
    args = parser.parse_args()

    if not args.from_folder and any(getattr(args, f) is None for f in ("empresa", "cargo", "data")):
        parser.error("pass --from FOLDER, or --empresa, --cargo and --data")

    derived = derive(args.from_folder) if args.from_folder else {"status": "Applied"}
    row = {
        f: getattr(args, f) if getattr(args, f) is not None else derived.get(f, "")
        for f in FIELDS
    }

    path = Path(args.path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if args.check_duplicate:
        if not path.exists():
            sys.exit(0)
        # Match on company AND role, never company alone: two different
        # roles at the same employer are two different applications, not a
        # duplicate (see workflows/daily.md's dedup step for why matching by
        # company alone would silently hide a genuinely different job).
        with open(path, encoding="utf-8", newline="") as f:
            for existing in csv.DictReader(f):
                same_empresa = existing.get("empresa", "").strip().lower() == row["empresa"].strip().lower()
                same_cargo = existing.get("cargo", "").strip().lower() == row["cargo"].strip().lower()
                if same_empresa and same_cargo:
                    print(f"already exists: {existing}")
                    sys.exit(1)
        sys.exit(0)

    is_new = not path.exists()
    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerow(row)
    print(f"✅ registered in {path}: {row['empresa']} — {row['cargo']} ({row['status']})")


if __name__ == "__main__":
    main()
