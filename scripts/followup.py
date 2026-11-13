#!/usr/bin/env python3
"""followup.py — which applications deserve a follow-up, and which went cold.

Cadence ported from career-ops' followup-cadence.mjs: first follow-up 7 days
after applying, at most 2, a week apart, then the application is cold. Also
from there: a follow-up only makes sense where there is a human to write to
(their "retire" rule), and for us that means an application sent by e-mail.
An ATS/LinkedIn application with no contact just ages until it goes cold.

Reads the Notion tracker (same NOTION_TOKEN as analyze_outcomes.py). Read-only
unless --apply, which sets Status "Sumiu" on the cold ones in Notion.

Usage:
  python3 scripts/followup.py                  # list follow-ups due + cold applications
  python3 scripts/followup.py --cold-days 45   # wait longer before calling it cold
  python3 scripts/followup.py --apply          # also mark the cold ones as Sumiu in Notion
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import analyze_outcomes as ao
from application_id import find
from outcome import normalize, parse

FIRST_FOLLOWUP_DAYS = 7     # career-ops applied_first
COLD_DAYS = 30              # ~career-ops' 2 follow-ups a week apart, plus slack for slow ATSs
# We don't log follow-ups already sent (career-ops keeps a follow-ups.md), so
# the list says how old the application is, not which follow-up number is due.
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
NO_REPLY = re.compile(r"^(?:no-?reply|noreply|do-?not-?reply)@", re.I)


def contact(row, applications_dir=None):
    """The e-mail the application went to, or None (no human to follow up with)."""
    if row.get("link", "").startswith("mailto:"):
        return row["link"][len("mailto:"):].split("?")[0]
    folder = find(row["empresa"], row["cargo"], applications_dir)
    if folder:
        for name in ("email.txt", "metadata.json"):
            path = folder / name
            if path.exists():
                match = re.search(r"(?:Para:|mailto:)\s*(" + EMAIL.pattern + ")", path.read_text(encoding="utf-8"))
                if match:
                    return match.group(1)
    for match in EMAIL.finditer(row.get("feedback") or ""):
        if not NO_REPLY.match(match.group(0)):
            return match.group(0)
    return None


def reached_a_stage(row, applications_dir=None):
    """Notion still says Aplicado, but the local outcome.md has an interview stage ticked."""
    folder = find(row["empresa"], row["cargo"], applications_dir)
    outcome_md = folder / "outcome.md" if folder else None
    return bool(outcome_md and outcome_md.exists() and parse(outcome_md.read_text(encoding="utf-8"))["furthest"])


def plan(rows, today, cold_days=COLD_DAYS, applications_dir=None):
    due, cold = [], []
    for row in rows:
        if normalize(row["status"]) != "applied" or not row.get("data"):
            continue
        try:
            age = (today - date.fromisoformat(row["data"][:10])).days
        except ValueError:
            continue
        if reached_a_stage(row, applications_dir):
            continue  # stale in Notion, not cold
        email = contact(row, applications_dir)
        item = {**row, "age": age, "email": email}
        if age >= cold_days:
            cold.append(item)
        elif email and age >= FIRST_FOLLOWUP_DAYS:
            due.append(item)
    key = lambda r: -r["age"]
    return sorted(due, key=key), sorted(cold, key=key)


def mark_ghosted(token, page_id):
    req = urllib.request.Request(
        f"https://api.notion.com/v1/pages/{page_id}", method="PATCH",
        data=json.dumps({"properties": {"Status": {"select": {"name": "Sumiu"}}}}).encode(),
        headers={"Authorization": f"Bearer {token}", "Notion-Version": ao.NOTION_VERSION,
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30):
        pass


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cold-days", type=int, default=COLD_DAYS)
    ap.add_argument("--apply", action="store_true", help="set Status=Sumiu in Notion on cold rows")
    ap.add_argument("--yes", action="store_true", help="required with --apply: confirms the full list printed")
    ap.add_argument("--all", action="store_true", help="print every cold row, not just the first 15")
    ap.add_argument("--from-json", help="read simplified rows from a file (offline)")
    args = ap.parse_args(argv)

    token = ao.load_token()
    if args.from_json:
        rows = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
    else:
        if not token:
            print("NOTION_TOKEN não encontrado (ver analyze_outcomes.py).", file=sys.stderr)
            return 1
        try:
            rows = [ao.simplify(p) for p in ao.fetch_pages(token, ao.data_source_id())]
        except (urllib.error.URLError, TimeoutError, KeyError) as exc:
            print(f"Falha ao ler o Notion: {exc}", file=sys.stderr)
            return 1

    due, cold = plan(rows, date.today(), args.cold_days)
    print(f"Follow-up por e-mail ({len(due)}):")
    for r in due:
        print(f"  {r['age']:>3}d  {r['empresa']} — {r['cargo']}  <{r['email']}>")
    print(f"\nSem resposta há {args.cold_days}+ dias ({len(cold)}), candidatas a 'Sumiu':")
    shown = cold if (args.all or args.apply) else cold[:15]
    for r in shown:
        print(f"  {r['age']:>3}d  {r['empresa']} — {r['cargo']}")
    if len(cold) > len(shown):
        print(f"  ... e mais {len(cold) - len(shown)} (--all para ver todas)")

    if args.apply and cold:
        if not token or args.from_json:
            print("--apply precisa do Notion (sem --from-json).", file=sys.stderr)
            return 1
        if not args.yes:
            print(f"\n--apply marcaria as {len(cold)} acima como Sumiu. Revise a lista e rode de novo com --apply --yes.")
            return 0
        failed = 0
        for r in cold:
            try:
                mark_ghosted(token, r["id"])
            except (urllib.error.URLError, TimeoutError) as exc:
                failed += 1
                print(f"  falhou: {r['empresa']} ({exc})", file=sys.stderr)
        print(f"\n{len(cold) - failed} marcadas como Sumiu no Notion" + (f", {failed} falharam." if failed else "."))
        return 1 if failed else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
