#!/usr/bin/env python3
"""gupy_search.py — remote jobs from the public Gupy portal, in the linkedin-search JSON shape.

Gupy is the source that converts best in our own funnel (72% response, 4%
advance on 78 applications, against 34% / 0% on LinkedIn), yet it only ever
reached /daily through freehire. Its portal API is public and returns, per
posting, the full description and a structured workplaceType, so neither a
page fetch nor the logged-in "Remoto" badge check is needed.

The API ignores its own remote filter, so filtering happens here: remote only,
published within --days, and titles above the candidate's ceiling dropped
(same rule as /daily step 1). Blocked companies and dedup stay in /daily.

Usage:
  python3 scripts/gupy_search.py                     # default terms, 14 days
  python3 scripts/gupy_search.py --days 3 --term "desenvolvedor node" --term react
Prints {"meta": {...}, "results": [{id, title, company, location, date, url,
workplaceType, description, source}]}.
"""
import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta

API = "https://portal.gupy.io/api/job-search/jobs"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
PAGE = 100
MAX_PER_TERM = 500
DEFAULT_TERMS = ["desenvolvedor", "developer", "engenheiro de software", "software engineer",
                 "full stack", "fullstack", "back-end", "backend", "front-end", "frontend",
                 "react", "node", "programador"]
# Same ceiling as /daily step 1 (profile/candidate.yaml deal_breakers). A range
# that includes an accepted level ("Pleno/Sênior", "PL/SR") passes.
ABOVE_CEILING = re.compile(r"s[eê]nior|\bsr\b|especialista|specialist|\bstaff\b|\blead(?:er)?\b|principal|"
                           r"\bmaster\b|architect|arquitet|\biii\b|\biv\b|coordena|l[ií]der\b|gerente|"
                           r"\bmanager\b|\bhead\b", re.I)
# "PL/SQL" and "Middleware" are not levels.
ACCEPTED_IN_RANGE = re.compile(r"pleno|\bpl\b(?!\s*/?\s*sql)|j[uú]nior|\bjr\b|\bmid\b", re.I)


def above_ceiling(title):
    return bool(ABOVE_CEILING.search(title)) and not ACCEPTED_IN_RANGE.search(title)


def plain(description):
    text = re.sub(r"<(br|/p|/li|/h\d)\s*/?>", "\n", description or "", flags=re.I)
    return re.sub(r"[ \t]+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text))).strip()


def to_result(job):
    city, state = job.get("city") or "", job.get("state") or ""
    return {
        "id": str(job["id"]),
        "title": " ".join((job.get("name") or "").split()),
        "company": " ".join((job.get("careerPageName") or "").split()),
        "location": ", ".join(p for p in (city, state) if p) or "Brasil",
        "date": (job.get("publishedDate") or "")[:10],
        "url": (job.get("jobUrl") or "").split("?")[0],
        "workplaceType": job.get("workplaceType") or "",
        "description": plain(job.get("description")),
        "source": "gupy",
    }


def keep(job, since):
    return (job["workplaceType"] == "remote" and job["date"] >= since
            and not above_ceiling(job["title"]))


def fetch_term(term, opener=urllib.request.urlopen):
    # The API reports pagination.total == limit, so "total" can't end the loop:
    # a short (or empty) page does.
    jobs, offset = [], 0
    while offset < MAX_PER_TERM:
        url = f"{API}?{urllib.parse.urlencode({'jobName': term, 'limit': PAGE, 'offset': offset})}"
        with opener(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30) as resp:
            page = json.load(resp).get("data", [])
        jobs += page
        if len(page) < PAGE:
            break
        offset += PAGE
    return jobs


def search(terms, days, today=None, fetch=fetch_term):
    since = ((today or date.today()) - timedelta(days=days)).isoformat()
    by_id, failed = {}, []
    for term in terms:
        try:
            batch = fetch(term)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            failed.append(term)  # one flaky term must not cost the whole source
            print(f"Gupy: termo '{term}' falhou ({exc}), seguindo com os outros", file=sys.stderr)
            continue
        for raw in batch:
            by_id.setdefault(raw["id"], raw)
    results = [r for r in map(to_result, by_id.values()) if keep(r, since)]
    results.sort(key=lambda r: r["date"], reverse=True)
    return {"meta": {"source": "gupy", "terms": terms, "days": days, "scanned": len(by_id),
                     "count": len(results), "failed_terms": failed}, "results": results}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--term", action="append", help="search term (repeatable); default: a broad dev list")
    ap.add_argument("--days", type=int, default=14)
    args = ap.parse_args(argv)
    out = search(args.term or DEFAULT_TERMS, args.days)
    if out["meta"]["failed_terms"] and not out["meta"]["scanned"]:
        print("Gupy indisponível: todos os termos falharam.", file=sys.stderr)
        return 1
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
