#!/usr/bin/env python3
"""track_append.py — tracker CSV (backend zero-dependência).

Usado por workflows/confirm.md quando profile.tracker.backend == "csv".
Stdlib apenas (módulo csv) — nenhuma dependência externa, roda em qualquer
agente com Python 3 instalado.

Uso:
  python3 scripts/track_append.py \
    --path documents/applications.csv \
    --empresa "Empresa X" --cargo "Backend Pleno" --url "https://..." \
    --status "Aplicado" --data "2026-07-27" --fonte "LinkedIn" \
    --nivel "Pleno" --stack "Node.js,TypeScript" --gaps "AWS,Kafka" \
    --versao-cv "main_empresa_x.tex" --feedback "notas dos gaps"
"""
import argparse
import csv
import sys
from pathlib import Path

FIELDS = [
    "data", "empresa", "cargo", "url", "status", "fonte", "nivel",
    "stack", "gaps", "versao_cv", "feedback",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    parser.add_argument("--empresa", required=True)
    parser.add_argument("--cargo", required=True)
    parser.add_argument("--url", default="")
    parser.add_argument("--status", default="Aplicado")
    parser.add_argument("--data", required=True)
    parser.add_argument("--fonte", default="")
    parser.add_argument("--nivel", default="")
    parser.add_argument("--stack", default="")
    parser.add_argument("--gaps", default="")
    parser.add_argument("--versao-cv", dest="versao_cv", default="")
    parser.add_argument("--feedback", default="")
    parser.add_argument("--check-duplicate", action="store_true",
                         help="só verifica se a empresa já existe (sem escrever), exit code 1 se já existe")
    args = parser.parse_args()

    path = Path(args.path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if args.check_duplicate:
        if not path.exists():
            sys.exit(0)
        with open(path, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                if row.get("empresa", "").strip().lower() == args.empresa.strip().lower():
                    print(f"já existe: {row}")
                    sys.exit(1)
        sys.exit(0)

    is_new = not path.exists()
    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerow({
            "data": args.data,
            "empresa": args.empresa,
            "cargo": args.cargo,
            "url": args.url,
            "status": args.status,
            "fonte": args.fonte,
            "nivel": args.nivel,
            "stack": args.stack,
            "gaps": args.gaps,
            "versao_cv": args.versao_cv,
            "feedback": args.feedback,
        })
    print(f"✅ registrado em {path}: {args.empresa} — {args.cargo} ({args.status})")


if __name__ == "__main__":
    main()
