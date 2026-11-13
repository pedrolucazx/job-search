#!/usr/bin/env python3
"""analyze_outcomes.py — does the fit score predict a response? Which source converts?

Reads every row of the Notion tracker (the only place where rejections are kept
up to date), joins each one to its local documents/applications/<slug>/ record
for the fit score and the interview stages reached, and prints conversion by
score band, source and month, plus the gaps that show up most among rejections.
Writes documents/funnel.json for build_dashboard.py. Stdlib only, read-only.

Usage:
  python3 scripts/analyze_outcomes.py                  # needs NOTION_TOKEN (env or .env)
  python3 scripts/analyze_outcomes.py --from-json rows.json   # offline, rows already simplified
  python3 scripts/analyze_outcomes.py --dump rows.json        # also save the fetched rows

"Sent" excludes withdrew (the candidate's own call) and unknown statuses.
"Responded" means a decision from the company: screening/technical/offer/hired,
rejected or position closed (a rejection is an answer; frozen is not).
"Advanced" is screening/technical/offer/hired in Notion, or an interview stage
ticked in the local outcome.md when Notion shows the process got an answer:
Notion only keeps the current status, so a rejection after a technical round
only counts as advanced if the stage was ticked locally.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from application_id import find
from outcome import ADVANCED, COMPANY_ANSWER, ENDED, NOT_SENT, normalize, parse

ROOT = Path(__file__).resolve().parent.parent
NOTION_VERSION = "2025-09-03"
# Fit score as the trackers write it ("Score real 71%", "Score heurístico: 67%",
# "Fit 90%"), never an ATS score.
SCORE_IN_TEXT = re.compile(r"(?<!ats )\b(?:score|fit)\b[^0-9%]{0,20}(\d{1,3})\s*%", re.I)
REQUIRED_PROPS = ("Empresa", "Cargo", "Status")
BANDS = [(80, "80+"), (70, "70-79"), (60, "60-69"), (0, "<60")]


# ---------- Notion ----------

def load_token():
    if os.environ.get("NOTION_TOKEN"):
        return os.environ["NOTION_TOKEN"]
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            key, _, value = line.partition("=")
            if key.strip() == "NOTION_TOKEN":
                return value.strip().strip('"').strip("'")
    return None


def data_source_id():
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_profile.py"),
                          "--get", "tracker.notion.data_source_id"],
                         capture_output=True, text=True, check=True)
    return out.stdout.strip()


def fetch_pages(token, source_id):
    pages, cursor = [], None
    while True:
        body = {"page_size": 100, **({"start_cursor": cursor} if cursor else {})}
        req = urllib.request.Request(
            f"https://api.notion.com/v1/data_sources/{source_id}/query",
            data=json.dumps(body).encode(), method="POST",
            headers={"Authorization": f"Bearer {token}", "Notion-Version": NOTION_VERSION,
                     "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.load(resp)
        pages += payload["results"]
        if not payload.get("has_more"):
            return pages
        cursor = payload["next_cursor"]


def _text(prop):
    if not prop:
        return ""
    kind = prop.get("type")
    if kind in ("title", "rich_text"):
        return "".join(part.get("plain_text", "") for part in prop[kind])
    if kind == "select":
        return (prop["select"] or {}).get("name", "")
    if kind == "date":
        return (prop["date"] or {}).get("start", "")
    if kind == "url":
        return prop["url"] or ""
    return ""


def simplify(page):
    """One Notion page -> the flat row the rest of this script works on."""
    props = page["properties"]
    missing = [name for name in REQUIRED_PROPS if name not in props]
    if missing:
        raise KeyError(f"propriedades ausentes no Notion: {', '.join(missing)}")
    gaps = props.get("Gaps identificados", {}).get("multi_select", [])
    return {
        "id": page.get("id", ""),
        "link": _text(props.get("Link")),
        "empresa": _text(props.get("Empresa")),
        "cargo": _text(props.get("Cargo")),
        "status": _text(props.get("Status")),
        "fonte": _text(props.get("Fonte")),
        "data": _text(props.get("Data")),
        "feedback": _text(props.get("Feedback")),
        "gaps": [g["name"] for g in gaps],
    }


# ---------- join + aggregate ----------

def enrich(row, applications_dir=None):
    """Add canonical state, score and 'advanced' from the row plus its local record."""
    state = normalize(row["status"])
    score, furthest, score_from = None, None, None
    folder = find(row["empresa"], row["cargo"], applications_dir)
    if folder:
        try:
            score = json.loads((folder / "metadata.json").read_text(encoding="utf-8")).get("score")
            score_from = "local" if score is not None else None
        except (OSError, json.JSONDecodeError):
            pass
        outcome_md = folder / "outcome.md"
        if outcome_md.exists():
            furthest = parse(outcome_md.read_text(encoding="utf-8"))["furthest"]
    if score is None:
        match = SCORE_IN_TEXT.search(row.get("feedback") or "")
        score = int(match.group(1)) if match else None
        score_from = "feedback" if match else None
    # A ticked local stage only counts once Notion shows an answer, so a fresh
    # re-application doesn't inherit the stages of an older process.
    return {**row, "state": state, "score": score, "score_from": score_from,
            "slug": folder.name if folder else None,
            "responded": state in COMPANY_ANSWER,
            "advanced": state in ADVANCED or (bool(furthest) and state in COMPANY_ANSWER | ENDED)}


def band(score):
    if score is None:
        return "sem score"
    return next(label for floor, label in BANDS if score >= floor)


def group(rows, key, order=None):
    buckets = defaultdict(list)
    for r in rows:
        buckets[key(r)].append(r)
    names = order or sorted(buckets, key=lambda k: -len(buckets[k]))
    out = []
    for name in names:
        members = buckets.get(name, [])
        if not members:
            continue
        n = len(members)
        out.append({"group": name, "sent": n,
                    "responded": sum(r["responded"] for r in members),
                    "advanced": sum(r["advanced"] for r in members),
                    "response_rate": sum(r["responded"] for r in members) / n,
                    "advance_rate": sum(r["advanced"] for r in members) / n})
    return out


def study_list(sent, top=8):
    """What to study, after career-ops' upskill.mjs: each application adds
    (100 - score) / 100 to every gap it names, so a gap that kept the fit low
    weighs more than one that showed up on a 95% match. Rows without a score
    count as 0.5."""
    weight, seen = Counter(), Counter()
    for r in sent:
        w = (100 - r["score"]) / 100 if r["score"] is not None else 0.5
        for g in r["gaps"]:
            weight[g] += w
            seen[g] += 1
    return [{"gap": g, "weight": round(w, 1), "sent": seen[g]} for g, w in weight.most_common(top)]


def analyze(raw_rows, applications_dir=None, today=None):
    rows = [enrich(r, applications_dir) for r in raw_rows]
    sent = [r for r in rows if r["state"] not in NOT_SENT | {"withdrew", "unknown"}]
    slugs = Counter(r["slug"] for r in rows if r["slug"])
    gap_sent, gap_rejected, gap_advanced = Counter(), Counter(), Counter()
    for r in sent:
        gap_sent.update(r["gaps"])
        if r["state"] == "rejected":
            gap_rejected.update(r["gaps"])
        if r["advanced"]:
            gap_advanced.update(r["gaps"])
    total = group(sent, lambda r: "total")[0] if sent else {"sent": 0, "response_rate": None, "advance_rate": None}
    return {
        "generated": (today or date.today()).isoformat(),
        "total": total,
        "by_state": dict(Counter(r["state"] for r in rows).most_common()),
        "by_score": group(sent, lambda r: band(r["score"]), [label for _, label in BANDS] + ["sem score"]),
        "by_source": group(sent, lambda r: r["fonte"] or "sem fonte"),
        "by_month": group(sent, lambda r: (r["data"] or "?")[:7], None),
        "gaps": [{"gap": g, "sent": n, "rejected": gap_rejected[g], "advanced": gap_advanced[g]}
                 for g, n in gap_sent.most_common(10)],
        "study": study_list(sent),
        "no_score": sum(1 for r in sent if r["score"] is None),
        "score_from_feedback": sum(1 for r in sent if r["score_from"] == "feedback"),
        "shared_local_record": sum(n for n in slugs.values() if n > 1),
        "unknown_status": [r["status"] for r in rows if r["state"] == "unknown"],
    }


# ---------- output ----------

def pct(x):
    return "  -" if x is None else f"{round(x * 100):3d}%"


def report(f):
    t = f["total"]
    lines = [f"Funil ({f['generated']}): {t['sent']} enviadas, resposta {pct(t['response_rate']).strip()}, "
             f"avanço {pct(t['advance_rate']).strip()}",
             "Estados: " + ", ".join(f"{k} {v}" for k, v in f["by_state"].items()), ""]
    for key, title in (("by_score", "Faixa de score"), ("by_source", "Fonte"), ("by_month", "Mês")):
        rows = sorted(f[key], key=lambda r: r["group"]) if key == "by_month" else f[key]
        lines.append(f"{title:<24} enviadas  resposta  avanço")
        lines += [f"{r['group']:<24} {r['sent']:>8}  {pct(r['response_rate']):>8}  {pct(r['advance_rate']):>6}" for r in rows]
        lines.append("")
    lines.append(f"{'Gap (tag do Notion)':<24} enviadas  rejeitadas  avançaram")
    lines += [f"{g['gap']:<24} {g['sent']:>8}  {g['rejected']:>10}  {g['advanced']:>9}" for g in f["gaps"]]
    if f.get("study"):
        lines.append("")
        lines.append(f"{'O que estudar (peso)':<24} {'peso':>8}  vagas")
        lines += [f"{s['gap']:<24} {s['weight']:>8}  {s['sent']:>5}" for s in f["study"]]
    lines.append(f"\n{f['no_score']} enviadas sem score; {f['score_from_feedback']} com score lido do Feedback; "
                 f"{f['shared_local_record']} linhas dividem a mesma pasta local (reaplicação).")
    if f["unknown_status"]:
        lines.append(f"ATENÇÃO: {len(f['unknown_status'])} status sem mapeamento em outcome.ALIASES, "
                     f"fora do funil: {sorted(set(f['unknown_status']))}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--from-json", help="read simplified rows from this file instead of Notion")
    ap.add_argument("--dump", help="save the fetched rows to this file")
    ap.add_argument("--out", default=str(ROOT / "documents" / "funnel.json"))
    args = ap.parse_args(argv)

    if args.from_json:
        rows = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
    else:
        token = load_token()
        if not token:
            print("NOTION_TOKEN não encontrado (variável de ambiente ou .env na raiz). "
                  "Crie uma integração interna em notion.so/profile/integrations e "
                  "compartilhe o banco 'Aplicações' com ela.", file=sys.stderr)
            return 1
        try:
            source_id = data_source_id()
            if not source_id:
                raise ValueError("tracker.notion.data_source_id vazio em profile/candidate.yaml")
            rows = [simplify(p) for p in fetch_pages(token, source_id)]
        except urllib.error.HTTPError as exc:
            print(f"Notion respondeu HTTP {exc.code}: {exc.read().decode(errors='replace')[:300]}", file=sys.stderr)
            return 1
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"Sem conexão com a API do Notion: {exc}", file=sys.stderr)
            return 1
        except (subprocess.CalledProcessError, ValueError, KeyError) as exc:
            print(f"Configuração inválida: {exc}", file=sys.stderr)
            return 1
        if args.dump:
            Path(args.dump).write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

    try:
        funnel = analyze(rows)
    except KeyError as exc:
        print(exc.args[0], file=sys.stderr)
        return 1
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(funnel, ensure_ascii=False, indent=1), encoding="utf-8")
    print(report(funnel))
    return 0


if __name__ == "__main__":
    sys.exit(main())
